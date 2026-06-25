# CustomTkinter

> Современный tkinter с тёмной темой и красивыми виджетами

## Theory

CustomTkinter — обёртка над tkinter с современным дизайном: тёмная тема, закруглённые углы, градиенты. Устанавливается через `pip install customtkinter`. Заменяет стандартные виджеты на `CTk*` версии.

## Code

```python
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("PC Booster")
app.geometry("400x300")

# Виджеты
lbl = ctk.CTkLabel(app, text="PC Booster", font=ctk.CTkFont(size=20, weight="bold"))
lbl.pack(pady=20)

btn = ctk.CTkButton(app, text="Оптимизировать", command=lambda: print("Go!"))
btn.pack(pady=10)

entry = ctk.CTkEntry(app, placeholder_text="Введите имя...")
entry.pack(pady=10)

slider = ctk.CTkSlider(app, from_=0, to=100)
slider.pack(pady=10)
slider.set(75)

switch = ctk.CTkSwitch(app, text="Автобуст")
switch.pack(pady=10)

progress = ctk.CTkProgressBar(app, width=250)
progress.pack(pady=10)
progress.set(0.67)

combo = ctk.CTkComboBox(app, values=["Игровой", "Рабочий", "Тихий"])
combo.pack(pady=10)

# Вкладки
tabs = ctk.CTkTabview(app)
tabs.add("Статус")
tabs.add("Настройки")
ctk.CTkLabel(tabs.tab("Статус"), text="Система в норме").pack(pady=20)

# Frame — контейнер
sidebar = ctk.CTkFrame(app, width=160, corner_radius=0)
sidebar.pack(side="left", fill="y")
content = ctk.CTkFrame(app, fg_color="transparent")
content.pack(side="left", fill="both", expand=True)

app.mainloop()
```

## Practice

1. Создай приложение с тремя кнопками профилей (Игровой, Рабочий, Тихий)
2. При переключении — показывай имя профиля и лог с временем

## Answers

```python
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Профили")
app.geometry("400x300")

current_profile = ctk.StringVar(value="Игровой")

def set_profile(name):
    current_profile.set(name)
    ts = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{ts}] Профиль: {name}\n")
    log_box.see("end")

ctk.CTkLabel(app, textvariable=current_profile,
             font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=5)

for name in ["Игровой", "Рабочий", "Тихий"]:
    ctk.CTkButton(btn_frame, text=name, width=100,
                  command=lambda n=name: set_profile(n)).pack(side="left", padx=5)

ctk.CTkLabel(app, text="Лог:").pack(padx=20, pady=(10, 0), anchor="w")
log_box = ctk.CTkTextbox(app, height=120)
log_box.pack(padx=20, pady=5)

set_profile("Игровой")
app.mainloop()
```

## Tips

- Используй классы для приложений с 5+ виджетами — храните переменные в `self`
- `lambda n=name: func(n)` — захват текущего значения в цикле
- `app.iconbitmap("icon.ico")` — установка иконки
