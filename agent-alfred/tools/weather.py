import httpx
import pandas as pd
from smolagents import tool
from configuration.constants import GEO_URL
from configuration.constants import WEATHER_URL


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
                GEO_URL, params={"name": country.strip().lower(), "count": 1}
            )
            response.raise_for_status()

            results = response.json().get("results")
            if not results:
                raise ValueError(f"No results found for '{country}'")

            return results[0]["latitude"], results[0]["longitude"]
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch coordinates: {e}") from e


@tool
def get_weather(country: str) -> dict:
    """Get the current weather, hourly and daily forecast for a country or city.
    IMPORTANT: If no location has been provided by the user, do not guess or infer one — ask the user to specify a city or country first.

    Args:
        country: The name of the country or city (e.g. "Australia", "New York").

    Returns:
        A dict with keys:
        - "current": temperature, humidity, rain, snowfall, weather_code, is_day
        - "hourly": temperature, humidity, rain, snowfall, weather_code per hour for today
        - "daily": max/min temperature, rain, showers, snowfall, weather_code per day

    WMO weather_code interpretation:
        0: Clear sky
        1: Mainly clear, 2: Partly cloudy, 3: Overcast
        45: Foggy, 48: Icy fog
        51: Light drizzle, 53: Moderate drizzle, 55: Dense drizzle
        61: Slight rain, 63: Moderate rain, 65: Heavy rain
        71: Slight snow, 73: Moderate snow, 75: Heavy snow
        80: Rain showers, 81: Moderate rain showers, 82: Violent rain showers
        95: Thunderstorm, 96: Thunderstorm with hail, 99: Thunderstorm with heavy hail
    """
    try:
        latitude, longitude = get_coordinates(country)

        with httpx.Client() as client:
            response = client.get(
                WEATHER_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "is_day",
                        "rain",
                        "showers",
                        "snowfall",
                        "weather_code",
                    ],
                    "hourly": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "rain",
                        "snowfall",
                        "weather_code",
                    ],
                    "daily": [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_probability_max",
                        "rain_sum",
                        "showers_sum",
                        "snowfall_sum",
                    ],
                    "timezone": "auto",
                    "forecast_days": 7,
                },
            )
            response.raise_for_status()
            data = response.json()

            daily_raw = data.get("daily", {})
            daily_df = pd.DataFrame(daily_raw).set_index("time")

            hourly_raw = data.get("hourly", {})
            hourly_df = pd.DataFrame(hourly_raw).set_index("time")

            return {
                "current": data.get("current", {}),
                "hourly": hourly_df,
                "daily": daily_df,
            }
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch weather: {e}") from e
