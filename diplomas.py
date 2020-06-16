import requests

url = "http://rsr-olymp.ru/part"


class DiplomaChecker:
    def __init__(self):
        self.old_string = requests.get(url).text

    def content_has_changed(self):
        return requests.get(url).text != self.old_string


