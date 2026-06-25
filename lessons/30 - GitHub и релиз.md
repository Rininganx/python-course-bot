# GitHub и релиз

> Предыдущая тема: 29 - Установщик NSIS

## Главная идея

GitHub — это не просто хранилище кода. Это визитная карточка разработчика, система версий, платформа для дистрибуции. Через GitHub Releases можно бесплатно публиковать `.exe` и установщик.

────────────────────
## Базовые команды Git

```bash
# Инициализация
git init
git add .
git commit -m "Initial commit"

# Подключение к GitHub
git remote add origin https://github.com/username/pc-booster.git
git push -u origin main

# Обычный рабочий цикл
git add .
git commit -m "Описание изменений"
git push

# Просмотр
git status        # что изменилось
git log --oneline # история коммитов
git diff          # детальные изменения
```

────────────────────
## .gitignore для Python проекта

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
*.egg-info/

# PyInstaller
build/
dist/
*.spec

# IDE
.vscode/
.idea/
*.swp

# Системные
.DS_Store
Thumbs.db
desktop.ini

# Конфиденциальное
*.env
secrets.json
config_local.json
```

────────────────────
## Структура README.md

```markdown
# ⚡ PC Booster

Приложение для оптимизации Windows — ускорение, очистка, мониторинг.

![screenshot](assets/screenshot.png)

## Возможности

- 📊 Мониторинг CPU, RAM, диска в реальном времени
- ⚡ Одним кликом: очистка temp, оптимизация реестра
- 🎮 Игровой режим — максимальная производительность
- 🚀 Управление автозагрузкой
- 📋 Управление службами Windows

## Установка

1. Скачай [последний релиз](https://github.com/username/pc-booster/releases)
2. Запусти `PCBooster_Setup.exe` от администратора
3. Готово

## Требования

- Windows 10 / 11 (64-bit)
- Права администратора для некоторых функций

## Разработка

```bash
git clone https://github.com/username/pc-booster.git
cd pc-booster
pip install -r requirements.txt
python main.py
```

## Лицензия

MIT
```

────────────────────
## GitHub Releases — публикация релиза

1. Открой репозиторий на GitHub
2. Нажми **Releases → Create a new release**
3. Создай тег версии: `v1.0.0`
4. Заголовок: `PC Booster v1.0.0`
5. Опиши изменения (changelog)
6. Прикрепи файлы: `PCBooster_Setup_1.0.0.exe` и `PCBooster_portable_1.0.0.exe`
7. Нажми **Publish release**

────────────────────
## requirements.txt — зависимости проекта

```bash
# Сгенерировать автоматически
pip freeze > requirements.txt

# Установить из файла
pip install -r requirements.txt
```

```txt
# requirements.txt
customtkinter==5.2.2
psutil==5.9.8
pywin32==306
pyinstaller==6.3.0
```

────────────────────
## Семантическое версионирование

```
v1.0.0
  │ │ └── PATCH — исправление багов (1.0.0 → 1.0.1)
  │ └──── MINOR — новые функции без поломки (1.0.0 → 1.1.0)
  └────── MAJOR — ломающие изменения (1.0.0 → 2.0.0)
```

────────────────────
## Практика — чеклист перед релизом

```
□ Код закоммичен и запушен
□ Версия обновлена в коде и в .iss
□ requirements.txt актуален
□ README обновлён
□ .exe протестирован на чистой машине
□ Установщик создан и протестирован
□ Скриншоты актуальны
□ GitHub Release создан с файлами
```

────────────────────
## Задание

PC Booster готов к публикации. Подготовь репозиторий и создай первый релиз на GitHub.

**Дано:**
- Готовый `PCBooster.exe` и установщик `PCBooster_Setup_1.0.0.exe`

**Нужно:**
1. Инициализировать git-репозиторий
2. Создать `.gitignore` и `requirements.txt`
3. Написать `README.md` с описанием проекта
4. Сделать коммит и запушить
5. Создать релиз на GitHub через `gh`

**Ожидаемый вывод:**
```
$ git init
$ git add .
$ git commit -m "Initial project structure"
$ git push -u origin main
$ gh release create v1.0.0 PCBooster.exe PCBooster_Setup_1.0.0.exe --title "v1.0.0" --notes "Первый релиз"
https://github.com/username/pc-booster/releases/tag/v1.0.0
```

💡 Подсказка 1
> `requirements.txt` — список зависимостей: `pip freeze > requirements.txt`

💡 Подсказка 2
> `gh release create v1.0.0 файл1 файл2 --title "v1.0.0" --notes "текст"` — создаёт релиз с файлами.

💡 Подсказка 3
> Коммить часто с понятными сообщениями: `"Add RAM calculator"` а не `"update"`.

## Решение

```bash
# 1. Инициализация
git init
git remote add origin https://github.com/username/pc-booster.git

# 2. Зависимости
pip freeze > requirements.txt

# 3. Первый коммит
git add .
git commit -m "Initial project structure"
git push -u origin main

# 4. Релиз с файлами
gh release create v1.0.0 \
    dist/PCBooster.exe \
    release/PCBooster_Setup_1.0.0.exe \
    --title "PC Booster v1.0.0" \
    --notes "Первый релиз PC Booster"
```

Структура репозитория:
```
pc-booster/
├── main.py
├── build.py
├── requirements.txt
├── .gitignore
├── README.md
├── PCBooster.iss
├── icon.ico
├── assets/
│   └── ...
└── profiles/
    ├── game.json
    └── work.json
```

**Разбор:**
1. `git init` → создаёт скрытую папку `.git` — начало отслеживания версий
2. `pip freeze > requirements.txt` → сохраняет все установленные библиотеки в файл
3. `git add .` → добавляет все файлы в staging area (подготовка к коммиту)
4. `git commit -m "..."` → сохраняет снимок файлов с описанием
5. `gh release create v1.0.0 файл1 файл2` → создаёт релиз на GitHub и загружает файлы — теперь любой может скачать `.exe`

────────────────────
## Заметки на полях

💡 Коммить часто, малыми порциями
> `"Fixed bug"` — плохо. `"Fix crash when RAM usage > 99%"` — хорошо.
> Описывай что именно изменилось — через год сам скажешь спасибо.

📝 GitHub Pages — бесплатный сайт
> Можно сделать лендинг для приложения прямо на GitHub Pages.
> Настройки репозитория → Pages → Source: main / docs.
> Бесплатный хостинг на `username.github.io/pc-booster`.