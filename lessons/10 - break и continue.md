# break и continue

> Предыдущая тема: 09 - Цикл while
> Следующая тема: 11 - Списки

## Главная идея

`break` — досрочно выходит из цикла. `continue` — пропускает текущую итерацию и идёт к следующей. Оба делают циклы гибче.

────────────────────
## break — выход из цикла

```python
for i in range(10):
    if i == 5:
        break
    print(i)
# → 0 1 2 3 4  (остановился на 5)
```

```python
# Найти первый проблемный процесс и остановиться
processes = ["chrome", "svchost", "malware", "discord"]

for proc in processes:
    if proc == "malware":
        print(f"Найден: {proc} — стоп!")
        break
    print(f"OK: {proc}")
```

────────────────────
## continue — пропуск итерации

```python
for i in range(6):
    if i % 2 == 0:
        continue       # пропускаем чётные
    print(i)
# → 1 3 5
```

```python
# Вывести только тяжёлые процессы, лёгкие пропустить
processes = [("chrome", 850), ("calc", 12), ("steam", 340), ("notepad", 8)]

for name, mem in processes:
    if mem < 100:
        continue       # пропускаем лёгкие
    print(f"{name}: {mem} MB")

# → chrome: 850 MB
# → steam: 340 MB
```

────────────────────
## break vs continue

 • `break` • `continue`
Что делает • Выходит из цикла полностью • Пропускает эту итерацию
Цикл продолжается? • Нет • Да
Аналогия • Экстренный стоп • Пропустить шаг

────────────────────
## Флаг как альтернатива break

Иногда нужно выйти из вложенного цикла — `break` выходит только из внутреннего. Используй флаг:

```python
found = False

for group in [["svchost", "chrome"], ["malware", "steam"]]:
    for proc in group:
        if proc == "malware":
            found = True
            break
    if found:
        break

print("Найдено!" if found else "Чисто")
```

────────────────────
## Практика — PC Booster

```python
processes = [
    ("svchost.exe",   45,  True),
    ("chrome.exe",   920, False),
    ("malware.exe",  200, False),
    ("discord.exe",  220, False),
    ("teams.exe",    680, False),
]

print("=== Сканирование процессов ===")

suspicious = []

for name, mem, is_system in processes:
    # Пропускаем системные
    if is_system:
        print(f"[SYS] {name} — пропущен")
        continue

    # Стоп если нашли malware
    if "malware" in name:
        print(f" {name} — УГРОЗА ОБНАРУЖЕНА. Стоп.")
        suspicious.append(name)
        break

    print(f"[OK]  {name} — {mem} MB")

if suspicious:
    print(f"\nПодозрительные: {', '.join(suspicious)}")
```

Вывод:
```
=== Сканирование процессов ===
[SYS] svchost.exe — пропущен
[OK]  chrome.exe — 920 MB
 malware.exe — УГРОЗА ОБНАРУЖЕНА. Стоп.

Подозрительные: malware.exe
```

────────────────────
## Задание

PC Booster ищет самый тяжёлый процесс. Напиши программу которая проходит по списку и останавливается на первом критическом.

**Дано:**
```python
processes = [
    ("explorer.exe",  95),
    ("chrome.exe",   820),
    ("python.exe",   180),
    ("teams.exe",    910),
    ("discord.exe",  215),
    ("photoshop.exe",1240),
]
```

**Нужно:**
1. Пройти по списку циклом `for`
2. Если RAM < 200 MB — вывести "Пропуск" и `continue`
3. Вывести "Проверка" для остальных
4. Если RAM > 900 MB — вывести "СТОП" и `break`
5. Если ни один не найден — вывести "Нет критических"

**Ожидаемый вывод:**
```
Пропуск: explorer.exe (95 MB)
Проверка: chrome.exe (820 MB)
Пропуск: python.exe (180 MB)
Проверка: teams.exe (910 MB)
СТОП — критический процесс: teams.exe (910 MB)
```

💡 Подсказка 1
> Используй `continue` для пропуска лёгких процессов — код после `continue` не выполнится.

💡 Подсказка 2
> `break` полностью выходит из цикла — код после цикла продолжит работу.

💡 Подсказка 3
> Чтобы проверить что цикл завершился без `break`, используй `for...else`: блок `else` выполнится только если не было `break`.

## Решение

```python
processes = [
    ("explorer.exe",  95),
    ("chrome.exe",   820),
    ("python.exe",   180),
    ("teams.exe",    910),
    ("discord.exe",  215),
    ("photoshop.exe",1240),
]

for name, mem in processes:
    if mem < 200:
        print(f"Пропуск: {name} ({mem} MB)")
        continue

    print(f"Проверка: {name} ({mem} MB)")

    if mem > 900:
        print(f"СТОП — критический процесс: {name} ({mem} MB)")
        break
else:
    print("Нет критических процессов")
```

**Разбор:**
1. `if mem < 200: continue` → пропускаем лёгкие процессы, идём к следующему
2. `print("Проверка...")` → выполняется только если RAM >= 200
3. `if mem > 900: break` → нашли критический → выходим из цикла
4. `else` после `for` → выполняется **только** если цикл завершился без `break`
5. Если бы не было процесса > 900 MB — сработал бы `else`

────────────────────
## Заметки на полях

💡 `for ... else` — редко но полезно
> ```python
> for proc in processes:
>     if proc == "malware":
>         break
> else:
>     print("Всё чисто")  # выполнится только если break не сработал
> ```

⚠️ `continue` в `while` — не забудь про шаг
> ```python
> i = 0
> while i < 5:
>     i += 1        # ← должно быть ДО continue
>     if i == 3:
>         continue
>     print(i)
> ```
> Если инкремент ПОСЛЕ `continue` — попадёшь в бесконечный цикл.