# Day 35 — Keys, Authentication & Environment Variables

## Course exercise

Build a rain-alert bot that:
1. Calls the OpenWeatherMap forecast API for the next 12 hours.
2. Checks whether any forecast interval has a weather condition code below 700 (precipitation).
3. Sends an SMS via the Twilio API with the result — "bring an umbrella" or "no umbrella needed".
4. Loads all API keys and phone numbers from environment variables (never hardcoded).

## Concepts covered

- **Environment variables** — separating secrets from code using `.env` files.
- **`python-dotenv`** — loading `.env` into `os.environ` at runtime with `load_dotenv()`.
- **API authentication** — passing keys as query parameters (OWM) and via SDK credentials (Twilio).
- **REST API calls** — using `requests.get()` with a params dict; handling `raise_for_status()`.
- **JSON parsing** — navigating nested API response objects.
- **Twilio SDK** — instantiating `Client`, calling `client.messages.create()`.
- **OWM weather codes** — codes below 700 cover thunderstorm, drizzle, rain, snow, and atmosphere. 700+ is clear/cloudy.
- **Conditional messaging** — building different message bodies based on forecast result.
- **Timestamps** — formatting `datetime.now()` for human-readable output.
