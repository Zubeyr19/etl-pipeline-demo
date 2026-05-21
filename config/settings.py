import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_LOCATIONS = [
    {"name": "Copenhagen", "latitude": 55.6761, "longitude": 12.5683},
    {"name": "Aarhus", "latitude": 56.1629, "longitude": 10.2039},
    {"name": "Odense", "latitude": 55.4038, "longitude": 10.4024},
]

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "etl-staging")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///weather_data.db")

SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "1"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "etl_pipeline.log")
