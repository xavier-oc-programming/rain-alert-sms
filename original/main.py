import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime

# -------------------- LOAD ENV VARIABLES --------------------
load_dotenv()

OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
OWM_API_KEY = os.getenv("OWM_API_KEY")  # keep secret

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")  # WhatsApp sandbox sender
TO_NUMBER = os.getenv("TWILIO_WHATSAPP_TO")      # Verified WhatsApp number

# -------------------- GET WEATHER DATA --------------------
params = {
    "q": "Madrid",        # City name is fine to keep in code
    "appid": OWM_API_KEY,
    "units": "metric",
    "cnt": 4,             # next 12 hours (4 x 3h intervals)
}

response = requests.get(OWM_ENDPOINT, params=params)
response.raise_for_status()
weather_data = response.json()

# -------------------- CHECK FOR RAIN --------------------
will_rain = False

for forecast in weather_data["list"]:
    condition_code = forecast["weather"][0]["id"]
    print(f"{forecast['dt_txt']}: condition {condition_code}")
    if condition_code < 700:
        will_rain = True
        break

print()

# -------------------- TIMESTAMP --------------------
now = datetime.now()
timestamp = now.strftime("%A, %d %B %Y %H:%M")

# -------------------- ALERT --------------------
client = Client(ACCOUNT_SID, AUTH_TOKEN)

if will_rain:
    body = f"[{timestamp}] It's going to rain today ☔ Bring an umbrella!"
else:
    body = f"[{timestamp}] No rain expected today 🌤️ No umbrella needed."

message = client.messages.create(
    body=body,
    from_=FROM_NUMBER,
    to=TO_NUMBER
)

print("Message status:", message.status)
