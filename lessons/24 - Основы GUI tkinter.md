# Основы GUI tkinter

> Библиотека для создания оконных приложений — встроена в Python

## Theory

tkinter — встроенная библиотека Python для GUI. Содержит окна, кнопки, поля ввода, метки. Не требует установки. Идеальна для изучения основ: виджеты, layout, обработка событий. Основа — `Tk()` и `mainloop()`.

## Code

```python
import tkinter as tk

# Первое окно
root = tk.Tk()
root.title("PC Booster")
root.geometry("400x300")
root.resizable(False, False)
root.mainloop()  # всегда последней строкой

# Основные виджеты
root = tk.Tk()
lbl = tk.Label(root, text="Привет!", font=("Arial", 14))
lbl.pack(pady=10)

def on_click():
    lbl.config(text="Нажато!")

btn = tk.Button(root, text="Нажми", command=on_click)
btn.pack(pady=5)

entry = tk.Entry(root, width=25)
entry.pack(pady=5)

tk.Button(root, text="Прочитать", command=lambda: print(entry.get())).pack()

# Layout: pack, grid, place
lbl.pack(side="top", fill="x", pady=5)       # простое размещение
tk.Label(root, text="RAM:").grid(row=0, column=0)  # сетка
btn.place(x=50, y=100)                        # точные координаты

# Связанные переменные
status_var = tk.StringVar(value="Норма")
lbl = tk.Label(root, textvariable=status_var)
status_var.set("Перегрев!")  # Label обновится сам

# Проверка (Checkbutton)
check_var = tk.BooleanVar()
tk.Checkbutton(root, text="Автобуст", variable=check_var).pack()

# Таймер обновления (не time.sleep!)
root.after(2000, update_func)  # вызов через 2 сек
root.destroy()  # закрыть окно
root.quit()     # остановить mainloop
```

## Practice

1. Создай окно с двумя полями ввода (Всего RAM, Занято RAM) и кнопкой "Рассчитать"
2. При нажатии — показать свободную RAM и статус: зелёный (>50%), жёлтый (25-50%), красный (<25%)

## Answers

```python
import tkinter as tk

def calculate():
    try:
        total = float(entry_total.get())
        used = float(entry_used.get())
        free = total - used
        pct = free / total * 100

        result.config(text=f"Свободно: {free:.1f} GB ({pct:.1f}%)")

        if pct < 25:
            status.config(text="Критично", fg="red")
        elif pct < 50:
            status.config(text="Внимание", fg="orange")
        else:
            status.config(text="Норма", fg="green")
    except ValueError:
        result.config(text="Ошибка: введи числа", fg="red")

root = tk.Tk()
root.title("RAM Калькулятор")
root.geometry("300x200")

tk.Label(root, text="Всего RAM (GB):").pack()
entry_total = tk.Entry(root)
entry_total.pack()

tk.Label(root, text="Занято RAM (GB):").pack()
entry_used = tk.Entry(root)
entry_used.pack()

tk.Button(root, text="Рассчитать", command=calculate).pack(pady=10)
result = tk.Label(root, text="Свободно: --- GB")
result.pack()
status = tk.Label(root, text="Статус: ---")
status.pack()
root.mainloop()
```

## Tips

- `mainloop()` всегда последней строкой — всё после неё не выполнится
- Не используй `time.sleep()` — заморозит интерфейс, используй `root.after()`
- `entry.get()` возвращает строку, конвертируй через `float()` с `try/except`
