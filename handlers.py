import asyncio
import random
import json

from data.system_functions import *

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from config import FULL_NAME, REGISTER_WORDS, LOGIN_WORDS, MURAD_TEXT_PATH


def load_texts():
    lst = [MURAD_TEXT_PATH]
    texts = []
    for filename in lst:
        with open(filename, encoding='utf-8') as f:
            texts.append(f.readlines())
    return texts


MURAD_TEXT = load_texts()[0]

# Add a keyboards
reply_keyboard_not_login = [['Регистрация', 'Авторизация']]
markup_not_login = ReplyKeyboardMarkup(
    reply_keyboard_not_login,
    one_time_keyboard=False,
    resize_keyboard=True
)
reply_keyboard_is_login = [['/logout']]
markup_is_login = ReplyKeyboardMarkup(
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


def change_keyboard(tg_user_id):
    if get_current_user(tg_user_id) is None:
        return markup_not_login
    else:
        return markup_is_login


async def handle_messages(update, context):
    text = update.message.text.lower()
    if text in REGISTER_WORDS:
        return asyncio.create_task(register_user(update, context))
    elif text in LOGIN_WORDS:
        return asyncio.create_task(login_user(update, context))
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text(
            "Остановитесь! Зайдите в аккаунт или зарегистрируйтесь"
        )
        return
    else:
        await update.message.reply_text(
            random.choice(MURAD_TEXT).replace('{REPLACE}', user.name)
        )
    # await update.message.reply_text(text)


async def start(update, context):
    await update.message.reply_text(
        f"Привет, меня зовут {FULL_NAME}. "
        f"Я ваш личный ассистент. Чем могу помочь?",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='STICKER_ID')


async def help(update, context):
    await update.message.reply_text("HEEEELLLPP.")


async def register_user(update, context):
    if get_current_user(update.message.from_user.id) is not None:
        await update.message.reply_text("Для начала выйдите из аккаунта")
        return ConversationHandler.END
    await update.message.reply_text("Регистрация...")
    await update.message.reply_text("Введите никнейм ->", reply_markup=markup_stop)
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
    await update.message.reply_text(f"{context.user_data['nickname']}! Введи номер телефона")
    return 'get_phone'


async def get_phone(update, context):  # Получение телефона. Конец регистрации
    phone = update.message.text
    context.user_data['phone'] = phone
    context.user_data['tg_id'] = update.message.from_user.id
    register(context.user_data)
    await update.message.reply_text("...")
    await update.message.reply_text(
        "Успех. Наслаждайся",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text(
        "Ну блин!",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def login_user(update, context):
    if get_current_user(update.message.from_user.id) is not None:
        await update.message.reply_text("Для начала выйдите из аккаунта")
        return ConversationHandler.END
    await update.message.reply_text("Авторизация.,.")
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
        await update.message.reply_text("Ага!!! что-то не так!!! Ещё разок >>> ")
        return 'get_l_password'
    await update.message.reply_text(
        "Всё норм",
        reply_markup=change_keyboard(update.message.from_user.id)
    )
    return ConversationHandler.END


async def logout_user(update, context):
    logout(update.message.from_user.id)
    await update.message.reply_text(
        "Вы вышли из аккаунта! Пока",
        reply_markup=change_keyboard(update.message.from_user.id)
    )


async def say_hello(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Зайдите в аккаунт!")
        return
    await update.message.reply_text(f"Привет, {user.fio}")
    await update
