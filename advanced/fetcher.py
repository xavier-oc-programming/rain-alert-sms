import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from config import OWM_ENDPOINT


class WeatherFetcher:
    """Fetches forecast data from the OpenWeatherMap API."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_forecast(self, city: str, intervals: int, units: str) -> list[dict]:
        """
        Fetch the next `intervals` forecast slots for `city`.

        Returns a list of forecast dicts from the OWM /forecast endpoint.
        Raises requests.HTTPError on a non-2xx response.
        """
        params = {
            "q": city,
            "appid": self._api_key,
            "units": units,
            "cnt": intervals,
        }
        response = requests.get(OWM_ENDPOINT, params=params, timeout=20)
        response.raise_for_status()
        return response.json()["list"]
