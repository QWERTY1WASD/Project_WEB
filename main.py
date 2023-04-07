from data import db_session

import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN
from handlers import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def main():
    db_session.global_init('db/tg_bot.db')
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info('Start Bot')
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register_user', register_user_begin)],
        states={
            'get_nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nickname)],
            'get_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            'get_repeat_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_repeat_password)],
            'get_name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            'get_surname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            'get_phone': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            'register_user_end': [MessageHandler(filters.TEXT & ~filters.COMMAND, register_user_end)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
