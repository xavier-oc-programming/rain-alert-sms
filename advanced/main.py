import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
from datetime import datetime
from dotenv import load_dotenv

from config import (
    CITY,
    FORECAST_INTERVALS,
    UNITS,
    RAIN_CODE_THRESHOLD,
    TIMESTAMP_FORMAT,
    CHANNEL,
)
from fetcher import WeatherFetcher
from notifier import Notifier

load_dotenv(Path(__file__).parent.parent / ".env")

# ── credentials ──────────────────────────────────────────────────────────────
OWM_API_KEY     = os.getenv("OWM_API_KEY")
ACCOUNT_SID     = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN")
SMS_FROM        = os.getenv("TWILIO_FROM")
SMS_TO          = os.getenv("TWILIO_TO")
WHATSAPP_FROM   = os.getenv("TWILIO_WHATSAPP_FROM")
WHATSAPP_TO     = os.getenv("TWILIO_WHATSAPP_TO")

missing = [k for k, v in {
    "OWM_API_KEY": OWM_API_KEY,
    "TWILIO_ACCOUNT_SID": ACCOUNT_SID,
    "TWILIO_AUTH_TOKEN": AUTH_TOKEN,
}.items() if not v]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# ── fetch forecast ────────────────────────────────────────────────────────────
fetcher = WeatherFetcher(OWM_API_KEY)
forecast = fetcher.get_forecast(CITY, FORECAST_INTERVALS, UNITS)

# ── check for rain ────────────────────────────────────────────────────────────
will_rain = any(slot["weather"][0]["id"] < RAIN_CODE_THRESHOLD for slot in forecast)

for slot in forecast:
    code = slot["weather"][0]["id"]
    print(f"  {slot['dt_txt']}: condition {code}")
print()

# ── build message ─────────────────────────────────────────────────────────────
timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
if will_rain:
    body = f"[{timestamp}] Rain expected in {CITY} in the next 12 hours. Bring an umbrella."
else:
    body = f"[{timestamp}] No rain expected in {CITY} in the next 12 hours."

# ── send notification ─────────────────────────────────────────────────────────
if CHANNEL == "whatsapp":
    from_number = WHATSAPP_FROM or SMS_FROM
    to_number   = WHATSAPP_TO   or SMS_TO
else:
    from_number = SMS_FROM
    to_number   = SMS_TO

notifier = Notifier(ACCOUNT_SID, AUTH_TOKEN, from_number, to_number)

if CHANNEL == "whatsapp":
    status = notifier.send_whatsapp(body)
else:
    status = notifier.send_sms(body)

print(f"Channel: {CHANNEL.upper()}")
print(f"Message: {body}")
print(f"Status:  {status}")
