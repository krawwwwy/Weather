from datetime import datetime, timedelta
import requests
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN: Final = '6552948051:AAF4dMTVjQU-fnqn8JhIMBW3Fe1mcU_OHnk'
OPENWEATHERMAP_API_KEY = 'a5da20252a648f28a4a091f020b22d19'
BOT_USERNAME: Final = '@Weather_Volgograd_bot'


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, это мой первый телеграм бот написанный при помощи python-telegram-bot. Нажми /help чтобы увидеть список комманд")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Команда /weather показывает погоду в данный момент времени,
Команда /forecast - показывает прогноз на завтрашний день''')


async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(message_text)
    else:
        await update.message.reply_text("Не удалось получить прогноз на завтра")


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = 'Volgograd'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)
    weather_data = response.json()

    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']

    message_text = f'Текущая погода в {city}:\nТемпература: {temperature}°C\nОписание: {description}'
    await update.message.reply_text(message_text)


async def error_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print("DA NUUUUUUUU")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('weather', weather_command))
    app.add_handler(CommandHandler('forecast', forecast_command))

    app.add_error_handler(error_message)

    app.run_polling()

