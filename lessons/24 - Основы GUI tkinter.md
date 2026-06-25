# Основы GUI tkinter

> Предыдущая тема: 23 - Планировщик задач
> Следующая тема: 25 - CustomTkinter

## Главная идея

`tkinter` — встроенная библиотека Python для создания оконных приложений. Не требует установки. Это не самый красивый фреймворк, но идеален для понимания основ GUI — окна, кнопки, метки, поля ввода.

────────────────────
## Первое окно

```python
import tkinter as tk

root = tk.Tk()
root.title("PC Booster")
root.geometry("400x300")    # ширина x высота
root.resizable(False, False) # запретить изменение размера

root.mainloop()   # запустить цикл событий (всегда последняя строка)
```

────────────────────
## Основные виджеты

```python
import tkinter as tk

root = tk.Tk()
root.title("Виджеты")
root.geometry("300x250")

# Label — текстовая метка
lbl = tk.Label(root, text="Привет, PC Booster!", font=("Arial", 14))
lbl.pack(pady=10)

# Button — кнопка
def on_click():
    lbl.config(text="Нажато!")

btn = tk.Button(root, text="Нажми меня", command=on_click)
btn.pack(pady=5)

# Entry — поле ввода
entry = tk.Entry(root, width=25)
entry.pack(pady=5)

# Чтение значения из Entry
def read_entry():
    print(entry.get())

tk.Button(root, text="Прочитать", command=read_entry).pack()

# Text — многострочный текст
txt = tk.Text(root, height=4, width=30)
txt.pack(pady=5)
txt.insert("1.0", "Многострочный\nтекст")

root.mainloop()
```

────────────────────
## Layouts — размещение виджетов

```python
# pack() — простое размещение
lbl.pack(side="top", fill="x", pady=5)
btn.pack(side="left", padx=5)

# grid() — сетка (строки и столбцы)
tk.Label(root, text="RAM:").grid(row=0, column=0, sticky="w", padx=5)
tk.Label(root, text="16 GB").grid(row=0, column=1, sticky="e", padx=5)

tk.Label(root, text="CPU:").grid(row=1, column=0, sticky="w", padx=5)
tk.Label(root, text="72°C").grid(row=1, column=1, sticky="e", padx=5)

# place() — точные координаты
btn.place(x=50, y=100)
```

────────────────────
## Переменные tkinter

```python
# StringVar, IntVar, BooleanVar — переменные связанные с виджетами
status_var = tk.StringVar(value="Норма")
check_var  = tk.BooleanVar(value=False)

# Label обновляется автоматически при изменении переменной
lbl = tk.Label(root, textvariable=status_var)
lbl.pack()

# Изменить — Label обновится сам
status_var.set("Перегрев!")

# Checkbutton
chk = tk.Checkbutton(root, text="Автобуст", variable=check_var)
chk.pack()
print(check_var.get())   # True или False
```

────────────────────
## Практика — PC Booster (простой монитор)

```python
import tkinter as tk
import psutil

def update_stats():
    """Обновляет данные каждые 2 секунды."""
    cpu  = psutil.cpu_percent(interval=None)
    ram  = psutil.virtual_memory()

    cpu_var.set(f"CPU:  {cpu:.1f}%")
    ram_var.set(f"RAM:  {ram.percent:.1f}%  ({ram.available/1024**3:.1f} GB свободно)")

    # Цвет по уровню загрузки
    cpu_lbl.config(fg="red" if cpu > 80 else "orange" if cpu > 50 else "green")
    ram_lbl.config(fg="red" if ram.percent > 85 else "orange" if ram.percent > 70 else "green")

    root.after(2000, update_stats)   # повторить через 2000 мс

root = tk.Tk()
root.title("PC Booster — Монитор")
root.geometry("320x150")
root.configure(bg="#1e1e1e")

cpu_var = tk.StringVar(value="CPU:  ---")
ram_var = tk.StringVar(value="RAM:  ---")

cpu_lbl = tk.Label(root, textvariable=cpu_var, font=("Consolas", 14),
                   bg="#1e1e1e", fg="green")
cpu_lbl.pack(pady=15)

ram_lbl = tk.Label(root, textvariable=ram_var, font=("Consolas", 14),
                   bg="#1e1e1e", fg="green")
ram_lbl.pack()

tk.Button(root, text="Обновить", command=update_stats,
          bg="#333", fg="white").pack(pady=10)

update_stats()
root.mainloop()
```

────────────────────
## Задание

PC Booster показывает калькулятор RAM в окне. Сделай GUI с tkinter.

**Дано:**
- Два поля ввода: "Всего RAM (GB)" и "Занято RAM (GB)"
- Кнопка "Рассчитать"

**Нужно:**
1. Считать свободную RAM и процент
2. Вывести результат: свободно и статус
3. Статус: < 25% свободно → "Критично" (красный), < 50% → "Внимание" (жёлтый), иначе → "Норма" (зелёный)
4. Обработать нечисловой ввод через `try/except`

**Ожидаемый вид окна:**
```
[ Всего RAM (GB): 16    ]
[ Занято RAM (GB): 12   ]
[ Рассчитать              ]

Свободно: 4.0 GB (25.0%)
Статус: Внимание
```

💡 Подсказка 1
> `float(entry.get())` — получает текст из поля и конвертирует в число.

💡 Подсказка 2
> `label.config(text="...", fg="red")` — меняет текст и цвет метки.

💡 Подсказка 3
> `try/except ValueError` вокруг `float()` — если пользователь введёт не число.

## Решение

```python
import tkinter as tk

def calculate():
    try:
        total = float(entry_total.get())
        used  = float(entry_used.get())

        if total <= 0 or used < 0 or used > total:
            result_label.config(text="Ошибка: некорректные значения", fg="red")
            return

        free     = total - used
        free_pct = free / total * 100

        result_label.config(text=f"Свободно: {free:.1f} GB ({free_pct:.1f}%)")

        if free_pct < 25:
            status_label.config(text="Статус: Критично", fg="red")
        elif free_pct < 50:
            status_label.config(text="Статус: Внимание", fg="orange")
        else:
            status_label.config(text="Статус: Норма", fg="green")

    except ValueError:
        result_label.config(text="Ошибка: введи числа", fg="red")

root = tk.Tk()
root.title("PC Booster — RAM Калькулятор")
root.geometry("300x200")

tk.Label(root, text="Всего RAM (GB):").pack(pady=(10, 0))
entry_total = tk.Entry(root, width=20)
entry_total.pack()

tk.Label(root, text="Занято RAM (GB):").pack(pady=(5, 0))
entry_used = tk.Entry(root, width=20)
entry_used.pack()

tk.Button(root, text="Рассчитать", command=calculate).pack(pady=10)

result_label = tk.Label(root, text="Свободно: --- GB (---%)")
result_label.pack()

status_label = tk.Label(root, text="Статус: ---")
status_label.pack()

root.mainloop()
```

**Разбор:**
1. `entry.get()` → получает текст из поля ввода как строку
2. `float(...)` → конвертирует строку в дробное число. Если не число → `ValueError`
3. `label.config(text=..., fg=...)` → обновляет текст и цвет виджета
4. `command=calculate` → привязывает функцию к кнопке (вызывается при нажатии)
5. `root.mainloop()` → запускает цикл обработки событий окна (всегда последней строкой)

────────────────────
## Заметки на полях

⚠️ `mainloop()` — всегда последним
> Всё что после `root.mainloop()` не выполнится пока окно не закроется. Размещай логику до `mainloop()` или в функциях-обработчиках.

💡 `root.after(ms, func)` — таймер
> Правильный способ делать обновления в tkinter. Не используй `time.sleep()` — это заморозит весь интерфейс.

📝 Закрыть окно программно
> ```python
> root.destroy()    # закрыть окно
> root.quit()       # остановить mainloop
> ```