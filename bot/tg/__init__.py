import bson

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
from bot import config

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
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{info["name"]}\n{info["description"]}",
        reply_markup=reply_markup,
    )


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
    return MAIN


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if util.compare_input(update.message.text, "поиск"):
        await update.message.reply_text("Введите название места", reply_markup=searching_keyboard)
        return SEARCHING
    if util.compare_input(update.message.text, "категории"):
        return CHOOSING_CATEGORY
    return MAIN


async def searching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if util.compare_input(update.message.text, "отменить"):
        await update.message.reply_text(welcome_string, reply_markup=main_keyboard)
        return MAIN
    context.user_data["results"] = list(places.collect.find({"$text": {"$search": update.message.text}}))
    context.user_data["results_counter"] = 0
    return await return_to_main_or_next(update, context)


async def choosing_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = cat.get_all()
    keyboard = [[InlineKeyboardButton(c["name"], callback_data=f"category {c["_id"]}")] for c in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)


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


async def show_in_category(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    category_id = data[1]
    category = cat.get_by_id(category_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Места категории {category['name']}:", reply_markup=next_or_exit_keyboard)
    res = list(places.collect.aggregate([
        {"$match": {
            "category_id": bson.ObjectId(category_id),
        }},
    ]))
    context.user_data["results"] = res
    context.user_data["results_counter"] = 0
    return await return_to_main_or_next(update, context)


def configure_application() -> Application:
    application = Application.builder().token("7608142171:AAGMY-exBpwKtxSIJZLIug2Oa-5YIfztLF8").build()

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
    return application
