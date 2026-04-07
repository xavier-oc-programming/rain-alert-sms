# Paths
from pathlib import Path
BASE_DIR = Path(__file__).parent

# API / URLs
OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

# Weather / Forecast
CITY = "Madrid"
FORECAST_INTERVALS = 4      # 4 x 3-hour intervals = 12-hour window
UNITS = "metric"
RAIN_CODE_THRESHOLD = 700   # OWM codes < 700 indicate precipitation

# Notification channel
CHANNEL = "whatsapp"        # "sms" or "whatsapp"

# Output / formatting
TIMESTAMP_FORMAT = "%A, %d %B %Y %H:%M"


def condition_label(code: int) -> str:
    """Convert an OWM condition code to a colloquial description."""
    if code == 800:
        return "clear skies"
    if code == 801:
        return "mostly clear"
    if code == 802:
        return "partly cloudy"
    if 803 <= code <= 804:
        return "mostly cloudy"
    if 200 <= code <= 299:
        return "thunderstorm"
    if 300 <= code <= 399:
        return "drizzle"
    if code == 500:
        return "light rain"
    if code == 501:
        return "moderate rain"
    if 502 <= code <= 504:
        return "heavy rain"
    if 500 <= code <= 599:
        return "showers"
    if 600 <= code <= 699:
        return "snow"
    if 700 <= code <= 799:
        return "fog / mist"
    return f"unknown ({code})"
