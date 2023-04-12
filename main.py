import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
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

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages)

    # Register
    reg_handler = ConversationHandler(
        entry_points=[text_handler],
        states={
            'get_r_nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_r_nickname)],
            'get_r_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_r_password)],
            'get_repeat_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_repeat_password)],
            'get_name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            'get_surname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            'get_phone': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    # Login
    login_handler = ConversationHandler(
        entry_points=[text_handler],
        states={
            'get_l_nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_l_nickname)],
            'get_l_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_l_password)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    # Add handlers
    # application.add_handler(text_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("say_hello", say_hello))
    application.add_handler(CommandHandler("logout", logout_user))
    application.add_handler(reg_handler)
    application.add_handler(login_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
