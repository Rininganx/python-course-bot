# Работа с REST API

> Программное общение с сервисами через HTTP запросы

## Theory

API — способ получить/отправить данные. GET — получить, POST — создать, PUT — обновить, DELETE — удалить. Авторизация через заголовки или параметры. JSON — основной формат данных. Основа 80% фриланс-заказов.

## Code

```python
import requests

# GET — получить данные
response = requests.get("https://api.example.com/users")
data = response.json()

# POST — создать
new_user = {"name": "Андрей", "email": "andrey@test.com"}
response = requests.post("https://api.example.com/users", json=new_user)

# Авторизация
headers = {"Authorization": "Bearer YOUR_API_KEY"}
response = requests.get("https://api.example.com/data", headers=headers)

# Погода через OpenWeatherMap
def get_weather(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "ru"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"],
        }
    return {"error": response.status_code}

# Запрос с повторными попытками
def api_request(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                import time; time.sleep(60)
        except requests.Timeout:
            continue
    return None
```

## Practice

1. Напиши функцию курса валют через `https://api.exchangerate-api.com/v4/latest/USD`
2. Добавь кэширование в JSON файл на 1 час

## Answers

```python
import requests, json
from datetime import datetime, timedelta

CACHE_FILE = "cache.json"

def get_rate(base="USD", target="RUB"):
    try:
        with open(CACHE_FILE) as f: cache = json.load(f)
    except: cache = {}

    key = f"{base}_{target}"
    if key in cache:
        cached_time = datetime.fromisoformat(cache[key]["time"])
        if datetime.now() - cached_time < timedelta(hours=1):
            print(f"Из кэша: 1 {base} = {cache[key]['rate']} {target}")
            return cache[key]["rate"]

    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base}", timeout=10)
    if response.status_code == 200:
        rate = response.json()["rates"][target]
        cache[key] = {"rate": rate, "time": datetime.now().isoformat()}
        with open(CACHE_FILE, "w") as f: json.dump(cache, f, indent=2)
        print(f"С API: 1 {base} = {rate} {target}")
        return rate
    return None

rate = get_rate("USD", "RUB")
if rate: print(f"100 USD = {rate * 100} RUB")
```

## Tips

- Всегда проверяй `response.status_code` перед чтением `.json()`
- `timeout=10` — предотвращает зависание
- Кэшируй результаты чтобы не превышать rate limits
