This demonazed bot for telegram privat chat. His use PEP 3143  -- Standard daemon process library
For start you need register on telegram bot used BotFather - https://core.telegram.org/bots
Then create chat on self bot, get and remeber your id - identification nubmer

After create in folder your scripts "settings.ini" and write sections "DEFAULT" and properties like this:

[DEFAULT]

INTERVAL = 3

ADMIN_ID = <ID>

URL = https://api.telegram.org/bot

TOKEN = <YOUR TOKEN BOT>

TRANSMISSION_LOGIN = <LOGIN TRANSMISSION>

TRANSMISSION_PASS =  <PASSWORD TRANSMISSION>

Save and exit

Then run pybot_telerent:

  $ python3 daemon_bot.py

check your working bot:
 
  $ ps aux | grep daemon_bot

kill your bot:

  $ kill <PID>

log in folder bot:

  $ tail -f ham.log


