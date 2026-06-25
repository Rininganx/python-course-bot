# Процессы и память — psutil

> Предыдущая тема: 20 - Реестр Windows
> Следующая тема: 22 - Службы Windows

## Главная идея

`psutil` — библиотека для мониторинга системы в реальном времени: CPU, RAM, диск, сеть, процессы. Это сердце любого PC Booster приложения.

────────────────────
## Установка

```bash
pip install psutil
```

────────────────────
## CPU

```python
import psutil

# Загрузка CPU
print(psutil.cpu_percent(interval=1))          # % за 1 секунду
print(psutil.cpu_percent(percpu=True))          # % каждого ядра
print(psutil.cpu_count())                       # количество ядер (логических)
print(psutil.cpu_count(logical=False))          # физических ядер
print(psutil.cpu_freq().current)                # частота МГц

# Статистика CPU
times = psutil.cpu_times_percent()
print(f"User: {times.user}%")
print(f"System: {times.system}%")
print(f"Idle: {times.idle}%")
```

────────────────────
## Память (RAM)

```python
import psutil

ram = psutil.virtual_memory()

print(f"Всего:    {ram.total    / 1024**3:.1f} GB")
print(f"Занято:   {ram.used     / 1024**3:.1f} GB")
print(f"Свободно: {ram.available/ 1024**3:.1f} GB")
print(f"Процент:  {ram.percent}%")

# Swap (файл подкачки)
swap = psutil.swap_memory()
print(f"Swap: {swap.used / 1024**3:.1f} / {swap.total / 1024**3:.1f} GB ({swap.percent}%)")
```

────────────────────
## Диски

```python
import psutil

# Все разделы
for part in psutil.disk_partitions():
    try:
        usage = psutil.disk_usage(part.mountpoint)
        print(f"{part.mountpoint}  "
              f"{usage.total/1024**3:.0f} GB  "
              f"занято {usage.percent}%")
    except PermissionError:
        continue

# Скорость дисков
disk_io = psutil.disk_io_counters()
print(f"Прочитано: {disk_io.read_bytes  / 1024**2:.1f} MB")
print(f"Записано:  {disk_io.write_bytes / 1024**2:.1f} MB")
```

────────────────────
## Сеть

```python
import psutil

# Статистика сети
net = psutil.net_io_counters()
print(f"Отправлено:  {net.bytes_sent / 1024**2:.1f} MB")
print(f"Получено:    {net.bytes_recv / 1024**2:.1f} MB")

# Сетевые интерфейсы
for iface, addrs in psutil.net_if_addrs().items():
    for addr in addrs:
        if addr.family == 2:   # IPv4
            print(f"{iface}: {addr.address}")
```

────────────────────
## Процессы

```python
import psutil

# Все процессы
for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
    try:
        info = proc.info
        mem_mb = info["memory_info"].rss / 1024**2
        if mem_mb > 100:
            print(f"PID {info['pid']:>6}  {info['name']:<25} {mem_mb:>8.1f} MB")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

# Завершить процесс
def kill_process(name: str) -> bool:
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"].lower() == name.lower():
                proc.kill()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False
```

────────────────────
## Температуры (если поддерживается)

```python
import psutil

if hasattr(psutil, "sensors_temperatures"):
    temps = psutil.sensors_temperatures()
    if temps:
        for chip, readings in temps.items():
            for r in readings:
                print(f"{chip} — {r.label}: {r.current}°C")
    else:
        print("Датчики не найдены")
else:
    # На Windows часто нет прямого доступа через psutil
    # Используй Open Hardware Monitor или WMI
    print("Температуры доступны через WMI или OpenHardwareMonitor")
```

────────────────────
## Практика — PC Booster

```python
import psutil
import os

def full_system_snapshot() -> dict:
    """Полный снимок состояния системы."""
    ram  = psutil.virtual_memory()
    cpu  = psutil.cpu_percent(interval=0.5)
    disk = psutil.disk_usage("C:\\")

    # Топ процессов по RAM
    procs = []
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            mem = p.info["memory_info"].rss
            procs.append((p.info["name"], mem))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    top5 = sorted(procs, key=lambda x: x[1], reverse=True)[:5]

    return {
        "cpu_pct":    cpu,
        "ram_pct":    ram.percent,
        "ram_free_gb": round(ram.available / 1024**3, 1),
        "disk_pct":   disk.percent,
        "disk_free_gb": round(disk.free / 1024**3, 1),
        "top_procs":  [(n, round(m/1024**2, 1)) for n, m in top5],
    }

def print_snapshot(snap: dict):
    print("╔══════════════════════════════════╗")
    print("║       PC Booster — Монитор       ║")
    print("╠══════════════════════════════════╣")
    print(f"║  CPU:   {snap['cpu_pct']:>5.1f}%                    ║")
    print(f"║  RAM:   {snap['ram_pct']:>5.1f}%  ({snap['ram_free_gb']} GB свободно)  ║")
    print(f"║  Диск:  {snap['disk_pct']:>5.1f}%  ({snap['disk_free_gb']} GB свободно)  ║")
    print("╠══════════════════════════════════╣")
    print("║  Топ процессов по RAM:           ║")
    for name, mb in snap["top_procs"]:
        print(f"║    {name:<20} {mb:>6.1f} MB    ║")
    print("╚══════════════════════════════════╝")

snap = full_system_snapshot()
print_snapshot(snap)
```

────────────────────
## Задание

PC Booster выводит мониторинг системы в реальном времени. Напиши цикл который обновляется каждые 2 секунды.

**Дано:**
- Библиотека `psutil` уже установлена
- Нужно выводить CPU, RAM и диск C:

**Нужно:**
1. Выводить строку с меткой времени, CPU%, RAM%, диск%
2. Обновлять каждые 2 секунды
3. Остановиться по `Ctrl+C` и показать сколько показаний снято

**Ожидаемый вывод:**
```
[12:00:01] CPU:  12.3% | RAM:  67.4% | Диск C: 54.2%
[12:00:03] CPU:  18.7% | RAM:  68.1% | Диск C: 54.2%
[12:00:05] CPU:   9.2% | RAM:  67.9% | Диск C: 54.2%
^C
Мониторинг остановлен. Снято показаний: 3
```

💡 Подсказка 1
> Используй `psutil.cpu_percent(interval=1)` для точного значения CPU.

💡 Подсказка 2
> Метку времени: `datetime.now().strftime("%H:%M:%S")` — часы:минуты:секунды.

💡 Подсказка 3
> `Ctrl+C` перехватывается через `except KeyboardInterrupt` в цикле `while True`.

## Решение

```python
import psutil
import time
from datetime import datetime

def monitor():
    """Мониторинг системы в реальном времени."""
    count = 0

    try:
        while True:
            ts = datetime.now().strftime("%H:%M:%S")
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\").percent

            print(f"[{ts}] CPU: {cpu:>5.1f}% | RAM: {ram:>5.1f}% | Диск C: {disk:.1f}%")
            count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\nМониторинг остановлен. Снято показаний: {count}")

monitor()
```

**Разбор:**
1. `psutil.cpu_percent(interval=1)` → ждёт 1 секунду и возвращает точный % CPU
2. `psutil.virtual_memory().percent` → процент занятой RAM
3. `psutil.disk_usage("C:\\").percent` → процент занятого места на диске C:
4. `while True` → бесконечный цикл мониторинга
5. `except KeyboardInterrupt` → ловит `Ctrl+C` и выводит итоги

────────────────────
## Заметки на полях

⚠️ `cpu_percent(interval=None)` — неточно
> Первый вызов без интервала вернёт 0.0 — psutil не знает предыдущего значения.
> Всегда используй `interval=0.5` или `interval=1` для точных данных.

📝 Байты → читаемый формат
> ```python
> def fmt_bytes(b):
>     for unit in ["B", "KB", "MB", "GB", "TB"]:
>         if b < 1024:
>             return f"{b:.1f} {unit}"
>         b /= 1024
> ```