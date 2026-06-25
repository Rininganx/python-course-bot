# Цикл while

> Повторяй пока условие истинно — идеально для ввода и меню.

## Theory

`while` выполняет блок кода пока условие `True`. Отличие от `for`: количество повторений **неизвестно** заранее.

Главное — не забывай менять переменную в цикле, иначе будет бесконечный цикл.

`while True` + `break` — стандартный паттерн для бесконечного цикла с выходом. Используется для меню и валидации ввода.

## Code

```python
# Базовый while
count = 1
while count <= 5:
    print(count)
    count += 1  # 1 2 3 4 5

# Бесконечный цикл с выходом
while True:
    cmd = input("Команда (exit для выхода): ")
    if cmd == "exit":
        break
    print(f"Выполняю: {cmd}")

# Валидация ввода — диапазон
while True:
    temp = float(input("Температура (-50..150): "))
    if -50 <= temp <= 150:
        break
    print("Ошибка! Попробуй снова.")

# Валидация — значение из списка
valid = ["game", "work", "silent"]
while True:
    profile = input("Профиль: ").lower()
    if profile in valid:
        break
    print(f"Выбери из: {', '.join(valid)}")

# Счётчик попыток
attempts = 0
while attempts < 3:
    pin = input("PIN: ")
    attempts += 1
    if pin == "1234":
        print("Доступ открыт!")
        break
    print(f"Осталось: {3 - attempts}")
else:
    print("Блокировка!")

# Накопление данных
total = 0
while True:
    num = int(input("Число (0=стоп): "))
    if num == 0:
        break
    total += num
print(f"Сумма: {total}")
```

## Practice

1. Создай меню: 1) Сканирование 2) Оптимизация 0) Выход. Считай количество действий. При выходе выведи итог.
2. Запрашивай число от пользователя, пока не введут число > 0 и < 100.
3. Напиши цикл: `n = 1`. Пока `n < 1000` — умножай на 2. Выведи итог.

## Answers

```python
# Задача 1
actions = 0
while True:
    print("\n1) Сканирование\n2) Оптимизация\n0) Выход")
    choice = input("Выбор: ")
    if choice == "1":
        print("Сканирование...")
        actions += 1
    elif choice == "2":
        print("Оптимизация...")
        actions += 1
    elif choice == "0":
        print(f"Действий: {actions}")
        break

# Задача 2
while True:
    num = int(input("Число (0-100): "))
    if 0 < num < 100:
        print(f"Принято: {num}")
        break
    print("Неверный диапазон!")

# Задача 3
n = 1
while n < 1000:
    n *= 2
print(f"Результат: {n}")
```

## Tips

- Забыл `count += 1` — бесконечный цикл. Всегда меняй переменную условия.
- `Ctrl+C` — экстренная остановка зависшей программы.
- `while True` + `break` — самый читаемый способ сделать меню.
