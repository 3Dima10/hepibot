import telebot
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from info import get_info

TOKEN = '7634814709:AAElSEd3C758Y9X6XS4sZx84pnE_GeWDK7k'
bot = telebot.TeleBot(TOKEN)

group_chat_id = None  # Глобальная переменная для хранения идентификатора чата группы

def check_birthdays():
    today = datetime.now().strftime("%d-%m")
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT `user-name` FROM hepi WHERE `date` = ?", (today,))
    users = cursor.fetchall()
    conn.close()
    return users

def name_to_id():
    users = check_birthdays()
    user_ids = []
    for user in users:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT `name` FROM hepi WHERE `user-name` = ?", (user[0],))
        user_id = cursor.fetchone()
        conn.close()
        if user_id:
            user_ids.append(user_id[0])
    return user_ids

def send_birthday_messages():
    if group_chat_id is None:
        print("Group chat ID is not set.")
        return

    users = check_birthdays()
    name_user = name_to_id()
    if users:
        for user in users:
            bot.send_message(group_chat_id, f'{name_user} {get_info()} , @{user[0]}!')
    # else:
    #     bot.send_message(group_chat_id, "Сегодня нет дней рождения.")

@bot.message_handler(commands=['start'])
def start(message):
    global group_chat_id
    group_chat_id = message.chat.id
    bot.send_message(group_chat_id, 'Привет, бот запущен. Теперь я буду поздравлять с днём рождения!')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n/start - Запуск бота\n/help - Помощь")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_birthday_messages, 'cron', hour=0, minute=0)  # Запуск каждый день в полночь
    scheduler.start()
    
    print('Бот запущен')
    bot.polling(none_stop=True)
    print('Бот остановлен')
