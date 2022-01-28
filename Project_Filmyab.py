from flask import Response, request, Flask
import json
import requests
import re
from bs4 import BeautifulSoup
import os


url = 'https://api.telegram.org/bot5266843431:AAGHOaV8ul_2YO3vJ82D9a0Nvne2jmahgVk/'
site_url = 'https://digimovie.bid/'

app = Flask(__name__)


def get_all_updates():
    response = requests.get(url + 'getUpdates')
    return response.json()


def get_last_update(all_updates):
    return all_updates['result'][-1]


def get_chat_id(last_update):
    return last_update['message']['chat']['id']


def get_name(last_update):
    return last_update['message']['from']['first_name']


def get_username(last_update):
    return last_update['message']['from']['username']


def get_message_id(last_update):
    return last_update['message']['message_id']


def get_text(last_update: dict):
    return last_update['message']['text']


def reply_message(chat_id, message_id, text):
    data = {
        'chat_id': chat_id,
        'text': text,
        'reply_to_message_id': message_id
    }
    return requests.get(url + 'sendMessage', data)


def send_message(chat_id, text):
    data = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.get(url + 'sendMessage', data)


def write_json(data, filename='favorite_list.json'):
    with open(filename, 'w') as target:
        json.dump(data, target, indent=4, ensure_ascii=False)


def read_json(filename='favorite_list.json'):
    with open(filename, 'r') as target:
        data = json.load(target)
    return data


favorite_list = dict()


def Search(text: str):
    text.replace(' ', '-')
    a = requests.get(site_url + '?s=' + text + '/').text
    b = re.findall('<a title=\"(د.+)\" href', a)
    name_f = []
    for i in range(7):
        if i >= 3:
            if 'دانلود انیمیشن' in b[i]:
                name_f.append(b[i].remove('دانلود انیمیشن'))
            elif 'دانلود فیلم' in b[i]:
                name_f.append(b[i].remove('دانلود فیلم'))
    response = ''
    for i in name_f:
        response += f'/{i}\n'
    return response


def describe_movie(text: str):
    text.replace(' ', '-')
    a = requests.get(site_url + text + '/').text
    my_dict = {
        'Name': text[1:],
        'IMDB Score': re.findall('\"ratingValue\": \"(.+)\"', a)[0],
        'Actors': re.findall('\"name\": \"(.+)\"', a)[:3],
        'Descript': re.findall('\"description\": \".+\"', a)[0][16:-1],
        'Download Link': re.findall('\"url\": \".+\"', a)[0][8:-1],
    }
    response = f''
    for i, j in my_dict.items():
        response += f'{i}: {j}\n'
    return response


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id = get_chat_id(msg)
        text = get_text(msg)
        name = get_name(msg)
        username = get_username(msg)
        message_id = get_message_id(msg)
        if text == '/start':
            send_message(chat_id, f'Hi {name}\n Welcome to IUST_Filmyab')
            send_message(chat_id, '''Click on /Favorite_List to see your favorite list or
                                  Click on /Search to search the movie you want')''')
        elif text == '/Favorite_List':
            if username not in favorite_list or len(favorite_list[username]) == 0:
                reply_message(chat_id, message_id, "You don't have any favorite movie!")
            else:
                my_list = favorite_list[username]
                response = ''
                for i in my_list:
                    response += i+'\n'
                reply_message(chat_id, message_id, response)
        elif text == '/Yes':
            if username not in favorite_list.keys():
                favorite_list[username].appened()
                reply_message(chat_id, message_id, 'Movie added to Your Favorite list')
        elif text == '/No':
            reply_message(chat_id, message_id, 'Ok :)')
        elif text == '/Search':
            reply_message(chat_id, message_id, "Please enter your movie's name")
        else:
            if text[0] == '/':
                favorite_movie = text[1:]
                send_message(chat_id, describe_movie(text[1:]))
                send_message(chat_id, '''Do you want to add this movie to your favorites list?
                /Yes
                /No''')
            else:
                reply_message(chat_id, message_id, Search(text))
        return Response('ok', status=200)
    else:
        return 'salam'


app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))


