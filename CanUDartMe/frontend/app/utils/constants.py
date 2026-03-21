import os

# Override via environment for production builds
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
WS_BASE_URL  = os.getenv("WS_BASE_URL",  "ws://localhost:8000")

# Dart board region labels
REGIONS = ["inner", "middle", "outer"]
REGION_COLORS = {
    "inner":  "#E53935",   # red
    "middle": "#FB8C00",   # orange
    "outer":  "#43A047",   # green
}
REGION_POINTS = {"inner": 30, "middle": 20, "outer": 10}

APP_TITLE = "CanUDartMe"
MAX_PLAYERS = 6
