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
CHANNEL = "sms"             # "sms" or "whatsapp"

# Output / formatting
TIMESTAMP_FORMAT = "%A, %d %B %Y %H:%M"
