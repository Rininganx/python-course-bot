# Работа с REST API

> Предыдущая тема: 31 - Веб-скрейпинг
> Следующая тема: 33 - Telegram боты

## Главная идея

API — способ программно общаться с сервисами. Погода, курсы валют, перевод текста, отправка сообщений — всё через API. Это основа 80% фриланс-заказов.

────────────────────
## HTTP методы

```python
import requests

# GET — получить данные
response = requests.get("https://api.example.com/users")
data = response.json()

# POST — создать данные
new_user = {"name": "Андрей", "email": "andrey@test.com"}
response = requests.post("https://api.example.com/users", json=new_user)
print(response.status_code)  # 201 Created

# PUT — обновить данные
update = {"name": "Андрей Иванов"}
response = requests.put("https://api.example.com/users/1", json=update)

# DELETE — удалить данные
response = requests.delete("https://api.example.com/users/1")
```

────────────────────
## Заголовки и авторизация

```python
# API ключ в заголовках
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
response = requests.get("https://api.example.com/data", headers=headers)

# API ключ в параметрах
params = {"api_key": "YOUR_KEY", "q": "python"}
response = requests.get("https://api.example.com/search", params=params)
```

────────────────────
## Практический пример: Погода

```python
import requests

def get_weather(city, api_key):
    """Получить погоду через OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"]
        }
    else:
        return {"error": f"Ошибка: {response.status_code}"}

# Использование
weather = get_weather("Москва", "YOUR_API_KEY")
if "error" not in weather:
    print(f"Погода в {weather['city']}:")
    print(f"  Температура: {weather['temp']}°C")
    print(f"  Описание: {weather['description']}")
    print(f"  Влажность: {weather['humidity']}%")
    print(f"  Ветер: {weather['wind']} м/с")
```

────────────────────
## Обработка ошибок API

```python
import requests
from time import sleep

def api_request(url, max_retries=3):
    """Запрос к API с повторными попытками."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait = int(response.headers.get("Retry-After", 60))
                print(f"Rate limit. Ждём {wait} сек...")
                sleep(wait)
            elif response.status_code >= 500:
                print(f"Ошибка сервера. Попытка {attempt + 1}")
                sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Ошибка клиента: {response.status_code}")
                return None

        except requests.Timeout:
            print(f"Таймаут. Попытка {attempt + 1}")
        except requests.RequestException as e:
            print(f"Ошибка: {e}")
            return None

    return None
```

────────────────────
## Задание

1. Напиши функцию для получения курса валют через API
2. Добавь кэширование результатов (чтобы не делать повторных запросов)
3. Сохрани историю запросов в файл

Используй `https://api.exchangerate-api.com/v4/latest/USD` для курса валют. Для кэширования — словарь с временными метками.

────────────────────
## Решение

```python
import requests
import json
from datetime import datetime, timedelta

CACHE_FILE = "exchange_cache.json"
CACHE_TTL = timedelta(hours=1)

def load_cache():
    """Загрузить кэш из файла."""
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    """Сохранить кэш в файл."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_exchange_rate(base="USD", target="RUB"):
    """Получить курс валют с кэшированием."""
    cache = load_cache()
    cache_key = f"{base}_{target}"

    # Проверить кэш
    if cache_key in cache:
        cached = cache[cache_key]
        cached_time = datetime.fromisoformat(cached["time"])
        if datetime.now() - cached_time < CACHE_TTL:
            print(f"Из кэша: 1 {base} = {cached['rate']} {target}")
            return cached["rate"]

    # Запрос к API
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rate = data["rates"].get(target)
        if rate:
            # Сохранить в кэш
            cache[cache_key] = {
                "rate": rate,
                "time": datetime.now().isoformat()
            }
            save_cache(cache)
            print(f"С API: 1 {base} = {rate} {target}")
            return rate
        else:
            print(f"Валюта {target} не найдена")
            return None

    except requests.RequestException as e:
        print(f"Ошибка API: {e}")
        return None

def get_history():
    """Показать историю запросов."""
    cache = load_cache()
    print("=== История запросов ===")
    for key, value in cache.items():
        print(f"  {key}: {value['rate']} ({value['time'][:16]})")

# Использование
rate = get_exchange_rate("USD", "RUB")
if rate:
    print(f"\n100 USD = {rate * 100} RUB")

get_history()
```

────────────────────
## Что мы научились

- Отправлять GET, POST, PUT, DELETE запросы
- Работать с JSON ответами
- Использовать заголовки и авторизацию
- Обрабатывать ошибки и rate limits
- Кэшировать результаты API запросов