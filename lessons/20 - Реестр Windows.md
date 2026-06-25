# Реестр Windows

> Реестр — база данных настроек системы и программ.

## Theory
Реестр Windows хранит настройки системы, программ и пользователей. Модуль `winreg` позволяет читать и изменять записи реестра. Основные ветки: `HKEY_LOCAL_MACHINE` (системные настройки) и `HKEY_CURRENT_USER` (настройки пользователя).

## Code
```python
import winreg

# Чтение значения из реестра
def read_reg(hive, path, name):
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None

# Пример: версия Windows
version = read_reg(
    winreg.HKEY_LOCAL_MACHINE,
    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
    "ProductName"
)
print(f"Windows: {version}")

# Запись в реестр (требует прав администратора)
def write_reg(hive, path, name, value):
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)
        return True
    except PermissionError:
        print("Нет прав администратора")
        return False

# Автозагрузка: чтение программ
def get_startup():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    programs = {}
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
    i = 0
    while True:
        try:
            name, value, _ = winreg.EnumValue(key, i)
            programs[name] = value
            i += 1
        except OSError:
            break
    winreg.CloseKey(key)
    return programs
```

## Practice
1. Прочитай имя компьютера из реестра.
2. Получи список программ в автозагрузке.
3. Проверь существование ключа реестра.

## Answers
```python
import winreg

# 1. Имя компьютера
name = read_reg(
    winreg.HKEY_LOCAL_MACHINE,
    r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
    "ComputerName"
)
print(f"Компьютер: {name}")

# 2. Автозагрузка
startup = get_startup()
for app, path in startup.items():
    print(f"{app}: {path}")

# 3. Проверка ключа
def key_exists(hive, path):
    try:
        winreg.OpenKey(hive, path)
        return True
    except FileNotFoundError:
        return False

print(key_exists(winreg.HKEY_CURRENT_USER, r"Software\MyApp"))
```

## Tips
- Запись в `HKEY_LOCAL_MACHINE` требует прав администратора.
- Всегда закрывай ключи после работы через `winreg.CloseKey()`.
- Используй `try/except` для обработки ошибок доступа и отсутствия ключей.