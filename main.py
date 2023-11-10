from datetime import datetime, timedelta
import requests
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from urllib.parse import quote

TOKEN: Final = '6552948051:AAF4dMTVjQU-fnqn8JhIMBW3Fe1mcU_OHnk'
OPENWEATHERMAP_API_KEY = 'a5da20252a648f28a4a091f020b22d19'
BOT_USERNAME: Final = '@Weather_Volgograd_bot'

# Dictionary to store user-selected cities
user_cities = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, это мой первый телеграм бот написанный при помощи python-telegram-bot. Нажми /help чтобы увидеть список команд")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Команда /weather показывает погоду в данный момент времени,
    Команда /forecast - показывает прогноз на завтрашний день
    Команда /weeklyforecast - показывает прогноз на неделю
    Команда /setcity - установить город для прогноза погоды''')

async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = update.message.from_user.id
        # Combine all arguments as the city name
        city_name = ' '.join(context.args)
        user_cities[user_id] = city_name
        await update.message.reply_text(f'Город установлен на {city_name}')
    else:
        await update.message.reply_text('Используйте команду так: /setcity <город>')

async def weekly_forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Prompt the user to set the city if not already set
    if user_id not in user_cities:
        await update.message.reply_text('Пожалуйста, установите город с помощью команды /setcity <город>')
        return

    city = quote(user_cities[user_id])

    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    # Check if the API request was successful
    if response.status_code != 200:
        await update.message.reply_text('Извините, произошла ошибка при получении погоды. Пожалуйста, убедитесь, что введенный город корректен.')
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

    message_text = f'Недельный прогноз погоды в {user_cities[user_id]}:\n'

    for day, data in daily_forecast.items():
        avg_temperature = sum(data['temperatures']) / len(data['temperatures'])
        avg_description = max(set(data['descriptions']), key=data['descriptions'].count)  # Most frequent description

        message_text += f'{day}: Средняя температура: {avg_temperature:.1f}°C, Общее описание: {avg_description}\n'

    await update.message.reply_text(message_text)

async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Prompt the user to set the city if not already set
    if user_id not in user_cities:
        await update.message.reply_text('Пожалуйста, установите город с помощью команды /setcity <город>')
        return

    city = quote(user_cities[user_id])

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')

    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    # Check if the API request was successful
    if response.status_code != 200:
        await update.message.reply_text('Извините, произошла ошибка при получении прогноза. Пожалуйста, убедитесь, что введенный город корректен.')
        return

    weather_data = response.json()

    forecast = [item for item in weather_data['list'] if item['dt_txt'].startswith(tomorrow_date)]

    if forecast:
        temperature = forecast[0]['main']['temp']
        description = forecast[0]['weather'][0]['description']
        message_text = f'Прогноз погоды в {user_cities[user_id]} на завтра:\nТемпература: {temperature}°C\nОписание: {description}'
        await update.message.reply_text(message_text)
    else:
        await update.message.reply_text("Не удалось получить прогноз на завтра")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Prompt the user to set the city if not already set
    if user_id not in user_cities:
        await update.message.reply_text('Пожалуйста, установите город с помощью команды /setcity <город на английском>')
        return

    city = quote(user_cities[user_id])

    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(api_url)

    # Check if the API request was successful
    if response.status_code != 200:
        await update.message.reply_text('Извините, произошла ошибка при получении погоды. Пожалуйста, убедитесь, что введенный город корректен.')
        return

    weather_data = response.json()

    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']

    message_text = f'Текущая погода в {user_cities[user_id]}:\nТемпература: {temperature}°C\nОписание: {description}'
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

