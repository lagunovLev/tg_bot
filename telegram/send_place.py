from telegram.bot import bot


def send_place(chat_id, info, reply_markup):
    bot.send_message(chat_id, f"{info["name"]}\n{info["description"]}", reply_markup=reply_markup)
