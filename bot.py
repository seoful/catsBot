import requests
import telebot
import json
import time
import db
from multiprocessing import *
import schedule

API_KEY = "1103395186:AAEjPT2Yo0Nc5KSGoJgYuDAbQdIXGTix0ys"
bot = telebot.TeleBot(API_KEY, threaded=False)
CREATOR_CHAT_ID = 377263029
AUTHOR_MARK = "Photo by <a href=\"{0}?&utm_source=CatSender&utm_medium=referral\">{1}</a> on <a " \
              "href=\"https://unsplash.com/?utm_source=CatsSendere&utm_medium=referral\">Unsplash</a> "
SAD_ID = "AgACAgIAAxkDAAIEtl6LASyDNzPq99scOMgDFK9niibeAAJQrDEbqYBZSARMTDqu88gxHILBDwAEAQADAgADbQADKmAGAAEYBA"


def get_photo(request):
    response = requests.get(
        "https://api.unsplash.com/photos/random?client_id=xqeRzqIeuPGTeFeRtw3_WvrAiGuce6p4-eTU9BuWZUs&count=1&query=" + request)
    if response.ok:
        photo_data = {}
        response = json.loads(response.text)
        response1 = response[0]["links"]["download_location"]
        response2 = requests.get(response1 + "?client_id=xqeRzqIeuPGTeFeRtw3_WvrAiGuce6p4-eTU9BuWZUs")
        response3 = response[0]["urls"]["regular"]
        response4 = requests.get(response3)
        photo_data["file"] = response4.content
        photo_data["username"] = response[0]["user"]["links"]["html"]
        print(photo_data["username"])
        photo_data["name"] = response[0]["user"]["name"]
        return photo_data
    else:
        return {'file': None}


def download_photo():
    return get_photo("cat")


def send_photo(chat_id, photo, error_chat_id, caption="", error_message=""):
    if photo["file"] is not None:
        return bot.send_photo(chat_id, photo["file"],
                              caption + "\n" + AUTHOR_MARK.format(
                                  photo["username"], photo["name"]),
                              parse_mode="HTML").photo[0].file_id
    else:
        bot.send_message(chat_id, error_message)
        return "error"


def scheduled_photo():
    photo = download_photo()
    ids = get_ids()
    if len(ids) > 0:
        file_id = send_photo(ids[0], photo, ids[0], "Good morning!",
                             "Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.However,have a nice "
                             "day!")
    ids.pop(0)
    if file_id != "error":
        for chat_id in ids:
            send_photo(chat_id, photo, chat_id, "Good morning!",
                       "Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.However,have a nice "
                       "day!")


def image_to_all(admin_id, caption="from admin with love"):
    local_photo = get_photo("cat")
    ids = get_ids()
    if len(ids) > 0:
        file_id = send_photo(admin_id, local_photo, admin_id, caption,
                             "something went wrong")
    ids.remove(str(admin_id) + "\n")
    if file_id != "error":
        for chat_id in ids:
            send_photo(chat_id, local_photo, chat_id, caption)


def text_to_all(admin_id, text):
    for chat_id in get_ids():
        bot.send_message(chat_id, text)


def count(admin_id):
    bot.send_message(admin_id, len(get_ids()))


class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


def get_ids():
    db.get_ids()
    with open("id.txt", "r+") as file:
        return file.readlines()


def add_id(chat_id):
    db.get_ids()
    flag = False
    with open("id.txt", "r+") as file:
        ids = file.readlines()
        if str(chat_id) + '\n' not in ids:
            file.write(str(chat_id) + '\n')
            flag = True
        else:
            flag = False
    if flag:
        db.write_to_pastebin()
    return flag


def delete_id(chat_id):
    db.get_ids()
    flag = False
    with open("id.txt", "r") as file:
        ids = file.readlines()
    if str(chat_id) + '\n' in ids:
        with open("id.txt", "w") as file:
            ids.remove(str(chat_id) + '\n')
            print(ids)
            for i in ids:
                file.write(str(i))

        flag = True
    else:
        flag = False
    if flag:
        db.write_to_pastebin()
    return flag


def send_ids(admin_id):
    db.get_ids()
    with open("id.txt") as file:
        if len(file.read()) > 3:
            bot.send_document(admin_id, file, disable_notification=True)


def log(message):
    print(str(message.from_user.username) + " " + message.text)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    log(message)
    bot.send_message(message.chat.id, "Write / to see commands")


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    log(message)
    if add_id(message.chat.id):
        photo = get_photo("cat")
        send_photo(message.chat.id, photo, message.chat.id,
                   "Thank you for subscribing to cat photo at 9AM every day.",
                   "Subscribed to cat photo at 9AM every day.")

        bot.send_message(CREATOR_CHAT_ID, "@" + str(message.from_user.username) + " sub",
                         disable_notification=True)
        # send_ids(CREATOR_CHAT_ID)

    else:
        bot.send_message(message.chat.id, "You are already subscribed")


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    log(message)
    if delete_id(message.chat.id):
        bot.send_photo(message.chat.id, SAD_ID, "You are now not subscribed")

        bot.send_message(CREATOR_CHAT_ID, "@" + str(message.from_user.username) + " unsub",
                         disable_notification=True)
        # send_ids(CREATOR_CHAT_ID)
    else:
        bot.send_message(message.chat.id, "You were not subscribed")


@bot.message_handler(commands=['cat'])
def send_cat(message):
    log(message)
    photo = get_photo("cat")
    send_photo(message.chat.id, photo, message.chat.id,
               error_message="Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.")
    # if photo is not None:
    #     bot.send_photo(message.chat.id, photo)
    # else:
    #     bot.send_message(message.chat.id,
    #                      "Error getting photo.Sorry( Maybe,we`ve run out of requests. Wait for an hour.")


@bot.message_handler(commands=['admin'])
def admin(message):
    log(message)
    args = message.text.split(" ")[1:]
    command = args[0]
    if command == "imageall":
        image_to_all(message.chat.id, (" ".join(args[1:])))
    elif command == "textall":
        text_to_all(message.chat.id, (" ".join(args[1:])))
    elif command == "count":
        count(message.chat.id)


schedule.every().day.at("04:00").do(scheduled_photo)

if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
