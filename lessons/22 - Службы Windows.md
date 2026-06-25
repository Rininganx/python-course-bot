# Службы Windows

> Предыдущая тема: 21 - Процессы и память — psutil
> Следующая тема: 23 - Планировщик задач

## Главная идея

Службы Windows — это фоновые процессы которые запускаются вместе с системой. Многие из них не нужны большинству пользователей и просто жрут ресурсы. Через Python можно управлять службами: смотреть, запускать, останавливать, менять тип запуска.

────────────────────
## Через subprocess (без дополнительных библиотек)

```python
import subprocess

def run_sc(args: list) -> str:
    """Выполняет команду sc.exe."""
    result = subprocess.run(
        ["sc"] + args,
        capture_output=True, text=True, encoding="cp866"
    )
    return result.stdout

# Статус службы
print(run_sc(["query", "wuauserv"]))   # Windows Update

# Остановить службу (требует прав администратора)
print(run_sc(["stop", "wuauserv"]))

# Запустить службу
print(run_sc(["start", "wuauserv"]))

# Изменить тип запуска
# auto | demand | disabled
print(run_sc(["config", "wuauserv", "start=", "demand"]))
```

────────────────────
## Через psutil — список служб

```python
import psutil

# Все службы
for svc in psutil.win_service_iter():
    try:
        info = svc.as_dict()
        if info["status"] == "running":
            print(f"{info['name']:<40} {info['display_name']}")
    except Exception:
        continue

# Конкретная служба
svc = psutil.win_service_get("wuauserv")
info = svc.as_dict()
print(f"Имя:    {info['name']}")
print(f"Статус: {info['status']}")
print(f"Запуск: {info['start_type']}")
```

────────────────────
## Через pywin32 (расширенное управление)

```bash
pip install pywin32
```

```python
import win32serviceutil
import win32service

# Статус службы
status = win32serviceutil.QueryServiceStatus("wuauserv")
# status[1] == 4 означает SERVICE_RUNNING

# Остановить
win32serviceutil.StopService("wuauserv")

# Запустить
win32serviceutil.StartService("wuauserv")

# Изменить тип запуска
win32serviceutil.ChangeServiceConfig(
    "wuauserv",
    startType=win32service.SERVICE_DEMAND_START   # по требованию
)
```

────────────────────
## Типы запуска служб

Константа • Значение • Смысл
`SERVICE_AUTO_START` • `2` • Автоматически при старте
`SERVICE_DEMAND_START` • `3` • Вручную по требованию
`SERVICE_DISABLED` • `4` • Отключена
`SERVICE_BOOT_START` • `0` • При загрузке ядра
`SERVICE_SYSTEM_START` • `1` • При инициализации системы

────────────────────
## Практика — PC Booster

```python
import subprocess
import psutil

# Службы которые можно безопасно отключить для геймеров
SAFE_TO_DISABLE = {
    "TabletInputService":   "Рукописный ввод и клавиатура",
    "WSearch":              "Индексирование файлов (Windows Search)",
    "SysMain":              "Superfetch — предзагрузка приложений",
    "DiagTrack":            "Телеметрия и сбор данных",
    "WerSvc":               "Служба отчётов об ошибках",
    "PrintSpooler":         "Диспетчер печати (если нет принтера)",
    "Fax":                  "Факс",
    "XboxGipSvc":           "Xbox Accessory Management",
}

def get_service_status(name: str) -> str:
    """Возвращает статус службы."""
    try:
        svc = psutil.win_service_get(name)
        return svc.as_dict()["status"]
    except Exception:
        return "not_found"

def audit_services() -> list:
    """Проверяет статус служб из списка."""
    results = []
    for name, description in SAFE_TO_DISABLE.items():
        status = get_service_status(name)
        results.append({
            "name":        name,
            "description": description,
            "status":      status,
            "can_disable": status == "running",
        })
    return results

def print_service_report(services: list):
    running  = [s for s in services if s["status"] == "running"]
    stopped  = [s for s in services if s["status"] == "stopped"]
    missing  = [s for s in services if s["status"] == "not_found"]

    print(f"\n{'='*55}")
    print(f"  Аудит служб — кандидаты на отключение")
    print(f"{'='*55}")

    if running:
        print(f"\n  Запущены ({len(running)}) — можно отключить:")
        for s in running:
            print(f"    ● {s['name']:<25} {s['description']}")

    if stopped:
        print(f"\n  Уже остановлены ({len(stopped)}):")
        for s in stopped:
            print(f"    ○ {s['name']}")

    print(f"\n  Потенциальная экономия: ~{len(running) * 20}-{len(running) * 50} MB RAM")

report = audit_services()
print_service_report(report)
```

────────────────────
## Задание

PC Booster переключает профили служб Windows. Напиши функции для игрового и обычного режима.

**Дано:**
```python
GAME_MODE_DISABLE  = ["WSearch", "SysMain", "DiagTrack", "WerSvc"]
NORMAL_MODE_ENABLE = ["WSearch", "SysMain"]
```

**Нужно:**
- `enable_game_mode()` — останавливает службы из `GAME_MODE_DISABLE`
- `disable_game_mode()` — запускает службы из `NORMAL_MODE_ENABLE`
- `get_mode_status()` — выводит таблицу статусов

**Ожидаемый вывод:**
```
=== Режим: Игровой ===
WSearch    → Остановлена
SysMain    → Остановлена
DiagTrack  → Остановлена
WerSvc     → Остановлена
```

⚠️ Для реального запуска нужны права администратора
> Тестируй только чтение статуса — не запускай `sc stop` на реальной системе.

💡 Подсказка 1
> Используй `psutil.win_service_get(name).as_dict()["status"]` для проверки статуса.

💡 Подсказка 2
> Для управления — `subprocess.run(["sc", "stop", name])` и `["sc", "start", name]`.

💡 Подсказка 3
> В `get_mode_status()` проверяй все службы из обоих списков через `set().union()`.

## Решение

```python
import psutil
import subprocess

GAME_MODE_DISABLE  = ["WSearch", "SysMain", "DiagTrack", "WerSvc"]
NORMAL_MODE_ENABLE = ["WSearch", "SysMain"]

def get_service_status(name: str) -> str:
    """Возвращает статус службы."""
    try:
        svc = psutil.win_service_get(name)
        return svc.as_dict()["status"]
    except Exception:
        return "не найдена"

def get_mode_status():
    """Выводит статус всех служб."""
    all_services = set(GAME_MODE_DISABLE).union(NORMAL_MODE_ENABLE)
    print("=== Статус служб ===")
    for name in sorted(all_services):
        status = get_service_status(name)
        print(f"  {name:<12} → {status}")

def enable_game_mode():
    """Останавливает службы для игрового режима."""
    print("=== Включаю игровой режим ===")
    for name in GAME_MODE_DISABLE:
        result = subprocess.run(
            ["sc", "stop", name],
            capture_output=True, text=True, encoding="cp866"
        )
        status = "Остановлена" if result.returncode == 0 else f"Ошибка"
        print(f"  {name:<12} → {status}")

def disable_game_mode():
    """Запускает службы обратно."""
    print("=== Включаю обычный режим ===")
    for name in NORMAL_MODE_ENABLE:
        result = subprocess.run(
            ["sc", "start", name],
            capture_output=True, text=True, encoding="cp866"
        )
        status = "Запущена" if result.returncode == 0 else "Ошибка"
        print(f"  {name:<12} → {status}")

# Показать текущий статус
get_mode_status()
```

**Разбор:**
1. `psutil.win_service_get(name)` → получает объект службы по имени
2. `svc.as_dict()["status"]` → возвращает словарь со всей информацией, берём статус
3. `subprocess.run(["sc", "stop", name])` → останавливает службу (нужны права админа)
4. `set().union()` → объединяет два списка в множество без дублей
5. `result.returncode == 0` → код 0 означает успех команды

────────────────────
## Заметки на полях

⚠️ Не отключай незнакомые службы
> Некоторые службы критически важны для системы. Всегда гугли название службы перед отключением.
> Безопасный список — тот что в коде выше. Не расширяй его без исследования.

💡 Как найти что делает служба
> `sc qc ИМЯ_СЛУЖБЫ` — полная информация включая путь к исполняемому файлу.
> Или открой `services.msc` (Win+R) и читай описание в интерфейсе.