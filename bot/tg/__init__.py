import bson
from bson import ObjectId
from flask import url_for

from . import util
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from bot.database import categories as cat, db_client
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

from bot.database import places
from bot import config, app
from bot.fs import fs

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MAIN, SEARCHING, NEXT_OR_EXIT, CHOOSING_CATEGORY = range(4)

main_keyboard = ReplyKeyboardMarkup([
    ["Поиск🔎", "Популярные✨"],
    ["Категории🗃️", "Случайное место🎲"],
], one_time_keyboard=False)

searching_keyboard = ReplyKeyboardMarkup([
    ["Отменить🚫"],
], one_time_keyboard=False)

next_or_exit_keyboard = ReplyKeyboardMarkup([
    ["Отменить🚫", "Следующее⬇️"],
], one_time_keyboard=False)

welcome_string = "Здесь вы можете узнать о достопримечательностях Удмуртии"


async def send_place(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_markup):
    info = context.user_data["results"][context.user_data["results_counter"]]
    with app.app_context():
        for p in info["photos"]:
            if p['filename']:
                f = fs.get_last_version(p['filename'])
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=f.read(),
                )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{info["name"]}\n{info["description"]}",
        reply_markup=reply_markup,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Оценить место",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(f"Лайк👍{info["likes"]}", callback_data=f"like {info["_id"]} {update.effective_chat.id}"),
            InlineKeyboardButton(f"Дизлайк👎{info["dislikes"]}", callback_data=f"dislike {info["_id"]} {update.effective_chat.id}")
        ]]),
    )


async def edit_message_with_place(update: Update, context: ContextTypes.DEFAULT_TYPE, place_id):
    info = places.collect.find_one({"_id": ObjectId(place_id)})
    query = update.callback_query
    await context.bot.edit_message_reply_markup(
       chat_id=query.message.chat.id,
       message_id=query.message.message_id,
       reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(f"Лайк👍{info["likes"]}", callback_data=f"like {info["_id"]} {update.effective_chat.id}"),
            InlineKeyboardButton(f"Дизлайк👎{info["dislikes"]}", callback_data=f"dislike {info["_id"]} {update.effective_chat.id}")
        ]]),)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        welcome_string,
        reply_markup=main_keyboard,
    )
    db_client[config.db_name]["tg_users"].update_one(
        {"chat_id": update.effective_chat.id},
        {"$setOnInsert": {"chat_id": update.effective_chat.id}},
        True
    )

    #await context.bot.send_venue(
    #    chat_id=update.effective_chat.id,
    #    #latitude=50,
    #    #longitude=40,
    #    #title="Пиво",
    #    #address="Улица Пушкина дом колотушкина"
    #)

    return MAIN


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if util.compare_input(update.message.text, "поиск"):
        await update.message.reply_text("Введите название места", reply_markup=searching_keyboard)
        return SEARCHING
    if util.compare_input(update.message.text, "категории"):
        categories = cat.get_all()
        keyboard = [[InlineKeyboardButton(c["name"], callback_data=f"category {c["_id"]}")] for c in categories]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)
        return MAIN
    if util.compare_input(update.message.text, "случайное место"):
        context.user_data["results"] = list(places.get_with_photos({"$sample": {"size": 10}}))
        context.user_data["results_counter"] = 0
        return await return_to_main_or_next(update, context)
    if util.compare_input(update.message.text, "популярные"):
        context.user_data["results"] = list(places.get_with_photos({"$sort": {"likes": -1}}))
        context.user_data["results_counter"] = 0
        return await return_to_main_or_next(update, context)
    return MAIN


async def searching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if util.compare_input(update.message.text, "отменить"):
        await update.message.reply_text(welcome_string, reply_markup=main_keyboard)
        return MAIN
    context.user_data["results"] = list(places.get_with_photos({"$match": {"$text": {"$search": update.message.text}}}))
    context.user_data["results_counter"] = 0
    return await return_to_main_or_next(update, context)


#async def choosing_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    categories = cat.get_all()
#    keyboard = [[InlineKeyboardButton(c["name"], callback_data=f"category {c["_id"]}")] for c in categories]
#    reply_markup = InlineKeyboardMarkup(keyboard)
#    logger.info("Печать категорий")
#
#    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)
#    return MAIN


async def return_to_main_or_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data["results"]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ничего не нашлось", reply_markup=main_keyboard)
        return MAIN
    if len(context.user_data["results"]) == 1:
        await send_place(update, context, main_keyboard)
        return MAIN
    await send_place(update, context, next_or_exit_keyboard)
    context.user_data["results_counter"] += 1
    return NEXT_OR_EXIT


async def next_or_exit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if util.compare_input(update.message.text, "отменить"):
        await update.message.reply_text(welcome_string, reply_markup=main_keyboard)
        return MAIN
    if util.compare_input(update.message.text, "следующее"):
        if context.user_data["results_counter"] >= len(context.user_data["results"]) - 1:
            await send_place(update, context, main_keyboard)
            return MAIN
        await send_place(update, context, next_or_exit_keyboard)
        context.user_data["results_counter"] += 1
        return NEXT_OR_EXIT


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    #await query.edit_message_text(text=f"Selected option: {query.data}")
    data = query.data.split()
    if data[0] == "category":
        await show_in_category(update, context, data)
    elif data[0] == "like":
        places.give_like(data[1], data[2])
        await edit_message_with_place(update, context, data[1])
    elif data[0] == "dislike":
        places.give_dislike(data[1], data[2])
        await edit_message_with_place(update, context, data[1])


async def show_in_category(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    category_id = data[1]
    category = cat.get_by_id(category_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Места категории {category['name']}:", reply_markup=next_or_exit_keyboard)
    res = list(places.get_with_photos(
        {"$match": {
            "category_id": bson.ObjectId(category_id),
        }},
    ))
    context.user_data["results"] = res
    context.user_data["results_counter"] = 0
    return await return_to_main_or_next(update, context)


def configure_application() -> Application:
    application = (Application.builder()
                   .token("7608142171:AAGMY-exBpwKtxSIJZLIug2Oa-5YIfztLF8")
                   .read_timeout(100)
                   .write_timeout(100)
                   .build())

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
            #CHOOSING_CATEGORY: [
            #    MessageHandler(
            #        filters.ALL,
            #        choosing_category,
            #    )
            #]
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    return application
