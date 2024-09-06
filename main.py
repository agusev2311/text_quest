import requests
import json
import telebot

config = dict([])

for i in open("config", "r").readlines():
    config[i.split(" = ")[0]] = i.split(" = ")[1].split("\n")[0]

print("Введите тему")
topic = input()

messages = [
    # {
    #     "role": "system",
    #     "text": ""
    # },
    {
        "role": "user", 
        "text": f"Ты ведущий текстового квеста. Ты должен выдавать части квеста, после каждой задавай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4. Пользователь не определяет сюжет, а только выбирает собственные действия. Тема квеста: {topic}. Расскажи первую часть и задай первый вопрос."
    }
]

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

tokens = 0

while True:
    response = requests.post(url, headers=headers, json=prompt)
    result = json.loads(response.text)
    print(result)
    print(result["result"]["alternatives"][0]["message"]["text"])
    tokens += int(result["result"]["usage"]["totalTokens"])
    print("Input: " + result["result"]["usage"]["inputTextTokens"] + ", output:" + result["result"]["usage"]["completionTokens"])
    print("Всего потрачено токенов: " + str(tokens))
    mes = {
        "role": "assistant", 
        "text": result["result"]["alternatives"][0]["message"]["text"]
    }
    messages.append(mes)
    ans = {
        "role": "user", 
        "text": f"Игрок выбрал ответ {input()}. Расскажи следующую часть квеста и задай игроку вопрос с 4 вариантами ответа с номерами от 1 до 4."
    }
    messages.append(ans)