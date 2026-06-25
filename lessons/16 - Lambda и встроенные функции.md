# Lambda и встроенные функции

> Предыдущая тема: 15 - Область видимости
> Следующая тема: 17 - Работа с файлами

## Главная идея

Lambda — одноразовая анонимная функция в одну строку. Встроенные функции `map()`, `filter()`, `sorted()` обрабатывают коллекции без явных циклов. Это делает код короче и выразительнее.

────────────────────
## Lambda

```python
# Обычная функция
def double(x):
    return x * 2

# То же самое через lambda
double = lambda x: x * 2

print(double(5))   # → 10

# Lambda с несколькими аргументами
add = lambda a, b: a + b
print(add(3, 4))   # → 7
```

💡 Когда использовать lambda
> Lambda полезна как аргумент другой функции — там где нужна простая функция один раз. Если логика сложнее одного выражения — пиши обычный `def`.

────────────────────
## sorted() с key

```python
processes = [("chrome", 850), ("discord", 220), ("steam", 340)]

# Сортировка по памяти (второй элемент кортежа)
by_ram = sorted(processes, key=lambda p: p[1], reverse=True)
print(by_ram)
# → [('chrome', 850), ('steam', 340), ('discord', 220)]

# Сортировка по имени
by_name = sorted(processes, key=lambda p: p[0])
print(by_name)
# → [('chrome', 850), ('discord', 220), ('steam', 340)]
```

────────────────────
## map() — применить функцию к каждому элементу

```python
mems_mb = [850, 220, 340, 680]

# Перевести в GB
mems_gb = list(map(lambda x: round(x / 1024, 2), mems_mb))
print(mems_gb)   # → [0.83, 0.21, 0.33, 0.66]

# То же через list comprehension (часто читабельнее)
mems_gb = [round(x / 1024, 2) for x in mems_mb]
```

────────────────────
## filter() — отфильтровать коллекцию

```python
mems = [850, 45, 220, 12, 680, 95, 340]

heavy = list(filter(lambda x: x > 300, mems))
print(heavy)   # → [850, 680, 340]

# То же через list comprehension
heavy = [x for x in mems if x > 300]
```

────────────────────
## Полезные встроенные функции

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

print(sum(nums))          # → 31
print(min(nums))          # → 1
print(max(nums))          # → 9
print(len(nums))          # → 8
print(abs(-42))           # → 42
print(round(3.14159, 2))  # → 3.14
print(sorted(nums))       # → [1, 1, 2, 3, 4, 5, 6, 9]
print(list(reversed(nums)))  # → [6, 2, 9, 5, 1, 4, 1, 3]
print(any([False, True, False]))   # → True  (хотя бы один True)
print(all([True, True, True]))     # → True  (все True)
print(all([True, False, True]))    # → False
```

────────────────────
## Практика — PC Booster

```python
processes = [
    {"name": "chrome.exe",  "ram": 850, "cpu": 12.5, "safe": True},
    {"name": "svchost.exe", "ram":  45, "cpu":  0.5, "safe": False},
    {"name": "teams.exe",   "ram": 680, "cpu":  9.1, "safe": True},
    {"name": "discord.exe", "ram": 220, "cpu":  3.2, "safe": True},
    {"name": "steam.exe",   "ram": 340, "cpu":  7.8, "safe": True},
]

# Топ-3 по RAM среди безопасных для завершения
candidates = sorted(
    filter(lambda p: p["safe"] and p["ram"] > 200, processes),
    key=lambda p: p["ram"],
    reverse=True
)[:3]

print("Топ кандидатов на завершение:")
for i, p in enumerate(candidates, 1):
    print(f"  {i}. {p['name']:<15} {p['ram']:>5} MB  CPU: {p['cpu']}%")

# Суммарная RAM всех процессов
total = sum(map(lambda p: p["ram"], processes))
print(f"\nВсего занято: {total} MB")

# Есть ли критические процессы?
has_critical = any(p["ram"] > 800 for p in processes)
print(f"Критические процессы: {'Да' if has_critical else 'Нет'}")
```

Вывод:
```
Топ кандидатов на завершение:
  1. chrome.exe       850 MB  CPU: 12.5%
  2. teams.exe        680 MB  CPU: 9.1%
  3. steam.exe        340 MB  CPU: 7.8%

Всего занято: 2135 MB
Критические процессы: Да
```

────────────────────
## Задание

PC Booster анализирует процессы через функциональные инструменты Python.

**Дано:**
```python
processes = [
    {"name": "photoshop.exe", "ram": 1240, "cpu": 22.1, "safe": True},
    {"name": "lsass.exe",     "ram":   38, "cpu":  0.2, "safe": False},
    {"name": "chrome.exe",    "ram":  920, "cpu": 18.5, "safe": True},
    {"name": "python.exe",    "ram":  180, "cpu":  5.1, "safe": True},
    {"name": "antivirus.exe", "ram":  310, "cpu":  3.4, "safe": False},
    {"name": "discord.exe",   "ram":  215, "cpu":  2.8, "safe": True},
]
```

**Нужно:**
1. Отфильтровать `filter()` — только безопасные с RAM > 200 MB
2. Отсортировать `sorted()` — по CPU по убыванию
3. Преобразовать `map()` — в строки формата `"name: RAM MB / CPU%"`
4. Вывести список и суммарную RAM

**Ожидаемый вывод:**
```
photoshop.exe: 1240 MB / 22.1%
chrome.exe: 920 MB / 18.5%
discord.exe: 215 MB / 2.8%

Суммарная RAM: 2375 MB
```

💡 Подсказка 1
> `filter(lambda p: p["safe"] and p["ram"] > 200, processes)` — оставляет только подходящие.

💡 Подсказка 2
> `sorted(..., key=lambda p: p["cpu"], reverse=True)` — сортировка по CPU от большего.

💡 Подсказка 3
> `map(lambda p: f"{p['name']}: {p['ram']} MB / {p['cpu']}%", filtered)` — превращает словари в строки.

## Решение

```python
processes = [
    {"name": "photoshop.exe", "ram": 1240, "cpu": 22.1, "safe": True},
    {"name": "lsass.exe",     "ram":   38, "cpu":  0.2, "safe": False},
    {"name": "chrome.exe",    "ram":  920, "cpu": 18.5, "safe": True},
    {"name": "python.exe",    "ram":  180, "cpu":  5.1, "safe": True},
    {"name": "antivirus.exe", "ram":  310, "cpu":  3.4, "safe": False},
    {"name": "discord.exe",   "ram":  215, "cpu":  2.8, "safe": True},
]

# Шаг 1: фильтрация
filtered = list(filter(lambda p: p["safe"] and p["ram"] > 200, processes))

# Шаг 2: сортировка
sorted_procs = sorted(filtered, key=lambda p: p["cpu"], reverse=True)

# Шаг 3: строки для вывода
lines = list(map(lambda p: f"{p['name']}: {p['ram']} MB / {p['cpu']}%", sorted_procs))

# Вывод
for line in lines:
    print(line)

total = sum(p["ram"] for p in filtered)
print(f"\nСуммарная RAM: {total} MB")
```

**Разбор:**
1. `filter(функция, коллекция)` — оставляет только элементы где функция вернула `True`
2. `sorted(коллекция, key=функция)` — сортирует по значению которое вернёт `key`
3. `map(функция, коллекция)` — применяет функцию к каждому элементу
4. Цепочка: filter → sorted → map — функциональный стиль, каждая функция делает одно действие
5. `sum(p["ram"] for p in filtered)` — generator expression, не создаёт промежуточный список

────────────────────
## Заметки на полях

💡 `any()` и `all()` — быстрая проверка условий
> ```python
> temps = [72, 68, 91, 75]
> if any(t > 90 for t in temps):
>     print("Есть перегрев!")
> if all(t < 100 for t in temps):
>     print("Всё в безопасном диапазоне")
> ```

📝 map vs comprehension
> ```python
> # map — функциональный стиль
> result = list(map(lambda x: x * 2, nums))
>
> # comprehension — питоновский стиль, чаще предпочтительнее
> result = [x * 2 for x in nums]
> ```
> Оба варианта правильные. В Python-коде comprehension встречается чаще.