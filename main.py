import telebot
from telebot import types
import json

TOKEN = "6646399421:AAGpSnSQRcZhEqI3e4ZLWkT48BkxbTerfpI"

bot = telebot.TeleBot(TOKEN)

menu_items = [
    {"name": "Грибной суп", "price": "450 руб.", "photo": "mushroom_soup.png"},
    {"name": "Салат Цезарь", "price": "550 руб.", "photo": "caesar.png"},
    {"name": "Утка с апельсинами", "price": "700 руб.", "photo": "duck_orange.png"},
    {"name": "Бефстроганов", "price": "650 руб.", "photo": "stroganoff.png"},
    {"name": "Ризотто", "price": "500 руб.", "photo": "risotto.png"},
    {"name": "Тирамису", "price": "400 руб.", "photo": "tiramisu.png"},
    {"name": "Блины", "price": "300 руб.", "photo": "pancakes.png"},
    {"name": "Паста Карбонара", "price": "550 руб.", "photo": "carbonara.png"},
    {"name": "Гаспачо", "price": "350 руб.", "photo": "gazpacho.png"},
    {"name": "Фалафель", "price": "400 руб.", "photo": "falafel.png"}]

ITEMS_PER_PAGE = 4


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Меню", reply_markup=generate_markup())


def button_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    btn1 = types.KeyboardButton("Меню")
    btn2 = types.KeyboardButton("Корзина")

    markup.add(btn1, btn2)
    return markup


user_info = {}


@bot.message_handler(commands=['add_info'])
def add_info(message):
    chat_id = message.chat.id
    user_info[chat_id] = {}
    msg = bot.send_message(chat_id, "Введите ваше имя:")
    bot.register_next_step_handler(msg, process_name_step)
    # dump_data()


def process_name_step(message):
    chat_id = message.chat.id
    user_info[chat_id]['name'] = message.text

    msg = bot.send_message(chat_id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(msg, process_phone_step)


def process_phone_step(message):
    chat_id = message.chat.id
    phone_number = message.text
    if check_phone(phone_number):
        user_info[chat_id]['phone'] = phone_number
        dump_data(user_info)
        bot.send_message(chat_id,
                         f"Ваше имя: {user_info[chat_id]['name']}\nВаш номер телефона: {user_info[chat_id]['phone']}")
    else:
        bot.send_message(chat_id, "Номер должен содержать только цифры (0,1,2,3,4,5,6,7,8,9)")


def dump_data(data):
    # with open('data.json', 'r', encoding='utf-8') as file:
    #     info = json.load(file)

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def check_phone(phone_number):
    return phone_number.isdigit()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Меню":

        markup = types.InlineKeyboardMarkup()
        for item in menu_items:
            button = types.InlineKeyboardButton(item['name'], callback_data=item['name'])
            markup.add(button)

        bot.send_message(message.chat.id, "Выберите блюдо:", reply_markup=markup)

    elif message.text == "Корзина":
        items_in_cart = get_cart(message.chat.id)

        markup = types.InlineKeyboardMarkup()
        for item in items_in_cart:
            minus_button = types.InlineKeyboardButton("-", callback_data=f"minus_{item}")
            name_button = types.InlineKeyboardButton(f"{item[0]} x{item[1]}", callback_data=f"name_{item}")
            plus_button = types.InlineKeyboardButton("+", callback_data=f"plus_{item}")

            # Добавляем кнопки в строку markup
            markup.add(minus_button, name_button, plus_button)

        bot.send_message(message.chat.id, "Корзина:", reply_markup=markup)


def add_to_cart(client_id, item, ):
    with open("data.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            for cart_item in client["id"]:
                if cart_item[0] == item:
                    cart_item[1] += 1
            else:
                client["cart"].append([item, 1])

    with open("data.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def del_to_cart(client_id, item):
    with open("data.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            for cart_item in client["cart"]:
                if cart_item[0] == item:
                    cart_item[1] -= 1
                    if cart_item[1] == 0:
                        client["cart"].remove(cart_item)
                        break


    with open("data.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def get_cart(client_id):
    print(client_id)

    with open("data.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            return client.get("cart", [])

    return None


def generate_markup(page=0):
    markup = types.InlineKeyboardMarkup()
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    for item in menu_items[start_index:end_index]:
        button = types.InlineKeyboardButton(f"{item["name"]} - {item["price"]}",
                                            callback_data=f"Menu{menu_items.index(item)}")
        markup.add(button)

    if page > 0:
        markup.add(types.InlineKeyboardButton(text="<<", callback_data=f"page_{page - 1}"))
    if end_index < len(menu_items):
        markup.add(types.InlineKeyboardButton(text=">>", callback_data=f"page_{page + 1}"))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):

    bot.answer_callback_query(call.id)
    if call.data.startswith("minus_"):
        item = call.data[len("minus_"):]
        del_to_cart(call.from_user.id,item )
    if call.data.startswith('page_'):
        _, page = call.data.split('_')
        markup = generate_markup(int(page))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите элемент:", reply_markup=markup)
    elif call.data.startswith('item_'):
        _, item_index = call.data.split('_')
        add_to_cart(call.message.chat.id, menu_items[int(item_index)]["name"])
        bot.send_message(call.message.chat.id, f'{menu_items[int(item_index)]["name"]} добавлено в заказ')


bot.polling()

if __name__ == "__main__":
    bot.polling(none_stop=True)
