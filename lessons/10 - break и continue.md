# break и continue

> Управляй циклом: выходи досрочно или пропускай итерации.

## Theory

`break` — полностью выходит из цикла. `continue` — пропускает текущую итерацию и переходит к следующей.

`for...else` — блок `else` выполняется только если цикл завершился **без** `break`. Полезно для проверки "ничего не найдено".

Во вложенных циклах `break` выходит только из внутреннего. Для выхода из внешнего используй флаг.

## Code

```python
# break — выход на 5
for i in range(10):
    if i == 5:
        break
    print(i)    # 0 1 2 3 4

# continue — пропуск чётных
for i in range(6):
    if i % 2 == 0:
        continue
    print(i)    # 1 3 5

# continue — фильтрация процессов
processes = [("chrome", 850), ("calc", 12), ("steam", 340)]
for name, ram in processes:
    if ram < 100:
        continue
    print(f"{name}: {ram} MB")

# for...else — поиск с результатом
targets = ["chrome", "svchost", "discord"]
search = "malware"
for proc in targets:
    if proc == search:
        print(f"Найден: {proc}")
        break
else:
    print("Не найден — система чиста")

# Флаг для выхода из вложенного цикла
found = False
groups = [["a", "b"], ["c", "malware"]]
for group in groups:
    for proc in group:
        if proc == "malware":
            found = True
            break
    if found:
        break
print("Найдено!" if found else "Чисто")

# continue в while — аккуратно с инкрементом
i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)  # 1 2 4 5
```

## Practice

1. Дан список `[95, 820, 180, 910, 215]`. Пропусти значения < 200 (`continue`), выведи остальные. Остановись при значении > 900 (`break`).
2. Поиск элемента: `nums = [3, 7, 2, 9, 5]`. Найди число 9 с помощью `break`. Если не найдено — выведи через `for...else`.
3. Напиши бесконечный цикл ввода чисел. При вводе 0 — выход (`break`). Считай сумму введённых.

## Answers

```python
# Задача 1
data = [95, 820, 180, 910, 215]
for val in data:
    if val < 200:
        print(f"Пропуск: {val}")
        continue
    print(f"Проверка: {val}")
    if val > 900:
        print(f"СТОП: {val}")
        break

# Задача 2
nums = [3, 7, 2, 9, 5]
for n in nums:
    if n == 9:
        print(f"Найден: {n}")
        break
else:
    print("Не найден")

# Задача 3
total = 0
while True:
    num = int(input("Число (0 = выход): "))
    if num == 0:
        break
    total += num
print(f"Сумма: {total}")
```

## Tips

- `continue` в `while` — инкремент должен быть **до** `continue`, иначе бесконечный цикл.
- `break` выходит только из одного цикла. Для вложенных — используй флаг.
- `for...else` — else сработает только если не было `break`.
