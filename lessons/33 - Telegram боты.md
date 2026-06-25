# Telegram боты

> Самый популярный тип заказов на Python-фрилансе

## Theory

Telegram бот — приложение внутри Telegram. `python-telegram-bot` — основная библиотека. Боты принимают заказы, отправляют уведомления, парсят данные. Настройка: @BotFather → `/newbot` → скопировать токен.

## Code

```bash
pip install python-telegram-bot
```

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Привет, {update.effective_user.first_name}!")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Погода", callback_data="weather"),
         InlineKeyboardButton("Курс", callback_data="rate")]
    ]
    await update.message.reply_text("Выбери:",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "weather":
        await query.edit_message_text("Погода: 25°C")
    elif query.data == "rate":
        await query.edit_message_text("USD/RUB: 89.5")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
```

```python
# Хранение данных
import json
from pathlib import Path

DATA_FILE = Path("bot_data.json")

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
```

## Practice

1. Создай бота с командами /start, /help, /weather
2. Добавь inline кнопки и историю запросов

## Answers

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import requests, json
from pathlib import Path

TOKEN = "YOUR_BOT_TOKEN"
DATA_FILE = Path("weather_data.json")

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"history": []}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Москва", callback_data="Москва"),
                 InlineKeyboardButton("Питер", callback_data="Санкт-Петербург")]]
    await update.message.reply_text("Выбери город:",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": "KEY", "units": "metric", "lang": "ru"})
    if response.status_code == 200:
        data = response.json()
        text = f"Погода в {city}: {data['main']['temp']}°C"
        all_data = load_data()
        all_data["history"].append({"city": city, "temp": data['main']['temp']})
        save_data(all_data)
        await query.edit_message_text(text)
    else:
        await query.edit_message_text("Город не найден")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(weather))
app.run_polling()
```

## Tips

- Используй `context.user_data` для хранения состояния пользователя
- `async def` — все обработчики должны быть асинхронными
- Не храни токен в коде — используй переменные окружения
