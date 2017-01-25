'''
author: None.Pavel
email: pav.pnz@gmail.com
Description: this script uses for add torrent from telegram private chat. User under working daemon_bot
             need right for write in transmission directory
exapmple: $ python3 daemon_bot.py
'''
import requests
import time
import subprocess
import os
import lockfile
import daemon
import logging
import signal
import traceback
import configparser
logging.getLogger("urllib3").setLevel(logging.WARNING)


class MyDaemonBot:
    settings = configparser.ConfigParser()
    settings.read('settings.ini', encoding='utf-8')
    INTERVAL = settings.getint('DEFAULT', 'INTERVAL')
    ADMIN_ID = settings.getint('DEFAULT', 'ADMIN_ID')
    URL = settings.get('DEFAULT', 'URL')
    TOKEN = settings.get('DEFAULT', 'TOKEN')
    TRANSMISSION_LOGIN = settings.get('DEFAULT', 'TRANSMISSION_LOGIN')
    TRANSMISSION_PASS = settings.get('DEFAULT', 'TRANSMISSION_PASS')
    offset = 0  # ID latest received message
    MAGNET = 'magnet'

    def __init__(self):
        self.from_id = 'None'
        self.text = 'None'
        self.success = 'success'  # res = 0
        self.duplicate = 'duplicate'  # res = 1
        self.invalid = 'invalid'  # res = 2
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.log = logging.getLogger('RutackerBot')
        self.log.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler('ham.log')
        self.fh.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(self.formatter)
        self.log.addHandler(self.fh)
        self.log.info('START BOT')

    def run(self):
        while True:
            try:
                self.check_updates()
                time.sleep(5)
            except ConnectionError as e:
                self.log.error('Connerction Error')
                time.sleep(5)
            except (OSError, IOError) as e:
                bot.log.error(traceback.format_exc())
                time.sleep(5)
            except Exception as e:
                self.log.error('Exception: '.format(e.__class__.__name__))
                time.sleep(5)

    def reload_bot(self):
        self.log.info('Reload bot')

    def exit_bot(self):
        self.log.info('Exit bot')

    def check_updates(self):
        data = {'offset': MyDaemonBot.offset + 1, 'limit': 5, 'timeout': 0}  # request

        request = requests.post(MyDaemonBot.URL + MyDaemonBot.TOKEN + '/getUpdates', data=data)  # chek update

        if not request.status_code == 200:
            data = None
            return False

        # if response 'OK' that all ok :)
        if not request.json()['ok']:
            data = None
            return False

        data = None

        for update in request.json()['result']:  # Check element list
            MyDaemonBot.offset = update['update_id']  # Id messages

            # If in update not messages or in messages not test then pass
            if not 'message' in update or not 'text' in update['message']:
                self.log.error('Unknown update: {0}'.format(update))
                continue

            from_id = update['message']['chat']['id']  # Check id chat who send messages
            name = update['message']['chat']['username']  # Check username who send messages

            if from_id != MyDaemonBot.ADMIN_ID:  # if not admin
                self.send_text(from_id, "You're not authorized to use me!")
                self.log.error('not authorized user: '.format(update))
                continue

            message = update['message']['text']  # Check message

            parameters = (MyDaemonBot.offset, name, from_id, message)

            self.log.info('Message (id{0}) from {1} (id{2}): "{3}"'.format(*parameters))
            self.run_command(*parameters)

    def run_command(self, offest, name, from_id, cmd):
        if cmd == '/ping':  # ping
            self.send_text(from_id, 'pong')  # Отправка ответа

        elif cmd == '/help':  # help
            self.send_text(from_id, 'No help today. Sorry.')  # Ответ

        elif MyDaemonBot.MAGNET in cmd:  # add torrent
            self.send_text(from_id, 'try add torrent from magnet url')
            result = self.add_torrent(cmd)

            if result == 0:
                self.send_text(from_id, 'torrent add success')

            elif result == 1:
                self.send_text(from_id, 'duplicate torrent')

            elif result == 2:
                self.send_text(from_id, 'invalid torrent')

            elif result == 3:
                self.send_text(from_id, 'unknown error')
        else:
            self.send_text(from_id, 'Got it.')  # send answer

    def add_torrent(self, text):
        # example success add torrent: localhost:9091/transmission/rpc/ responded: "success"
        # example duplicate torrent: Error: duplicate torrent
        # example invalid or corrupt torrent: Error: invalid or corrupt torrent file

        res = -1
        self.text = text
        try:
            p1 = subprocess.Popen(["transmission-remote", "-n",
                                        MyDaemonBot.TRANSMISSION_LOGIN+":"+MyDaemonBot.TRANSMISSION_PASS, "-a",
                                        self.text],
                                       stdout=subprocess.PIPE).communicate()[0]
        except:
            self.log.error('error transmission remote')
            res = 2
            return res

        output = p1.decode('utf-8')
        if self.success in output:
            res = 0
            return res

        elif self.duplicate in output:
            res = 1
            return res

        elif self.invalid in output:
            res = 2
            return res

        else:
            res = 3  # res = 3 unknown result
            return res

    def send_text(self, chat_id, text):
        """ send test to chat_id
        ToDo: repeat if failed
        :param text: type string
        :param chat_id: type int id chat"""
        #self.chat_id = chat_id
        self.text = text
        self.log.info('Sending to {0}: {1}'.format(chat_id, text))
        data = {'chat_id': chat_id, 'text': text}
        request = requests.post(MyDaemonBot.URL + MyDaemonBot.TOKEN + '/sendMessage', data=data)
        if not request.status_code == 200:
            #data = None
            return False

        #data = None
        return request.json()['ok']

    def __str__(self):
        return '{}'.format(self.text)


if __name__ == "__main__":
    bot = MyDaemonBot()
    context = daemon.DaemonContext(
        working_directory=bot.path,
        umask=0o002,
        pidfile=lockfile.FileLock(bot.path + '/telegram_bot.pid'),
    )
    # exit()
    if context.pidfile.is_locked():
        exit('daemon is running now!')

    # context.signal_map = {
    #     signal.SIGTSTP: None,
    #     signal.SIGTTIN: None,
    #     signal.SIGTTOU: None,
    #     signal.SIGTERM: 'terminate',
    # }

    context.files_preserve = [bot.fh.stream]  # logging

    while True:
        try:
            with context:
                bot.run()
        except Exception as e:
            bot.log.error(traceback.format_exc())
            time.sleep(5)
