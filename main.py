import requests
import json
import telebot
from telebot import types
import sqlite3
import time
from threading import Thread
import datetime

import datetime

# код для запроса для фото-нейросети

import time
import base64

from random import randint as r
from random import choice as ch

import os

try:
    os.mkdir(os.getcwd().replace("\\", "/") + f'/' + 'result')
except:
    pass

config = dict([])

for i in open("config", "r").readlines():
    config[i.split(" = ")[0]] = i.split(" = ")[1].split("\n")[0]
    
class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)
def gen_photo(prom):
    dirr = "result"
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', dict['API_key_for_kandinsky'], dict['secret_key_kandinskiy'])
    # print(api.get_model())
    model_id = api.get_model()
    uuid = api.generate(prom, model_id)
    images = api.check_generation(uuid)

    # Здесь image_base64 - это строка с данными изображения в формате base64
    image_base64 = images[0]

    # Декодируем строку base64 в бинарные данные
    image_data = base64.b64decode(image_base64)

    # Открываем файл для записи бинарных данных изображения
    try:
        with open(f"{dirr}/0.jpg", "wb") as file:
            file.write(image_data)
    except:
        remove(f"{dirr}/0.jpg")
        with open(f"{dirr}/0.jpg", "w+") as file:
            file.write(image_data)

# конец
"""
zapros = промпт

    try:
        os.mkdir(os.getcwd().replace("\\", "/") + f'/' + zapros.replace("\n", " ").split(".")[0])
    except FileExistsError:
        print('exist')

    gen_photo(zapros.replace("\n", " ")+', реализм, вид от первого лица, без текста', zapros.replace("\n", " ").split(".")[0])
"""

def check_request_limit(user_id):
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    current_time = datetime.datetime.now()
    one_hour_ago = current_time - datetime.timedelta(hours=1)
    cursor.execute('''
        SELECT COUNT(*) FROM requests
        WHERE user_id = ? AND time > ?
    ''', (user_id, one_hour_ago))
    request_count = cursor.fetchone()[0]
    conn.close()
    max_requests_per_hour = int(config['max_requests_per_hour'])
    if request_count >= max_requests_per_hour:
        return False
    return True

conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        messages TEXT,
        response TEXT,
        user_id TEXT,
        time TEXT
    )
''')
conn.commit()
conn.close()

global requests_queue
requests_queue = []

def save_request(messages, response, id):
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO requests (messages, response, user_id, time) VALUES (?, ?, ?, ?)
    ''', (json.dumps(messages), json.dumps(response), json.dumps(id), datetime.datetime.now()))
    conn.commit()
    conn.close()


bot = telebot.TeleBot(config["telegram_token"])

def generate(messages):
    prompt = {
        "modelUri": f"gpt://{config['ac_id']}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 1,
            "maxTokens": config['max_tokens']
        },
        "messages": messages
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-key {config['secret_key']}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = json.loads(response.text)
    return result

def gen_2():
    global requests_queue
    global messages
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("1", callback_data='button1')
    button2 = types.InlineKeyboardButton("2", callback_data='button2')
    button3 = types.InlineKeyboardButton("3", callback_data='button3')
    button4 = types.InlineKeyboardButton("4", callback_data='button4')
    markup.add(button1, button2)
    markup.add(button3, button4)
    while True:
        try:
            if (len(requests_queue) < 1):
                time.sleep(2)
                continue
            bot.send_message(requests_queue[0][0], "Генерация...")
            msgs = requests_queue[0][1]
            ans = generate(msgs)


            zapros = ans["result"]["alternatives"][0]["message"]["text"]

           

            gen_photo(zapros.replace("\n", " ")+', реализм, вид от первого лица, без текста')


            
            save_request(msgs, ans, requests_queue[0][0])
            messages[int(requests_queue[0][0])].append(ans["result"]["alternatives"][0]["message"]["text"])
            bot.send_photo(requests_queue[0][0], "")
            bot.send_message(requests_queue[0][0], ans["result"]["alternatives"][0]["message"]["text"], reply_markup=markup, parse_mode="markdown")
            
            
            if int(ans["result"]["usage"]["totalTokens"]) > 7200:
                bot.send_message(requests_queue[0][0], "Ваш запрос преодалел предел в 7200 токенов. Ваш диалог был сброшен")
                messages[int(requests_queue[0][0])] = []
            requests_queue.pop(0)
        except:
            try:
                bot.send_message(requests_queue[0][0], "При обработке запроса произошла ошибка. Попробуйте отправить запрос ещё раз.")
            except:
                pass
            requests_queue.pop(0)
        time.sleep(2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """Привет! Я бот, который ведёт текстовый квест. В процессе игры ты будешь принимать решения, выбирая один из предложенных вариантов ответов. Каждый выбор будет влиять на дальнейшее развитие сюжета. Чтобы начать квестна пишите /start_quest <тема квеста>

Если ты столкнешься с ошибками или у тебя возникнут вопросы, пожалуйста, напиши об этом @agusev2311. Приятной игры!
""")

messages = dict([])

@bot.message_handler(commands=["start_quest"])
def start_quest(message):
    tags = message.text.split()
    if (len(tags)) == 1:
        bot.send_message(message.chat.id, """Эта команда позволяет запускать новый рассказ. Чтобы его запустить напишите /start_quest и тему рассказа

Пример:
/start_quest Как спасти планету от нашествия бананов""")
    else:
        if not check_request_limit(message.from_user.id):
            bot.send_message(message.chat.id, f"За последний час вы отправили больше {config['max_requests_per_hour']} реквестов.")
            return
        topic = message.text[message.text.find(" ")+1:]
        
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("1", callback_data='button1')
        button2 = types.InlineKeyboardButton("2", callback_data='button2')
        button3 = types.InlineKeyboardButton("3", callback_data='button3')
        button4 = types.InlineKeyboardButton("4", callback_data='button4')
        markup.add(button1, button2, button3, button4)

        tf = True
        for i in requests_queue:
            if i[0] == message.from_user.id:
                tf = False
            elif i[0] == message.chat.id:
                tf = False
        if not tf:
            bot.send_message(message.chat.id, "Сейчас вы не можете сделать это действие, так как вы находитесь в очереди. Дождитесь пока вы выйдете из очереди.")
            return 0

        if (len(requests_queue) > 0):
            bot.reply_to(message, f"Вы добавлены в очередь. Перед вами {len(requests_queue)} реквест(ов/а)")
        else:
            pass
        messages[int(message.chat.id)] = [f"Ты ведущий текстового квеста. Ты должен выдавать части квеста, после каждой задавай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4. Пользователь не определяет сюжет, а только выбирает собственные действия. Тема квеста: {topic}. Расскажи первую часть и задай первый вопрос."]
        msgs = [
            {
                "role": "user", 
                "text": f"Ты ведущий текстового квеста. Ты должен выдавать части квеста, после каждой задавай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4. Пользователь не определяет сюжет, а только выбирает собственные действия. Тема квеста: {topic}. Расскажи первую часть и задай первый вопрос."
            }
        ]
        requests_queue.append([message.chat.id, msgs])


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if not check_request_limit(call.from_user.id):
            bot.send_message(call.message.chat.id, f"За последний час вы отправили больше {config['max_requests_per_hour']} реквестов.")
            return
    tf = True
    for i in requests_queue:
        if i[0] == call.from_user.id:
            tf = False
        elif i[0] == call.message.chat.id:
            tf = False
    if not tf:
        bot.send_message(call.message.chat.id, "Сейчас вы не можете сделать это действие, так как вы находитесь в очереди. Дождитесь пока вы выйдете из очереди.")
        return 0
    msgs = []
    if not (int(call.message.chat.id) in messages):
        bot.send_message(call.message.chat.id, f"У вас нету истории запросов. Скорее всего бот был перезагружен, а при перезагрузке вся история переписок удаляется. Попробуйте начать квест заново. Если вам нужна история вашей переписки с ботом вы можете обратьтиться ко мне (@agusev2311)!")
        return
    if messages[call.message.chat.id] == []:
        bot.send_message(call.message.chat.id, f"У вас нету истории запросов. Скорее всего бот был перезагружен, а при перезагрузке вся история переписок удаляется. Попробуйте начать квест заново. Если вам нужна история вашей переписки с ботом вы можете обратьтиться ко мне (@agusev2311)!")
        return
    if call.data == 'button1':
        messages[int(call.message.chat.id)].append("Игрок выбрал ответ 1. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button2':
        messages[int(call.message.chat.id)].append("Игрок выбрал ответ 2. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button3':
        messages[int(call.message.chat.id)].append("Игрок выбрал ответ 3. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button4':
        messages[int(call.message.chat.id)].append("Игрок выбрал ответ 4. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    for i in range(len(messages[call.message.chat.id])):
        if (i % 2 == 0):
            msgs.append({"role": "user", "text": messages[call.message.chat.id][i]})
        else:
            msgs.append({"role": "assistant", "text": messages[call.message.chat.id][i]})
    if (len(requests_queue) > 0):
        bot.send_message(call.message.chat.id, f"Вы добавлены в очередь. Перед вами {len(requests_queue)} реквест(ов/а)")
    else:
        pass
    requests_queue.append([call.message.chat.id, msgs])


@bot.message_handler(commands=["my_message"])
def start_quest(message):
    bot.send_message(message.chat.id, message)

generate_thread = Thread(target=gen_2)
generate_thread.start()

bot.polling(none_stop=True)
