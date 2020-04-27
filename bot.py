import requests
import telebot
import json
from datetime import datetime
from atlas import Atlas
from time import sleep
from threading import Thread
from templates import Templates

API_KEY = "1103395186:AAEjPT2Yo0Nc5KSGoJgYuDAbQdIXGTix0ys"
CREATOR_CHAT_ID = 377263029
AUTHOR_MARK = "Photo by <a href=\"{0}?&utm_source=CatSender&utm_medium=referral\">{1}</a> on <a " \
              "href=\"https://unsplash.com/?utm_source=CatSender&utm_medium=referral\">Unsplash</a> "
SAD_ID = "AgACAgIAAxkDAAIEtl6LASyDNzPq99scOMgDFK9niibeAAJQrDEbqYBZSARMTDqu88gxHILBDwAEAQADAgADbQADKmAGAAEYBA"

atlas = None
templates = None
bot = telebot.TeleBot(API_KEY)


def get_photo(request):
    print("getting photo")
    response = requests.get(
        "https://api.unsplash.com/photos/random?client_id=xqeRzqIeuPGTeFeRtw3_WvrAiGuce6p4-eTU9BuWZUs&count=1&query="
        + request)
    if response.ok:
        response = json.loads(response.text)
        download_location = response[0]["links"]["download_location"]
        requests.get(download_location + "?client_id=xqeRzqIeuPGTeFeRtw3_WvrAiGuce6p4-eTU9BuWZUs")
        url = response[0]["urls"]["regular"]
        photo = requests.get(url)
        file = photo.content
        username = response[0]["user"]["links"]["html"]
        name = response[0]["user"]["name"]
        caption = "\n" + AUTHOR_MARK.format(username, name)
        print("Photo got")
        return {'file': file,
                'caption': caption}
    else:
        print("error photo")
        return {'file': None}


def send_photo_unsplash(request, chat_id, caption=""):
    photo = get_photo(request)
    if photo['file'] is not None:
        try:
            msg = bot.send_photo(chat_id, photo['file'], caption + photo['caption'], parse_mode='HTML',
                                 reply_markup=templates.COMMAND_KEYBOARD())
            return {'file_id': msg.photo[0].file_id,
                    'caption': photo['caption']}
        except:
            bot.send_message(chat_id, "Error sending photo.Try again.", reply_markup=templates.COMMAND_KEYBOARD())
            return {'file_id': None}
    else:
        bot.send_message(chat_id, "Error getting photo.Try again.", reply_markup=templates.COMMAND_KEYBOARD())
        return {'file_id': None}


def send_photo_by_file_id(chat_id, photo, caption=""):
    if photo['file_id'] is not None:
        try:
            msg = bot.send_photo(chat_id, photo['file_id'], caption + photo['caption'], parse_mode='HTML',
                                 reply_markup=templates.COMMAND_KEYBOARD())
        except:
            bot.send_message(chat_id, "Error sending photo.Try again.")


def get_gif(request):
    print("getting gif")
    response = requests.get(
        "https://api.giphy.com/v1/gifs/random?api_key=Tne7LiT79HXXntOhyyXPzSDDuBAYMbJP&rating=G&tag=" + request)
    if response.ok:
        json_response = json.loads(response.text)
        url = json_response["data"]["images"]["downsized"]["url"]
        print('gif got')
        return url
    else:
        print("error gif")
        return None


def send_gif_from_giphy(request, chat_id, caption=""):
    gif = get_gif(request)
    if gif is not None:
        try:
            msg = bot.send_animation(chat_id, gif, caption=caption + "\nPowered by GIPHY",
                                     reply_markup=templates.COMMAND_KEYBOARD())
            return msg.animation.file_id
        except:
            bot.send_message(chat_id, "Error sending gif.Try again.", reply_markup=templates.COMMAND_KEYBOARD())
            return None
    else:
        bot.send_message(chat_id, "Error getting gif.Try again.", reply_markup=templates.COMMAND_KEYBOARD())
        return None


def send_gif_by_file_id(chat_id, file_id, caption=""):
    if file_id is not None:
        try:
            msg = bot.send_animation(chat_id, file_id, caption=caption + "\nPowered by GIPHY",
                                     reply_markup=templates.COMMAND_KEYBOARD())
        except:
            bot.send_message(chat_id, "Error sending gif.Try again.", reply_markup=templates.COMMAND_KEYBOARD())


def log(message):
    print(str(message.from_user.username) + " " + message.text)


class Sender(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self) -> None:
        sleep_time = 60
        while True:
            ids = atlas.get_ids_for_sender()
            morning = ids['morning']
            evening = ids['evening']
            for i in morning:
                chat_id = i['chat_id']
                if i['type'] == 'photo':
                    send_photo_unsplash('cat', chat_id, 'Good morning!')
                else:
                    send_gif_from_giphy('cat', chat_id, 'Good morning!')
            for i in evening:
                chat_id = i['chat_id']
                if i['type'] == 'photo':
                    send_photo_unsplash('cat sleep', chat_id, 'Good night!')
                else:
                    send_gif_from_giphy('cat sleep', chat_id, 'Good night!')

            sleep(sleep_time)


@bot.message_handler(commands=['start'])
def start(message):
    log(message)
    id = message.chat.id
    if atlas.add_user(message):
        bot.send_chat_action(id, "typing")
        send_photo_unsplash('cat', id, "Hello")
        sleep(1)
        bot.send_message(id, "I am a bot that sends you cats. Let's begin!")
        bot.send_chat_action(id, "typing")
        sleep(3)
        bot.send_message(id, 'Now, you will receive some settings that you may change.')
        bot.send_chat_action(id, "typing")
        sleep(3)
        bot.send_message(id, 'First af all, modify your timezone. ')
        bot.send_chat_action(id, "typing")
        sleep(3)
        bot.send_message(id, 'Also, you can turn on cat mailing, modify mailing time and '
                             'decide whether to get photo or gif every day')
        bot.send_chat_action(id, "typing")
        sleep(3)
        bot.send_message(id, 'Later you will be able to open settings by typing /settings '
                             'and see commands by typing /help')
        bot.send_chat_action(id, "typing")
        sleep(3)
        msg = templates.SETTINGS_INLINE()
        bot.send_message(id, msg['text'], reply_markup=msg['keyboard'])
    else:
        bot.send_message(id,
                         'You have already used this command.\n'
                         'To see commands, type /help\n'
                         'To modify bot, type /settings.')


@bot.message_handler(commands=['help'])
def help(message):
    log(message)
    bot.send_message(message.chat.id, "Here are commands you can use:\n"
                                      "/help - opens this menu\n"
                                      "/settings - opens settings menu\n"
                                      "/cat - sends you a photo of a cat\n"
                                      "/kitten - sends you a photo of a kitten\n"
                                      "/gif - sends you a gif with a cat\n"
                                      "/gif_kitten - sends you a gif with a kitten\n"
                                      "/statistics - sends you a little of your statistics")


@bot.message_handler(commands=['cat'])
def send_cat(message):
    log(message)
    bot.send_chat_action(message.chat.id, "upload_photo")
    send_photo_unsplash('cat', message.chat.id, )
    atlas.increment(message.chat.id, 'photo')


@bot.message_handler(commands=['kitten'])
def send_kitten(message):
    log(message)
    bot.send_chat_action(message.chat.id, "upload_photo")
    send_photo_unsplash('kitten', message.chat.id)
    atlas.increment(message.chat.id, 'photo')


@bot.message_handler(commands=['gif'])
def send_cat_gif(message):
    log(message)
    bot.send_chat_action(message.chat.id, "upload_photo")
    send_gif_from_giphy('cat', message.chat.id)
    atlas.increment(message.chat.id, 'gif')


@bot.message_handler(commands=['gif_kitten'])
def send_kitten_gif(message):
    log(message)
    bot.send_chat_action(message.chat.id, "upload_photo")
    send_gif_from_giphy('kitten', message.chat.id)
    atlas.increment(message.chat.id, 'gif')


@bot.message_handler(commands=['admin'])
def admin(message):
    log(message)
    args = message.text.split(" ")[1:]
    command = args[0]
    if message.chat.id != CREATOR_CHAT_ID:
        bot.send_message(message.chat.id, "You are not an admin.")
        return
    if command == 'stats':
        stats = atlas.count_enable()
        bot.send_message(message.chat.id, 'Morning: {0}\nEvening: {1}'.format(stats['morning'], stats['evening']))
    elif command == 'textall':
        m = ' '.join(args[1:])
        for id in atlas.get_ids():
            bot.send_message(id, m)
    elif command == 'imageall':
        m = ' '.join(args[1:])
        photo = send_photo_unsplash('cat', message.chat.id, m)
        ids = atlas.get_ids()
        ids.remove(message.chat.id)
        for id in ids:
            send_photo_by_file_id(id, photo, m)
    elif command == 'gifall':
        m = ' '.join(args[1:])
        gif = send_gif_from_giphy('cat', message.chat.id, m)
        ids = atlas.get_ids()
        ids.remove(message.chat.id)
        for id in ids:
            send_gif_by_file_id(id, gif, m)
    elif command == 'start':
        l = [348400632,
             379697872,
             486420525,
             405604496,
             460187408,
             256554535,
             432757640,
             413088395,
             457408035,
             491230672,
             569021825,
             127348025,
             437275821,
             363724806,
             388649178,
             245658683,
             423577489,
             331194061,
             377263029,
             425364439]
        for id in l:
            bot.send_message(id, "The bot was updated.\n"
                                 "To make him working, please write /start")
            bot.send_message(id, "Otherwise, it won`t be working")
            bot.send_message(id, "Try it NOW!!!!!!")


@bot.message_handler(commands=['settings'])
def send_settings(message):
    log(message)
    msg = templates.SETTINGS_INLINE()
    bot.send_message(message.chat.id, msg['text'], reply_markup=msg['keyboard'])


@bot.message_handler(commands=['statistics'])
def stats(message):
    log(message)
    statistics = atlas.count_personal(message.chat.id)
    bot.send_message(message.chat.id, "So far, you have received {0} photos and {1} gifs.".format(statistics['photos'],
                                                                                                  statistics['gifs']))


@bot.callback_query_handler(func=lambda c: c.data == 'back_to_settings')
def back_to_settings(c: telebot.types.CallbackQuery):
    message = c.message
    msg = templates.SETTINGS_INLINE()
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'])


@bot.callback_query_handler(func=lambda c: c.data == 'morning' or c.data == 'evening')
def sender_settings(c: telebot.types.CallbackQuery):
    message = c.message
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, c.data)
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data == 'timezone')
def timezone_settings(c: telebot.types.CallbackQuery):
    message = c.message
    msg = templates.TIMEZONE_SETTINGS_INLINE(message.chat.id)
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('change_timezone'))
def change_timezone_menu(c: telebot.types.CallbackQuery):
    message = c.message
    msg = templates.TIMEZONES_INLINE()
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('timezone_change'))
def change_timezone(c: telebot.types.CallbackQuery):
    message = c.message
    timezone = c.data.split('_')[2]
    atlas.change_timezone(message.chat.id, timezone)
    msg = templates.TIMEZONE_SETTINGS_INLINE(message.chat.id)
    bot.answer_callback_query(c.id, "Timezone is changed to MSK" + timezone)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('disable'))
def disable(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    atlas.enable_or_disable(message.chat.id, when, False)
    bot.answer_callback_query(c.id, "Your " + when + ' cat is disabled.')
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, when)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('enable'))
def enable(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    atlas.enable_or_disable(message.chat.id, when, True)
    bot.answer_callback_query(c.id, "Your " + when + ' cat is enabled.')
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, when)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('set'))
def change(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    query_type = c.data.split('_')[2]
    atlas.change_type(message.chat.id, when, query_type)
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, when)
    bot.answer_callback_query(c.id, "Your " + when + ' cat is set to ' + query_type)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data == 'change_morning' or c.data == 'change_evening')
def choose_hour(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    keyboard = templates.HOURS_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set hour:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('hour'))
def change_hour(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    h = c.data.split('_')[2]
    atlas.change_hour(message.chat.id, when, h)
    time = atlas.time(message.chat.id, when)
    bot.answer_callback_query(c.id, "Time is changed to " + time)


@bot.callback_query_handler(func=lambda c: c.data.startswith('go_to_min'))
def go_to_min(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[3]
    keyboard = templates.MINUTES_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set minute:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('go_to_hour'))
def go_to_hour(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[3]
    keyboard = templates.HOURS_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set hour:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('min'))
def change_minute(c: telebot.types.CallbackQuery):
    message = c.message
    when = c.data.split('_')[1]
    m = c.data.split('_')[2]
    atlas.change_minute(message.chat.id, when, m)
    time = atlas.time(message.chat.id, when)
    bot.answer_callback_query(c.id, "Time is changed to " + time)


if __name__ == '__main__':
    atlas = Atlas()
    templates = Templates(atlas)
    sender = Sender()
    sender.start()
    try:
        bot.polling(none_stop=True)
    except:
        pass
