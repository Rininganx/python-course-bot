# PyInstaller — сборка в exe

> Упаковка Python скрипта в standalone .exe файл

## Theory

PyInstaller собирает Python + зависимости в один `.exe`. Пользователю не нужен Python. `--onefile` — всё в один файл (медленный старт). `--onedir` — папка с файлами (быстрый старт). `--windowed` — без консоли для GUI.

## Code

```bash
pip install pyinstaller

# Базовая сборка
pyinstaller --onefile main.py

# С иконкой и без консоли
pyinstaller --onefile --windowed --icon=icon.ico main.py

# Пересборка из .spec
pyinstaller main.spec
```

```python
# Доступ к ресурсам в .exe
import sys, os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Проверка прав администратора
import ctypes
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: return False

# build.py — скрипт сборки
import subprocess, shutil
def clean():
    for folder in ["build", "dist"]:
        if os.path.exists(folder): shutil.rmtree(folder)

def build():
    cmd = ["pyinstaller", "--onefile", "--windowed",
           "--name=PCBooster", "--icon=icon.ico",
           "--add-data=assets;assets", "main.py"]
    subprocess.run(cmd)
```

## Practice

1. Напиши `resource_path()` для корректного поиска файлов в .exe и в разработке
2. Напиши `build.py` с командой PyInstaller

## Answers

```python
# main.py — добавить в начало
import sys, os, ctypes

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: return False

# build.py
import subprocess, os

cmd = ["pyinstaller", "--onefile", "--windowed",
       "--icon=icon.ico", "--name=PCBooster",
       "--add-data", "assets;assets", "main.py"]

result = subprocess.run(cmd)
if result.returncode == 0:
    exe = os.path.join("dist", "PCBooster.exe")
    size = os.path.getsize(exe) / 1024 / 1024
    print(f"Готово: {exe} ({size:.1f} MB)")
```

## Tips

- `--add-data "src;dst"` — разделитель `;` на Windows, `:` на Linux
- Антивирусы могут блокировать .exe — это ложные срабатывания
- Nuitka компилирует Python в C — .exe меньше и запускается быстрее
