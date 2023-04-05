from data import db_session
from data.user import User

import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import BOT_TOKEN, FULL_NAME

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def echo(update, context):
    await update.message.reply_text(update.message.text)


async def start(update, context):
    await update.message.reply_text(
        f"Привет, меня зовут {FULL_NAME}. "
        f"Я ваш личный ассистент. Чем могу помочь?"
    )


async def help(update, context):
    await update.message.reply_text("HEEEELLLPP.")


async def register_user_in_tg(update, context):
    await update.message.reply_text("HEEEELLLPP.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("register_user_in_tg", register_user_in_tg))

    application.add_handler(text_handler)
    application.run_polling()

    db_session.global_init('db/tg_bot.db')
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()