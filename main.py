import g4f

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
    print("Choose GPT model (3.5 or 4)")
elif (language == 2):
    print("Выберете модель GPT (3.5 или 4)")

gpt_model = input()

if (language == 1):
    if (not gpt_model in ["3.5", "4"]):
        print("There is no such option. I was too lazy to do while, so run the program again!!!")
        exit(0)
elif (language == 2):
    if (not gpt_model in ["3.5", "4"]):
        print("Такого варианта нет. Мне было лень делать while, так что запускайте программу снова!!!")
        exit(0)


