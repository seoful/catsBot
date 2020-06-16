import requests
import telebot
import json
from atlas import Atlas
from time import sleep
from threading import Thread
from templates import Templates
from diplomas import DiplomaChecker

API_KEY = "1103395186:AAEjPT2Yo0Nc5KSGoJgYuDAbQdIXGTix0ys"
CREATOR_CHAT_ID = 377263029
AUTHOR_MARK = "Photo by <a href=\"{0}?&utm_source=CatSender&utm_medium=referral\">{1}</a> on <a " \
              "href=\"https://unsplash.com/?utm_source=CatSender&utm_medium=referral\">Unsplash</a> "

atlas = None
templates = None
diploma_checker = None
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
            msg = bot.send_photo(chat_id, photo['file'], caption + photo['caption'], parse_mode='HTML')
            return {'file_id': msg.photo[0].file_id,
                    'caption': photo['caption']}
        except:
            bot.send_message(chat_id, "Error sending photo.Try again.")
            return {'file_id': None}
    else:
        bot.send_message(chat_id, "Error getting photo.Try again.")
        return {'file_id': None}


def send_photo_by_file_id(chat_id, photo, caption=""):
    if photo['file_id'] is not None:
        try:
            msg = bot.send_photo(chat_id, photo['file_id'], caption + photo['caption'], parse_mode='HTML')
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
            msg = bot.send_animation(chat_id, gif, caption=caption + "\nPowered by GIPHY")
            return msg.animation.file_id
        except:
            bot.send_message(chat_id, "Error sending gif.Try again.")
            return None
    else:
        bot.send_message(chat_id, "Error getting gif.Try again.")
        return None


def send_gif_by_file_id(chat_id, file_id, caption=""):
    if file_id is not None:
        try:
            bot.send_animation(chat_id, file_id, caption=caption + "\nPowered by GIPHY")
        except:
            bot.send_message(chat_id, "Error sending gif.Try again.")


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
                    send_photo_unsplash('cat', chat_id, 'Good night!')
                else:
                    send_gif_from_giphy('cat', chat_id, 'Good night!')

            sleep(sleep_time)


class DiplomaSender(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self) -> None:
        sleep_time = 3600

        if diploma_checker.content_has_changed():
            bot.send_message(CREATOR_CHAT_ID, "Maybe, diplomas are available now!!!!!!!!")

        sleep(sleep_time)


@bot.message_handler(commands=['start'])
def start(message):
    log(message)
    chat_id = message.chat.id
    if message.chat.type == 'private':
        if atlas.add_user(message):
            bot.send_chat_action(chat_id, "typing")
            send_photo_unsplash('cat', chat_id, "Hello")
            sleep(1)
            bot.send_message(chat_id, "Cats are cool, you know. Let's begin!")
            bot.send_chat_action(chat_id, "typing")
            sleep(2)
            bot.send_message(chat_id, 'Now, you will receive some settings that you may change.')
            bot.send_chat_action(chat_id, "typing")
            sleep(2)
            bot.send_message(chat_id, 'First af all, modify your timezone.')
            bot.send_chat_action(chat_id, "typing")
            sleep(2)
            bot.send_message(chat_id, 'Also, you can turn on cat mailing, modify mailing time and '
                                      'decide whether to get photo or gif every day')
            bot.send_chat_action(chat_id, "typing")
            sleep(2)
            bot.send_message(chat_id, 'Later you will be able to open settings by typing /settings '
                                      'and see commands by typing /help')
            bot.send_chat_action(chat_id, "typing")
            sleep(2)
            bot.send_message(chat_id, 'Here is a keyboard for you', reply_markup=templates.COMMAND_KEYBOARD())
            sleep(2)
            msg = templates.SETTINGS_INLINE()
            bot.send_message(chat_id, msg['text'], reply_markup=msg['keyboard'])
        else:
            bot.send_message(chat_id,
                             'You have already used this command.\n'
                             'To see commands, type /help\n'
                             'To modify bot, type /settings.')
    elif message.chat.type == 'group' or message.chat.type == 'supergroup':
        if atlas.add_group(message):
            send_photo_unsplash('cat', chat_id, "Hello")
            sleep(1)
            msg = templates.SETTINGS_INLINE()
            bot.send_message(chat_id, msg['text'], reply_markup=msg['keyboard'])


@bot.message_handler(commands=['help'])
def send_help(message):
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
        mailing = atlas.count_enable()
        queries = atlas.count_queries()
        num = atlas.count()
        bot.send_message(message.chat.id,
                         'Users: {2}\nMorning: {0}\nEvening: {1}\nPhoto requests: {3}\nGif requests: {4}'.format(
                             mailing['morning'], mailing['evening'], num, queries['photos'], queries['gifs']))
    elif command == 'all':
        users = atlas.all_users()
        for user in users:
            bot.send_message(message.chat.id, user)
        groups = atlas.all_groups()
        for group in groups:
            bot.send_message(message.chat.id, group)

    elif command == 'textall':
        m = ' '.join(args[1:])
        for chat_id in atlas.get_ids():
            bot.send_message(chat_id, m)
    elif command == 'imageall':
        m = ' '.join(args[1:])
        photo = send_photo_unsplash('cat', message.chat.id, m)
        ids = atlas.get_ids()
        ids.remove(message.chat.id)
        for chat_id in ids:
            send_photo_by_file_id(chat_id, photo, m)
    elif command == 'gifall':
        m = ' '.join(args[1:])
        gif = send_gif_from_giphy('cat', message.chat.id, m)
        ids = atlas.get_ids()
        ids.remove(message.chat.id)
        for chat_id in ids:
            send_gif_by_file_id(chat_id, gif, m)


@bot.message_handler(commands=['settings'])
def send_settings(message):
    log(message)
    msg = templates.SETTINGS_INLINE()
    bot.send_message(message.chat.id, msg['text'], reply_markup=msg['keyboard'])


@bot.message_handler(commands=['statistics'])
def stats(message):
    log(message)
    statistics = atlas.count_personal(message.chat.id)
    bot.send_message(message.chat.id, "So far, you have asked for {0} photos and {1} gifs.".format(statistics['photos'],
                                                                                                   statistics['gifs']))


def check_admin_rights(c: telebot.types.CallbackQuery) -> bool:
    if c.message.chat.type == 'private':
        return True

    admins = bot.get_chat_administrators(c.message.chat.id)
    for i in range(len(admins)):
        admins[i] = admins[i].user.id

    if c.from_user.id not in admins:
        bot.answer_callback_query(c.id, 'You are not an admin to do this.')
        return False
    else:
        return True


@bot.callback_query_handler(func=lambda c: c.data == 'back_to_settings')
def back_to_settings(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    msg = templates.SETTINGS_INLINE()
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'])


@bot.callback_query_handler(func=lambda c: c.data == 'morning' or c.data == 'evening')
def sender_settings(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, c.data)
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data == 'timezone')
def timezone_settings(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    msg = templates.TIMEZONE_SETTINGS_INLINE(message.chat.id)
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('change_timezone'))
def change_timezone_menu(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    msg = templates.TIMEZONES_INLINE()
    bot.answer_callback_query(c.id)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('timezone_change'))
def change_timezone(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    timezone = c.data.split('_')[2]
    atlas.change_timezone(message.chat.id, timezone)
    msg = templates.TIMEZONE_SETTINGS_INLINE(message.chat.id)
    bot.answer_callback_query(c.id, "Timezone is changed to MSK" + timezone)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('disable'))
def disable(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[1]
    atlas.enable_or_disable(message.chat.id, when, False)
    bot.answer_callback_query(c.id, "Your " + when + ' cat is disabled.')
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, when)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('enable'))
def enable(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[1]
    atlas.enable_or_disable(message.chat.id, when, True)
    bot.answer_callback_query(c.id, "Your " + when + ' cat is enabled.')
    msg = templates.SENDER_SETTINGS_INLINE(message.chat.id, when)
    bot.edit_message_text(msg['text'], message.chat.id, message.message_id, reply_markup=msg['keyboard'],
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('set'))
def change(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
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
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[1]
    keyboard = templates.HOURS_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set hour:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('hour'))
def change_hour(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[1]
    h = c.data.split('_')[2]
    atlas.change_hour(message.chat.id, when, h)
    time = atlas.time(message.chat.id, when)
    bot.answer_callback_query(c.id, "Time is changed to " + time)


@bot.callback_query_handler(func=lambda c: c.data.startswith('go_to_min'))
def go_to_min(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[3]
    keyboard = templates.MINUTES_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set minute:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('go_to_hour'))
def go_to_hour(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[3]
    keyboard = templates.HOURS_INLINE(when)
    bot.answer_callback_query(c.id)
    bot.edit_message_text("Set hour:", message.chat.id, message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('min'))
def change_minute(c: telebot.types.CallbackQuery):
    if not check_admin_rights(c):
        return
    message = c.message
    when = c.data.split('_')[1]
    m = c.data.split('_')[2]
    atlas.change_minute(message.chat.id, when, m)
    time = atlas.time(message.chat.id, when)
    bot.answer_callback_query(c.id, "Time is changed to " + time)


if __name__ == '__main__':
    atlas = Atlas()
    templates = Templates(atlas)
    diploma_checker = DiplomaChecker()
    sender = Sender()
    sender.start()
    diploma_sender = DiplomaSender()
    diploma_sender.start()
    try:
        bot.polling(none_stop=True)
    except:
        pass
