from math import ceil

from datetime import datetime
import pymysql
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

connection = pymysql.connect(host='localhost',
                             user='u2302856_default',
                             password='46oqSFjiF5TsQqu6',
                             database='u2302856_default',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

bot = telebot.TeleBot('6940155807:AAGYmedNi6fRVyCmP5OPplRZZg2DRNnRy9k')

start_text = '''Привет, я Himera Bot. С моей помощью, ты можешь:
Расчитать стоимость товара🧮
Посмотреть стоимость доставки🚚
Заказать себе что нибудь🛍️
Посмотреть отзывы или оставить свой💬'''


def log(id, type_e, text=None):
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE tg_id = {id}')
        db_user = cursor.fetchone()
    if not db_user:
        with connection.cursor() as cursor:
            print(f'INSERT INTO Users (tg_id) VALUE ({id})')
            cursor.execute(f'INSERT INTO Users (tg_id) VALUE ({id})')
            connection.commit()
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM Users')
            db_user = cursor.fetchone()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO History  (user, type, msg, data) VALUE ({str(db_user["id"])}, {type_e}, "{text}", "{str(datetime.now())}")')
        connection.commit()


def curs():
    with open('/var/www/u2302856/data/www/himerastore.ru/kurs.txt', 'r') as f:
        return float(f.read())


def send_error(id, text):
    bot.send_message(id, f'ERROR:\n{text}', parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start_command_handler(msg):
    log(msg.chat.id, 1)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Расчитать стоимость товара🧮', callback_data='s_calc'))
    markup.add(InlineKeyboardButton('Заказать', callback_data='zakaz'))
    markup.add(InlineKeyboardButton('Посмотреть отзывы или оставить свой💬', url='https://t.me/himeramanager'))
    bot.send_photo(msg.chat.id, open('/var/www/u2302856/data/www/himerastore.ru/ava.jpg', 'rb'), caption=start_text, reply_markup=markup)


@bot.message_handler(commands=['rasl'])
def rasl_command_handler(msg):
    if msg.chat.id != 5937350677:
        return
    bot.send_message(msg.chat.id, 'Готов')
    bot.register_next_step_handler(msg, send_rasl)


def send_rasl(msg):
    with connection.cursor() as cursor:
        cursor.execute('SELECT (tg_id) FROM Users')
        users = cursor.fetchall()
    for user in users:
        bot.copy_message(user['tg_id'], msg.chat.id, msg.id)


@bot.callback_query_handler(func=lambda call: '_calc' in call.data)
def calc(call):
    markup = InlineKeyboardMarkup()
    text = f'''Введите стоимость товара в юанях'''
    markup.add(InlineKeyboardButton('Назад', callback_data='from_start'))
    bot.send_message(call.message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(call.message, calc_done)


def calc_done(msg):
    markup = InlineKeyboardMarkup()
    if not all([i in '1234567890.' for i in msg.text]):
        send_error(msg.chat.id, 'Думаю это не цена, введи ещё раз.\n В цене могут содержаться только эти символы <b>"1234567890."</b>')
        bot.register_next_step_handler(msg, calc_done)
        log(msg.chat.id, 3)
        return
    markup.add(InlineKeyboardButton('Рассчитать ещё', callback_data=f's_calc'))
    markup.add(InlineKeyboardButton('Заказать', callback_data='zakaz'))

    cost = int(float(msg.text) * curs() + 1000)
    log(msg.chat.id, 4, text=cost)
    bot.send_message(msg.chat.id, f'''✅ Стоимость товара с учетом доставки до двери или пункта выдачи составляет: {cost}₽
    🚕  Планируемое время доставки: 8 - 14 дней 
    ⚠️  Цена может уменьшится, если вес товара будет меньше планируемого
    Для более точного расчета напишите <a href="https://t.me/himeramanager">менеджеру</a> (время ответа 4 мин, c 10:00 до 20:00)''', parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'from_start')
def to_start(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    start_command_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'zakaz')
def to_start(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('На главную', callback_data='from_start'))
    bot.send_message(call.message.chat.id, '''СОКРАЩЁННАЯ ИНСТРУКЦИЯ ДЛЯ ОСУЩЕСТВЛЕНИЯ ЗАКАЗОВ:
    1) Вам необходимо скачать приложение dewu (это и есть POIZON | китайский маркетплейс, исключительно для внутреннего рынка) 
        Ссылка для скачивания:
            • <a href="https://www.anxinapk.com/rj/12201303.html">Скачать POIZON на Android</a>
            • <a href="https://apps.apple.com/kz/app/%E5%BE%97%E7%89%A9-%E6%9C%89%E6%AF%92%E7%9A%84%E8%BF%90%E5%8A%A8-%E6%BD%AE%E6%B5%81-%E5%A5%BD%E7%89%A9/id1012871328">Скачать POIZON на iOS</a>
    2) Вы должны выбрать нужный вам товар в каталоге 
    3) Нужно прислать скриншот выбранной вами вещи нашему <a href="https://t.me/himeramanager">менеджеру</a> (вы должны указать ваш размер) 
    4) Вам нужно заполнить форму для осуществления выкупа, а также доставки
''', parse_mode='HTML', reply_markup=markup, disable_web_page_preview=True)


# TODO - сделать нормально
@bot.callback_query_handler(func=lambda x: True)
def zaglushka(call):
    log(call.message.chat.id, 5)
    bot.send_message(call.message.chat.id, """Обратитесть к менеджеру https://t.me/himeramanager
Бот пока такого не умеет, но если вы закажете что-нибудь разрабу купят кофе и разработка пойдёт быстрее))""")


bot.set_my_commands([
    BotCommand('/start', 'Запуск/Перезапуск бота')
])
bot.infinity_polling()
