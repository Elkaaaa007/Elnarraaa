import telebot
from telebot import types
from datetime import datetime

TOKEN = "8243439599:AAGlLmbUhwnA90YFS637_1DCddSkz1nI5uo"  
bot = telebot.TeleBot(TOKEN)

hotels_db = [
    {"name": "Almaty Central Hotel", "city": "Almaty", "stars": 3, "price": 40},
    {"name": "Grand Almaty", "city": "Almaty", "stars": 4, "price": 70},
    {"name": "Luxury Almaty Resort", "city": "Almaty", "stars": 5, "price": 120},

    {"name": "Astana Place", "city": "Astana", "stars": 3, "price": 50},
    {"name": "Skyline Astana", "city": "Astana", "stars": 4, "price": 80},
    {"name": "Astana Luxury Inn", "city": "Astana", "stars": 5, "price": 130},

    {"name": "Shymkent Comfort", "city": "Shymkent", "stars": 3, "price": 35},
    {"name": "Shymkent Grand", "city": "Shymkent", "stars": 4, "price": 60},
    {"name": "Shymkent Royal", "city": "Shymkent", "stars": 5, "price": 100},

    {"name": "Karaganda Hotel", "city": "Karaganda", "stars": 3, "price": 30},
    {"name": "Karaganda Plaza", "city": "Karaganda", "stars": 4, "price": 55},
    {"name": "Karaganda Elite", "city": "Karaganda", "stars": 5, "price": 95},
]

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cities = ["Almaty", "Astana", "Shymkent", "Karaganda"]
    for city in cities:
        markup.add(city)

    photo_url = "https://yandex.kz/images/search?cbir_id=13530739%2FfIeHWP804Cc4J4g0yf4wew2886&rpt=imageview&img_url=https%3A%2F%2Fimg.freepik.com%2Ffree-vector%2Flifestyle-hotel-abstract-concept-illustration_335657-2476.jpg%3Fsemt%3Dais_hybrid%26w%3D740&rdrnd=403415&cbird=152&lr=162&url=https%3A%2F%2Favatars.mds.yandex.net%2Fget-images-cbir%2F13530739%2FfIeHWP804Cc4J4g0yf4wew2886%2Forig&cbir_page=similar" 

    bot.send_photo(
        chat_id,
        photo=photo_url,
        caption="Привет👋🏻, Я HotelBotKZ 🏨\n"
                "Этот бот создан  для поиска отелей в Казахстане.\n"
                "Выберите город для поиска отелей🔎:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text in ["Almaty", "Astana", "Shymkent", "Karaganda"])
def city_handler(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"city": message.text}
    bot.send_message(chat_id, "Введите дату заезда (YYYY-MM-DD):")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "checkin" not in user_data[message.chat.id])
def checkin_handler(message):
    chat_id = message.chat.id
    try:
        checkin = datetime.strptime(message.text, "%Y-%m-%d")
        user_data[chat_id]["checkin"] = checkin
        bot.send_message(chat_id, "Введите дату выезда (YYYY-MM-DD):")
    except ValueError:
        bot.send_message(chat_id, "❌ Ошибка! Введите дату в формате YYYY-MM-DD")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "checkin" in user_data[message.chat.id] and "checkout" not in user_data[message.chat.id])
def checkout_handler(message):
    chat_id = message.chat.id
    try:
        checkout = datetime.strptime(message.text, "%Y-%m-%d")

        if checkout <= user_data[chat_id]["checkin"]:
            bot.send_message(chat_id, "❌ Дата выезда должна быть позже даты заезда!")
            return

        user_data[chat_id]["checkout"] = checkout
        bot.send_message(chat_id, "Введите максимальную цену за ночь ($):")

    except ValueError:
        bot.send_message(chat_id, "❌ Ошибка! Введите дату в формате YYYY-MM-DD")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "checkout" in user_data[message.chat.id] and "max_price" not in user_data[message.chat.id])
def price_handler(message):
    chat_id = message.chat.id

    if not message.text.isdigit():
        bot.send_message(chat_id, "❌ Введите ЧИСЛО!")
        return
    
    user_data[chat_id]["max_price"] = int(message.text)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for stars in ["3", "4", "5"]:
        markup.add(stars)

    bot.send_message(chat_id, "Выберите звезд отеля ⭐️:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_data and "max_price" in user_data[message.chat.id] and "stars" not in user_data[message.chat.id])
def stars_handler(message):
    chat_id = message.chat.id

    if message.text not in ["3", "4", "5"]:
        bot.send_message(chat_id, "Выберите через кнопку!")
        return
    user_data[chat_id]["stars"] = int(message.text)
    bot.send_message(chat_id, "🔎 Ищем отели...")
    
    show_hotels(chat_id)

def show_hotels(chat_id):
    city = user_data[chat_id]["city"]
    checkin = user_data[chat_id]["checkin"]
    checkout = user_data[chat_id]["checkout"]
    max_price = user_data[chat_id]["max_price"]
    stars = user_data[chat_id]["stars"]

    filtered = [
        h for h in hotels_db
        if h["city"] == city and h["price"] <= max_price and h["stars"] == stars
    
    ]

    if not filtered:
        filtered = [h for h in hotels_db if h["city"] == city]
        bot.send_message(chat_id, "⚠️ Точных совпадений нет, показываю доступные отели:")

    if not filtered:
        bot.send_message(chat_id, "❌ В этом городе нет отелей в базе.")
        return

    for hotel in filtered:
        markup = types.InlineKeyboardMarkup()
        buttton = types.InlineKeyboardButton("Забронировать 🔑", url="https://www.booking.com")        
        markup.add(buttton)
       
        bot.send_message(
            chat_id,
            f"🏨 {hotel['name']}\n"
            f"Город: {hotel['city']}\n"
            f"Цена: ${hotel['price']}/ночь\n"
            f"Звёзды: {hotel['stars']}\n"
            f"Заезд: {checkin.strftime('%Y-%m-%d')}\n"
            f"Выезд: {checkout.strftime('%Y-%m-%d')}",
            reply_markup=markup
        )

    user_data.pop[chat_id, None]
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for city in ["Almaty", "Astana", "Shymkent", "Karaganda"]:
          markup.add(city)

    bot.send_message(chat_id, "🔁 Начать новый поиск:", reply_markup=markup)


if __name__ == "__main__":
    bot.polling(none_stop=True)
      