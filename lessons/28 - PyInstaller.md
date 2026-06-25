# PyInstaller — сборка в exe

> Предыдущая тема: 27 - Многопоточность
> Следующая тема: 29 - Установщик NSIS

## Главная идея

PyInstaller упаковывает Python скрипт + все зависимости в один `.exe` файл. Пользователю не нужно устанавливать Python — он просто запускает файл.

────────────────────
## Установка

```bash
pip install pyinstaller
```

────────────────────
## Базовая сборка

```bash
# Один файл (всё в один .exe)
pyinstaller --onefile main.py

# С иконкой
pyinstaller --onefile --icon=icon.ico main.py

# Без окна консоли (для GUI приложений)
pyinstaller --onefile --windowed --icon=icon.ico main.py

# Сборка в папку (быстрее запускается, несколько файлов)
pyinstaller --onedir --windowed --icon=icon.ico main.py
```

После сборки:
- `dist/` — готовый `.exe`
- `build/` — временные файлы (можно удалить)
- `main.spec` — файл конфигурации сборки

────────────────────
## .spec файл — тонкая настройка

```python
# main.spec — генерируется автоматически, можно редактировать

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings.json', '.'),       # включить файл настроек
        ('assets/', 'assets/'),       # включить папку с иконками
        ('profiles/', 'profiles/'),   # включить профили
    ],
    hiddenimports=[
        'psutil',
        'customtkinter',
        'winreg',
    ],
    ...
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='PCBooster',
    icon='icon.ico',
    console=False,        # без консоли
    uac_admin=True,       # запрашивать права администратора
)
```

────────────────────
## Пересборка из .spec файла

```bash
pyinstaller main.spec
```

────────────────────
## Доступ к файлам внутри .exe

Когда приложение упаковано в `.exe`, пути к файлам меняются. Используй эту функцию:

```python
import sys
import os

def resource_path(relative_path: str) -> str:
    """Возвращает путь к ресурсу — работает и в .py и в .exe."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller распаковывает файлы в _MEIPASS при запуске
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

# Использование
icon_path    = resource_path("assets/icon.ico")
config_path  = resource_path("settings.json")
```

────────────────────
## Запрос прав администратора

```python
import ctypes
import sys

def is_admin() -> bool:
    """Проверяет запущено ли приложение от администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def require_admin():
    """Перезапускает приложение с правами администратора если нужно."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas",
            sys.executable,
            " ".join(sys.argv),
            None, 1
        )
        sys.exit()

# В начале main.py
if __name__ == "__main__":
    require_admin()
    # ... запуск приложения
```

────────────────────
## Практика — build скрипт

```python
# build.py — скрипт сборки запускается вручную
import subprocess
import shutil
import os

APP_NAME    = "PCBooster"
MAIN_SCRIPT = "main.py"
ICON_FILE   = "assets/icon.ico"
VERSION     = "1.0.0"

def clean():
    """Удалить старую сборку."""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    print("Очищено")

def build():
    """Собрать .exe."""
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        "--add-data=assets;assets",
        "--add-data=profiles;profiles",
        "--hidden-import=psutil",
        "--hidden-import=customtkinter",
        "--uac-admin",
        MAIN_SCRIPT,
    ]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        exe = os.path.join("dist", f"{APP_NAME}.exe")
        size = os.path.getsize(exe) / 1024 / 1024
        print(f"\nГотово: {exe} ({size:.1f} MB)")
    else:
        print("Ошибка сборки")

if __name__ == "__main__":
    clean()
    build()
```

────────────────────
## Задание

PC Booster готовится к сборке в `.exe`. Напиши скрипт `build.py` который собирает проект.

**Дано:**
```
PCBooster/
├── main.py
├── icon.ico
├── assets/
├── profiles/
│   ├── game.json
│   └── work.json
└── build.py
```

**Нужно:**
1. Написать `resource_path()` для корректного поиска файлов в `.exe` и в разработке
2. Написать `is_admin()` для проверки прав администратора
3. Написать `build.py` с командой PyInstaller
4. Добавить все ресурсы в `.spec`

**Ожидаемый вывод `build.py`:**
```
=== Сборка PC Booster ===
Команда: pyinstaller --onefile --windowed --icon=icon.ico --add-data "assets;assets" --add-data "profiles;profiles" main.py
Сборка завершена! Файл: dist/main.exe
```

💡 Подсказка 1
> `resource_path("assets/icon.ico")` — в dev возвращает путь напрямую, в `.exe` — из временной папки: `os.path.join(sys._MEIPASS, relative_path)`.

💡 Подсказка 2
> `is_admin()` — через `ctypes.windll.shell32.IsUserAnAdmin() != 0`.

💡 Подсказка 3
> `subprocess.run(["pyinstaller", ...])` — запускает сборку из Python.

## Решение

```python
# === main.py (добавить в начало) ===
import os
import sys
import ctypes

def resource_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к ресурсу (работает и в dev, и в .exe)."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: файлы во временной папке
        return os.path.join(sys._MEIPASS, relative_path)
    # Разработка: файлы в папке проекта
    return os.path.join(os.path.abspath("."), relative_path)

def is_admin() -> bool:
    """Проверяет запущен ли скрипт с правами администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

# Использование:
icon_path = resource_path("assets/icon.ico")
profiles_path = resource_path("profiles/game.json")

print(f"Иконка: {icon_path}")
print(f"Профиль: {profiles_path}")
print(f"Админ: {is_admin()}")
```

```python
# === build.py ===
import subprocess
import os

print("=== Сборка PC Booster ===")

cmd = [
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--icon=icon.ico",
    "--name=PCBooster",
    "--add-data", "assets;assets",
    "--add-data", "profiles;profiles",
    "main.py",
]

print(f"Команда: {' '.join(cmd)}")

result = subprocess.run(cmd)

if result.returncode == 0:
    exe_path = os.path.join("dist", "PCBooster.exe")
    size_mb = os.path.getsize(exe_path) / 1024 / 1024
    print(f"Сборка завершена! Файл: {exe_path} ({size_mb:.1f} MB)")
else:
    print("Ошибка сборки!")
```

**Разбор:**
1. `sys._MEIPASS` — существует только внутри PyInstaller-`.exe`, содержит путь к временной папке с распакованными файлами
2. `resource_path()` — если в `.exe` → берёт из `_MEIPASS`, если в dev → из текущей папки
3. `ctypes.windll.shell32.IsUserAnAdmin()` — Windows API для проверки прав админа
4. `--add-data "src;dst"` — добавляет папки в `.exe`. На Windows разделитель `;`, на Linux `:`
5. `--windowed` — без окна консоли (для GUI-приложений)

────────────────────
## Заметки на полях

⚠️ Антивирусы могут блокировать .exe
> PyInstaller-приложения часто ложно срабатывают как вирусы — это нормально.
> Решение: подпись кода (Code Signing Certificate) или публикация на GitHub для проверки.

💡 --onefile медленнее запускается
> `--onefile` распаковывает себя во временную папку при каждом запуске → медленный старт.
> `--onedir` запускается быстрее, но это папка с файлами — неудобно распространять без установщика.

📝 Nuitka — быстрее чем PyInstaller
> ```bash
> pip install nuitka
> nuitka --onefile --windows-disable-console main.py
> ```
> Компилирует Python в C — `.exe` меньше и запускается быстрее. Но сборка долгая.