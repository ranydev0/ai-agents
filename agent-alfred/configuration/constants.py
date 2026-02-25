import os

NL_IP: str = os.environ.get("NL_IP", "")
NL_PORT: str = os.environ.get("NL_PORT", "")
NL_TOKEN: str = os.environ.get("NL_TOKEN", "")
NL_URL: str = f"http://{NL_IP}:{NL_PORT}/api/v1/{NL_TOKEN}"

HF_TOKEN: str = os.environ.get("HF_TOKEN", "")
TB_TOKEN: str = os.environ.get("TB_TOKEN", "")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
