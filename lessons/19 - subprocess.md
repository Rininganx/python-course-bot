# subprocess

> `subprocess` запускает внешние программы и команды из Python.

## Theory
Модуль `subprocess` позволяет выполнять системные команды (CMD, PowerShell) и получать их вывод. Основная функция — `subprocess.run()`. Важно использовать `capture_output=True` для захвата вывода и `text=True` для получения строк.

## Code
```python
import subprocess

# Запуск команды CMD
result = subprocess.run(
    ["ipconfig"],
    capture_output=True,
    text=True,
    encoding="cp866"
)
print(result.stdout)

# PowerShell скрипт
def run_powershell(script):
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout.strip()

# Пример: получить имя компьютера
hostname = subprocess.run(
    ["hostname"],
    capture_output=True,
    text=True,
    encoding="cp866"
).stdout.strip()
print(f"Имя ПК: {hostname}")

# Проверка результата
if result.returncode == 0:
    print("Команда выполнена успешно")
else:
    print("Ошибка:", result.stderr)
```

## Practice
1. Получи информацию о сети через `ipconfig`.
2. Запусти PowerShell-команду для получения версии Windows.
3. Обработай ошибку, если команда не найдена.

## Answers
```python
import subprocess

# 1. Сетевая информация
result = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding="cp866")
print(result.stdout)

# 2. Версия Windows
ps_cmd = "(Get-CimInstance Win32_OperatingSystem).Caption"
version = subprocess.run(
    ["powershell", "-NoProfile", "-Command", ps_cmd],
    capture_output=True, text=True, encoding="utf-8"
).stdout.strip()
print(f"ОС: {version}")

# 3. Обработка ошибок
try:
    result = subprocess.run(["некоманда"], capture_output=True, text=True)
except FileNotFoundError:
    print("Команда не найдена")
```

## Tips
- Используй `encoding="cp866"` для CMD-команд и `encoding="utf-8"` для PowerShell.
- Избегай `shell=True` для безопасности — передавай аргументы списком.
- Для скрытия окна консоли используй `startupinfo` с флагом `STARTF_USESHOWWINDOW`.