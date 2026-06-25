# Процессы и память — psutil

> `psutil` мониторит систему в реальном времени: CPU, RAM, диск, процессы.

## Theory
Библиотека `psutil` предоставляет информацию о системных ресурсах. Она используется для мониторинга загрузки CPU, использования памяти, состояния дисков и управления процессами.

## Code
```python
import psutil

# CPU
print(psutil.cpu_percent(interval=1))  # загрузка за 1 сек
print(psutil.cpu_count())  # количество ядер

# RAM
ram = psutil.virtual_memory()
print(f"Всего: {ram.total / 1024**3:.1f} GB")
print(f"Свободно: {ram.available / 1024**3:.1f} GB")

# Диски
for part in psutil.disk_partitions():
    usage = psutil.disk_usage(part.mountpoint)
    print(f"{part.mountpoint}: {usage.percent}%")

# Процессы
for proc in psutil.process_iter(["pid", "name", "memory_info"]):
    info = proc.info
    mem_mb = info["memory_info"].rss / 1024**2
    if mem_mb > 100:
        print(f"{info['name']}: {mem_mb:.1f} MB")

# Завершение процесса
def kill_process(name):
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"].lower() == name.lower():
            proc.kill()
            return True
    return False
```

## Practice
1. Выведи загрузку CPU и использование RAM.
2. Найди топ-5 процессов по потреблению памяти.
3. Проверь свободное место на диске C:.

## Answers
```python
import psutil

# 1. CPU и RAM
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent
print(f"CPU: {cpu}%, RAM: {ram}%")

# 2. Топ процессов
procs = []
for p in psutil.process_iter(["name", "memory_info"]):
    try:
        mem = p.info["memory_info"].rss
        procs.append((p.info["name"], mem))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
top5 = sorted(procs, key=lambda x: x[1], reverse=True)[:5]
for name, mem in top5:
    print(f"{name}: {mem / 1024**2:.1f} MB")

# 3. Свободное место
disk = psutil.disk_usage("C:\\")
free_gb = disk.free / 1024**3
print(f"Свободно на C:: {free_gb:.1f} GB")
```

## Tips
- Используй `interval=1` в `cpu_percent()` для точных значений.
- Обрабатывай `psutil.NoSuchProcess` и `psutil.AccessDenied` при переборе процессов.
- Для конвертации байтов в GB дели на `1024**3`.