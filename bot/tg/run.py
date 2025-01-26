from telegram.ext import CallbackQueryHandler

from bot.tg import *


def run_bot():
    application = Application.builder().token("7608142171:AAE39yOjyqB4Phq79DCCUxz67EWb5OqXnrs").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN: [
                MessageHandler(
                    filters.ALL, main_menu
                ),
            ],
            SEARCHING: [
                MessageHandler(
                    filters.ALL, searching
                )
            ],
            NEXT_OR_EXIT: [
                MessageHandler(
                    filters.ALL,
                    next_or_exit,
                )
            ],
            CHOOSING_CATEGORY: [
                MessageHandler(
                    filters.ALL,
                    choosing_category,
                )
            ]
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
