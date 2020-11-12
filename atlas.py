import json

import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError


class Atlas:
    def __init__(self):
        self.client = MongoClient(
            'mongodb+srv://seoful:florotp57@subscribers-rucm4.mongodb.net/test?retryWrites=true&w=majority')
        self.db = self.client['bot']
        self.users = self.db['users']

    def add_user(self, msg):
        try:
            self.users.insert_one({'chat_id': msg.chat.id,
                                   'first_name': msg.from_user.first_name,
                                   'last_name': msg.from_user.last_name,
                                   'username': msg.from_user.username,
                                   'id': msg.from_user.id,
                                   'timezone': "+00:00",
                                   'morning': True,
                                   'morning_type': 'photo',
                                   'morning_local_time': datetime(2020, 1, 1, 9, 0),
                                   'morning_utc_time': datetime(2020, 1, 1, 6, 0),
                                   'evening': False,
                                   'evening_type': 'gif',
                                   'evening_local_time': datetime(2020, 1, 1, 23, 0),
                                   'evening_utc_time': datetime(2020, 1, 1, 20, 0),
                                   'photo_queries': 0,
                                   'gif_queries': 0,
                                   'giphy_id': self.get_giphy_id(),
                                   })
            return True
        except DuplicateKeyError:
            return False

    def add_group(self, msg):
        try:
            self.users.insert_one({'chat_id': msg.chat.id,
                                   'id': -1,
                                   'chat_name': msg.chat.title,
                                   'timezone': "+00:00",
                                   'morning': False,
                                   'morning_type': 'photo',
                                   'morning_local_time': datetime(2020, 1, 1, 9, 0),
                                   'morning_utc_time': datetime(2020, 1, 1, 6, 0),
                                   'evening': False,
                                   'evening_type': 'gif',
                                   'evening_local_time': datetime(2020, 1, 1, 23, 0),
                                   'evening_utc_time': datetime(2020, 1, 1, 20, 0),
                                   'photo_queries': 0,
                                   'gif_queries': 0,
                                   'giphy_id': self.get_giphy_id(),
                                   })
            return True
        except DuplicateKeyError:
            return False

    def get_giphy_id(self):
        response = requests.get(
            "https://api.giphy.com/v1/randomid?api_key=Tne7LiT79HXXntOhyyXPzSDDuBAYMbJP&rating=G")
        if response.ok:
            json_response = json.loads(response.text)
            id = json_response["data"]["random_id"]
            return id
        else:
            print("error giphy id")
            return None

    def change_time(self, chat_id, query_type, time):
        time = self.parse_time(time)
        if time is False:
            return False
        else:
            local_time = datetime(2020, 1, 1, time['hour'], time['minute'])
            timezone = self.parse_timezone(self.users.find_one({'chat_id': chat_id})['timezone'])

            if timezone['sign'] == '+':
                utc_time = local_time - timezone['timedelta']
            else:
                utc_time = local_time + timezone['timedelta']

            utc_time = self.__normalize_date(utc_time)

            self.users.update_one({'chat_id': chat_id}, {
                "$set": {query_type + '_local_time': local_time,
                         query_type + '_utc_time': utc_time}})
            return True

    def change_hour(self, chat_id, when, hour):
        local_time = datetime(2020, 1, 1, int(hour),
                              self.users.find_one({'chat_id': chat_id})[when + '_local_time'].minute)
        timezone = self.parse_timezone(self.users.find_one({'chat_id': chat_id})['timezone'])

        if timezone['sign'] == '+':
            utc_time = local_time - timezone['timedelta']
        else:
            utc_time = local_time + timezone['timedelta']

        utc_time = self.__normalize_date(utc_time)

        self.users.update_one({'chat_id': chat_id}, {
            "$set": {when + '_local_time': local_time,
                     when + '_utc_time': utc_time}})

    def change_minute(self, chat_id, when, minute):
        local_time = datetime(2020, 1, 1, self.users.find_one({'chat_id': chat_id})[when + '_local_time'].hour,
                              int(minute))
        timezone = self.parse_timezone(self.users.find_one({'chat_id': chat_id})['timezone'])

        if timezone['sign'] == '+':
            utc_time = local_time - timezone['timedelta']
        else:
            utc_time = local_time + timezone['timedelta']

        utc_time = self.__normalize_date(utc_time)

        self.users.update_one({'chat_id': chat_id}, {
            "$set": {when + '_local_time': local_time,
                     when + '_utc_time': utc_time}})

    def change_timezone(self, chat_id, timezone):
        parsed_timezone = self.parse_timezone(timezone)
        if parsed_timezone is False:
            return False
        else:
            document = self.users.find_one({'chat_id': chat_id})
            morning_local_time = document['morning_local_time']
            evening_local_time = document['evening_local_time']
            if parsed_timezone['sign'] == '+':
                morning_utc_time = morning_local_time - parsed_timezone['timedelta']
                evening_utc_time = evening_local_time - parsed_timezone['timedelta']
            else:
                morning_utc_time = morning_local_time + parsed_timezone['timedelta']
                evening_utc_time = evening_local_time + parsed_timezone['timedelta']

            morning_utc_time = self.__normalize_date(morning_utc_time)
            evening_utc_time = self.__normalize_date(evening_utc_time)

            self.users.update_one({'chat_id': chat_id}, {
                '$set': {'timezone': timezone,
                         'morning_utc_time': morning_utc_time,
                         'evening_utc_time': evening_utc_time}})

    def change_type(self, chat_id, when, query_type):
        self.users.update_one({'chat_id': chat_id}, {'$set': {when + '_type': query_type}})

    def time(self, chat_id, when):
        time = self.users.find_one({'chat_id': chat_id})[when + '_local_time']
        h = time.hour
        m = time.minute
        if h < 10:
            hour = '0' + str(h)
        else:
            hour = str(h)
        if m < 10:
            min = '0' + str(m)
        else:
            min = str(m)
        return hour + ':' + min

    def timezone(self, chat_id):
        return self.users.find_one({'chat_id': chat_id})['timezone']

    def type(self, chat_id, when):
        return self.users.find_one({"chat_id": chat_id})[when + '_type']

    def enable_or_disable(self, chat_id, when, enable):
        self.users.update_one({'chat_id': chat_id}, {"$set": {when: enable}})

    def is_enabled(self, chat_id, when):
        return self.users.find_one({"chat_id": chat_id})[when]

    def increment(self, chat_id, query_type):
        self.users.update_one({'chat_id': chat_id}, {"$inc": {query_type + '_queries': 1}})

    def giphy_id(self, chat_id):
        return self.users.find_one({"chat_id": chat_id})["giphy_id"]

    def delete_user(self, chat_id):
        if self.users.count({'chat_id': chat_id}) != 0:
            self.users.delete_one({'chat_id', chat_id})
            return True
        else:
            return False

    def count_enable(self):
        morning = self.users.count({'morning': True})
        evening = self.users.count({'evening': True})
        return {'morning': morning,
                'evening': evening}

    def count_queries(self):
        photos = gifs = 0
        cursor = self.users.find()
        for user in cursor:
            photos += user['photo_queries']
            gifs += user['gif_queries']
        return {'photos': photos,
                'gifs': gifs}

    def count(self):
        return self.users.count()

    def count_personal(self, chat_id):
        photos = self.users.find_one({'chat_id': chat_id})['photo_queries']
        gifs = self.users.find_one({'chat_id': chat_id})['gif_queries']
        return {'photos': photos,
                'gifs': gifs}

    def all_users(self):
        users = self.users.find({'id': {'$ne': -1}})
        l = []
        for user in users:
            l.append(str(user))
        return l

    def all_groups(self):
        groups = self.users.find({'id': {'eq': -1}})
        l = []
        for user in groups:
            l.append(str(user))
        return l

    def get_ids(self):
        cursor = self.users.find({'id': {'$ne': -1}})
        chat_ids = []
        for user in cursor:
            chat_ids.append(user['chat_id'])
        return chat_ids

    def get_ids_for_sender(self):
        now = self.__normalize_date(datetime.now())
        print(now)
        cursor = self.users.find({'morning': True, "morning_utc_time": now})
        data = {}
        t = []
        for user in cursor:
            t.append({'chat_id': user['chat_id'],
                      'type': user['morning_type']})
        data['morning'] = t
        t = []
        cursor = self.users.find({'evening': True, "evening_utc_time": now})
        for user in cursor:
            t.append({'chat_id': user['chat_id'],
                      'type': user['evening_type']})
        data['evening'] = t
        return data

    @staticmethod
    def __normalize_date(datetime):
        datetime = datetime.replace(year=2020)
        datetime = datetime.replace(month=1)
        datetime = datetime.replace(day=1)
        datetime = datetime.replace(second=0)
        datetime = datetime.replace(microsecond=0)
        return datetime

    @staticmethod
    def parse_time(time):
        try:
            h = int(time.split(':')[0])
            m = int(time.split(':')[1])
            assert 0 <= h <= 23
            assert 0 <= m <= 59
            return {'hour': h,
                    'minute': m}
        except:
            return False

    @staticmethod
    def parse_timezone(time):
        try:
            sign = time[0]
            assert sign == '+' or sign == '-'
            times = time.split(':')

            hour = int(times[0])
            minute = int(times[1])
            assert -12 <= hour <= 12
            assert 0 <= minute <= 59
            if hour >= -3:
                sign = '+'
                td = timedelta(hours=hour + 3, minutes=minute)
            else:
                sign = '-'
                td = timedelta(hours=-1 * hour - 3, minutes=minute)
            timezone = {'sign': sign,
                        'timedelta': td}
            return timezone

        except:
            return False
