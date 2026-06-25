# Python Course Telegram Bot

Interactive Telegram bot for learning Python. 36 lessons organized in 8 modules, from basics to freelancing. Tracks progress, streaks, bookmarks — fully customizable.

## Features

- **36 structured lessons** across 8 themed modules
- **Module navigation** — browse lessons by topic (Basics, Logic, Data Structures, Functions, System, Automation, GUI, Advanced)
- **Progress tracking** — visual progress bar with per-module stats
- **Learning streak** — track consecutive days of activity
- **Bookmarks** — save lessons for quick access
- **Random lesson** — jump to a random uncompleted lesson
- **Inline keyboard navigation** — browse lessons with buttons
- **Continue learning** — pick up where you left off
- **Search** — find lessons by keyword
- **Daily reminders** — automatic lesson notification at 8:00
- **Multi-user support** — each user has their own progress
- **Section splitting** — long lessons split into readable parts

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/stats` | Detailed statistics (streak, per-module progress) |
| `/random` | Jump to a random uncompleted lesson |
| `/bookmark` | View your bookmarks |
| `/reset` | Reset all progress (with confirmation) |
| `/health` | Check bot status |

## Quick Start

```bash
# Clone
git clone https://github.com/Rininganx/python-course-bot.git
cd python-course-bot

# Install
pip install -r requirements.txt

# Set token
export TELEGRAM_BOT_TOKEN="your_bot_token"

# Run
python bot.py
```

## Deploy (Free)

1. Fork this repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect GitHub repo
4. Add env var: `TELEGRAM_BOT_TOKEN`
5. Deploy

## Project Structure

```
├── bot.py              # Main bot code
├── lessons/            # 36 lesson files (.md)
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker config
└── README.md
```

## Modules

| # | Module | Lessons |
|---|--------|---------|
| 1 | Basics | Arithmetic, Variables, Strings |
| 2 | Logic | Conditions, Loops, Break/Continue |
| 3 | Data Structures | Lists, Dicts, Tuples/Sets |
| 4 | Functions | Functions, Scope, Lambda, Try/Except |
| 5 | System | Files, OS, Subprocess, Registry, Pip |
| 6 | Automation | Psutil, Services, Scheduler, OOP |
| 7 | GUI | Tkinter, CustomTkinter, PyInstaller |
| 8 | Advanced | Scraping, API, Telegram Bots, DB, Freelancing |

## Customization

Replace files in `lessons/` with your own `.md` content and update `LESSONS_ORDER` + `MODULES` in `bot.py`.

## Tech Stack

- Python 3.11
- python-telegram-bot 22.7
- Deployed on Render.com (free, 24/7)

## License

MIT
