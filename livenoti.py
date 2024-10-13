import os
import time
import schedule
import logging
import argparse
from ping3 import ping
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Constants
FILE_PATH = "filelist.txt"
ONLINE_MESSAGE = "{} is online"
OFFLINE_MESSAGE = "{} is offline"
FILE_NOT_FOUND_MESSAGE = "File not found"
ADDED_DOMAIN_MESSAGE = "Added domain: {}"
CHECKING_DOMAIN_MESSAGE = "Checking domain: {}"
USAGE_MESSAGE = """Usage:
1. /adddomain <domain>: Add a new domain to be monitored.
2. /checkdomain <domain>: Check if a specific domain is online.
3. /checklist: Check all domains in the filelist.txt.
4. /help: Show this help message.
5. /setcredentials <token> <chat_id>: Set the bot token and chat ID.
"""

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = None
CHAT_ID = None
bot = None

def notify_telegram(message):
    if bot and CHAT_ID:
        bot.send_message(chat_id=CHAT_ID, text=message)

def check_host(host):
    response = ping(host)
    message = ONLINE_MESSAGE.format(host) if response else OFFLINE_MESSAGE.format(host)
    notify_telegram(message)

def clean_domain(domain):
    return domain.replace("https://", "").replace("http://", "").replace("www.", "")

def clean_and_check_host(domain):
    clean_domain_name = clean_domain(domain)
    check_host(clean_domain_name)

def handle_add_domain(update, context):
    if context.args:
        domain = context.args[0]
        clean_domain_name = clean_domain(domain)
        with open(FILE_PATH, "a") as file:
            file.write(f"{clean_domain_name}\n")
        notify_telegram(ADDED_DOMAIN_MESSAGE.format(clean_domain_name))
        clean_and_check_host(clean_domain_name)
    else:
        notify_telegram("Please provide a domain.")
        
def handle_single_domain(update, context):
    if context.args:
        domain = context.args[0]
        clean_and_check_host(domain)
        notify_telegram(CHECKING_DOMAIN_MESSAGE.format(domain))
    else:
        notify_telegram("Please provide a domain to check.")

def handle_file_list(update, context):
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            for line in file:
                domain = line.strip()
                if domain:  # Check for empty lines
                    clean_and_check_host(domain)
    else:
        notify_telegram(FILE_NOT_FOUND_MESSAGE)

def check_hosts_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                domain = line.strip()
                if domain:  # Check for empty lines
                    clean_and_check_host(domain)

schedule.every(1).hour.do(check_hosts_from_file, file_path=FILE_PATH)

def show_usage(update, context):
    notify_telegram(USAGE_MESSAGE)

def handle_set_credentials(update, context):
    global BOT_TOKEN, CHAT_ID, bot
    if len(context.args) == 2:
        BOT_TOKEN = context.args[0]
        CHAT_ID = context.args[1]
        bot = Bot(token=BOT_TOKEN)
        notify_telegram("Success!")
    else:
        notify_telegram("Please provide bot token and chat ID.")


def main():
    global bot
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("adddomain", handle_add_domain))
    dp.add_handler(CommandHandler("checkdomain", handle_single_domain))
    dp.add_handler(CommandHandler("checklist", handle_file_list))
    dp.add_handler(CommandHandler("help", show_usage))  
    dp.add_handler(CommandHandler("setcredentials", handle_set_credentials))  

    updater.start_polling()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Host Checker Bot")
    parser.add_argument("--token", type=str, help="Your Telegram Bot Token")
    parser.add_argument("--chat_id", type=str, help="Your Telegram Chat ID")
    args = parser.parse_args()

    if args.token and args.chat_id:
        BOT_TOKEN = args.token
        CHAT_ID = args.chat_id
        bot = Bot(token=BOT_TOKEN)
        main()
    else:
        print("Please provide both --token and --chat_id.")
