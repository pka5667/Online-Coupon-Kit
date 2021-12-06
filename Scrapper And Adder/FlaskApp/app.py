# https://www.toptal.com/python/telegram-bot-tutorial-python
# https://djangostars.com/blog/how-to-create-and-deploy-a-telegram-bot/

import os
import threading
from flask import Flask, request
import requests
import telegram
from adders.adder import add_to_database
from time import sleep

global bot 
global TOKEN
global FLASK_APP_HOST_URL 

TOKEN = os.environ['BOT_TOKEN']
bot = telegram.Bot(token=TOKEN)
FLASK_APP_HOST_URL = os.environ['FLASK_APP_HOST_URL']

global added_courses_urls_list
added_courses_urls_list = []

global awake_thread
global keep_sending_message_thread
global scrap_add_thread_obj

# start the flask app 
app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global keep_sending_message_thread
    global scrap_add_thread_obj
    global added_courses_urls_list
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    try:
        if update.message:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
            text = update.message.text.encode('utf-8').decode()
        else:
            return "not ok"
    except Exception as e:
      print(e)
      return "not ok"

    # check the text recieved 
    if text == "/start":
        bot_welcome = "Welcome to OnlineCouponKit bot\n\nYou can add this bot to your channel for automatically posting new coupon code updates to your channel."
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id, parse_mode="markdown")
    elif text == "/time_left" and chat_id == int(os.environ['My_Telegram_Chat_id']):
        bot_msg = f"Time left in next message {keep_sending_message_thread.MESSAGE_SEND_AFTER}\nTime left in next scrap {scrap_add_thread_obj.SCRAP_ADD_AFTER}"
        bot.sendMessage(chat_id=chat_id, text=bot_msg, reply_to_message_id=msg_id, parse_mode="markdown")
    elif text == "/total_courses_left_to_send" and chat_id == int(os.environ['My_Telegram_Chat_id']):
        bot_msg = f"Total courses left in array to send are {len(added_courses_urls_list)}"
        bot.sendMessage(chat_id=chat_id, text=bot_msg, reply_to_message_id=msg_id, parse_mode="markdown")
    else:
        # bot.sendPhoto(chat_id=chat_id,photo=url, reply_to_message_id=msg_id)
        bot.sendMessage(chat_id=chat_id, text="Contact owner to add this bot to your channel to get daily updates about new coupon codes on your channel")

    return 'ok'



# WEBHOOK - It is a simple http request when something happens. sometimes an interaction between apps online requires immediate response to the event, while solutions for constant and continuous connections are mostly cumbersome, exacting and hard to support. In this case, the best and the easiest solution is immediate callback via HTTP (most often POST).
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot.setWebhook('{URL}{HOOK}'.format(URL=FLASK_APP_HOST_URL, HOOK=TOKEN))
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"



########### MORE FUNCTIONS #############


def keep_awake():
    while True:
        sleep(1500)
        requests.get(FLASK_APP_HOST_URL)
        requests.get("https://www.onlinecouponkit.tk/")
        requests.get("https://www.onlinecouponkit.tk/")


  
# SCRAP ADD THREAD CLASS
class Scrap_add_thread(threading.Thread):
    SCRAP_ADD_AFTER = 60 * 60 * 12

    def __init__(self):
       threading.Thread.__init__(self)
    

    def run(self):
        global added_courses_urls_list
        global keep_sending_message_thread
        while True:
            self.SCRAP_ADD_AFTER = 60 * 60 * 5
            while self.SCRAP_ADD_AFTER > 0:
                sleep(1)
                self.SCRAP_ADD_AFTER-=1
            try:
              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text= "Scrapping Sites") # to pka5667
              new_list = add_to_database()
              added_courses_urls_list = added_courses_urls_list + new_list
              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text=f"Scrapped GeeksGod and added {len(new_list)} courses to database") # to pka5667
              keep_sending_message_thread.MESSAGE_SEND_AFTER = 5
            except Exception as e:
              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text= e) # to pka5667


# MESSAGE SEND THREAD CLASS 
class Send_Message_Thread(threading.Thread):
    MESSAGE_SEND_AFTER = 60 * 60 * 6

    def __init__(self):
       threading.Thread.__init__(self)
    

    def run(self):
        global added_courses_urls_list
        while True:
            self.MESSAGE_SEND_AFTER = 60 * 60 * 5
            while self.MESSAGE_SEND_AFTER > 0: # after every 5 hours
                sleep(1)
                self.MESSAGE_SEND_AFTER -= 1
            try:
              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text=f"Sending message out of {len(added_courses_urls_list)}") # alert pka5667
              
              # if len(added_courses_urls_list) > 0:
              #     message = '>>*Udemy Coupon*\n\nNote : If coupon do not work try using VPN\n\nCreate New Account after connecting to VPN , and then apply coupon\n\n'
              #     for _ in range(min(5, len(added_courses_urls_list))):
              #         message = message + added_courses_urls_list[0] + "\n"
              #         added_courses_urls_list = added_courses_urls_list[1:]

              if len(added_courses_urls_list) > 0:
                  for _ in range(min(10, len(added_courses_urls_list))):
                    try:
                      message = added_courses_urls_list[0]['message']
                      photo_link = added_courses_urls_list[0]['thumbnail_url']
                      bot.send_photo(os.environ['My_Telegram_Channel_Chat_id'], photo_link, caption=message, parse_mode="markdown")# Send message to my channel
                      added_courses_urls_list = added_courses_urls_list[1:]
                    except Exception as e:
                      print(e)

                  bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text=f"Messages Sent Successfully Now left {len(added_courses_urls_list)} messages")

              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text=f"Nothing to send from {len(added_courses_urls_list)}")
            except Exception as e:
              bot.sendMessage(chat_id = os.environ['My_Telegram_Chat_id'], text= e) # to pka5667



# FUNCTION TO SEND MESSAGE FOR THE LEFT COURSE IN ADDED COURSE ARRAY IMMEDIATELY 
@app.route(os.environ['send_message_route']) # to send message right now
def send_message_to_channel_now():
    global keep_sending_message_thread
    keep_sending_message_thread.MESSAGE_SEND_AFTER = 5
    return "Sending Message immediately"
    


# FUNCTION TO SCRAP AND ADD COURSES FROM SITES 
@app.route('/scrap_and_add_course') # to srap right now
def scrap_and_add_course():
    global scrap_add_thread_obj
    scrap_add_thread_obj.SCRAP_ADD_AFTER = 5
    return "Scrapping and Addeding Queued"



@app.route('/')
def index():
    return 'Yes its working.'


# we cant use global variables in different threads it will only change in main thread if I will use route
awake_thread = threading.Thread(target=keep_awake)
keep_sending_message_thread = Send_Message_Thread()
scrap_add_thread_obj = Scrap_add_thread()

def main():
  global awake_thread
  global keep_sending_message_thread
  global scrap_add_thread_obj
  
  awake_thread.start()
  keep_sending_message_thread.start()
  scrap_add_thread_obj.start()

  app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
  main()

