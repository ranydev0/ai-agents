import os

NL_IP: str = os.environ.get("NL_IP", "")
NL_PORT: str = os.environ.get("NL_PORT", "")
NL_TOKEN: str = os.environ.get("NL_TOKEN", "")
NL_URL: str = f"http://{NL_IP}:{NL_PORT}/api/v1/{NL_TOKEN}"

HF_TOKEN: str = os.environ.get("HF_TOKEN", "")
TB_TOKEN: str = os.environ.get("TB_TOKEN", "")

GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5"
WEATHER_API = os.environ.get("WEATHER_API", "")
