from data.system_functions import register, is_nickname_unique, login

from telegram.ext import ConversationHandler
from config import FULL_NAME


async def echo(update, context):
    await update.message.reply_text(update.message.text)


async def start(update, context):
    await update.message.reply_text(
        f"Привет, меня зовут {FULL_NAME}. "
        f"Я ваш личный ассистент. Чем могу помочь?"
    )


async def help(update, context):
    await update.message.reply_text("HEEEELLLPP.")


async def register_user(update, context):
    await update.message.reply_text("Регистрация...")
    await update.message.reply_text("Введите никнейм ->")
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
    # Проверка пароля на символы из того года
    await update.message.reply_text("Теперь продублируйте пароль..")
    return 'get_repeat_password'


async def get_repeat_password(update, context):
    repeat_password = update.message.text
    if context.user_data['password'] != repeat_password:
        context.user_data['password'] = None
        # user_info['password'] = None
        await update.message.reply_text("Ошибкааа. Пароли не совпадают!!! Ещё раз.")
        return 'get_r_password'
    await update.message.reply_text("Ok. Введите Ваше настоящее имя")
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


async def get_phone(update, context):
    phone = update.message.text
    context.user_data['phone'] = phone
    await update.message.reply_text(register(context.user_data))
    await update.message.reply_text("...")
    await update.message.reply_text("Всё OK!")
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Ну блин!")
    return ConversationHandler.END


async def login_user(update, context):
    await update.message.reply_text("Авторизация.,.")
    await update.message.reply_text("Введите никнейм: ")
    return 'get_l_nickname'


async def get_l_nickname(update, context):
    nickname = update.message.text
    context.user_data['nickname'] = nickname
    await update.message.reply_text(f"{nickname}, надеюсь ты помнишь пароль!")
    return 'get_l_password'


async def get_l_password(update, context):
    password = update.message.text
    context.user_data['password'] = password
    user = login(context.user_data)
    if user is None:
        await update.message.reply_text("Ага!!! что-то не так!!! Ещё разок >>> ")
        return 'get_l_nickname'
    context.current_user = user
    await update.message.reply_text(f"Всё норм, {user.fio}")
    return ConversationHandler.END


async def login_user_end(update, context):
    await update.message.reply_text("Ну блин!")
    return ConversationHandler.END
