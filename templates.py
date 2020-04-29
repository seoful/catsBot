from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from atlas import Atlas


class Templates:
    def __init__(self, atlas: Atlas):
        self.atlas = atlas
        self.timezones = ['-01:00', '+00:00', '+01:00', '+02:00', '+03:00', '+04:00', '+05:00', '+06:00', "+07:00",
                          "+08:00", "+09:00"]

    def COMMAND_KEYBOARD(self) -> ReplyKeyboardMarkup:
        item_cat = KeyboardButton('/cat')
        item_gif = KeyboardButton('/gif')
        item_kitten = KeyboardButton('/kitten')
        item_gif_kitten = KeyboardButton('/gif_kitten')
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        keyboard.add(item_cat, item_gif)
        keyboard.row(item_kitten, item_gif_kitten)
        return keyboard

    def SETTINGS_INLINE(self):
        morning_btn = InlineKeyboardButton('Morning cat settings', callback_data='morning')
        evening_btn = InlineKeyboardButton('Evening cat settings', callback_data='evening')
        timezone_btn = InlineKeyboardButton('Timezone settings', callback_data='timezone')
        keyboard = InlineKeyboardMarkup().row(morning_btn, evening_btn)
        keyboard.row(timezone_btn)
        return {'text': 'Here are some settings for you:',
                'keyboard': keyboard}

    def SENDER_SETTINGS_INLINE(self, chat_id, when):
        is_enabled = self.atlas.is_enabled(chat_id, when)
        query_type = self.atlas.type(chat_id, when)
        time = self.atlas.time(chat_id, when)

        if is_enabled:
            e_str = 'enabled'
            en_btn = InlineKeyboardButton('Disable', callback_data='disable_' + when)
        else:
            e_str = 'disabled'
            en_btn = InlineKeyboardButton('Enable', callback_data='enable_' + when)
        if query_type == 'photo':
            t_btn = InlineKeyboardButton('Send gif instead', callback_data='set_' + when + '_gif')
        else:
            t_btn = InlineKeyboardButton('Send photo instead', callback_data='set_' + when + '_photo')

        text = "Your *{3}* cat *{2}* is *{0}*\nTime is set to *{1}*".format(e_str, time, query_type, when)
        change_btn = InlineKeyboardButton('Change time', callback_data='change_' + when)
        back_btn = InlineKeyboardButton('<<Back to settings', callback_data='back_to_settings')
        keyboard = InlineKeyboardMarkup().row(en_btn, change_btn).row(back_btn, t_btn)
        return {'text': text,
                'keyboard': keyboard}

    def TIMEZONE_SETTINGS_INLINE(self, chat_id):
        timezone = self.atlas.timezone(chat_id)
        text = 'Your timezone is set to *MSK' + timezone + '*'

        change_btn = InlineKeyboardButton('Change timezone', callback_data='change_timezone')
        back_btn = InlineKeyboardButton('<<Back to settings', callback_data='back_to_settings')
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.row(change_btn)
        keyboard.row(back_btn)
        return {'text': text,
                'keyboard': keyboard}

    def HOURS_INLINE(self, when):
        back_btn = InlineKeyboardButton('<<Back', callback_data=when)
        go_to_min_btn = InlineKeyboardButton('Change minutes >>', callback_data='go_to_min_' + when)
        keyboard = InlineKeyboardMarkup(row_width=6)
        for i in range(4):
            s = []
            for j in range(6):
                h = 6 * i + j
                s.append(InlineKeyboardButton(str(h), callback_data='hour_' + when + '_' + str(h)))
            keyboard.row(s[0], s[1], s[2], s[3], s[4], s[5])
        keyboard.row(back_btn, go_to_min_btn)

        return keyboard

    def MINUTES_INLINE(self, when):
        back_btn = InlineKeyboardButton('<<Back', callback_data=when)
        go_to_min_btn = InlineKeyboardButton('<<Change hour', callback_data='go_to_hour_' + when)

        keyboard = InlineKeyboardMarkup(row_width=6)
        for i in range(2):
            s = []
            for j in range(6):
                m = 30 * i + 5 * j
                s.append(InlineKeyboardButton(str(m), callback_data='min_' + when + '_' + str(m)))
            keyboard.row(s[0], s[1], s[2], s[3], s[4], s[5])
        keyboard.row(go_to_min_btn, back_btn)

        return keyboard

    def TIMEZONES_INLINE(self):
        back_btn = InlineKeyboardButton('<<Back', callback_data='timezone')
        keyboard = InlineKeyboardMarkup(row_width=2)

        for i in range(5):
            keyboard.row(
                InlineKeyboardButton("MSK" + self.timezones[i], callback_data="timezone_change_" + self.timezones[i]),
                InlineKeyboardButton("MSK" + self.timezones[6 + i],
                                     callback_data="timezone_change_" + self.timezones[6 + i]))
        keyboard.row(
            InlineKeyboardButton("MSK" + self.timezones[5], callback_data="timezone_change_" + self.timezones[5]),
            back_btn)
        return {'text': 'Choose timezone:',
                'keyboard': keyboard}
