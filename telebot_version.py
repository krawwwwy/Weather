import requests
import telebot
from datetime import datetime, timedelta

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = '6552948051:AAF4dMTVjQU-fnqn8JhIMBW3Fe1mcU_OHnk'
OPENWEATHERMAP_API_KEY = 'a5da20252a648f28a4a091f020b22d19'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот погоды. Используйте /weather, чтобы узнать текущую погоду в Волгограде, и /forecast, чтобы получить прогноз погоды на завтра.')

@bot.message_handler(commands=['weather'])
def handle_weather(message):
    city = 'Volgograd'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)
    weather_data = response.json()

    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']

    message_text = f'Текущая погода в {city}:\nТемпература: {temperature}°C\nОписание: {description}'
    bot.send_message(message.chat.id, message_text)

@bot.message_handler(commands=['forecast'])
def handle_forecast(message):
    city = 'Volgograd'
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')

    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)
    weather_data = response.json()

    forecast = [item for item in weather_data['list'] if item['dt_txt'].startswith(tomorrow_date)]

    if forecast:
        temperature = forecast[0]['main']['temp']
        description = forecast[0]['weather'][0]['description']
        message_text = f'Прогноз погоды в {city} на завтра:\nТемпература: {temperature}°C\nОписание: {description}'
        bot.send_message(message.chat.id, message_text)
    else:
        bot.send_message(message.chat.id, 'Не удалось получить прогноз погоды на завтра.')

if __name__ == '__main__':
    bot.polling(none_stop=True)
