import asyncio
import random
import requests

from data.system_functions import *

from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ConversationHandler
from constants import *


murad_text = going_to_the_river_text = flarakrad_text = ''
poems_list = []


def load_texts():
    global murad_text, going_to_the_river_text, flarakrad_text, poems_list

    lst = [MURAD_TEXT_PATH, GOING_TO_THE_RIVER_PATH, FLARAKRAD_PATH]
    texts = []
    for filename in lst:
        with open(filename, encoding='utf-8') as f:
            texts.append(f.readlines())
    with open(POEMS_PATH, encoding='utf-8') as f_poems:
        texts.append(f_poems.read().split(POEMS_SEPARATOR))
    murad_text, going_to_the_river_text, flarakrad_text, poems_list = texts


load_texts()
# Add a keyboards
reply_keyboard_not_login = [['Регистрация', 'Авторизация']]
markup_not_login = ReplyKeyboardMarkup(
    reply_keyboard_not_login,
    one_time_keyboard=False,
    resize_keyboard=True
)
reply_keyboard_is_login = [
    ['Случайная задача 🤔', 'Случайное место 🌍', 'Случайная поэма 📖'],
    ['Позвать Мурада 🔞', 'Позвать идущего к реке', 'Позвать FlaRakRad', 'Слушать эхо'],
    ['Инфо', 'Выход ', 'Помощь 🆘']
]
markup_main_keyboard = ReplyKeyboardMarkup(
    reply_keyboard_is_login,
    one_time_keyboard=False,
    resize_keyboard=True,
    is_persistent=True
)
reply_keyboard_stop = [['/stop']]
markup_stop = ReplyKeyboardMarkup(
    reply_keyboard_stop,
    one_time_keyboard=False,
    resize_keyboard=True
)
request_contact_markup = ReplyKeyboardMarkup([[
    KeyboardButton('Сбросить номер телефона', request_contact=True)]],
    one_time_keyboard=False,
    resize_keyboard=True)


async def request_contact(update, context):
    await update.message.reply_text(
        f"gggive youuur numbberrr",
        reply_markup=request_contact_markup
    )
    a = Update.message
    await update.message.reply_text(f'{Update.message.contact.phone_number}')


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
            "Остановитесь! ❌❌❌ Зайдите в аккаунт или зарегистрируйтесь")
        return
    elif text in EXIT_WORDS:
        return asyncio.create_task(logout_user(update, context))
    elif text in INFO_WORDS:
        return asyncio.create_task(user_info(update, context))
    elif text in RANDOM_CASE_WORDS:
        return asyncio.create_task(generate_random_case(update, context))
    elif text in RANDOM_PLACE_WORDS:
        return asyncio.create_task(get_random_place(update, context))
    elif text in RANDOM_POEM_WORDS:
        asyncio.create_task(print_random_poem(update, context))
        return
    elif text in HELP_WORDS:
        asyncio.create_task(help(update, context))
        return
    companion = user.selected_companion
    if text in CHANGE_COMPANION:
        companion = COMPANIONS[CHANGE_COMPANION.index(text)]
        change_selected_companion(user.telegram_id, companion)
        await update.message.reply_text('Сейчас всё будет..')
    if companion == COMPANIONS[0]:
        current_text = murad_text
    elif companion == COMPANIONS[1]:
        current_text = going_to_the_river_text
    elif companion == COMPANIONS[2]:
        current_text = flarakrad_text
    else:
        await update.message.reply_text(update.message.text)
        return
    text = random.choice(current_text).replace('{REPLACE}', user.name)
    try:
        while text == context.user_data['text']:
            text = random.choice(current_text).replace('{REPLACE}', user.name)  # Чтобы не было повторений
    except KeyError:
        context.user_data['text'] = ' '
    await update.message.reply_text(text)
    context.user_data['text'] = text


async def start(update: Update, context):
    await update.message.reply_text(
        f"Привет 👋, меня зовут {FULL_NAME}. "
        f"С нами Вы сможете очень хорошо провести некоторую часть Вашего времени."
        f"Чем могу помочь?",
        reply_markup=change_keyboard(update.message.from_user.id)
    )


async def help(update, context):
    await update.message.reply_text(HELP_TEXT)


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
    await update.message.reply_text(
        f"{context.user_data['nickname']}! Скинь номер телефона 📲 (нажми на кнопку)",
        reply_markup=request_contact_markup)
    return 'get_phone'


async def get_phone(update, context):  # Получение телефона. Конец регистрации
    phone = update.message.contact.phone_number
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
        await update.message.reply_text("Зайдите в аккаунт или зарегистрируйтесь")
        return
    logout(user)
    await update.message.reply_text(
        "Вы вышли из аккаунта! Пока 🥺",
        reply_markup=change_keyboard(update.message.from_user.id)
    )


async def user_info(update, context):
    user = get_current_user(update.message.from_user.id)
    if user is None:
        await update.message.reply_text("Зайдите в аккаунт или зарегистрируйтесь")
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
        await update.message.reply_text("Зайдите в аккаунт или зарегистрируйтесь")
        return
    poem = random.choice(poems_list)
    await update.message.reply_text(poem.replace('{REPLACE}', user.name), parse_mode="Markdown")


async def generate_random_case(update, context):
    if get_current_user(update.message.from_user.id) is None:
        await update.message.reply_text("Зайдите в аккаунт или зарегистрируйтесь")
        return
    first_number = random.randint(0, 100)
    second_number = random.randint(0, 100)
    sign = random.choice(['+', '-', '*'])
    text = f'{first_number} {sign} {second_number}'
    context.user_data['answer'] = eval(text)
    await update.message.reply_text(f'Сколько будет {text}? 🤔')
    return 'get_user_answer'


async def get_user_answer(update, context):
    user_answer = update.message.text
    if user_answer.strip() == str(context.user_data["answer"]):
        await update.message.reply_text('Молодец 😚')
    else:
        await update.message.reply_text(f'ХАХАХА Не правильно. Будет {context.user_data["answer"]}')
    return ConversationHandler.END


async def get_random_place(update, context):
    if get_current_user(update.message.from_user.id) is None:
        await update.message.reply_text("Зайдите в аккаунт или зарегистрируйтесь")
        return
    try:
        map_request = "http://static-maps.yandex.ru/1.x/"
        ll = (random.randint(MIN_AND_MAX_LONGITUDE[0], MIN_AND_MAX_LONGITUDE[1]) / 100,
              random.randint(MIN_AND_MAX_LONGITUDE[0], MIN_AND_MAX_LONGITUDE[1]) / 100)
        spn = random.randint(MIN_AND_MAX_SCALE[0], MIN_AND_MAX_SCALE[1]) / 100
        response = requests.get(map_request, params={
            'll': f'{ll[0]},{ll[1]}',
            'spn': f'{spn},{spn}',
            'l': 'sat,skl'
        })
        await update.message.reply_text(f'🧐 Случайное место с координатами: {ll[0]}, {ll[1]}. '
                                        f'Масштаб: {spn}')
        await update.message.reply_photo(response.content)
    except Exception:
        await update.message.reply_text('Что-то пошло не так!!!')


# Admins only
async def get_all_users_info(update, context):
    user = get_current_user(update.message.from_user.id)
    await update.message.reply_text("Сейчас посмотрим...")
    if not user.is_admin:
        await update.message.reply_text("У вас нет таких привилегий!!!")
    else:
        users_data = get_all_users(update.message.from_user.id)
        await update.message.reply_text('\n'.join(f"{user.id}. {user}" for user in users_data))


async def reload_data(update, context):
    user = get_current_user(update.message.from_user.id)
    await update.message.reply_text("Сейчас посмотрим...")
    if not user.is_admin:
        await update.message.reply_text("У вас нет таких привилегий!!!")
        return
    try:
        load_texts()
    except Exception as e:
        await update.message.reply_text(f"ERROR!!!: {e}")
    else:
        await update.message.reply_text("Всё ок")


async def info_bot(update, context):
    await update.message.reply_text(f"""
Телеграмм-бот: {FULL_NAME},
Разработал: {DEV_NAME},
Git Hub: {DEV_GIT_HUB},
Телеграм-id: {DEV_TG_NAME}
(Пишите, звоните по вопросам рекламы и предложений)

Версия: {VERSION}
Спасибо, за использование!
    """)
