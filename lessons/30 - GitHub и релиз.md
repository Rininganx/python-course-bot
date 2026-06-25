# GitHub и релиз

> Хранилище кода и публикация .exe через GitHub Releases

## Theory

GitHub — хранилище кода, система версий, платформа для дистрибуции. Через Releases можно бесплатно публиковать .exe и установщики. Семантическое версионирование: MAJOR.MINOR.PATCH.

## Code

```bash
# Инициализация
git init
git remote add origin https://github.com/user/repo.git
git add .
git commit -m "Initial commit"
git push -u origin main

# Рабочий цикл
git add .
git commit -m "Описание изменений"
git push

# Просмотр
git status
git log --oneline

# Релиз
gh release create v1.0.0 PCBooster.exe PCBooster_Setup.exe --title "v1.0.0" --notes "Первый релиз"

# Зависимости
pip freeze > requirements.txt
```

```gitignore
# .gitignore
__pycache__/
*.pyc
build/
dist/
*.spec
.vscode/
.idea/
*.env
secrets.json
```

```markdown
# README.md
# PC Booster

Приложение для оптимизации Windows.

## Установка
1. Скачай [релиз](https://github.com/user/repo/releases)
2. Запусти PCBooster_Setup.exe

## Разработка
git clone https://github.com/user/repo.git
pip install -r requirements.txt
python main.py
```

## Practice

1. Инициализируй git-репозиторий с .gitignore и requirements.txt
2. Создай релиз на GitHub через `gh release create`

## Answers

```bash
# 1. Инициализация
git init
pip freeze > requirements.txt
git add .
git commit -m "Initial project structure"
git push -u origin main

# 2. Релиз
gh release create v1.0.0 \
    dist/PCBooster.exe \
    release/PCBooster_Setup_1.0.0.exe \
    --title "PC Booster v1.0.0" \
    --notes "Первый релиз"
```

## Tips

- Коммить часто с понятными сообщениями: `"Fix crash when RAM > 99%"` а не `"update"`
- Версионирование: PATCH (баги), MINOR (фичи), MAJOR (ломающие изменения)
- GitHub Pages — бесплатный лендинг для приложения
