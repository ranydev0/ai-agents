import os

NL_IP: str = os.environ("NL_IP", "")
NL_PORT: str = os.environ("NL_PORT", "")
NL_TOKEN: str = os.environ("NL_TOKEN", "")
NL_URL: str = f"http://{NL_IP}:{NL_PORT}/api/v1/{NL_TOKEN}"
