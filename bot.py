import re
import os
import time

import psycopg2
import telebot
from dotenv import load_dotenv
import paramiko
import logging

# запускаем логирование
log_handler = logging.FileHandler(filename='bot.log', encoding='utf-8')
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Старт бота')

# Загружаем информацию из .env файла

load_dotenv()

# Ubuntu_20

token = os.getenv('TOKEN')
rm_host = os.getenv('RM_HOST')
rm_port = os.getenv('RM_PORT')
rm_user = os.getenv('RM_USER')
rm_password = os.getenv('RM_PASSWORD')

# Данные о бд

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Данные реплики

db_repl_host = os.getenv('DB_REPL_HOST')
db_repl_port = os.getenv('DB_REPL_PORT')

# Стартовое сообщение + список возможных команд

start_text = ("Привет. Я бот студента по имени Пеньков Дмитрий. Мой функционал:\n"
              "1 часть:\n"
              "  /find_email - поиск email адресов в тексте\n"
              "  /find_phone_number - поиск телефонных номеров в тексте\n"
              "2 часть:\n"
              "  /verify_password {password} - проверка сложности пароля\n"
              "3 часть:\n"
              "  /get_release - информация о релизе.\n"
              "  /get_uname - информация об архитектуре процессора, имени хоста системы и версии ядра.\n"
              "  /get_uptime - информация о времени работы.\n"
              "  /get_df - информация о о состоянии файловой системы.\n"
              "  /get_free - информация о состоянии оперативной памяти.\n"
              "  /get_mpstat - информация о производительности системы.\n"
              "  /get_w - информация о работающих в данной системе пользователях.\n"
              "  /get_auths - информация о последних 10 входов в систему.\n"
              "  /get_critical - информация о последних 5 критических событиях.\n"
              "  /get_ps - информация о запущенных процессах.\n"
              "  /get_ss - информация об используемых портах.\n"
              "  /get_apt_list ?{package name} - информация об установленных пакетах (или о конкретном пакете).\n"
              "  /get_services - информация о запущенных сервисах.\n"
              "  /get_repl_logs - вывести логи о репликации.\n"
              "  /get_emails - вывести список сохранённых email адресов.\n"
              "  /get_phone_numbers - вывести список сохранённых телефонных номеров.")

cmd_list = [
    "/find_email",
    "/find_phone_number",
    "/verify_password",
    "/get_release",
    "/get_uname",
    "/get_uptime",
    "/get_df",
    "/get_free",
    "/get_mpstat",
    "/get_w",
    "/get_auths",
    "/get_critical",
    "/get_ps",
    "/get_ss",
    "/get_apt_list",
    "/get_services",
    "/get_repl_logs",
    "/get_emails",
    "/get_phone_numbers"
]

# Начинаем работу бота

bot = telebot.TeleBot(token)


# Функция для подключения к хосту по ssh, отправки ему команды и получения ответа

def exec_ssh_command(command):
    global rm_host
    global rm_port
    global rm_user
    global rm_password
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, port=int(rm_port), username=rm_user, password=rm_password)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


# Каждая функция выполняет соответствующее её названию действие
def find_email(msg):
    emails = re.findall(r'\S@{1}\S+\.{1}[A-Za-z]+', msg)
    if len(emails) > 0:
        return emails
    else:
        return "Ничего не найдено 😥"

def find_phone_number(msg):
    numbers = re.findall(r'\+?[78]\s?[(-]?\d{3}[)-]?\s?\d{3}-?\s?\d{2}-?\s?\d{2}', msg)
    if len(numbers) > 0:
        return numbers
    else:
        return "Ничего не найдено 😥"


def verify_password(password):
    if len(password) < 8:
        return "Пароль простой"
    elif len(re.findall(r'[A-Z]+', password)) == 0:
        return "Пароль простой"
    elif len(re.findall(r'[a-z]+', password)) == 0:
        return "Пароль простой"
    elif len(re.findall(r'\d+', password)) == 0:
        return "Пароль простой"
    elif len(re.findall(r'[!@#$%^&*()]+', password)) == 0:
        return "Пароль простой"
    else:
        return "Пароль сложный"


def get_release():
    return exec_ssh_command("cat /etc/os-release")


def get_uname():
    return exec_ssh_command("uname -a")


def get_uptime():
    return exec_ssh_command("uptime")


def get_df():
    return exec_ssh_command("df -h")


def get_free():
    return exec_ssh_command("free -h")


def get_mpstat():
    return exec_ssh_command("mpstat")


def get_w():
    return exec_ssh_command("w")


def get_auths():
    return exec_ssh_command("last -10")


def get_critical():
    return exec_ssh_command("journalctl -p crit -n 5")


def get_ps():
    return exec_ssh_command("ps")


def get_ss():
    return exec_ssh_command("ss -lntu")


def get_apt_list_all():
    return exec_ssh_command("apt list")


def get_apt_list_single(pkg):
    return exec_ssh_command("apt-cache show " + pkg)


def get_services():
    return exec_ssh_command("service  --status-all | grep \"[+]\"")


def get_repl_logs():
    global db_user
    global db_password
    global rm_port
    global db_host
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=db_host, port=int(rm_port), username=db_user, password=db_password)
    stdin, stdout, stderr = client.exec_command(
        'sudo cat /var/log/postgresql/postgresql.log | grep -i \"repl_user\" | tail -20')
    # stdin, stdout, stderr = client.exec_command(
    #     'whoami')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def get_emails(host, database, user, password):
    conn = psycopg2.connect(dbname=database, user=user, password=password, host=host)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM emails;')
    records = "\n".join(row[0] for row in cursor.fetchall())
    cursor.close()
    conn.close()
    return str(records)

def get_phone_numbers(host, database, user, password):
    conn = psycopg2.connect(dbname=database, user=user, password=password, host=host)
    cursor = conn.cursor()
    cursor.execute('SELECT number FROM phone_numbers;')
    records = "\n".join(row[0] for row in cursor.fetchall())
    cursor.close()
    conn.close()
    return str(records)


# функция вставки в бд

def insert_into_db(table, column, values):
    global db_database
    global db_host
    global db_user
    global db_password
    conn = psycopg2.connect(dbname=db_database, user=db_user, password=db_password, host=db_host)
    cursor = conn.cursor()
    for value in values:
        cursor.execute(f'INSERT INTO {table} ({column}) VALUES (\'{value}\');')
        print(value)
    conn.commit()
    cursor.close()
    conn.close()


# Начало общения с ботом


@bot.message_handler(commands=['start'])
def start(message):
    global start_text
    global cmd_list
    logging.info(f'Получено сообщение: {message.text}')
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in cmd_list:
        markup.add(telebot.types.KeyboardButton(cmd))
    bot.send_message(message.from_user.id, start_text, reply_markup=markup)


# Обработка комманд, полученных ботом

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global db_host
    global db_password
    global db_user
    global db_database
    global rm_port
    global db_repl_host
    global cmd_list
    request = message.text
    logging.debug(f'Получено сообщение: {request}')

    # "/find_email"
    if request == cmd_list[0]:
        try:
            bot.send_message(message.from_user.id, 'Введите ваш текст:')

            @bot.message_handler(content_types=['text'])
            def message_input_step(message):
                emails = find_email(message.text)
                if type(emails) == type([]):
                    msg = "Найденные email:\n" + "\n".join(email for email in emails)
                    bot.reply_to(message, msg)
                    logging.info(f'Получен ответ: {msg}')

                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(telebot.types.KeyboardButton("Да"))
                    markup.add(telebot.types.KeyboardButton("Нет"))
                    bot.send_message(message.from_user.id,
                                     'Сохранить найденные адреса?',
                                     reply_markup=markup)
                    logging.info(f'Получен ответ: Сохранить найденные адреса?')

                    @bot.message_handler(content_types=['text'])
                    def message_input_step(message):
                        global cmd_list

                        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                        for cmd in cmd_list:
                            markup.add(telebot.types.KeyboardButton(cmd))

                        logging.info(f'Получено сообщение: {message.text}')
                        if message.text == 'Да':
                            try:
                                insert_into_db('emails', 'email', emails)
                                bot.send_message(message.from_user.id,
                                                 'Успех!',
                                                 reply_markup=markup)
                                logging.info(f'Получен ответ: Успех')
                            except Exception as e:
                                bot.send_message(message.from_user.id,
                                                 f'Произощла ошибка:\n{e}',
                                                 reply_markup=markup)
                                logging.error(f'Ошибка: {e}')

                    bot.register_next_step_handler(message, message_input_step)
                else:
                    bot.reply_to(message, emails)
            bot.register_next_step_handler(message, message_input_step)
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/find_phone_number"
    elif request == cmd_list[1]:
        try:
            bot.send_message(message.from_user.id, 'Введите ваш текст:')

            @bot.message_handler(content_types=['text'])
            def message_input_step(message):
                numbers = find_phone_number(message.text)
                if type(numbers) == type([]):
                    msg = "Найденные номера:\n" + "\n".join(number for number in numbers)
                    bot.reply_to(message, msg)
                    logging.info(f'Получен ответ: {msg}')

                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(telebot.types.KeyboardButton("Да"))
                    markup.add(telebot.types.KeyboardButton("Нет"))
                    bot.send_message(message.from_user.id,
                                     'Сохранить найденные номера?',
                                     reply_markup=markup)
                    logging.info(f'Получен ответ: Сохранить найденные номера?')

                    @bot.message_handler(content_types=['text'])
                    def message_input_step(message):
                        global cmd_list

                        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                        for cmd in cmd_list:
                            markup.add(telebot.types.KeyboardButton(cmd))

                        logging.info(f'Получено сообщение: {message.text}')
                        if message.text == 'Да':
                            try:
                                insert_into_db('phone_numbers', 'number', numbers)
                                bot.send_message(message.from_user.id,
                                                 'Успех!',
                                                 reply_markup=markup)
                                logging.info(f'Получен ответ: Успех')
                            except Exception as e:
                                bot.send_message(message.from_user.id,
                                                 f'Произощла ошибка:\n{e}',
                                                 reply_markup=markup)
                                logging.error(f'Ошибка: {e}')

                    bot.register_next_step_handler(message, message_input_step)
                else:
                    bot.reply_to(message, numbers)
            bot.register_next_step_handler(message, message_input_step)
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/verify_password"
    elif request == cmd_list[2]:
        try:
            bot.send_message(message.from_user.id, 'Введите ваш текст:')

            @bot.message_handler(content_types=['text'])
            def message_input_step(message):
                msg = verify_password(message.text)
                bot.reply_to(message, msg)

            bot.register_next_step_handler(message, message_input_step)
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_release"
    elif request == cmd_list[3]:
        try:
            msg = get_release()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_uname"
    elif request == cmd_list[4]:
        try:
            msg = get_uname()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_uptime"
    elif request == cmd_list[5]:
        try:
            msg = get_uptime()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_df"
    elif request == cmd_list[6]:
        try:
            msg = get_df()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_free"
    elif request == cmd_list[7]:
        try:
            msg = get_free()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_mpstat"
    elif request == cmd_list[8]:
        try:
            msg = get_mpstat()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_w"
    elif request == cmd_list[9]:
        try:
            msg = get_w()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_auths"
    elif request == cmd_list[10]:
        try:
            msg = get_auths()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_critical"
    elif request == cmd_list[11]:
        try:
            msg = get_critical()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_ps"
    elif request == cmd_list[12]:
        try:
            msg = get_ps()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_ss"
    elif request == cmd_list[13]:
        try:
            msg = get_ss()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_apt_list"
    elif request == cmd_list[14]:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("Все"))
        markup.add(telebot.types.KeyboardButton("Конкретный"))
        bot.send_message(message.from_user.id, 'Вы хотите вывести все пакеты или получить информацию об определённом?',
                         reply_markup=markup)

        @bot.message_handler(content_types=['text'])
        def message_input_step(message):
            global cmd_list

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for cmd in cmd_list:
                markup.add(telebot.types.KeyboardButton(cmd))
            try:
                logging.info(f'Получено сообщение: {message.text}')
                if message.text == "Все":
                    # Сначала сохраняем весь список, а потом выводим по частям из-за лимита длинны сообщения + задержки чтобы не заблокировали
                    msg = get_apt_list_all()
                    for i in range(0, len(msg), 4096):
                        time.sleep(1)
                        bot.send_message(message.from_user.id, msg[i:min(i + 4096, len(msg) - 1)], reply_markup=markup)
                    logging.info(f'Получен ответ: {msg}')
                elif message.text == "Конкретный":
                    bot.send_message(message.from_user.id, 'Введите название пакета:', reply_markup=markup)

                    @bot.message_handler(content_types=['text'])
                    def message_input_step(message):
                        msg = get_apt_list_single(message.text)
                        bot.reply_to(message, msg)
                        logging.info(f'Получен ответ: {msg}')

                    bot.register_next_step_handler(message, message_input_step)
                else:
                    bot.send_message(message.from_user.id, 'Ошибка в вводе', reply_markup=markup)
                    logging.info(f'Получен ответ: Ошибка в вводе')
            except Exception as e:
                logging.error(f'Ошибка: {e}')

        bot.register_next_step_handler(message, message_input_step)

    # "/get_services"
    elif request == cmd_list[15]:
        try:
            msg = get_services()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_repl_logs"
    elif request == cmd_list[16]:
        try:
            msg = get_repl_logs()
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}')

    # "/get_emails"
    elif request == cmd_list[17]:
        try:
            msg = get_emails(db_host, db_database, db_user, db_password)
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}. Пробую подключиться к реплике.')
            try:
                msg = get_emails(db_host, db_database, db_user, db_password)
                bot.send_message(message.from_user.id, msg)
                logging.info(f'Получен ответ: {msg}')
            except Exception as e:
                logging.error(f'Ошибка: {e}. Пробую подключиться к реплике.')

    # "/get_phone_numbers"
    elif request == cmd_list[18]:
        try:
            msg = get_phone_numbers(db_host, db_database, db_user, db_password)
            bot.send_message(message.from_user.id, msg)
            logging.info(f'Получен ответ: {msg}')
        except Exception as e:
            logging.error(f'Ошибка: {e}. Пробую подключиться к реплике.')
            try:
                msg = get_phone_numbers(db_host, db_database, db_user, db_password)
                bot.send_message(message.from_user.id, msg)
                logging.info(f'Получен ответ: {msg}')
            except Exception as e:
                logging.error(f'Ошибка: {e}. Пробую подключиться к реплике.')

    # Ввёл что-то не то
    else:
        msg = "Попробуйте ввести известную команду..."
        bot.send_message(message.from_user.id, msg)


bot.polling(none_stop=True, interval=0)
