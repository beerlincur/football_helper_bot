from aiohttp import BasicAuth
from keyboards import ListOfButtons
from configparser import ConfigParser


config = ConfigParser()
config.read("config.ini")


TOKEN = config['token']['TOKEN']

BOT_URL = config['bot_url']['BOT_URL']

ADMINS_IDS = (int(config['chat_ids']['BOSS_ID']), int(config['chat_ids']['KUSHER_ID']))

#|-------------------- PROXIE ----------------|
PROXIE_URL = config['proxie']['PROXIE_URL']

PROXIE_LOGIN = config['proxie']['PROXIE_LOGIN']

PROXIE_PASSWORD = config['proxie']['PROXIE_PASSWORD']

PROXIE_AUTH = BasicAuth(
    login = PROXIE_LOGIN,
    password = PROXIE_PASSWORD
)

PROXIE_URL_W_AUTH = config['proxie']['PROXIE_URL_W_AUTH']


BASE_RATING = 5.0


MAIN_KEYBOARD = ListOfButtons(
    text = [
        'Добавление',
        'Просмотр',
        'Изменение',
        'Удаление',
        'Просмотреть пару команд',
        'Ввести результаты игры'
    ],
    align = [2, 2, 1, 1]
).reply_keyboard


ADD_KEYBOARD = ListOfButtons(
    text = [
        'Добавить команду',
        'Добавить лигу',
        'Добавить турнир',
        'Назад на главную',
    ],
    align = [1, 2, 1]
).reply_keyboard


SHOW_KEYBOARD = ListOfButtons(
    text = [
        'Команды лиги',
        'Команды турнира',
        'Лиги турнира',
        'Турниры',
        'Назад на главную',
    ],
    align = [2, 2, 1]
).reply_keyboard


EDIT_KEYBOARD = ListOfButtons(
    text = [
        'Изменить рейтинг команды',
        'Изменить коэффициент силы лиги',
        'Назад на главную',
    ],
    align = [1, 1, 1]
).reply_keyboard


DELETE_KEYBOARD = ListOfButtons(
    text = [
        'Удалить команду',
        'Удалить лигу',
        'Удалить турнир',
        'Назад на главную',
    ],
    align = [1, 1, 1, 1]
).reply_keyboard


MAIN_CANCEL = ListOfButtons(
    text = [
        'Отменить действие'
    ],
    callback=["main_cancel"],
    align = [1]
).inline_keyboard