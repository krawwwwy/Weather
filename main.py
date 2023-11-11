from datetime import datetime, timedelta
import requests
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from urllib.parse import quote

TOKEN: Final = '6552948051:AAF4dMTVjQU-fnqn8JhIMBW3Fe1mcU_OHnk'
OPENWEATHERMAP_API_KEY = 'a5da20252a648f28a4a091f020b22d19'
BOT_USERNAME: Final = '@Weather_Volgograd_bot'

user_cities = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, this is my first Telegram bot, written using python-telegram-bot. Press /help to see a list of commands")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''The /weather command shows the weather at a given time,
Command /forecast - shows the forecast for tomorrow
Command /weeklyforecast - shows the forecast for the week
Command /setcity - set the city for the weather forecast''')

async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = update.message.from_user.id
        city_name = ' '.join(context.args)
        user_cities[user_id] = city_name
        await update.message.reply_text(f'City set to {city_name}')
    else:
        await update.message.reply_text('Use the command like this: /setcity <сity>')


async def weekly_forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_cities:
        await update.message.reply_text('Please set the city using the command /setcity <city>')
        return

    city = quote(user_cities[user_id])

    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    if response.status_code != 200:
        await update.message.reply_text('Sorry, there was an error getting the weather. Please make sure the city entered is correct.')
        return

    weather_data = response.json()

    daily_forecast = {}

    for item in weather_data['list']:
        date = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        day = date.strftime('%A')
        temperature = item['main']['temp']
        description = item['weather'][0]['description']

        if day not in daily_forecast:
            daily_forecast[day] = {'temperatures': [], 'descriptions': []}

        daily_forecast[day]['temperatures'].append(temperature)
        daily_forecast[day]['descriptions'].append(description)

    message_text = f'Weekly weather forecast for {user_cities[user_id]}:\n\n'

    for day, data in daily_forecast.items():
        avg_temperature = sum(data['temperatures']) / len(data['temperatures'])
        avg_description = max(set(data['descriptions']), key=data['descriptions'].count)  # Most frequent description

        message_text += f'{day}: Average temperature: {avg_temperature:.1f}°C \n General description: {avg_description}\n\n'

    await update.message.reply_text(message_text)

async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_cities:
        await update.message.reply_text('Please set the city using the command /setcity <city>')
        return

    city = quote(user_cities[user_id])

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')

    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    if response.status_code != 200:
        await update.message.reply_text('Sorry, there was an error retrieving the forecast. Please make sure the city entered is correct.')
        return

    weather_data = response.json()

    forecast = [item for item in weather_data['list'] if item['dt_txt'].startswith(tomorrow_date)]

    if forecast:
        temperature = forecast[0]['main']['temp']
        description = forecast[0]['weather'][0]['description']
        message_text = f'Weather forecast for {user_cities[user_id]} for tomorrow:\n\nTemperature: {temperature}°C\nDescription: {description}'
        await update.message.reply_text(message_text)
    else:
        await update.message.reply_text("Failed to get forecast for tomorrow")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_cities:
        await update.message.reply_text('Please set the city using the command /setcity <city>')
        return

    city = quote(user_cities[user_id])

    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    if response.status_code != 200:
        await update.message.reply_text('Sorry, there was an error getting the weather. Please make sure the city entered is correct.')
        return

    weather_data = response.json()

    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']

    message_text = f'Current weather in {user_cities[user_id]}:\n\nTemperature: {temperature}°C\nDescription: {description}'
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
    app.add_handler(CommandHandler('weeklyforecast', weekly_forecast_command))
    app.add_handler(CommandHandler('setcity', set_city))

    app.add_error_handler(error_message)

    app.run_polling()

