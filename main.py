import requests
import json
import telebot
from telebot import types
import sqlite3
import time
from threading import Thread

conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        messages TEXT,
        response TEXT,
        user_id TEXT
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
        INSERT INTO requests (messages, response, user_id) VALUES (?, ?, ?)
    ''', (json.dumps(messages), json.dumps(response), json.dumps(id)))
    conn.commit()
    conn.close()

config = dict([])

for i in open("config", "r").readlines():
    config[i.split(" = ")[0]] = i.split(" = ")[1].split("\n")[0]

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
    markup.add(button1, button2, button3, button4)
    while True:
        if (len(requests_queue) < 1):
            time.sleep(2)
            continue
        # print(requests_queue)
        bot.send_message(requests_queue[0][0], "Генерация...")
        msgs = requests_queue[0][1]
        ans = generate(msgs)
        save_request(msgs, ans, requests_queue[0][0])
        messages[int(requests_queue[0][0])].append(ans["result"]["alternatives"][0]["message"]["text"])
        bot.send_message(requests_queue[0][0], ans["result"]["alternatives"][0]["message"]["text"], reply_markup=markup)
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
    tf = True
    for i in requests_queue:
        print(i)
        if i[0] == call.from_user.id:
            tf = False
    if not tf:
        bot.send_message(call.message.chat.id, "Сейчас вы не можете сделать это действие, так как вы находитесь в очереди. Дождитесь пока вы выйдете из очереди.")
        return 0
    msgs = []
    if not (int(call.message.chat.id) in messages):
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