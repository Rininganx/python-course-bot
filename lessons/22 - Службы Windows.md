# Службы Windows

> Службы — фоновые процессы, которые запускаются вместе с системой.

## Theory
Службы Windows работают в фоновом режиме. Через Python можно управлять ими: запускать, останавливать, менять тип запуска. Используются `subprocess` с командой `sc` или библиотека `psutil`.

## Code
```python
import subprocess
import psutil

# Через subprocess (команда sc)
def run_sc(args):
    result = subprocess.run(
        ["sc"] + args,
        capture_output=True, text=True, encoding="cp866"
    )
    return result.stdout

# Статус службы
status = run_sc(["query", "wuauserv"])
print(status)

# Остановить службу (нужны права админа)
run_sc(["stop", "wuauserv"])

# Запустить службу
run_sc(["start", "wuauserv"])

# Через psutil — список служб
for svc in psutil.win_service_iter():
    info = svc.as_dict()
    if info["status"] == "running":
        print(f"{info['name']}: {info['display_name']}")

# Информация о службе
svc = psutil.win_service_get("wuauserv")
info = svc.as_dict()
print(f"Статус: {info['status']}, Запуск: {info['start_type']}")
```

## Practice
1. Получи статус службы Windows Update.
2. Выведи список запущенных служб.
3. Останови ненужную службу (только для тестов).

## Answers
```python
import psutil

# 1. Статус Windows Update
svc = psutil.win_service_get("wuauserv")
print(f"Статус: {svc.as_dict()['status']}")

# 2. Запущенные службы
for svc in psutil.win_service_iter():
    if svc.as_dict()["status"] == "running":
        print(svc.as_dict()["name"])

# 3. Остановка службы (пример)
import subprocess
result = subprocess.run(
    ["sc", "stop", "wuauserv"],
    capture_output=True, text=True, encoding="cp866"
)
print("Успех" if result.returncode == 0 else "Ошибка")
```

## Tips
- Управление службами требует прав администратора.
- Не отключай незнакомые службы — это может сломать систему.
- Используй `sc qc имя_службы` для получения подробной информации.