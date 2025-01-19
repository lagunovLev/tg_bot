from telebot import types
from bot.telegram import util
from bot import database as cat, database as places
from bot.telegram.send_place import send_place
from bot.telegram.bot import bot


main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_keyboard.add(types.KeyboardButton("Поиск🔎"), types.KeyboardButton("Популярные✨"), types.KeyboardButton("Категории🗃️"), types.KeyboardButton("Случайное место🎲"))

cancel_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cancel_keyboard.add(types.KeyboardButton("Отменить🚫"))

show_popular_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
show_popular_keyboard.add(types.KeyboardButton("Отменить🚫"), types.KeyboardButton("Следующее⬇️"))


welcome_string = "Здесь вы можете узнать о достопримечательностях Удмуртии"


@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)


@bot.message_handler(func=lambda m: util.compare_input(m.text, "поиск"))
def search(message):
	# bot.reply_to(message, message.text)
	# bot.send_photo(message.chat.id, photo='https://images.wallpaperscraft.com/image/single/lake_mountain_tree_36589_2650x1600.jpg')  # http://localhost:5000/api/get-file/IMG_1531.JPG
	bot.send_message(message.chat.id, "Введите название места", reply_markup=cancel_keyboard)
	bot.register_next_step_handler(message, searching)


@bot.message_handler(func=lambda m: util.compare_input(m.text, "популярные"))
def show_popular(message):
	bot.send_message(message.chat.id, "Популярные места:", reply_markup=show_popular_keyboard)  # todo
	f = show_popular_next()
	f(message, True)


@bot.message_handler(func=lambda m: util.compare_input(m.text, "категории"))
def categories(message):
	categories = cat.get_all()
	kb = types.InlineKeyboardMarkup(row_width=1)
	# print(categories)
	for c in categories:
		# print(c)
		# print(str({'type': "category", "data": c["_id"]}))
		kb.add(types.InlineKeyboardButton(text=c["name"], callback_data=f"category {c["_id"]}"))
	bot.send_message(message.chat.id, "Категории:", reply_markup=kb)  # todo


@bot.message_handler(func=lambda m: util.compare_input(m.text, "случайное место"))
def random_place(message):
	bot.send_message(message.chat.id, "Случайное место", reply_markup=main_keyboard)  # todo


@bot.message_handler()
def reset(message):
	bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)


def show_popular_next():
	counter = 0

	def func(message, first_time=False):
		nonlocal counter
		if util.compare_input(message.text, "следующее") or first_time:
			bot.send_message(message.chat.id, "Какое-то место " + str(counter), reply_markup=show_popular_keyboard)  # todo
			counter += 1
			bot.register_next_step_handler(message, func)
		elif util.compare_input(message.text, "отменить"):
			bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)

	return func


def searching(message):
	text = message.text
	if util.compare_input(message.text, "отменить"):
		bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)
		return
	res = list(places.collect.find({"$text": {"$search": text}}))
	if not res:
		bot.send_message(message.chat.id, "Не удалось ничего найти", reply_markup=main_keyboard)
	else:
		f = searching_next()
		f(message, res, True)


def searching_next():
	counter = 0

	def func(message, search_results, first_time=False):
		nonlocal counter
		if util.compare_input(message.text, "следующее") or first_time:
			send_place(message.chat.id, search_results[counter], show_popular_keyboard)
			counter += 1
			if counter < len(search_results):
				bot.register_next_step_handler(message, func)
			else:
				bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)
		elif util.compare_input(message.text, "отменить"):
			bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)

	return func


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "category")
def callback_inline(call):
	category_id = call.data.split()[1]
	category = cat.get_by_id(category_id)
	bot.send_message(call.message.chat.id, f"Места категории {category['name']}:", reply_markup=show_popular_keyboard)
	f = show_category_next()
	f(call.message, True)


def show_category_next():
	counter = 0

	def func(message, first_time=False):
		nonlocal counter
		if util.compare_input(message.text, "следующее") or first_time:
			bot.send_message(message.chat.id, "Какое-то место " + str(counter), reply_markup=show_popular_keyboard)  # todo
			counter += 1
			bot.register_next_step_handler(message, func)
		elif util.compare_input(message.text, "отменить"):
			bot.send_message(message.chat.id, welcome_string, reply_markup=main_keyboard)

	return func
