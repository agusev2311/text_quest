import g4f

debug_mode = True

print("Choose language\n1. English\n2. Русский")

try:
    language = int(input())
except:
    print("There is no such option. I was too lazy to do while, so run the program again!!!")
    exit(0)

if (not language in [1, 2]):
    print("There is no such option. I was too lazy to do while, so run the program again!!!")
    exit(0)

if (language == 1):
    print("Choose GPT model (g4f 3.5, g4f 4  gpt 4o mini)")
elif (language == 2):
    print("Выберете модель GPT (g4f 3.5, g4f 4 или gpt 4o mini)")

gpt_model = input()

if (language == 1):
    if (not gpt_model in ["3.5", "4"]):
        print("There is no such option. I was too lazy to do while, so run the program again!!!")
        exit(0)
elif (language == 2):
    if (not gpt_model in ["3.5", "4"]):
        print("Такого варианта нет. Мне было лень делать while, так что запускайте программу снова!!!")
        exit(0)

print("На какую тему вы хотите диалог (пример: моё путешествие в тёмном лесу)")
topic = input()

resp_eng = f"You are the host of a text quest. You must write the plot, and after each part of the story ask the user a question on which the continuation of the quest depends. This can be a choice of several options, or a free-form answer. The quest must contain inventory, a change of locations. You must also draw ASCII art before each answer. The player wants a story on the topic of «{topic}»."
resp_rus = f"Вы ведущий текстового квеста. Вы должны писать сюжет, и после каждой части рассказа задавать пользователю вопрос, от которого зависит продолжение квеста. Это может быть выбор из нескольких вариантов, или ответ в свободной форме. Квест должен содержать инвентарь, смену локаций. Также вы должны рисовать ASCII арт перед каждым ответом. Игрок хочет рассказ на тему «{topic}»."

dialog = []

while True:
    convers = "Ваш диалог с пользователем:"
    if dialog == []:
        convers = ""
    else:
        for i in dialog:
            convers += f"\n{i}"
    if debug_mode:
        print("===============")
        print("Dialog: ", end="")
        print(dialog)
        print("===============")
        print("Convers: " + convers)
        print("===============")
        print("Response: " + resp_rus + " " + convers)
        print("===============")

    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": resp_rus + " " + convers}],
        stream=True,
    )

    text = ""
    for message in response:
        text += message
    print(text)

    dialog.append(f"ChatGPT: {text}")
    ans = input()
    if (ans == "restart" and debug_mode):
        dialog == []
    else:
        dialog.append(f"User: {ans}")
