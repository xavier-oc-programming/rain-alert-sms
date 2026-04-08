# Rain Alert SMS Bot

Fetches a 12-hour weather forecast and sends an SMS (or WhatsApp) alert via Twilio if rain is expected.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick start](#2-quick-start)
3. [Builds comparison](#3-builds-comparison)
4. [Usage](#4-usage)
5. [Data flow](#5-data-flow)
6. [Features](#6-features)
7. [Navigation flow](#7-navigation-flow)
8. [Architecture](#8-architecture)
9. [Module reference](#9-module-reference)
10. [Configuration reference](#10-configuration-reference)
11. [Data schema](#11-data-schema)
12. [Environment variables](#12-environment-variables)
13. [Design decisions](#13-design-decisions)
14. [Course context](#14-course-context)
15. [Dependencies](#15-dependencies)

---

## 1. Prerequisites

You need accounts on two services before the bot can run. Both have free tiers.

---

### OpenWeatherMap

1. Create a free account at [openweathermap.org](https://openweathermap.org)
2. After signing in, click your username (top right) → **My API Keys**
3. A default key is generated automatically — copy it
4. New keys take **up to 2 hours** to activate

| .env variable | Where to find it |
|---|---|
| `OWM_API_KEY` | My API Keys page — the string next to your default key |

---

### Twilio

1. Create a free account at [twilio.com](https://twilio.com)
2. After signing in, go to the **Console Dashboard** (home page)

**Account credentials** — visible on the dashboard under "Account Info":

| .env variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | Dashboard → Account Info → Account SID (starts with `AC`) |
| `TWILIO_AUTH_TOKEN` | Dashboard → Account Info → Auth Token (click the eye icon to reveal) |

---

#### Option A — SMS (requires a Twilio phone number)

3. Go to **Phone Numbers → Manage → Active Numbers**
4. If empty, click **Buy a number** (free on a trial account — cost is deducted from your trial balance)
5. Claim any number with SMS capability

| .env variable | Where to find it |
|---|---|
| `TWILIO_FROM` | Active Numbers — the number you just claimed (e.g. `+15204927666`) |
| `TWILIO_TO` | Your own mobile number in E.164 format (e.g. `+34665151440`) |

> Trial accounts can only send SMS to **verified numbers**. Go to **Verified Caller IDs** to add and verify your number if sends fail.

---

#### Option B — WhatsApp sandbox (no phone number purchase needed)

3. Go to **Messaging → Try it out → Send a WhatsApp message**
4. On the **Sandbox** tab, follow the "Connect to sandbox" step: send the displayed join keyword (e.g. `join <word>-<word>`) via WhatsApp to `+14155238886`
5. Once connected, the sandbox can send messages to your number

| .env variable | Where to find it |
|---|---|
| `TWILIO_WHATSAPP_FROM` | Always `whatsapp:+14155238886` (the Twilio sandbox number) |
| `TWILIO_WHATSAPP_TO` | Your WhatsApp number with the `whatsapp:` prefix (e.g. `whatsapp:+34665151440`) |

> The WhatsApp sandbox session expires after ~72 hours of inactivity. Re-send the join keyword to reconnect.

---

## 2. Quick start

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

## 3. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Fetches OWM 12-hour forecast | Yes | Yes |
| Sends SMS via Twilio | No | Yes (set `CHANNEL = "sms"`) |
| Sends WhatsApp via Twilio | Yes | Yes (set `CHANNEL = "whatsapp"`) |
| Credentials via `.env` | Yes | Yes |
| OOP (fetcher / notifier classes) | No | Yes |
| All constants in `config.py` | No | Yes |
| Startup credential validation | No | Yes |
| Configurable city | Hardcoded `Madrid` | `CITY` in `config.py` |
| Request timeout | No | Yes (20 s) |
| Colloquial condition labels | No | Yes (`condition_label()` in `config.py`) |
| GitHub Actions daily schedule | No | Yes (7:00 CET via cron) |

---

## 4. Usage

### Original

```bash
python original/main.py
```

Reads credentials from `.env` in the project root, fetches the Madrid forecast, prints each interval's condition code, then sends a WhatsApp message via the Twilio sandbox.

Example output:

```
2025-09-11 09:00:00: condition 501
2025-09-11 12:00:00: condition 800

Message status: queued
```

> Original prints raw OWM condition codes. Advanced translates them — see below.

### Advanced

```bash
python advanced/main.py
```

Behaviour is identical but structured. Change `CHANNEL` in [advanced/config.py](advanced/config.py) to `"sms"` to switch to SMS (requires a Twilio phone number).

Example output:

```
  2025-09-11 09:00:00: moderate rain
  2025-09-11 12:00:00: clear skies

Channel: WHATSAPP
Message: [Wednesday, 11 September 2025 09:14] Rain expected in Madrid in the next 12 hours. Bring an umbrella.
Status:  queued
```

---

## 5. Data flow

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

## 6. Features

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

**Colloquial condition labels.** `condition_label(code)` in `config.py` maps OWM numeric codes to plain English — `800` becomes `"clear skies"`, `502` becomes `"heavy rain"`, etc. Only the advanced build uses this; original prints raw codes.

**GitHub Actions daily schedule.** `.github/workflows/daily-rain-alert.yml` runs the advanced build automatically every day at 7:00 CET (6:00 UTC). Credentials are read from GitHub repository secrets — no `.env` file needed on the runner. The workflow can also be triggered manually from the Actions tab.

---

## 7. Navigation flow

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

## 8. Architecture

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
├── .github/
│   └── workflows/
│       └── daily-rain-alert.yml  # runs advanced build daily at 7:00 CET
│
├── docs/
│   └── COURSE_NOTES.md  # original exercise description and concepts
│
├── original/
│   └── main.py          # verbatim course solution (uses dotenv)
│
└── advanced/
    ├── config.py        # constants + condition_label() code→text mapping
    ├── fetcher.py       # WeatherFetcher — OWM API calls
    ├── notifier.py      # Notifier — Twilio SMS and WhatsApp
    └── main.py          # orchestrator — wires fetcher → check → notifier
```

---

## 9. Module reference

### `config.py` — functions (advanced/config.py)

| Function | Returns | Description |
|---|---|---|
| `condition_label(code)` | `str` | Converts an OWM condition code to a colloquial string (e.g. `502` → `"heavy rain"`, `800` → `"clear skies"`). Falls back to `"unknown (code)"` for unmapped values. |

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

## 10. Configuration reference

All constants live in [advanced/config.py](advanced/config.py).

| Constant | Default | Description |
|---|---|---|
| `OWM_ENDPOINT` | `https://api.openweathermap.org/data/2.5/forecast` | OWM forecast API URL |
| `CITY` | `"Madrid"` | City to fetch the forecast for |
| `FORECAST_INTERVALS` | `4` | Number of 3-hour intervals to fetch (4 = 12 hours) |
| `UNITS` | `"metric"` | Temperature units (`metric` = °C) |
| `RAIN_CODE_THRESHOLD` | `700` | OWM codes below this indicate precipitation |
| `CHANNEL` | `"whatsapp"` | Notification channel: `"sms"` or `"whatsapp"` |
| `TIMESTAMP_FORMAT` | `"%A, %d %B %Y %H:%M"` | `strftime` format for message timestamps |

---

## 11. Data schema

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

## 12. Environment variables

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

## 13. Design decisions

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

**`condition_label()` in `config.py`, not `main.py`.** The mapping from numeric code to human text is configuration, not orchestration logic. Putting it in `config.py` keeps `main.py` clean and makes the labels easy to edit without touching control flow.

**GitHub Actions cron at `0 6 * * *` UTC.** GitHub Actions has no timezone support — all crons run in UTC. `0 6 * * *` equals 7:00 CET (winter, UTC+1). During CEST (summer, UTC+2) it shifts to 8:00 Madrid time. A `workflow_dispatch` trigger is included so the workflow can be run manually at any time from the GitHub UI.

**GitHub Secrets instead of `.env` in CI.** The runner has no `.env` file. `load_dotenv()` is a no-op when the file is absent, and `os.getenv()` reads directly from the environment — which GitHub Actions populates from repository secrets. No code change required to run in CI vs locally.

---

## 14. Course context

Built as Day 35 of [100 Days of Code: The Complete Python Pro Bootcamp](https://www.udemy.com/course/100-days-of-code/) by Dr. Angela Yu.

**Concepts covered in the original build:** environment variables, `python-dotenv`, API key authentication, `requests` HTTP calls, JSON parsing, Twilio SDK, OWM weather codes, conditional messaging, `datetime` formatting.

**The advanced build extends into:** OOP class design, separation of concerns (fetcher / notifier), single-source-of-truth config, multi-channel notification, startup validation, request timeouts, `pathlib`, colloquial condition labels, GitHub Actions scheduling.

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 15. Dependencies

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
