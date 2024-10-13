import time , re ,os, schedule
from ping3 import ping
from telegram import Bot
from telegram.ext import Updater, CommandHandler

FILE_PATH='file.txt'
BOT_TOKEN=''
CHAT_ID=''

bot=Bot(token=BOT_TOKEN)

