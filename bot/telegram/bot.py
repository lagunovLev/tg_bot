import telebot
from bot import config

bot = telebot.TeleBot("7608142171:AAGGI3FRlT6dRj8FmSs5bvySQN8uJCJYqm8", threaded=False)
bot.remove_webhook()
bot.set_webhook(url=config.url + "/" + config.secret_key)
