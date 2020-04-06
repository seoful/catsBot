import requests
from lxml import etree


def get_user_key():
    key = requests.post("https://pastebin.com/api/api_login.php", data={
        'api_dev_key': 'c73edfdad88714d4bc3244ea28fcbaa5',
        'api_user_name': 'seoful',
        'api_user_password': 'florotp57'
    }).text
    return key


def get_paste_key():
    xml = requests.post(
        "https://pastebin.com/api/api_post.php", data={
            'api_dev_key': 'c73edfdad88714d4bc3244ea28fcbaa5',
            'api_option': 'list',
            'api_user_key': get_user_key(),
        }).text
    # print(xml)
    root = etree.fromstring("<p>\n" + xml + "\n</p>")

    for pastes in root.getchildren():
        dict = {}
        for elem in pastes.getchildren():
            dict[elem.tag] = elem.text
        if dict['paste_title'] == 'id':
            return dict['paste_key']


def write_to_pastebin():
    delete_paste()
    print("adding")
    with open("id.txt") as file:
        code = file.read()
    response = requests.post(
        "https://pastebin.com/api/api_post.php", data={
            'api_dev_key': 'c73edfdad88714d4bc3244ea28fcbaa5',
            'api_option': 'paste',
            'api_paste_code': code,
            'api_user_key': get_user_key(),
            'api_paste_name': 'id',
            'api_paste_private': 2
        })


def get_ids():
    print("getting ids")
    response = requests.post(
        "https://pastebin.com/api/api_raw.php", data={
            'api_dev_key': 'c73edfdad88714d4bc3244ea28fcbaa5',
            'api_paste_key': get_paste_key(),
            'api_user_key': get_user_key(),
            'api_option': 'show_paste'
        }).text
    print(response)
    with open("id.txt", 'w') as file:
        if len(response) > 3:
            file.write(response+'\n')


def delete_paste():
    print("deleting")
    response = requests.post(
        "https://pastebin.com/api/api_post.php", data={
            'api_dev_key': 'c73edfdad88714d4bc3244ea28fcbaa5',
            'api_option': 'delete',
            'api_paste_key': get_paste_key(),
            'api_user_key': get_user_key(),
        })
