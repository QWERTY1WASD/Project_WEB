import asyncio
import random
from io import BytesIO
import requests

from data.system_functions import *

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler
from config import *


def load_texts():
    lst = [MURAD_TEXT_PATH, GOING_TO_THE_RIVER_PATH, FLARAKRAD_PATH]
    texts = []
    for filename in lst:
        with open(filename, encoding='utf-8') as f:
            texts.append(f.readlines())
    with open(POEMS_PATH, encoding='utf-8') as f_poems:
        texts.append(f_poems.read().split(POEMS_SEPARATOR))
    return texts


MURAD_TEXT, GOING_TO_THE_RIVER_TEXT, FLARAKRAD_TEXT, POEMS_LIST = load_texts()
# Add a keyboards
reply_keyboard_not_login = [['Регистрация', 'Авторизация']]
markup_not_login = ReplyKeyboardMarkup(
    reply_keyboard_not_login,
    one_time_keyboard=False,
    resize_keyboard=True
)
reply_keyboard_is_login = [
    ['Случайная задача', 'Случайное место', 'Случайный стих'],
    ['Позвать Мурада 🔞', 'Позвать идущего к реке', 'Позвать FlaRakRad', 'Слушать эхо'],
    ['Инфо', 'Выход']
]
markup_main_keyboard = ReplyKeyboardMarkup(
    reply_keyboard_is_login,
    one_time_keyboard=False,
    resize_keyboard=True
)
reply_keyboard_stop = [['/stop']]
markup_stop = ReplyKeyboardMarkup(
    reply_keyboard_stop,
    one_time_keyboard=False,
    resize_keyboard=True
)
# Random place
# 502 lines!!!


def change_keyboard(tg_user_id):
    if get_current_user(tg_user_id) is None:
        return markup_not_login
    else:
        return markup_main_keyboard


async def handle_messages(update, context):
    text = update.message.text.lower()
    if text in REGISTER_WORDS:
        return asyncio.create_task(register_user(update, context))
    elif text in LOGIN_WORDS:
        return asyncio.create_task(login_user(update, context))
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text(
            "Остановитесь! ❌❌❌ Зайдите в аккаунт или зарегистрируйтесь"
        )
        return
    elif text in EXIT_WORDS:
        return asyncio.create_task(logout_user(update, context))
    elif text in INFO_WORDS:
        return asyncio.create_task(get_info(update, context))
    elif text in RANDOM_CASE_WORDS:
        return asyncio.create_task(generate_random_case(update, context))
    elif text in RANDOM_PLACE_WORDS:
        return asyncio.create_task(get_random_place(update, context))
    elif text in RANDOM_POEM_WORDS:
        asyncio.create_task(print_random_poem(update, context))
        return
    elif text in CHANGE_COMPANION:
        change_selected_companion(user.telegram_id, COMPANIONS[CHANGE_COMPANION.index(text)])
        await update.message.reply_text('Сейчас всё будет..')
    else:
        companion = user.selected_companion
        if companion == COMPANIONS[0]:
            text = MURAD_TEXT
        elif companion == COMPANIONS[1]:
            text = GOING_TO_THE_RIVER_TEXT
        elif companion == COMPANIONS[2]:
            text = FLARAKRAD_TEXT
        else:
            await update.message.reply_text(update.message.text)
            return
        await update.message.reply_text(random.choice(text).replace('{REPLACE}', user.name))


async def start(update: Update, context):
    await update.message.reply_text(
        f"Привет 👋, меня зовут {FULL_NAME}. "
        f"Я ваш личный ассистент 💼. Чем могу помочь?",
        reply_markup=change_keyboard(update.message.from_user.id)
    )


async def help(update, context):
    await update.message.reply_text("HEEEELLLPP 😭.")


async def register_user(update, context):
    if get_current_user(update.message.from_user.id) is not None:
        await update.message.reply_text("❌ Для начала выйдите из аккаунта")
        return ConversationHandler.END
    await update.message.reply_text("🧐 Регистрация...")
    await update.message.reply_text("Введите никнейм ✍️(◔◡◔) ->", reply_markup=markup_stop)
    return 'get_r_nickname'


async def get_r_nickname(update, context):
    nickname = update.message.text
    if is_nickname_unique(nickname):
        await update.message.reply_text(f"{nickname}... Хороший выбор.")
        context.user_data['nickname'] = nickname
        await update.message.reply_text("Введите пароль >.<")
        return 'get_r_password'
    await update.message.reply_text(f"Никнейм '{nickname}' уже занят((( Попробуйте снова")
    return 'get_r_nickname'


async def get_r_password(update, context):
    password = update.message.text
    context.user_data['password'] = password
    await update.message.reply_text("Теперь продублируйте пароль..")
    return 'get_repeat_password'


async def get_repeat_password(update, context):
    repeat_password = update.message.text
    if context.user_data['password'] != repeat_password:
        context.user_data['password'] = None
        await update.message.reply_text("Ошибкааа. Пароли не совпадают!!! Ещё раз.")
        return 'get_r_password'
    await update.message.reply_text(
        "Ok. Введите Ваше настоящее имя (Это очень важно для дальнейшей работоспособности бота)"
    )
    return 'get_name'


async def get_name(update, context):
    name = update.message.text
    context.user_data['name'] = name
    await update.message.reply_text("Введите Вашу фамилию")
    return 'get_surname'


async def get_surname(update, context):
    surname = update.message.text
    context.user_data['surname'] = surname
    await update.message.reply_text(f"{context.user_data['nickname']}! Введи номер телефона 📲")
    return 'get_phone'


async def get_phone(update, context):  # Получение телефона. Конец регистрации
    phone = update.message.text
    context.user_data['phone'] = phone
    context.user_data['tg_id'] = update.message.from_user.id
    register(context.user_data)
    await update.message.reply_text("...")
    await update.message.reply_text(
        "Успех. Наслаждайся 😘",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text(
        "Ну блин! 🤬",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def login_user(update, context):
    if get_current_user(update.message.from_user.id) is not None:
        await update.message.reply_text("Для начала выйдите из аккаунта 😵")
        return ConversationHandler.END
    await update.message.reply_text("Авторизация.,. 🤔")
    await update.message.reply_text("Введите никнейм: ", reply_markup=markup_stop)
    return 'get_l_nickname'


async def get_l_nickname(update, context):
    nickname = update.message.text
    context.user_data['nickname'] = nickname
    await update.message.reply_text(f"{nickname}, надеюсь ты помнишь пароль!")
    return 'get_l_password'


async def get_l_password(update, context):
    password = update.message.text
    context.user_data['password'] = password
    context.user_data['tg_id'] = update.message.from_user.id
    user_req = login(context.user_data)
    if not user_req:
        await update.message.reply_text("Ага!!! 😎 что-то не так!!! Ещё разок >>> ")
        return 'get_l_password'
    await update.message.reply_text(
        "Всё норм 😚",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def logout_user(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Прежде чем выходить, зайдите в аккаунт!")
        return
    logout(user.telegram_id)
    await update.message.reply_text(
        "Вы вышли из аккаунта! Пока 🥺",
        reply_markup=change_keyboard(update.message.from_user.id)
    )


async def say_hello(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Зайдите в аккаунт!")
        return
    await update.message.reply_text(f"Привет, {user.fio}")


async def get_info(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Зайдите в аккаунт!")
        return
    text = f'Пользователь с id={user.id} ** Никнейм: {user.nickname} ** ' \
           f'Имя: {user.name} ** Фамилия: {user.surname} ** ' \
           f'Номер телефона: {user.phone} ** ' \
           f'Дата и время создания: {user.created_date} ** ' \
           f'Пароль: Блин... он хэшируется ** {user.nickname}, доволен 🧐?'
    await update.message.reply_text(text.replace(' ** ', '\n'))


async def print_random_poem(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Зайдите в аккаунт!")
        return
    poem = random.choice(POEMS_LIST)
    await update.message.reply_text(poem.replace('{REPLACE}', user.name))


async def generate_random_case(update, context):
    first_number = random.randint(0, 100)
    second_number = random.randint(0, 100)
    sign = random.choice(['+', '-', '*'])
    text = f'{first_number} {sign} {second_number}'
    context.user_data['answer'] = eval(text)
    await update.message.reply_text(f'Сколько будет {text}?')
    return 'get_user_answer'


async def get_user_answer(update, context):
    user_answer = update.message.text
    if user_answer.strip() == str(context.user_data["answer"]):
        await update.message.reply_text('Молодец')
    else:
        await update.message.reply_text(f'ХАХАХА Не правильно. Будет {context.user_data["answer"]}')
    return ConversationHandler.END


async def get_random_place(update, context):
    try:
        map_request = "http://static-maps.yandex.ru/1.x/"
        ll = (random.randint(MIN_AND_MAX_LONGITUDE[0], MIN_AND_MAX_LONGITUDE[1]),
              random.randint(MIN_AND_MAX_LONGITUDE[0], MIN_AND_MAX_LONGITUDE[1]))
        spn = random.randint(1, 20) / 10
        response = requests.get(map_request, params={
            'll': f'{ll[0]},{ll[1]}',
            'spn': f'{spn},{spn}',
            'l': 'sat,skl'
        })
        await update.message.reply_text(f'Случайное место с координатами: {ll[0]}, {ll[1]}')
        await update.message.reply_photo(response.content)
    except Exception:
        await update.message.reply_text('Что-то пошло не так!!!')
