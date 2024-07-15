import telebot
from telebot import types
import psycopg2


host="localhost"
user="postgres"
password="Ka2004-skor"
db_name="list_task"

connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

cursor = connection.cursor()
cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY ,
        first_name varchar(128) NOT NULL
        );
        """
    )
connection.commit()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS list_tasks(
    tasks VARCHAR(128) NOT NULL,
    user_id BIGINT NOT NULL,
    
    CONSTRAINT user_id_fk FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """
)
connection.commit()

bot=telebot.TeleBot('7124192846:AAFxRcgqD9lqv825ETnLZQVqk3QKhy-31O8')

@bot.message_handler(commands=['start','info'])
def main(message):
     bot.send_message(message.chat.id,f"Добро пожаловать, {message.from_user.first_name}, в планировщик своих дел 😜")
     markup=types.InlineKeyboardMarkup()
     btn1=types.InlineKeyboardButton("Добавить задачу",callback_data="add")
     btn2=types.InlineKeyboardButton("Вывести список задач",callback_data="tsk")
     markup.row(btn1,btn2)
     bot.send_message(message.chat.id,"В этом боте есть 2 доступные команды:",reply_markup=markup)

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, f"Введите ваши задачу, разделяя их точкой")
    bot.register_next_step_handler(message,write_user)
def write_user(message):
    task = message.text.split('. ')

    cursor.execute("INSERT INTO users (id,first_name) SELECT '%s','%s' WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = ('%s'))" % (message.from_user.id,message.from_user.first_name,message.from_user.id))
    connection.commit()
    for t in task:
        cursor.execute("INSERT INTO list_tasks (tasks,user_id) VALUES ('%s','%s')" % (t,message.from_user.id))
        connection.commit()
    bot.reply_to(message,"Задачи добавлены!")

@bot.message_handler(commands=['tsk'])
def tsk(message):
    try:
        cursor.execute("SELECT tasks FROM list_tasks WHERE user_id=('%s') " % (message.from_user.id))
        tasks = cursor.fetchall()
        inf = ''
        for el in tasks:
            inf += f'{el[0]}\n'
        bot.send_message(message.chat.id, inf)
    except:
        bot.send_message(message.chat.id,f"У вас не добавлено ни одной задачи")


def tsk_for_button(message):
    try:
        cursor.execute("SELECT tasks FROM list_tasks WHERE user_id=('%s') " % (message.from_user.id))
        tasks = cursor.fetchall()
        inf = ''
        for el in tasks:
            inf += f'{el[0]}\n'
        bot.send_message(message.message.chat.id, inf)
    except:
        bot.send_message(message.message.chat.id,f"У вас не добавлено ни одной задачи")

@bot.callback_query_handler(func=lambda callback:True)
def callback_message(callback):
    if callback.data =="add":
        add(callback.message)
    if callback.data == "tsk":
        tsk_for_button(callback)











bot.infinity_polling()