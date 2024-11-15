import telebot
import random
import schedule
import time
from threading import Thread
from datetime import datetime

bot = telebot.TeleBot("7714638685:AAEKNyXvkTz2l_ZaKR0Tg7bY-1kp6o-HwPA")

user_data = {}

# Функция для записи сообщения в файл
def log_message(chat_id, message):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"chat_{chat_id}_{date}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

@bot.message_handler(commands=['start'])
def start_message(message):
    list = [
        "зачем стартуешь, делать нечего?",
        "очень не рад тебя тут видеть, но можешь остаться",
        "склонись перед величием чат-бота",
        "ты попал в место, где логика отдыхает"
    ]
    random_priv = random.choice(list)
    bot.reply_to(message, f'Приветствую тебя, человечишко, {random_priv}')
    
    user_data['chat_id'] = message.chat.id
    log_message(message.chat.id, f"Пользователь @{message.from_user.username} запустил бота.")

def send_random_fact():
    chat_id = user_data.get('chat_id')
    if chat_id:
        with open("абсурдные_факты.txt", "r", encoding="utf-8") as f:
            факты = f.readlines()
        факт = random.choice(факты).strip()
        bot.send_message(chat_id, факт)
        log_message(chat_id, f"Отправлен случайный факт: {факт}")
    

schedule.every().day.at("08:00").do(send_random_fact)
schedule.every().day.at("12:00").do(send_random_fact)
schedule.every().day.at("18:00").do(send_random_fact)
schedule.every().day.at("20:00").do(send_random_fact)

# Функция, чтобы постоянно проверять расписание
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)  

Thread(target=run_schedule).start()

слова = [
    "ёлки-палки", "Сандаль", "Тракторина", "Медовуха", "Негр-вампир", 
    "Йогурт", "Шепоток", "Пипидастр", "Мухосранск", "Барабулька",
    "Боеголовка", "Московский авиационный институт", "Выхухоль", "Харчо", "Гондола",
    "Чечевица", "Бульдозер", "Рододендрон", "Пюпитр", "Тарталетка" 
]

@bot.message_handler(commands=['game1'])
def start_game1(message):
    user_data[message.chat.id] = {"game1_started": True}
    bot.reply_to(message, "Игра началась! Чтобы завершить игру напиши 'ты не умеешь играть в слова'")
    bot.reply_to(message, "Напиши любое слово:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["game1_started"])
def play_word_game1(message):
    chat_id = message.chat.id
    log_message(chat_id, f"Пользователь @{message.from_user.username} ввел: {message.text}")
    if message.text.lower() == "ты не умеешь играть в слова":
        user_data[message.chat.id]["game1_started"] = False
        bot.reply_to(message, "Сам дурак, это ты играть не умеешь! До встречи в следующей игре!")
        log_message(chat_id, "Игра /game1 завершена.")
        return

    bot_word = random.choice(слова)
    bot.reply_to(message, bot_word)
    log_message(message.chat.id, "Игра /game1 началась.")
    log_message(chat_id, f"Бот ответил: {bot_word}")

    

words = ["яблоко", "банан", "апельсин", "груша", "ананас"]

game2_data = {}

@bot.message_handler(commands=['game2'])
def start_game2(message):
    word = random.choice(words)
    hidden_word = ["_"] * len(word)
    game2_data[message.chat.id] = {"word": word, "hidden_word": hidden_word, "attempts": 0}
    bot.reply_to(message, f"Я загадал слово: {' '.join(hidden_word)}. Попробуй угадать буквы!")
    log_message(message.chat.id, "Игра /game2 началась.")

@bot.message_handler(func=lambda message: message.chat.id in game2_data)
def play_game2(message):
    chat_id = message.chat.id
    data = game2_data[chat_id]
    letter = message.text.lower()
    log_message(chat_id, f"Пользователь @{message.from_user.username} ввел букву: {letter}")


    if len(letter) != 1 or not letter.isalpha():
        bot.reply_to(message, "Введите одну букву.")
        return

    data["attempts"] += 1

    if letter in data["word"]:
        for idx, char in enumerate(data["word"]):
            if char == letter:
                data["hidden_word"][idx] = letter
        bot.reply_to(message, f"Отлично! {' '.join(data['hidden_word'])}")
        log_message(chat_id, "Пользователь угадал букву.")
    else:
        bot.reply_to(message, "Нет такой буквы. Подсказка: слово связано с фруктами.")
        log_message(chat_id, "Пользователь не угадал букву.")

    if "_" not in data["hidden_word"]:
        bot.reply_to(message, f"Поздравляю! Вы отгадали слово '{data['word']}' за {data['attempts']} попыток.")
        log_message(chat_id, f"Пользователь выиграл! Слово: {data['word']}. Попыток: {data['attempts']}")
        del game2_data[chat_id]

@bot.message_handler(commands=['stop'])
def stop_game2(message):
    if message.chat.id in game2_data:
        del game2_data[message.chat.id]
        bot.reply_to(message, "Игра остановлена. Напишите '/game2', чтобы начать заново.")
        log_message(message.chat.id, "Игра /game2 остановлена.")



@bot.message_handler(commands=['help'])
def help_message(message):
    myhelp = (
        "/start - начало работы бота\n"
        "/help - помощь\n"
        "/game1 - игра в слова\n"
        "/game2 - игра Угадай слово"
    )
    bot.reply_to(message, f'Я умею:\n{myhelp}')
    log_message(message.chat.id, "Пользователь запросил помощь.")


bot.polling(none_stop=True)
