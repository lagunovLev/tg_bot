from . import util
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from database import categories as cat
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.database import places

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
    await update.message.reply_text(
        f"{info["name"]}\n{info["description"]}",
        reply_markup=reply_markup,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        welcome_string,
        reply_markup=main_keyboard,
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
    if not context.user_data["results"]:
        await update.message.reply_text("Ничего не нашлось", reply_markup=main_keyboard)
        return MAIN
    if len(context.user_data["results"]) == 1:
        await send_place(update, context, main_keyboard)
        return MAIN
    await send_place(update, context, next_or_exit_keyboard)
    context.user_data["results_counter"] += 1
    return NEXT_OR_EXIT


async def choosing_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = cat.get_all()
    keyboard = [[InlineKeyboardButton(c["name"], callback_data=f"category {c["_id"]}")] for c in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)


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
    # await update.message.reply_text(f"Места категории {category['name']}:", reply_markup=next_or_exit_keyboard)
    #context.user_data["results"] =
    #context.user_data["results_counter"] = 0


