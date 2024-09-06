import requests
import json

config = dict([])

for i in open("config", "r").readlines():
    config[i.split(" = ")[0]] = i.split(" = ")[1].split("\n")[0]

print("Введите тему")
topic = input()

messages = [
    {
        "role": "system",
        "text": "Ты ведущий текстового квеста. Он работает так: ты начинаешь рассказз, и говоришь пользователю только первую часть рассказа. Потом задаёшь ему вопрос, на который он должен ответить. Это может быть как выбор из трёх вариантов (1, 2, или 3). После этого отправляешь ему вторую часть рассказа которая строится учитывая его ответ. И так далее. Квест не должен никогда заканчиваться. Вы не должны отвечать за пользователя. Ещё раз напомнаю, что очень важно выводить за один ответ только одну часть рассказа"
    },
    {
        "role": "user", 
        "text": f"Тема рассказа - {topic}"
    }
]

prompt = {
    "modelUri": f"gpt://{config['ac_id']}/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 1,
        "maxTokens": "5000"
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
        "text": input()
    }
    messages.append(ans)