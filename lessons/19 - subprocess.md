# subprocess

> Предыдущая тема: 18 - Модуль os
> Следующая тема: 20 - Реестр Windows

## Главная идея

`subprocess` запускает внешние программы и команды прямо из Python. Хочешь выполнить команду CMD или PowerShell, запустить `.exe`, получить вывод команды — всё через `subprocess`.

────────────────────
## subprocess.run() — основной способ

```python
import subprocess

# Запустить команду и подождать завершения
result = subprocess.run(
    ["ipconfig"],
    capture_output=True,    # захватить stdout и stderr
    text=True,              # вернуть как строку, не байты
    encoding="cp866",       # кодировка CMD в Windows
)

print(result.stdout)        # вывод команды
print(result.returncode)    # 0 = успех, другое = ошибка
```

────────────────────
## Параметры subprocess.run()

Параметр • Что делает
`capture_output=True` • Захватить stdout и stderr
`text=True` • Вернуть строки, не байты
`encoding="cp866"` • Кодировка для CMD (Windows)
`shell=True` • Запустить через оболочку
`timeout=10` • Таймаут в секундах
`check=True` • Выбросить исключение при ошибке

────────────────────
## Запуск CMD команд

```python
import subprocess

def run_cmd(command: list) -> str:
    """Запускает команду CMD и возвращает вывод."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="cp866",
            timeout=30,
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return "Ошибка: превышено время ожидания"
    except FileNotFoundError:
        return "Ошибка: команда не найдена"

# Примеры
print(run_cmd(["ipconfig"]))
print(run_cmd(["tasklist"]))
print(run_cmd(["systeminfo"]))
print(run_cmd(["ping", "google.com", "-n", "2"]))
```

────────────────────
## PowerShell из Python

```python
def run_powershell(script: str) -> str:
    """Запускает PowerShell скрипт и возвращает вывод."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()

# Получить объём RAM
ram_info = run_powershell(
    "Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum | Select-Object -ExpandProperty Sum"
)
ram_gb = int(ram_info) // (1024**3)
print(f"RAM: {ram_gb} GB")

# Список процессов через PowerShell
procs = run_powershell(
    "Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 5 Name, WorkingSet | Format-Table -AutoSize"
)
print(procs)
```

────────────────────
## Практика — PC Booster

```python
import subprocess

def get_ip_info() -> dict:
    """Получает сетевую информацию."""
    output = subprocess.run(
        ["ipconfig"],
        capture_output=True, text=True, encoding="cp866"
    ).stdout

    result = {}
    for line in output.splitlines():
        if "IPv4" in line:
            result["ipv4"] = line.split(":")[-1].strip()
        if "Default Gateway" in line or "Основной шлюз" in line:
            val = line.split(":")[-1].strip()
            if val:
                result["gateway"] = val
    return result

def get_top_processes(n=5) -> list:
    """Топ N процессов по памяти через tasklist."""
    output = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, encoding="cp866"
    ).stdout

    procs = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.strip('"').split('","')
        if len(parts) >= 5:
            name = parts[0]
            try:
                mem_kb = int(parts[4].replace("\xa0", "").replace(",", "").replace("K", "").strip())
                procs.append((name, mem_kb))
            except ValueError:
                continue

    procs.sort(key=lambda x: x[1], reverse=True)
    return procs[:n]

def flush_dns():
    """Сбрасывает DNS кэш."""
    result = subprocess.run(
        ["ipconfig", "/flushdns"],
        capture_output=True, text=True, encoding="cp866"
    )
    return result.returncode == 0

print("=== Сетевая информация ===")
ip = get_ip_info()
for k, v in ip.items():
    print(f"  {k}: {v}")

print("\n=== Топ процессов по RAM ===")
for name, mem_kb in get_top_processes():
    print(f"  {name:<30} {mem_kb // 1024:>6} MB")
```

────────────────────
## Задание

PC Booster собирает информацию о системе через команды Windows. Напиши функцию `system_scan()`.

**Дано:**
- Команды для сбора информации: `hostname`, PowerShell-запросы, `ipconfig`

**Нужно:**
1. Получить имя компьютера через `hostname`
2. Получить версию Windows через PowerShell
3. Получить название CPU через PowerShell
4. Получить IP из вывода `ipconfig`
5. Вывести отчёт

**Ожидаемый вывод:**
```
=== Системный отчёт ===
Hostname:  MYPC-WIN11
OS:        Microsoft Windows 11 Pro
CPU:       Intel(R) Core(TM) i7-12700K
RAM:       16 GB
IP:        192.168.1.5
```

💡 Подсказка 1
> Каждую команду запускай отдельной функцией-обёрткой. `hostname` возвращает имя одной строкой.

💡 Подсказка 2
> Для PowerShell: `subprocess.run(["powershell", "-NoProfile", "-Command", script], ...)`

💡 Подсказка 3
> IP найди через перебор строк вывода `ipconfig` и поиск `"IPv4"`.

## Решение

```python
import subprocess

def run_cmd(args: list) -> str:
    """Запускает команду и возвращает stdout."""
    result = subprocess.run(
        args,
        capture_output=True, text=True, encoding="cp866"
    )
    return result.stdout.strip()

def run_ps(script: str) -> str:
    """Запускает PowerShell-команду и возвращает результат."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip()

def system_scan():
    """Собирает и выводит информацию о системе."""
    hostname = run_cmd(["hostname"])
    os_name = run_ps("(Get-CimInstance Win32_OperatingSystem).Caption")
    cpu_name = run_ps("(Get-CimInstance Win32_Processor).Name")
    ram_raw = run_ps(
        "Get-CimInstance Win32_PhysicalMemory | "
        "Measure-Object -Property Capacity -Sum | "
        "Select-Object -ExpandProperty Sum"
    )
    ram_gb = int(ram_raw) // (1024**3) if ram_raw.isdigit() else "?"

    ip = "?"
    ipconfig = run_cmd(["ipconfig"])
    for line in ipconfig.splitlines():
        if "IPv4" in line:
            ip = line.split(":")[-1].strip()
            break

    print("=== Системный отчёт ===")
    print(f"Hostname:  {hostname}")
    print(f"OS:        {os_name}")
    print(f"CPU:       {cpu_name}")
    print(f"RAM:       {ram_gb} GB")
    print(f"IP:        {ip}")

system_scan()
```

**Разбор:**
1. `run_cmd` — универсальная обёртка для CMD-команд: запускает, захватывает вывод
2. `run_ps` — обёртка для PowerShell: те же параметры, но другая кодировка (`utf-8`)
3. `hostname` — возвращает имя одной строкой, `.strip()` убирает лишние пробелы
4. `ip.split(":")[-1].strip()` → разбиваем строку по `:`, берём последнюю часть
5. `int(ram_raw) // (1024**3)` → байты → гигабайты (целочисленное деление)

────────────────────
## Заметки на полях

⚠️ shell=True — осторожно
> ```python
> subprocess.run("del C:\\*", shell=True)  # опасно если команда из ввода пользователя
> ```
> `shell=True` уязвим для инъекций если команда формируется из пользовательского ввода. Используй список аргументов `["del", "C:\\"]` когда возможно.

💡 Скрыть окно консоли (для GUI приложений)
> ```python
> startupinfo = subprocess.STARTUPINFO()
> startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
> subprocess.run(cmd, startupinfo=startupinfo)
> ```
> Без этого при запуске команды из GUI приложения будет мигать чёрное окно.