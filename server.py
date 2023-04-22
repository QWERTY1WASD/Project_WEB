import logging

from bot_token import BOT_TOKEN
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from handlers import *

logging.basicConfig(
    # filename='bot_log.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def main():
    db_session.global_init('db/tg_bot.db')
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info('Start Bot')

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages)

    # Register or login or other
    reg_or_log_and_other_handler = ConversationHandler(
        entry_points=[text_handler],
        states={
            'get_r_nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_r_nickname)],
            'get_r_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_r_password)],
            'get_repeat_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_repeat_password)],
            'get_name': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            'get_surname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            'get_phone': [MessageHandler(filters.CONTACT & ~filters.COMMAND, get_phone)],

            'get_l_nickname': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_l_nickname)],
            'get_l_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_l_password)],

            'generate_random_case': [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_random_case)],
            'get_user_answer': [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_answer)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    # Add handlers
    application.add_handler(reg_or_log_and_other_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("logout", logout_user))
    application.add_handler(CommandHandler("register_user", register_user))
    application.add_handler(CommandHandler("login_user", login_user))
    application.add_handler(CommandHandler("user_info", user_info))
    application.add_handler(CommandHandler("print_random_poem", print_random_poem))
    application.add_handler(CommandHandler("get_random_place", get_random_place))
    application.add_handler(CommandHandler("info_bot", info_bot))

    application.add_handler(CommandHandler("get_all_users_info", get_all_users_info))
    application.add_handler(CommandHandler("reload_data", reload_data))

    application.run_polling()


if __name__ == '__main__':
    main()
