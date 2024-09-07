import requests
import json
import telebot
from telebot import types
import sqlite3

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
        bot.reply_to(message, "Генерация...")
        messages[int(message.chat.id)] = [f"Ты ведущий текстового квеста. Ты должен выдавать части квеста, после каждой задавай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4. Пользователь не определяет сюжет, а только выбирает собственные действия. Тема квеста: {topic}. Расскажи первую часть и задай первый вопрос."]
        msgs = [
            {
                "role": "user", 
                "text": f"Ты ведущий текстового квеста. Ты должен выдавать части квеста, после каждой задавай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4. Пользователь не определяет сюжет, а только выбирает собственные действия. Тема квеста: {topic}. Расскажи первую часть и задай первый вопрос."
            }
        ]
        ans = generate(msgs)
        save_request(msgs, ans, message.chat.id)
        messages[int(message.chat.id)].append(ans["result"]["alternatives"][0]["message"]["text"])
        bot.send_message(message.chat.id, ans["result"]["alternatives"][0]["message"]["text"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("1", callback_data='button1')
    button2 = types.InlineKeyboardButton("2", callback_data='button2')
    button3 = types.InlineKeyboardButton("3", callback_data='button3')
    button4 = types.InlineKeyboardButton("4", callback_data='button4')
    markup.add(button1, button2, button3, button4)
    msgs = []
    for i in range(len(messages[call.from_user.id])):
        if (i % 2 == 0):
            msgs.append({"role": "user", "text": messages[call.from_user.id][i]})
        else:
            msgs.append({"role": "assistant", "text": messages[call.from_user.id][i]})
    if call.data == 'button1':
        messages[int(call.from_user.id)].append("Игрок выбрал ответ 1. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button2':
        messages[int(call.from_user.id)].append("Игрок выбрал ответ 2. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button3':
        messages[int(call.from_user.id)].append("Игрок выбрал ответ 3. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    elif call.data == 'button4':
        messages[int(call.from_user.id)].append("Игрок выбрал ответ 4. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4.")
    bot.send_message(call.from_user.id, "Генерация...")
    ans = generate(msgs)
    save_request(msgs, ans, call.from_user.id)
    messages[int(call.from_user.id)].append(ans["result"]["alternatives"][0]["message"]["text"])
    bot.send_message(call.from_user.id, ans["result"]["alternatives"][0]["message"]["text"], reply_markup=markup)


@bot.message_handler(commands=["my_message"])
def start_quest(message):
    bot.send_message(message.chat.id, message)

bot.polling()