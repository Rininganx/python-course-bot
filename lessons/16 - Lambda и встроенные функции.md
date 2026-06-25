# Lambda и встроенные функции

> Анонимные функции и функциональные инструменты Python.

## Theory

Lambda — одноразовая функция в одну строку: `lambda x: x * 2`. Встроенные `map()`, `filter()`, `sorted()` обрабатывают коллекции без циклов. Делает код короче и выразительнее.

## Code

```python
# Lambda
double = lambda x: x * 2
add = lambda a, b: a + b
print(double(5))  # → 10
print(add(3, 4))  # → 7

# sorted() с key
processes = [("chrome", 850), ("discord", 220), ("steam", 340)]
by_ram = sorted(processes, key=lambda p: p[1], reverse=True)
print(by_ram)  # → [('chrome', 850), ('steam', 340), ('discord', 220)]

# map() — применить функцию к каждому
mems_mb = [850, 220, 340]
mems_gb = list(map(lambda x: round(x / 1024, 2), mems_mb))
print(mems_gb)  # → [0.83, 0.21, 0.33]

# filter() — отфильтровать
heavy = list(filter(lambda x: x > 300, [850, 45, 220, 680]))
print(heavy)  # → [850, 680]

# Встроенные функции
nums = [3, 1, 4, 1, 5]
print(sum(nums))      # → 14
print(min(nums))      # → 1
print(max(nums))      # → 5
print(abs(-42))       # → 42
print(round(3.14, 1)) # → 3.1
print(any([False, True]))  # → True
print(all([True, False]))  # → False
```

## Practice

1. Отсортируй словарь процессов по значению RAM через `sorted()` и `lambda`
2. Используй `map()` чтобы перевести MB в GB для списка `[1024, 2048, 512]`

## Answers

```python
# 1
procs = {"chrome.exe": 850, "steam.exe": 340, "teams.exe": 680}
sorted_procs = sorted(procs.items(), key=lambda x: x[1], reverse=True)
print(sorted_procs)  # → [('chrome.exe', 850), ('teams.exe', 680), ...]

# 2
mb_list = [1024, 2048, 512]
gb_list = list(map(lambda x: x / 1024, mb_list))
print(gb_list)  # → [1.0, 2.0, 0.5]
```

## Tips

- Lambda полезна как аргумент другой функции, для сложного кода пиши `def`
- `map()` и `filter()` возвращают итератор — оборачивай в `list()`
- Часто list comprehension `[x*2 for x in nums]` читабельнее `map(lambda...)`
