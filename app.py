from flask import Flask, render_template, request
import telebot
import random
import schedule
import time
from threading import Thread
from datetime import datetime
import mysql.connector
import pandas as pd
import os
import datetime
import json
from sql_table import SQLTable

pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

app = Flask(__name__)
app.config['SECRET_KEY'] = '234569876'

# Database configuration (MySQL)
db_config = {
    'user': 'Ekaterina Puzankova',
    'password': 'EkaterinaPuzankova!!!',
    'host': 'LAPTOP-VJNPBOQI',
    'database': 'polzovateli_bota'
}
cnx = mysql.connector.connect(**db_config)

# Проверка подключения
if cnx.is_connected():
    print("Соединение с базой данных установлено.")
else:
    print("Ошибка подключения к базе данных.")
    exit()

cursor = cnx.cursor()

# Bot setup
TOKEN = '7714638685:AAEKNyXvkTz2l_ZaKR0Tg7bY-1kp6o-HwPA'  # Replace with your bot token
bot = telebot.TeleBot(TOKEN)

# Create SQLTable instance for users table
users_table = SQLTable(db_config, 'users')  
facts_table = SQLTable(db_config, 'facts') 


user_data = {} 

# Logging function
def log_message(chat_id, message):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"chat_{chat_id}_{date}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

# Send message function
def send_message(chat_id, text):
    bot.send_message(chat_id, text)

def get_user_data(chat_id):
    user_row = users_table.select_row_by_id(chat_id)
    if not user_row.empty:
        return user_row.to_dict(orient='records')[0]['data']
    return {}

def update_user_data(chat_id, data):
    users_table.update_column_by_id(chat_id, 'data', json.dumps(data))

def create_user(chat_id, username):
    users_table.insert_row({'chat_id': chat_id, 'username': username, 'data': '{}'})

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    username = message.from_user.username

    # Проверяем, существует ли пользователь в базе данных
    user_data = get_user_data(chat_id)
    if user_data:
        # Пользователь существует, просто приветствуем его
        list = [
            "зачем стартуешь, делать нечего?",
            "очень не рад тебя тут видеть, но можешь остаться",
            "склонись перед величием чат-бота",
            "ты попал в место, где логика отдыхает"
        ]
        random_priv = random.choice(list)
        bot.reply_to(message, f'Приветствую тебя, человечишко, {random_priv}')
    else:
        # Новый пользователь, создаем его в базе данных
        create_user(chat_id, username)
        bot.reply_to(message, 'Приветствую тебя, новичок! Я чат-бот, готов тебе помочь.')

    log_message(message.chat.id, f"Пользователь @{message.from_user.username} запустил бота.")

def send_random_fact():
    facts = facts_table.select_all_rows()
    if not facts.empty:
        # Выбираем случайный факт из базы данных
        fact = facts.sample(n=1).to_dict(orient='records')[0]['fact']
        
        # Получаем ID чата, которому нужно отправить факт
        # Используем ID чата из базы данных, если он задан
        chat_id = facts.sample(n=1).to_dict(orient='records')[0].get('chat_id', None)

        # Если чат не задан, выбираем случайного пользователя
        if chat_id is None:
            users = users_table.select_all_rows()
            if not users.empty:
                chat_id = users.sample(n=1).to_dict(orient='records')[0]['chat_id']

        # Отправляем факт, если удалось получить chat_id
        if chat_id:
            bot.send_message(chat_id, fact)
            log_message(chat_id, f"Отправлен случайный факт: {fact}")

# Расписание отправки фактов
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
    log_message(chat_id, "Игра /game1 началась.")
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

    
    # Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Проверяем, существует ли пользователь в базе данных
    user_data = get_user_data(message.chat.id)
    if not user_data:
        # Если пользователь не найден, создаем его
        create_user(message.chat.id, message.from_user.username)
        user_data = get_user_data(message.chat.id)

    # Доступ к данным пользователя
    print(f"user_data: {user_data['data']}")  # Вывод данных пользователя
    # Обработка сообщений
    if message.text.lower() == 'привет':
        bot.reply_to(message, 'И тебе привет!')
    elif message.text.lower() == 'пока':
        bot.reply_to(message, 'Пока-пока!')
    else:
        bot.reply_to(message, f"Извини, не понимаю: {message.text}")
    log_message(message.chat.id, f"Пользователь @{message.from_user.username} написал: {message.text}")

# Маршрут для основного веб-интерфейса
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для отправки сообщений боту
@app.route('/send_message', methods=['POST'])
def send_message_to_bot():
    chat_id = request.form['chat_id']
    message_text = request.form['message']

    # Проверка валидности chat_id
    if chat_id and chat_id.isdigit():
        send_message(int(chat_id), message_text)
        return 'Сообщение отправлено'
    else:
        return 'Неверный chat_id'
    
# Функция для отображения таблицы пользователей
@app.route('/view_users')
def view_users():
    # Соединение с MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Запрос на выбор данных из таблицы users
    cursor.execute("SELECT * FROM users")

    # Получение данных в виде списка словарей
    users_data = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor]

    # Закрытие соединения
    cursor.close()
    cnx.close()

    # Отображение данных в таблице
    return render_template('view_users.html', users=users_data)

# Запускаем приложение Flask
if __name__ == '__main__':
    app.run(debug=True)
    # Запускаем бота в отдельном потоке
    bot.polling(none_stop=True)

