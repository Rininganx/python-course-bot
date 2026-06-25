# Python Kurs Telegram Bot

Interaktiver Telegram-Bot zum Erlernen von Python. 36 Lektionen in 8 Modulen — von den Grundlagen bis zum Freelancing. Fortschrittsverfolgung, Lernserie, Lesezeichen — voll anpassbar.

## Funktionen

- **36 strukturierte Lektionen** in 8 thematischen Modulen
- **Modulnavigation** — Lektionen nach Themen durchsuchen (Grundlagen, Logik, Datenstrukturen, Funktionen, System, Automatisierung, GUI, Fortgeschritten)
- **Fortschrittsverfolgung** — visueller Fortschrittsbalken mit Modul-Statistiken
- **Lernserie** — aufeinanderfolgende Lerntage verfolgen
- **Lesezeichen** — Lektionen für schnellen Zugriff speichern
- **Zufällige Lektion** — zu einer zufälligen abgeschlossenen Lektion springen
- **Inline-Tastatur-Navigation** — Lektionen per Buttons durchsuchen
- **Weiterlernen** — dort weitermachen, wo du aufgehört hast
- **Suche** — Lektionen nach Stichwort finden
- **Tägliche Erinnerungen** — automatische Lektionsbenachrichtigung um 8:00 Uhr
- **Multi-User-Unterstutzung** — jeder Nutzer hat eigenen Fortschritt
- **Abschnittsteilung** — lange Lektionen in lesbare Teile aufgeteilt

## Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `/start` | Willkommensnachricht und Hauptmenu |
| `/stats` | Detaillierte Statistiken (Lernserie, Modulfortschritt) |
| `/random` | Zu einer zufälligen unvollständigen Lektion springen |
| `/bookmark` | Lesezeichen anzeigen |
| `/reset` | Gesamten Fortschritt zurucksetzen (mit Bestatigung) |
| `/health` | Bot-Status prufen |

## Schnellstart

```bash
# Klonen
git clone https://github.com/Rininganx/python-course-bot.git
cd python-course-bot

# Installieren
pip install -r requirements.txt

# Token setzen
export TELEGRAM_BOT_TOKEN="dein_bot_token"

# Starten
python bot.py
```

## Kostenlos bereitstellen

1. Repository forken
2. Zu [render.com](https://render.com) → New → Web Service
3. GitHub-Repository verbinden
4. Umgebungsvariable hinzufugen: `TELEGRAM_BOT_TOKEN`
5. Bereitstellen

## Projektstruktur

```
├── bot.py              # Bot-Hauptcode
├── lessons/            # 36 Lektionsdateien (.md)
├── requirements.txt    # Abhangigkeiten
├── Dockerfile          # Docker-Konfiguration
└── README_de.md        # Deutsche Anleitung
```

## Module

| # | Modul | Lektionen |
|---|-------|-----------|
| 1 | Grundlagen | Arithmetik, Variablen, Zeichenketten |
| 2 | Logik | Bedingungen, Schleifen, Break/Continue |
| 3 | Datenstrukturen | Listen, Dicts, Tupel/Mengen |
| 4 | Funktionen | Funktionen, Scope, Lambda, Try/Except |
| 5 | System | Dateien, OS, Subprocess, Registry, Pip |
| 6 | Automatisierung | Psutil, Dienste, Scheduler, OOP |
| 7 | GUI | Tkinter, CustomTkinter, PyInstaller |
| 8 | Fortgeschritten | Scraping, API, Telegram-Bots, DB, Freelancing |

## Anpassung

Ersetze die Dateien in `lessons/` mit eigenen `.md`-Inhalten und aktualisiere `LESSONS_ORDER` + `MODULES` in `bot.py`.

## Technologie-Stack

- Python 3.11
- python-telegram-bot 22.7
- Bereitgestellt auf Render.com (kostenlos, 24/7)

## Lizenz

MIT
