# CustomTkinter

> Предыдущая тема: 24 - Основы GUI tkinter
> Следующая тема: 26 - Дизайн интерфейса

## Главная идея

CustomTkinter — это современный tkinter с красивыми виджетами, тёмной темой и закруглёнными углами. Выглядит как нормальное современное приложение, не как Windows 95. Устанавливается одной командой.

────────────────────
## Установка

```bash
pip install customtkinter
```

────────────────────
## Первое окно

```python
import customtkinter as ctk

ctk.set_appearance_mode("dark")      # "dark" | "light" | "system"
ctk.set_default_color_theme("blue")  # "blue" | "green" | "dark-blue"

app = ctk.CTk()
app.title("PC Booster")
app.geometry("500x400")

app.mainloop()
```

────────────────────
## Основные виджеты CTk

```python
import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x500")
app.title("Виджеты CTk")

# Label
lbl = ctk.CTkLabel(app, text="PC Booster", font=ctk.CTkFont(size=20, weight="bold"))
lbl.pack(pady=20)

# Button
btn = ctk.CTkButton(app, text="Оптимизировать", command=lambda: print("Go!"),
                    corner_radius=8, fg_color="#7F77DD", hover_color="#534AB7")
btn.pack(pady=10)

# Entry
entry = ctk.CTkEntry(app, placeholder_text="Введите имя ПК...", width=250)
entry.pack(pady=10)

# Slider
slider = ctk.CTkSlider(app, from_=0, to=100, number_of_steps=100)
slider.pack(pady=10)
slider.set(75)

# Switch
switch = ctk.CTkSwitch(app, text="Автобуст")
switch.pack(pady=10)

# ProgressBar
progress = ctk.CTkProgressBar(app, width=250)
progress.pack(pady=10)
progress.set(0.67)  # 67%

# ComboBox
combo = ctk.CTkComboBox(app, values=["Игровой", "Рабочий", "Тихий"])
combo.pack(pady=10)
combo.set("Игровой")

# Checkbox
check = ctk.CTkCheckBox(app, text="Запускать при старте")
check.pack(pady=10)

# Tabview — вкладки
tabs = ctk.CTkTabview(app, width=350, height=120)
tabs.pack(pady=10)
tabs.add("Статус")
tabs.add("Настройки")
tabs.add("Лог")
ctk.CTkLabel(tabs.tab("Статус"), text="Система в норме").pack(pady=20)

app.mainloop()
```

────────────────────
## Frame — контейнер для виджетов

```python
import customtkinter as ctk

app = ctk.CTk()
app.geometry("500x400")

# Sidebar (боковая панель)
sidebar = ctk.CTkFrame(app, width=160, corner_radius=0)
sidebar.pack(side="left", fill="y")

# Основной контент
content = ctk.CTkFrame(app, fg_color="transparent")
content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

# Заголовок сайдбара
ctk.CTkLabel(sidebar, text="PC Booster",
             font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20, padx=20)

# Кнопки навигации
for name in ["Монитор", "Оптимизация", "Автозагрузка", "Настройки"]:
    ctk.CTkButton(sidebar, text=name, anchor="w",
                  fg_color="transparent", hover_color="#2b2b2b").pack(
        fill="x", padx=10, pady=2
    )

# Контент
ctk.CTkLabel(content, text="Добро пожаловать",
             font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")

app.mainloop()
```

────────────────────
## Практика — PC Booster Dashboard

```python
import customtkinter as ctk
import psutil

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PCBoosterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Booster")
        self.geometry("600x400")
        self.resizable(False, False)

        self._build_ui()
        self._update_stats()

    def _build_ui(self):
        # Заголовок
        ctk.CTkLabel(self, text="PC Booster",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15)

        # Фрейм метрик
        metrics = ctk.CTkFrame(self)
        metrics.pack(fill="x", padx=20, pady=5)
        metrics.columnconfigure((0, 1, 2), weight=1)

        # CPU
        ctk.CTkLabel(metrics, text="CPU",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=8)
        self.cpu_lbl = ctk.CTkLabel(metrics, text="---%")
        self.cpu_lbl.grid(row=1, column=0)
        self.cpu_bar = ctk.CTkProgressBar(metrics, width=150)
        self.cpu_bar.grid(row=2, column=0, padx=15, pady=8)

        # RAM
        ctk.CTkLabel(metrics, text="RAM",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, pady=8)
        self.ram_lbl = ctk.CTkLabel(metrics, text="---%")
        self.ram_lbl.grid(row=1, column=1)
        self.ram_bar = ctk.CTkProgressBar(metrics, width=150)
        self.ram_bar.grid(row=2, column=1, padx=15, pady=8)

        # DISK
        ctk.CTkLabel(metrics, text="Диск C:",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, pady=8)
        self.disk_lbl = ctk.CTkLabel(metrics, text="---%")
        self.disk_lbl.grid(row=1, column=2)
        self.disk_bar = ctk.CTkProgressBar(metrics, width=150)
        self.disk_bar.grid(row=2, column=2, padx=15, pady=8)

        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Оптимизировать",
                      fg_color="#7F77DD", hover_color="#534AB7",
                      command=self._optimize).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Очистить Temp",
                      command=self._clean_temp).pack(side="left", padx=8)

        # Лог
        self.log = ctk.CTkTextbox(self, height=100)
        self.log.pack(fill="x", padx=20, pady=5)

    def _update_stats(self):
        cpu  = psutil.cpu_percent(interval=None)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")

        self.cpu_lbl.configure(text=f"{cpu:.1f}%")
        self.ram_lbl.configure(text=f"{ram.percent:.1f}%")
        self.disk_lbl.configure(text=f"{disk.percent:.1f}%")

        self.cpu_bar.set(cpu / 100)
        self.ram_bar.set(ram.percent / 100)
        self.disk_bar.set(disk.percent / 100)

        self.after(2000, self._update_stats)

    def _optimize(self):
        self.log.insert("end", "✓ Оптимизация выполнена\n")
        self.log.see("end")

    def _clean_temp(self):
        self.log.insert("end", "✓ Temp очищен\n")
        self.log.see("end")

app = PCBoosterApp()
app.mainloop()
```

────────────────────
## Задание

PC Booster использует CustomTkinter для современного интерфейса. Добавь переключатель профилей.

**Дано:**
- Три профиля: Игровой, Рабочий, Тихий
- При выборе — в лог пишется время и название

**Нужно:**
1. Три кнопки с профилями в ряд
2. Метка текущего профиля
3. Лог внизу — записывает каждое переключение с временем

**Ожидаемый вид:**
```
[ Текущий: Игровой           ]
[ Игровой ] [ Рабочий ] [ Тихий ]

Лог:
[12:30:01] Профиль: Игровой
[12:30:05] Профиль: Рабочий
```

💡 Подсказка 1
> `ctk.CTkButton(master, text="Игровой", command=lambda: set_profile("Игровой"))` — кнопка с аргументом.

💡 Подсказка 2
> `ctk.CTkTextbox` — многострочное текстовое поле для лога. `.insert("end", text)` добавляет строку.

💡 Подсказка 3
> `datetime.now().strftime("%H:%M:%S")` — текущее время для лога.

## Решение

```python
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("PC Booster — Профили")
app.geometry("400x300")

current_profile = ctk.StringVar(value="Игровой")

def set_profile(name: str):
    current_profile.set(name)
    ts = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{ts}] Профиль: {name}\n")
    log_box.see("end")  # автопрокрутка вниз

# Заголовок
header = ctk.CTkLabel(
    app,
    textvariable=current_profile,
    font=ctk.CTkFont(size=18, weight="bold")
)
header.pack(pady=(15, 5))

# Кнопки профилей
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=5, padx=20)

for name in ["Игровой", "Рабочий", "Тихий"]:
    ctk.CTkButton(
        btn_frame, text=name, width=100,
        command=lambda n=name: set_profile(n)
    ).pack(side="left", padx=5)

# Лог
ctk.CTkLabel(app, text="Лог:", anchor="w").pack(fill="x", padx=20, pady=(10, 0))
log_box = ctk.CTkTextbox(app, height=120, width=360)
log_box.pack(padx=20, pady=(0, 10))

set_profile("Игровой")
app.mainloop()
```

**Разбор:**
1. `ctk.StringVar(value=...)` → реактивная переменная, привязанная к виджету
2. `textvariable=current_profile` → текст метки обновляется автоматически
3. `lambda n=name: set_profile(n)` → замыкание захватывает текущее значение `name`
4. `log_box.insert("end", text)` → добавляет текст в конец текстового поля
5. `log_box.see("end")` → прокручивает к последней строке

────────────────────
## Заметки на полях

💡 Классы для сложных приложений
> Как только в приложении больше 5-6 виджетов — оформляй как класс наследующий `CTk`. Это делает код управляемым и позволяет хранить переменные в `self`.

📝 Иконка приложения
> ```python
> app.iconbitmap("icon.ico")
> ```
> Файл `.ico` можно сделать через онлайн-конвертеры из PNG.