# Telegram боты на Python

> Предыдущая тема: 32 - Работа с API
> Следующая тема: 34 - Автоматизация офисных задач

## Главная идея

Telegram бот — самый популярный заказ на фрилансе. Бот может: принимать заказы, отправлять уведомления, парсить данные, работать как мини-приложение. 80% заказов на Python — это боты.

────────────────────
## Установка и настройка

```bash
pip install python-telegram-bot
```

1. Найди @BotFather в Telegram
2. Отправь `/newbot`
3. Введи имя и username бота
4. Скопируй токен

────────────────────
## Простой бот

```python
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! Я бот."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(
        "/start - Начать\n/help - Помощь\n/info - Информация"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на текстовые сообщения."""
    text = update.message.text
    await update.message.reply_text(f"Ты написал: {text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
```

────────────────────
## Inline кнопки

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Опция 1", callback_data="opt1"),
         InlineKeyboardButton("Опция 2", callback_data="opt2")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "opt1":
        await query.edit_message_text("Выбрана опция 1")
    elif query.data == "opt2":
        await query.edit_message_text("Выбрана опция 2")
```

────────────────────
## Хранение данных

```python
import json
from pathlib import Path

DATA_FILE = Path("bot_data.json")

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "name": update.effective_user.first_name,
            "joined": str(update.message.date)
        }
        save_data(data)

    await update.message.reply_text(f"Привет, {data[user_id]['name']}!")
```

────────────────────
## Задание

1. Создай бота с командами /start, /help, /weather
2. Добавь inline кнопки для выбора города
3. Сохрани историю запросов пользователя

Для /weather используй requests к OpenWeatherMap API. Храни историю в JSON файле.

────────────────────
## Решение

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import requests
import json
from pathlib import Path

TOKEN = "YOUR_BOT_TOKEN"
WEATHER_KEY = "YOUR_WEATHER_KEY"
DATA_FILE = Path("weather_bot_data.json")

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"users": {}, "history": []}

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()

    if str(user.id) not in data["users"]:
        data["users"][str(user.id)] = {
            "name": user.first_name,
            "cities": []
        }
        save_data(data)

    keyboard = [
        [InlineKeyboardButton("Москва", callback_data="weather_Москва"),
         InlineKeyboardButton("Питер", callback_data="weather_Санкт-Петербург")],
        [InlineKeyboardButton("Свой город", callback_data="custom_city")]
    ]

    await update.message.reply_text(
        f"Привет, {user.first_name}! Я покажу погоду.\nВыбери город:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "custom_city":
        await query.edit_message_text("Напиши название города:")
        context.user_data["waiting_city"] = True
        return

    city = query.data.split("_")[1]
    await send_weather(query, city)

async def send_weather(query, city):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_KEY, "units": "metric", "lang": "ru"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            text = (
                f"🌤 Погода в {data['name']}:\n"
                f"🌡 Температура: {data['main']['temp']}°C\n"
                f"☁️ Описание: {data['weather'][0]['description']}\n"
                f"💧 Влажность: {data['main']['humidity']}%\n"
                f"💨 Ветер: {data['wind']['speed']} м/с"
            )

            # Сохранить в историю
            all_data = load_data()
            all_data["history"].append({
                "user": query.from_user.id,
                "city": city,
                "temp": data['main']['temp']
            })
            save_data(all_data)

            await query.edit_message_text(text)
        else:
            await query.edit_message_text(f"Город {city} не найден")

    except Exception as e:
        await query.edit_message_text(f"Ошибка: {e}")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_city"):
        city = update.message.text
        context.user_data["waiting_city"] = False

        # Отправить "загрузка..."
        msg = await update.message.reply_text("Ищу погоду...")

        # Создать fake query для send_weather
        class FakeQuery:
            def __init__(self, message, user):
                self.message = message
                self.from_user = user
                self.data = f"weather_{city}"
            async def answer(self): pass
            async def edit_message_text(self, text):
                await message.reply_text(text)

        await send_weather(FakeQuery(msg, update.effective_user), city)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(weather_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Weather Bot запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
```

────────────────────
## Что мы научились

- Создавать Telegram ботов на Python
- Использовать команды и inline кнопки
- Хранить данные пользователей
- Интегрировать внешние API
- Обрабатывать callbacks и состояния