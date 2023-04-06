from data import db_session
from data.system_functions import register, is_nickname_unique

import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN, FULL_NAME

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

user_info = {
    'nickname': None,
    'password': None,
    'name': None,
    'surname': None,
    'age': None,
    'phone': None,
    'email': None,
    'created_date': None,
}


async def echo(update, context):
    await update.message.reply_text(update.message.text)


async def start(update, context):
    await update.message.reply_text(
        f"Привет, меня зовут {FULL_NAME}. "
        f"Я ваш личный ассистент. Чем могу помочь?"
    )


async def help(update, context):
    await update.message.reply_text("HEEEELLLPP.")


async def register_user_begin(update, context):
    await update.message.reply_text("Регистрация...")
    return 'nickname'


async def get_nickname(update, context):
    await update.message.reply_text("Введите никнейм ->")
    nickname = update.message.text
    if is_nickname_unique(nickname):
        await update.message.reply_text(f"{nickname}... Хороший выбор.")
        user_info['nickname'] = nickname
        print(user_info)
        return 'password'
    await update.message.reply_text(f"Никнейм '{nickname}' уже занят((( Попробуйте снова")
    return 'nickname'


async def get_password(update, context):
    await update.message.reply_text("Введите пароль >.<")
    password = update.message.text
    await update.message.reply_text("Теперь продублируйте пароль..")
    repeat_password = update.message.reply_text
    if password != repeat_password:
        await update.message.reply_text("Ошибкааа. Пароли не совпадают!!!")
    user_info['password'] = password
    return ConversationHandler.END


async def get_other(update, context):
    await update.message.reply_text("Введите Ваше настоящее имя")
    name = update.message.text
    await update.message.reply_text("Введите Вашу фамилию")
    surname = update.message.text
    await update.message.reply_text(f"{user_info['nickname']}! "
                                    f"Введи номер телефона")
    phone = update.message.text
    await update.message.reply_text("Введи ка свой email ...")
    # Проверка?
    email = update.message.text
    user_info['name'] = name
    user_info['surname'] = surname
    user_info['phone'] = phone
    user_info['email'] = email
    await update.message.reply_text("...")
    await update.message.reply_text("Всё OK!")
    return register_user_end


async def register_user_end(update, context):
    await update.message.reply_text(register(user_info))
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Ну блин!")
    return ConversationHandler.END


def main():
    db_session.global_init('db/tg_bot.db')
    application = Application.builder().token(BOT_TOKEN).build()
    # text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("register_user", register_user_begin))

    application.add_handler(MessageHandler(filters.TEXT, get_nickname))
    application.add_handler(MessageHandler(filters.TEXT, get_password))
    application.add_handler(MessageHandler(filters.TEXT, get_other))
    application.add_handler(MessageHandler(filters.TEXT, register_user_end))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register_user', start)],
        states={
            'nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nickname)],
            'password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            'other': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other)],
            'register_user_end': [MessageHandler(filters.TEXT & ~filters.COMMAND, register_user_end)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    # register({'nickname': 'QWERTY', })
    # application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
