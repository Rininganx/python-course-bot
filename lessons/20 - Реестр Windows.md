# Реестр Windows

> Предыдущая тема: 19 - subprocess
> Следующая тема: 21 - Процессы и память — psutil

## Главная идея

Реестр Windows — это огромная база данных настроек системы и программ. Через `winreg` Python может читать и изменять реестр: управлять автозагрузкой, применять твики производительности, менять системные параметры.

────────────────────
## Структура реестра

```
HKEY_LOCAL_MACHINE  (HKLM) — настройки системы (для всех пользователей)
HKEY_CURRENT_USER   (HKCU) — настройки текущего пользователя
HKEY_CLASSES_ROOT   (HKCR) — ассоциации файлов
HKEY_USERS          (HKU)  — настройки всех пользователей
HKEY_CURRENT_CONFIG (HKCC) — текущая аппаратная конфигурация
```

────────────────────
## Чтение реестра

```python
import winreg

def read_reg_value(hive, key_path: str, value_name: str):
    """Читает значение из реестра."""
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
        value, reg_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None
    except PermissionError:
        return "Нет доступа"

# Прочитать версию Windows
ver = read_reg_value(
    winreg.HKEY_LOCAL_MACHINE,
    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
    "ProductName"
)
print(f"Windows: {ver}")

# Прочитать имя компьютера
name = read_reg_value(
    winreg.HKEY_LOCAL_MACHINE,
    r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
    "ComputerName"
)
print(f"Компьютер: {name}")
```

────────────────────
## Запись в реестр

```python
import winreg

def write_reg_value(hive, key_path: str, value_name: str, value, reg_type=winreg.REG_DWORD):
    """Записывает значение в реестр."""
    try:
        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, value_name, 0, reg_type, value)
        winreg.CloseKey(key)
        return True
    except PermissionError:
        print("Нет прав. Запусти от администратора.")
        return False
    except FileNotFoundError:
        print("Ключ не найден")
        return False
```

────────────────────
## Типы значений реестра

Тип • Константа • Хранит
DWORD • `REG_DWORD` • 32-битное число (0 или 1 для вкл/выкл)
String • `REG_SZ` • Текстовая строка
Expand String • `REG_EXPAND_SZ` • Строка с переменными среды
Binary • `REG_BINARY` • Бинарные данные

────────────────────
## Автозагрузка

```python
import winreg

STARTUP_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

def get_startup_programs() -> dict:
    """Получает список программ в автозагрузке."""
    programs = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY)
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                programs[name] = value
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    return programs

def remove_from_startup(app_name: str) -> bool:
    """Убирает программу из автозагрузки."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            STARTUP_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
```

────────────────────
## Практика — PC Booster твики

```python
import winreg

class RegistryTweaks:
    """Коллекция твиков реестра для оптимизации."""

    @staticmethod
    def disable_visual_effects():
        """Отключает анимации для ускорения UI."""
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path, 0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    @staticmethod
    def get_windows_version() -> str:
        """Возвращает версию Windows."""
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )
        name, _ = winreg.QueryValueEx(key, "ProductName")
        build, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
        winreg.CloseKey(key)
        return f"{name} (Build {build})"

    @staticmethod
    def show_startup_count() -> int:
        """Считает программы в автозагрузке."""
        return len(get_startup_programs())

# Использование
tweaks = RegistryTweaks()
print(f"Система: {tweaks.get_windows_version()}")
print(f"В автозагрузке: {tweaks.show_startup_count()} программ")
```

────────────────────
## Задание

PC Booster проверяет автозагрузку Windows. Напиши функцию `startup_audit()`.

**Дано:**
- Ключ реестра: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`

**Нужно:**
1. Прочитать все записи автозагрузки из реестра
2. Проверить существует ли файл через `os.path.exists()`
3. Пометить несуществующие как `[БИТАЯ ССЫЛКА]`
4. Вывести отчёт

**Ожидаемый вывод:**
```
=== Автозагрузка ===
[OK]           Discord — C:\Users\User\AppData\Local\Discord\Update.exe
[OK]           Spotify — C:\Users\User\AppData\Roaming\Spotify\Spotify.exe
[БИТАЯ ССЫЛКА] OldApp  — C:\Program Files\OldApp\app.exe
Итого: 3 записи, 1 битых
```

💡 Подсказка 1
> Используй `winreg.EnumValue(key, i)` в цикле `for i in range(count)` для перебора записей.

💡 Подсказка 2
> `os.path.exists(path)` проверяет существование файла. Оберни в `try/except` — путь может быть с переменными среды.

💡 Подсказка 3
> Для вывода используй тернарный оператор: `"[OK]" if exists else "[БИТАЯ ССЫЛКА]"`

## Решение

```python
import winreg
import os

def startup_audit():
    """Проверяет автозагрузку и ищет битые ссылки."""
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
    except FileNotFoundError:
        print("Ключ автозагрузки не найден")
        return

    count = winreg.QueryInfoKey(key)[1]  # количество значений
    broken = 0

    print("=== Автозагрузка ===")

    for i in range(count):
        name, path, _ = winreg.EnumValue(key)
        exists = os.path.exists(path)
        status = "[OK]" if exists else "[БИТАЯ ССЫЛКА]"
        if not exists:
            broken += 1
        print(f"{status:<16} {name} — {path}")

    winreg.CloseKey(key)
    print(f"Итого: {count} записей, {broken} битых")

startup_audit()
```

**Разбор:**
1. `winreg.OpenKey(hive, path, 0, KEY_READ)` → открывает ключ реестра для чтения
2. `winreg.QueryInfoKey(key)[1]` → возвращает количество значений в ключе
3. `winreg.EnumValue(key)` → возвращает `(имя, данные, тип)` — на каждой итерации следующая запись
4. `os.path.exists(path)` → проверяет существует ли файл по указанному пути
5. `winreg.CloseKey(key)` → закрывает ключ (обязательно!)

────────────────────
## Заметки на полях

⚠️ Администраторские права
> Запись в `HKEY_LOCAL_MACHINE` требует прав администратора.
> `HKEY_CURRENT_USER` — доступен без прав администратора.
> В готовом приложении добавь проверку: `ctypes.windll.shell32.IsUserAnAdmin()`.

🐛 Всегда делай резервную копию перед изменением реестра
> Реестр — критически важная часть системы. В приложении перед изменением читай текущее значение и сохраняй его в файл — чтобы можно было откатить.

💡 regedit для исследования
> Открой `regedit` (Win+R → regedit) и исследуй реестр вручную перед тем как писать код. Найди нужный ключ, запомни путь, потом пиши Python код.