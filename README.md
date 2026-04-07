# Rain Alert SMS Bot

Fetches a 12-hour weather forecast and sends an SMS (or WhatsApp) alert via Twilio if rain is expected.

---

## Table of Contents

1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [Data flow](#4-data-flow)
5. [Features](#5-features)
6. [Navigation flow](#6-navigation-flow)
7. [Architecture](#7-architecture)
8. [Module reference](#8-module-reference)
9. [Configuration reference](#9-configuration-reference)
10. [Data schema](#10-data-schema)
11. [Environment variables](#11-environment-variables)
12. [Design decisions](#12-design-decisions)
13. [Course context](#13-course-context)
14. [Dependencies](#14-dependencies)

---

## 1. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys and phone numbers
python menu.py         # select 1 (original) or 2 (advanced)
```

Or run a build directly:

```bash
python original/main.py
python advanced/main.py
```

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Fetches OWM 12-hour forecast | Yes | Yes |
| Sends SMS via Twilio | Yes | Yes |
| Sends WhatsApp via Twilio | No | Yes (set `CHANNEL = "whatsapp"`) |
| Credentials via `.env` | Yes | Yes |
| OOP (fetcher / notifier classes) | No | Yes |
| All constants in `config.py` | No | Yes |
| Startup credential validation | No | Yes |
| Configurable city | Hardcoded `Madrid` | `CITY` in `config.py` |
| Request timeout | No | Yes (20 s) |

---

## 3. Usage

### Original

```bash
python original/main.py
```

Reads credentials from `.env` in the project root, fetches the Madrid forecast, prints each interval's condition code, then sends one SMS.

Example output:

```
2025-09-11 09:00:00: condition 501
2025-09-11 12:00:00: condition 800

Message status: queued
```

### Advanced

```bash
python advanced/main.py
```

Behaviour is identical but structured. Change `CHANNEL` in [advanced/config.py](advanced/config.py) to `"whatsapp"` to switch channels.

Example output:

```
  2025-09-11 09:00:00: condition 501
  2025-09-11 12:00:00: condition 800

Channel: SMS
Message: [Wednesday, 11 September 2025 09:14] Rain expected in Madrid in the next 12 hours. Bring an umbrella.
Status:  queued
```

---

## 4. Data flow

```
.env
  └─ load_dotenv()
       └─ OWM API key, Twilio credentials

OpenWeatherMap /forecast
  └─ GET ?q=Madrid&cnt=4&units=metric
       └─ JSON: list of 4 forecast slots (3 h each)
            └─ check weather[0].id < 700
                 └─ bool: will_rain

Twilio Messages API
  └─ client.messages.create(body, from_, to)
       └─ message.status (queued / sent / delivered)
```

**Format at each stage:**
- **Input**: environment variables (strings)
- **Fetch**: HTTP GET → JSON object with a `"list"` array
- **Process**: iterate `list`, read `weather[0]["id"]` integer, compare to threshold
- **Output**: one SMS/WhatsApp string; Twilio returns a status string

---

## 5. Features

### Both builds

**12-hour rain detection.** Requests 4 forecast intervals of 3 hours each (total 12 hours) from OpenWeatherMap. Any interval with a condition code below 700 (thunderstorm, drizzle, rain, snow) triggers the alert.

**Timestamped messages.** Every message body includes the current date and time so you know exactly when the alert was generated.

**Credential isolation.** All API keys and phone numbers are loaded from `.env` and never appear in source code.

### Advanced only

**Configurable channel.** Set `CHANNEL = "whatsapp"` in `config.py` to switch from SMS to WhatsApp without changing any other code.

**Startup validation.** If a required environment variable is missing, the script raises a `RuntimeError` with a clear list of what's missing before making any API calls.

**OOP modules.** `WeatherFetcher` owns all OWM logic; `Notifier` owns all Twilio logic. Each is independently testable and swappable.

**Request timeout.** All HTTP requests use a 20-second timeout to prevent silent hangs.

**Configurable city.** Change `CITY` in `config.py` to target any city supported by OWM.

---

## 6. Navigation flow

### a) Terminal menu tree

```
python menu.py
│
├── 1 → original/main.py  (runs, returns to menu)
├── 2 → advanced/main.py  (runs, returns to menu)
└── q → exit
```

### b) Execution flow (advanced build)

```
Start
  │
  ├─ load_dotenv() ──── missing vars? → raise RuntimeError → stop
  │
  ├─ WeatherFetcher.get_forecast(city, intervals, units)
  │     │
  │     └─ HTTP error (4xx/5xx)? → raise HTTPError → stop
  │
  ├─ any forecast code < 700?
  │     ├─ Yes → "Rain expected… Bring an umbrella."
  │     └─ No  → "No rain expected…"
  │
  ├─ CHANNEL == "whatsapp"?
  │     ├─ Yes → Notifier.send_whatsapp(body)
  │     └─ No  → Notifier.send_sms(body)
  │
  └─ print status → done
```

---

## 7. Architecture

```
rain-alert-sms/
│
├── menu.py              # CLI launcher — prints logo, routes to builds
├── art.py               # LOGO ASCII art constant
├── requirements.txt     # pip dependencies + Python version note
├── .gitignore           # ignores .env, __pycache__, old_files/, etc.
├── .env.example         # template for required environment variables
├── README.md
│
├── docs/
│   └── COURSE_NOTES.md  # original exercise description and concepts
│
├── original/
│   └── main.py          # verbatim course solution (uses dotenv)
│
└── advanced/
    ├── config.py        # all constants — city, threshold, channel, format
    ├── fetcher.py       # WeatherFetcher — OWM API calls
    ├── notifier.py      # Notifier — Twilio SMS and WhatsApp
    └── main.py          # orchestrator — wires fetcher → check → notifier
```

---

## 8. Module reference

### `WeatherFetcher` (advanced/fetcher.py)

| Method | Returns | Description |
|---|---|---|
| `__init__(api_key)` | — | Stores the OWM API key |
| `get_forecast(city, intervals, units)` | `list[dict]` | Fetches `intervals` x 3-hour forecast slots for `city`. Raises `requests.HTTPError` on failure. |

### `Notifier` (advanced/notifier.py)

| Method | Returns | Description |
|---|---|---|
| `__init__(account_sid, auth_token, from_number, to_number)` | — | Creates the Twilio client |
| `send_sms(body)` | `str` | Sends `body` as an SMS. Returns Twilio message status. |
| `send_whatsapp(body)` | `str` | Sends `body` as a WhatsApp message. Auto-prefixes numbers with `whatsapp:` if missing. Returns status. |

---

## 9. Configuration reference

All constants live in [advanced/config.py](advanced/config.py).

| Constant | Default | Description |
|---|---|---|
| `OWM_ENDPOINT` | `https://api.openweathermap.org/data/2.5/forecast` | OWM forecast API URL |
| `CITY` | `"Madrid"` | City to fetch the forecast for |
| `FORECAST_INTERVALS` | `4` | Number of 3-hour intervals to fetch (4 = 12 hours) |
| `UNITS` | `"metric"` | Temperature units (`metric` = °C) |
| `RAIN_CODE_THRESHOLD` | `700` | OWM codes below this indicate precipitation |
| `CHANNEL` | `"sms"` | Notification channel: `"sms"` or `"whatsapp"` |
| `TIMESTAMP_FORMAT` | `"%A, %d %B %Y %H:%M"` | `strftime` format for message timestamps |

---

## 10. Data schema

### OWM forecast response (relevant fields)

```json
{
  "list": [
    {
      "dt_txt": "2025-09-11 09:00:00",
      "weather": [
        {
          "id": 501,
          "main": "Rain",
          "description": "moderate rain"
        }
      ]
    }
  ]
}
```

`weather[0]["id"]` is the condition code. Codes `< 700` = precipitation. Codes `>= 700` = atmosphere, clouds, or clear.

### SMS / WhatsApp message body

```
[Wednesday, 11 September 2025 09:14] Rain expected in Madrid in the next 12 hours. Bring an umbrella.
```

or

```
[Wednesday, 11 September 2025 09:14] No rain expected in Madrid in the next 12 hours.
```

---

## 11. Environment variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Required | Description |
|---|---|---|
| `OWM_API_KEY` | Yes | OpenWeatherMap API key |
| `TWILIO_ACCOUNT_SID` | Yes | Twilio account SID (starts with `AC`) |
| `TWILIO_AUTH_TOKEN` | Yes | Twilio auth token |
| `TWILIO_FROM` | Yes (SMS) | Twilio trial phone number |
| `TWILIO_TO` | Yes (SMS) | Your verified phone number |
| `TWILIO_WHATSAPP_FROM` | Yes (WhatsApp) | Twilio WhatsApp sandbox sender (`whatsapp:+14155238886`) |
| `TWILIO_WHATSAPP_TO` | Yes (WhatsApp) | Your verified WhatsApp number (`whatsapp:+…`) |

---

## 12. Design decisions

**`config.py` — zero magic numbers.** Every tunable value (`CITY`, `FORECAST_INTERVALS`, `RAIN_CODE_THRESHOLD`, `CHANNEL`) lives in one file. Changing the city or switching channels requires editing one line, not hunting through code.

**Separate `WeatherFetcher` and `Notifier` modules.** Each class does one thing. You can unit-test `WeatherFetcher` against a mock HTTP response without touching Twilio, and vice versa. Swapping OWM for another weather provider only changes `fetcher.py`.

**Credentials via `.env`, never hardcoded.** API keys in source code get committed, indexed by search engines, and rotated expensively. `.env` keeps them local.

**`.env.example` committed, `.env` gitignored.** Documents every required variable for new collaborators without leaking actual secrets. The placeholder values make it clear what format each variable expects.

**`Path(__file__).parent` for all file paths.** The scripts run correctly whether launched from `menu.py` (via `subprocess.run` with `cwd=`) or directly from the terminal. Relative paths like `"../.env"` break depending on cwd; `Path(__file__).parent` does not.

**Pure-logic modules raise exceptions, not `sys.exit()`.** `WeatherFetcher` and `Notifier` raise `HTTPError` or `TwilioRestException` on failure. `main.py` decides how to handle errors. This keeps the modules reusable in any context (tests, other scripts, future async wrappers).

**`sys.path.insert` in each module.** Makes sibling imports work whether the module is imported from `menu.py` (via `subprocess.run`) or run directly. No `__init__.py` required.

**`subprocess.run` + `cwd=path.parent` in `menu.py`.** Ensures that when `main.py` does `Path(__file__).parent`, it resolves relative to the script's directory, not the terminal's working directory.

**`while True` in `menu.py` — no recursion.** Re-calling `main()` after each build would grow the call stack indefinitely. A loop with a `clear` flag avoids that and keeps error messages visible (the flag is only reset to `True` on a valid choice, not on invalid input).

**Console cleared before every valid menu draw, not after invalid input.** The error message "Invalid choice. Try again." stays on screen so the user sees what happened.

---

## 13. Course context

Built as Day 35 of [100 Days of Code: The Complete Python Pro Bootcamp](https://www.udemy.com/course/100-days-of-code/) by Dr. Angela Yu.

**Concepts covered in the original build:** environment variables, `python-dotenv`, API key authentication, `requests` HTTP calls, JSON parsing, Twilio SDK, OWM weather codes, conditional messaging, `datetime` formatting.

**The advanced build extends into:** OOP class design, separation of concerns (fetcher / notifier), single-source-of-truth config, multi-channel notification, startup validation, request timeouts, `pathlib`.

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 14. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `requests` | `advanced/fetcher.py`, `original/main.py` | HTTP GET to OpenWeatherMap API |
| `twilio` | `advanced/notifier.py`, `original/main.py` | Twilio REST client for SMS/WhatsApp |
| `python-dotenv` | `advanced/main.py`, `original/main.py` | Load `.env` into environment |
| `os` | `advanced/main.py`, `original/main.py`, `menu.py` | Read env vars, clear console |
| `datetime` | `advanced/main.py`, `original/main.py` | Timestamp formatting |
| `pathlib` | `advanced/main.py`, `advanced/fetcher.py`, `advanced/notifier.py`, `menu.py` | Portable file paths |
| `sys` | `advanced/main.py`, `advanced/fetcher.py`, `advanced/notifier.py`, `menu.py` | `sys.path.insert`, `sys.executable` |
| `subprocess` | `menu.py` | Launch builds as subprocesses |
