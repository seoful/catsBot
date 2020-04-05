import requests
import telebot
import json
import time
import datetime
from multiprocessing import *
import schedule

API_KEY = "1103395186:AAEjPT2Yo0Nc5KSGoJgYuDAbQdIXGTix0ys"
bot = telebot.TeleBot(API_KEY)
CREATOR_CHAT_ID = 377263029


def get_photo(request):
    response = requests.get(
        "https://api.unsplash.com/photos/random?client_id=xqeRzqIeuPGTeFeRtw3_WvrAiGuce6p4-eTU9BuWZUs&count=1&query=" + request)
    if (response.ok):
        response = json.loads(response.text)
        response = response[0]["urls"]["regular"]
        return requests.get(response).content
    else:
        return None


photo = get_photo("cat")


def download_photo():
    global photo
    photo = get_photo("cat")


def scheduled_photo():
    for chat_id in get_ids():
        if photo is not None:
            bot.send_photo(chat_id, photo)
        else:
            bot.send_message(chat_id,
                             "Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.")


def to_all(admin_id,caption="from admin with love"):
    local_photo = get_photo("cat")
    if local_photo is not None:
        for chat_id in get_ids():
            bot.send_photo(chat_id, local_photo,caption)
    else:
        bot.send_message(admin_id, "Something went wrong")


class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


def get_ids():
    with open("id.txt", "r+") as file:
        return file.readlines()


def add_id(chat_id):
    with open("id.txt", "r+") as file:
        ids = file.readlines()
        print(ids)
        if str(chat_id) + '\n' not in ids:
            file.write(str(chat_id) + '\n')
            return True
        else:
            return False


def delete_id(chat_id):
    with open("id.txt", "r") as file:
        ids = file.readlines()
    if str(chat_id) + '\n' in ids:
        with open("id.txt", "w") as file:
            ids.remove(str(chat_id) + '\n')
            for i in ids:
                file.write(str(i))
        return True
    else:
        return False


@bot.message_handler(commands=['cat'])
def send_сat(message):
    photo = get_photo("cat")
    if photo is not None:
        bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id,
                         "Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.")


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    if add_id(message.chat.id):
        bot.send_message(message.chat.id,
                         "Subscribed to cat photo at 9AM every day. To unsubscribe send \\unsubscribe.")
    else:
        bot.send_message(message.chat.id, "You are already subscribed")


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    if delete_id(message.chat.id):
        bot.send_message(message.chat.id, "You are now not subscribed")
    else:
        bot.send_message(message.chat.id, "You were not subscribed")


@bot.message_handler(commands=['admin'])
@bot.message_handler(func=lambda msg: msg.chat.id == CREATOR_CHAT_ID)
def admin(message):
    args = message.text.split(" ")[1:]
    command = args[0]
    if command == "toall":
        to_all(message.chat.id,(" ".join(args[1:])))


# schedule.every(1).minute.do(send_photo_every_minute)
schedule.every().day.at("04:00").do(scheduled_photo)
schedule.every().day.at("19:01").do(download_photo)

if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
