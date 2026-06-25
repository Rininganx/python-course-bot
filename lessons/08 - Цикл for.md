# Урок 08 — Цикл for

> ⬅ 07 - Сравнения и булевы операторы | 09 - Цикл while ➡

────────────────────
## 🧭 Что ты узнаешь

- Зачем нужны циклы и когда использовать `for`
- Как работает `range()` — все варианты
- Итерация по строке, списку, кортежу
- `enumerate()` — индекс + значение
- `zip()` — два списка одновременно
- Накопители и счётчики в цикле
- Вложенные циклы
- 3 задачи в стиле CodeChef

**Время:** ~50 минут | **XP за задачи:** 45

────────────────────
## 📖 Шаг 1 — Зачем нужны циклы

Представь что нужно проверить 50 запущенных процессов. Без цикла — 50 одинаковых строк кода. С циклом — 3 строки.

```python
# БЕЗ ЦИКЛА — ужасно
print("chrome.exe")
print("discord.exe")
print("steam.exe")
# ... ещё 47 строк

# С ЦИКЛОМ — отлично
processes = ["chrome.exe", "discord.exe", "steam.exe"]
for proc in processes:
    print(proc)
```

`for` используй когда **знаешь заранее** сколько раз нужно повторить, или когда перебираешь элементы коллекции.

────────────────────
## 📖 Шаг 2 — Базовый синтаксис

```python
for переменная in последовательность:
    # тело цикла — выполняется для каждого элемента
    код
# здесь цикл завершён, продолжаем дальше
```

На каждой итерации переменная принимает **следующее значение** из последовательности:

```python
for i in [1, 2, 3, 4, 5]:
    print(i)
```

Вывод:
```
1
2
3
4
5
```

────────────────────
## 📖 Шаг 3 — range()

`range()` генерирует последовательность чисел. Самый частый способ использования `for`.

### range(stop) — от 0 до stop-1

```python
for i in range(5):
    print(i)
# → 0 1 2 3 4
```

⚠️ range(5) даёт 0,1,2,3,4 — не 1,2,3,4,5
> Нумерация всегда начинается с нуля. Число в скобках — это количество итераций, не последний элемент.

### range(start, stop)

```python
for i in range(1, 6):
    print(i)
# → 1 2 3 4 5

for i in range(10, 15):
    print(i)
# → 10 11 12 13 14
```

### range(start, stop, step) — с шагом

```python
# Чётные числа
for i in range(0, 11, 2):
    print(i, end=" ")
# → 0 2 4 6 8 10

# Обратный отсчёт
for i in range(10, 0, -1):
    print(i, end=" ")
# → 10 9 8 7 6 5 4 3 2 1

# Каждые 10%
for pct in range(0, 101, 10):
    print(f"{pct}%", end=" ")
# → 0% 10% 20% 30% 40% 50% 60% 70% 80% 90% 100%
```

### Таблица range()

Вызов • Что генерирует
`range(5)` • 0, 1, 2, 3, 4
`range(1, 6)` • 1, 2, 3, 4, 5
`range(0, 10, 2)` • 0, 2, 4, 6, 8
`range(10, 0, -1)` • 10, 9, 8, ..., 1
`range(5, 5)` • (пусто)

────────────────────
## 📖 Шаг 4 — Итерация по строке

Строка — это последовательность символов, по ней тоже итерируют:

```python
city = "Berlin"

for char in city:
    print(char, end=" ")
# → B e r l i n

# Подсчёт гласных
vowels = "aeiouAEIOU"
word   = "Amsterdam"
count  = 0

for char in word:
    if char in vowels:
        count += 1

print(f"Гласных в '{word}': {count}")
# → Гласных в 'Amsterdam': 3

# Найти позицию символа вручную
filename = "report.txt"
for i, char in enumerate(filename):
    if char == ".":
        print(f"Точка на позиции {i}")
# → Точка на позиции 6
```

────────────────────
## 📖 Шаг 5 — Итерация по списку

```python
cities = ["Berlin", "Munich", "Vienna", "Amsterdam", "Prague"]

for city in cities:
    print(f"Город: {city} (букв: {len(city)})")
```

Вывод:
```
Город: Berlin (букв: 6)
Город: Munich (букв: 6)
Город: Vienna (букв: 6)
Город: Amsterdam (букв: 9)
Город: Prague (букв: 6)
```

────────────────────
## 📖 Шаг 6 — enumerate() — индекс + значение

Когда нужен и порядковый номер элемента, и само значение:

```python
processes = ["chrome.exe", "discord.exe", "steam.exe", "python.exe"]

# Без enumerate — некрасиво
i = 0
for proc in processes:
    print(f"{i}: {proc}")
    i += 1

# С enumerate — питоновский способ
for i, proc in enumerate(processes):
    print(f"{i}: {proc}")
# → 0: chrome.exe
# → 1: discord.exe
# → 2: steam.exe
# → 3: python.exe

# Нумерация с 1
for i, proc in enumerate(processes, start=1):
    print(f"{i}. {proc}")
# → 1. chrome.exe
# → 2. discord.exe
# → 3. steam.exe
# → 4. python.exe
```

────────────────────
## 📖 Шаг 7 — zip() — два списка одновременно

Когда нужно пройти по двум или трём спискам параллельно:

```python
cities      = ["Berlin", "Munich", "Vienna"]
populations = [3_645_000, 1_472_000, 1_897_000]
countries   = ["Germany", "Germany", "Austria"]

for city, pop, country in zip(cities, populations, countries):
    print(f"{city:<12} {pop:>10,}  ({country})")
```

Вывод:
```
Berlin        3,645,000  (Germany)
Munich        1,472,000  (Germany)
Vienna        1,897,000  (Austria)
```

💡 zip() останавливается по самому короткому списку
> ```python
> a = [1, 2, 3, 4, 5]
> b = ["a", "b", "c"]
> for x, y in zip(a, b):
>     print(x, y)
> # → 1 a
> # → 2 b
> # → 3 c  (4 и 5 пропущены — b закончился)
> ```

────────────────────
## 📖 Шаг 8 — Накопители в цикле

Очень частый паттерн — накапливать результат во время цикла:

```python
processes = [
    ("chrome.exe",    850),
    ("discord.exe",   220),
    ("steam.exe",     340),
    ("photoshop.exe", 1240),
    ("python.exe",    180),
]

# ── Сумма ──────────────────────────────
total_ram = 0
for name, mem in processes:
    total_ram += mem
print(f"Итого RAM: {total_ram} MB")
# → Итого RAM: 2830 MB

# ── Максимум ───────────────────────────
max_ram  = 0
max_name = ""
for name, mem in processes:
    if mem > max_ram:
        max_ram  = mem
        max_name = name
print(f"Самый тяжёлый: {max_name} ({max_ram} MB)")
# → Самый тяжёлый: photoshop.exe (1240 MB)

# ── Счётчик ────────────────────────────
heavy_count = 0
for name, mem in processes:
    if mem > 300:
        heavy_count += 1
print(f"Тяжёлых процессов: {heavy_count}")
# → Тяжёлых процессов: 3

# ── Фильтрация ─────────────────────────
heavy = []
for name, mem in processes:
    if mem > 300:
        heavy.append(name)
print(f"Тяжёлые: {heavy}")
# → Тяжёлые: ['chrome.exe', 'steam.exe', 'photoshop.exe']
```

────────────────────
## 📖 Шаг 9 — Вложенные циклы

Цикл внутри цикла. Для каждого элемента внешнего — выполняется весь внутренний:

```python
# Мониторинг нескольких серверов
servers = ["Berlin-01", "Munich-02", "Vienna-03"]
metrics = ["CPU", "RAM", "Disk"]

for server in servers:
    print(f"\n=== {server} ===")
    for metric in metrics:
        print(f"  Проверяю {metric}...")
```

Вывод:
```
=== Berlin-01 ===
  Проверяю CPU...
  Проверяю RAM...
  Проверяю Disk...

=== Munich-02 ===
  Проверяю CPU...
  Проверяю RAM...
  Проверяю Disk...

=== Vienna-03 ===
  Проверяю CPU...
  Проверяю RAM...
  Проверяю Disk...
```

────────────────────
## 📖 Шаг 10 — _ для неиспользуемой переменной

Если переменная цикла не нужна — по соглашению пишут `_`:

```python
# Просто повторить 5 раз
for _ in range(5):
    print("Сканирование...")

# Создать список из N одинаковых элементов
zeros = [0 for _ in range(10)]
print(zeros)   # → [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

────────────────────
## 🔨 Практика — PC Booster

### Пример — полный сканер процессов

```python
processes = [
    ("chrome.exe",    850, 12.5, False),
    ("svchost.exe",    45,  0.5, True),
    ("discord.exe",   220,  3.1, False),
    ("steam.exe",     340,  8.7, False),
    ("photoshop.exe", 1240, 22.1, False),
    ("python.exe",    180,  5.0, False),
]

# Заголовок таблицы
line = "=" * 52
print(line)
print(f"  {'№':<3} {'Процесс':<18} {'RAM':>8} {'CPU':>7} {'Тип'}")
print(line)

total_ram = 0
heavy     = 0

for i, (name, mem, cpu, is_sys) in enumerate(processes, start=1):
    ptype = "SYS" if is_sys else "USR"
    flag  = " ⚠" if mem > 500 else ""
    print(f"  {i:<3} {name:<18} {mem:>6} MB {cpu:>5.1f}% [{ptype}]{flag}")
    total_ram += mem
    if mem > 500:
        heavy += 1

print(line)
print(f"  {'Итого:':<22} {total_ram:>6} MB")
print(f"  Тяжёлых процессов (>500MB): {heavy}")
```

Вывод:
```
====================================================
  №   Процесс              RAM     CPU Тип
====================================================
  1   chrome.exe           850 MB  12.5% [USR] ⚠
  2   svchost.exe           45 MB   0.5% [SYS]
  3   discord.exe          220 MB   3.1% [USR]
  4   steam.exe            340 MB   8.7% [USR]
  5   photoshop.exe       1240 MB  22.1% [USR] ⚠
  6   python.exe           180 MB   5.0% [USR]
====================================================
  Итого:                  2875 MB
  Тяжёлых процессов (>500MB): 2
```

────────────────────
## Задание

PC Booster сканирует список процессов. Напиши программу которая считает статистику.

**Дано:**
```python
processes = [
    ("chrome.exe",    850, 12.5),
    ("discord.exe",   220,  3.1),
    ("steam.exe",     340,  8.7),
    ("photoshop.exe", 1240, 22.1),
    ("python.exe",    180,  5.0),
]
```
Каждый кортеж: `(имя, RAM в MB, CPU в %)`

**Нужно:**
1. Вывести пронумерованный список процессов
2. Посчитать суммарную RAM всех процессов
3. Найти самый тяжёлый процесс (по RAM)
4. Вывести сколько процессов с RAM > 300 MB

**Ожидаемый вывод:**
```
=== Сканирование ===
1. chrome.exe       850 MB  12.5%
2. discord.exe      220 MB   3.1%
3. steam.exe        340 MB   8.7%
4. photoshop.exe   1240 MB  22.1%
5. python.exe       180 MB   5.0%

Суммарная RAM: 2830 MB
Самый тяжёлый: photoshop.exe (1240 MB)
Тяжёлых (>300 MB): 3
```

💡 Подсказка 1
> Используй `enumerate(processes, start=1)` чтобы получить и номер, и данные.

💡 Подсказка 2
> Для поиска максимума — накапливай в переменной: `if mem > max_mem: max_mem = mem`

💡 Подсказка 3
> Счётчик тяжёлых: `heavy += 1` внутри условия `if mem > 300`.

## Решение

```python
processes = [
    ("chrome.exe",    850, 12.5),
    ("discord.exe",   220,  3.1),
    ("steam.exe",     340,  8.7),
    ("photoshop.exe", 1240, 22.1),
    ("python.exe",    180,  5.0),
]

print("=== Сканирование ===")

total_ram = 0
max_ram   = 0
max_name  = ""
heavy     = 0

for i, (name, mem, cpu) in enumerate(processes, start=1):
    print(f"{i}. {name:<18} {mem:>4} MB  {cpu:>5.1f}%")
    total_ram += mem
    if mem > max_ram:
        max_ram = mem
        max_name = name
    if mem > 300:
        heavy += 1

print()
print(f"Суммарная RAM: {total_ram} MB")
print(f"Самый тяжёлый: {max_name} ({max_ram} MB)")
print(f"Тяжёлых (>300 MB): {heavy}")
```

**Разбор:**
1. `enumerate(processes, start=1)` → на каждой итерации `i` = номер (с 1), `(name, mem, cpu)` = данные
2. `total_ram += mem` → накопитель: на каждом шаге прибавляем RAM текущего процесса
3. `if mem > max_ram` → если текущий процесс тяжелее запомненного — обновляем максимум
4. `heavy += 1` → счётчик: увеличиваем только если RAM > 300
5. `f"{name:<18}"` → выравнивание по левому краю на 18 символов для красивой таблицы

────────────────────
## ❌ Частые ошибки

🐛 range(5) — от 0, не от 1
> ```python
> for i in range(5):
>     print(i)
> # → 0 1 2 3 4  (не 1 2 3 4 5!)
>
> for i in range(1, 6):   # если нужно 1–5
>     print(i)
> ```

🐛 Изменение списка во время итерации
> ```python
> lst = [1, 2, 3, 4, 5]
> for item in lst:
>     if item % 2 == 0:
>         lst.remove(item)   # ❌ непредсказуемое поведение!
>
> # ✓ Правильно — итерировать по копии
> for item in lst[:]:
>     if item % 2 == 0:
>         lst.remove(item)
> ```

🐛 Забыть двоеточие после for
> ```python
> for i in range(5)    # ❌ SyntaxError
>     print(i)
>
> for i in range(5):   # ✓
>     print(i)
> ```

────────────────────
## 💡 Заметки на полях

💡 list(range()) — превратить range в список
> ```python
> nums = list(range(1, 6))
> print(nums)   # → [1, 2, 3, 4, 5]
> ```

💡 sum(), min(), max() с range — быстро и без цикла
> ```python
> print(sum(range(1, 101)))   # сумма от 1 до 100 = 5050
> print(max(range(10)))       # → 9
> ```

📝 Связь с PC Booster
> Цикл `for` — основа любого сканера процессов. Получил список процессов от системы (через `psutil`) → прошёл по каждому → проверил условия → вывел таблицу. Именно так работает Task Manager и твой будущий PC Booster.