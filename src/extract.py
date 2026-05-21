import logging
import requests
from typing import Optional
from config.settings import WEATHER_API_URL, WEATHER_LOCATIONS

logger = logging.getLogger(__name__)


def fetch_weather_data(location: dict) -> Optional[dict]:
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "Europe/Copenhagen",
        "forecast_days": 1,
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        data["location_name"] = location["name"]
        logger.info("Fetched weather data for %s", location["name"])
        return data
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching data for %s", location["name"])
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error for %s: %s", location["name"], e)
    except requests.exceptions.RequestException as e:
        logger.error("Request failed for %s: %s", location["name"], e)
    return None


def extract_all() -> list[dict]:
    results = []
    for location in WEATHER_LOCATIONS:
        data = fetch_weather_data(location)
        if data is not None:
            results.append(data)
    logger.info("Extraction complete: %d/%d locations successful", len(results), len(WEATHER_LOCATIONS))
    return results
