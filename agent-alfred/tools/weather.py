import httpx
import pandas as pd
from smolagents import tool
from configuration.constants import GEO_URL
from configuration.constants import WEATHER_URL
from configuration.constants import WEATHER_API
from datetime import datetime
from zoneinfo import ZoneInfo

AUS_TZ = ZoneInfo("Australia/Sydney")


def _simplify_forecast(items: list) -> list:
    """Flatten raw OpenWeatherMap forecast entries into simplified dicts.

    Args:
        items: List of forecast entries as returned by the OpenWeatherMap
               ``/forecast`` endpoint (3-hour intervals).

    Returns:
        A list of dicts with keys: dt, description, temp, feels_like,
        humidity, wind_speed, rain_chance, rain_mm.
    """
    return [
        {
            "dt": datetime.fromtimestamp(item["dt"], tz=AUS_TZ).strftime(
                "%Y-%m-%d %H:%M"
            ),
            "description": item["weather"][0]["description"],
            "temp": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "humidity": item["main"]["humidity"],
            "wind_speed": item["wind"]["speed"],
            "rain_chance": item["pop"],
            "rain_mm": item.get("rain", {}).get("3h", 0),
        }
        for item in items
    ]


def get_coordinates(country: str) -> tuple[float, float]:
    """Get the latitude and longitude of a country or city.

    Args:
        country: The name of the country or city (e.g. "Australia", "New York").

    Returns:
        A tuple of (latitude, longitude) as floats.
    """
    try:
        with httpx.Client() as client:
            response = client.get(
                GEO_URL,
                params={"q": country.strip().lower(), "limit": 1, "appid": WEATHER_API},
            )
            response.raise_for_status()

            results = response.json()
            if not results:
                raise ValueError(f"No results found for '{country}'")

            return results[0]["lat"], results[0]["lon"]
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch coordinates: {e}") from e


@tool
def get_weather(country: str) -> str:
    """Get the 5-day / 3-hour weather forecast for a country or city.

    IMPORTANT: If no location has been provided by the user, do not guess or
    infer one — ask the user to specify a city or country first.

    Args:
        country: The name of the country or city (e.g. "Australia", "New York").

    Returns:
        A markdown-formatted table (str) with one row per 3-hour interval
        containing columns: dt, description, temp (°C), feels_like (°C),
        humidity (%), wind_speed (m/s), rain_chance (0–1), rain_mm.
    """
    try:
        latitude, longitude = get_coordinates(country)

        with httpx.Client() as client:
            response = client.get(
                f"{WEATHER_URL}/forecast",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "units": "metric",
                    "appid": WEATHER_API,
                },
            )
            response.raise_for_status()
            df = pd.DataFrame(_simplify_forecast(response.json()["list"]))
            return df.to_markdown(index=False)

    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch weather: {e}") from e
