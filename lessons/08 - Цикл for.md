# Цикл for

> Повторяй действия для каждого элемента — 3 строки вместо 50.

## Theory

`for` перебирает элементы последовательности. Используй когда **знаешь** количество повторений.

`range(n)` — числа от 0 до n-1. `range(start, stop, step)` — с шагом.

`enumerate(list)` — даёт индекс + значение. `zip(a, b)` — идёт по двум спискам параллельно.

Накопители: `total += x` для суммы, `count += 1` для подсчёта, `if x > max: max = x` для максимума.

`_` используется когда переменная цикла не нужна: `for _ in range(5)`.

## Code

```python
# Базовый for
for i in range(5):
    print(i)          # 0 1 2 3 4

# range(start, stop, step)
for i in range(1, 6):
    print(i)          # 1 2 3 4 5

for i in range(0, 11, 2):
    print(i, end=" ") # 0 2 4 6 8 10

# Обратный отсчёт
for i in range(10, 0, -1):
    print(i, end=" ") # 10 9 8 7 6 5 4 3 2 1

# Итерация по строке
for char in "Python":
    print(char, end=" ")  # P y t h o n

# enumerate — индекс + значение
cities = ["Berlin", "Munich", "Vienna"]
for i, city in enumerate(cities, start=1):
    print(f"{i}. {city}")

# zip — два списка параллельно
names = ["CPU", "RAM", "Disk"]
values = [72, 85, 45]
for name, val in zip(names, values):
    print(f"{name}: {val}%")

# Накопитель — сумма и максимум
nums = [10, 25, 8, 30]
total = 0
max_val = 0
for n in nums:
    total += n
    if n > max_val:
        max_val = n
print(f"Сумма: {total}, Макс: {max_val}")

# Вложенные циклы
servers = ["SRV-01", "SRV-02"]
metrics = ["CPU", "RAM"]
for srv in servers:
    for m in metrics:
        print(f"{srv} — проверка {m}")
```

## Practice

1. Дан список процессов `[("chrome", 850), ("calc", 12), ("steam", 340)]`. Выведи пронумерованный список и общую RAM.
2. Посчитай количество чётных чисел в `range(1, 21)`.
3. Используя `zip`, выведи пары: `names = ["a","b","c"]`, `scores = [100, 85, 92]`.
4. Найди максимальное число в `nums = [3, 7, 1, 9, 4]` вручную через цикл (без `max()`).

## Answers

```python
# Задача 1
processes = [("chrome", 850), ("calc", 12), ("steam", 340)]
total = 0
for i, (name, ram) in enumerate(processes, 1):
    print(f"{i}. {name} — {ram} MB")
    total += ram
print(f"Итого: {total} MB")

# Задача 2
count = 0
for i in range(1, 21):
    if i % 2 == 0:
        count += 1
print(f"Чётных: {count}")

# Задача 3
names = ["a", "b", "c"]
scores = [100, 85, 92]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Задача 4
nums = [3, 7, 1, 9, 4]
max_val = nums[0]
for n in nums:
    if n > max_val:
        max_val = n
print(f"Максимум: {max_val}")
```

## Tips

- `range(5)` — от 0 до 4, не от 1 до 5.
- Не изменяй список во время итерации — итерируй по копии `lst[:]`.
- Если переменная цикла не нужна, используй `_`.
