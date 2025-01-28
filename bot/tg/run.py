from telegram.ext import CallbackQueryHandler

from bot.tg import *


def run_bot():
    application = configure_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
