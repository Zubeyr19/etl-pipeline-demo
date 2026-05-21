import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["hourly", "location_name"]
HOURLY_FIELDS = ["time", "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "precipitation"]

TEMP_MIN = -40.0
TEMP_MAX = 60.0
HUMIDITY_MIN = 0.0
HUMIDITY_MAX = 100.0
WIND_MIN = 0.0
WIND_MAX = 250.0


def validate_raw(raw: dict) -> bool:
    for field in REQUIRED_FIELDS:
        if field not in raw:
            logger.warning("Missing field '%s' in raw data for %s", field, raw.get("location_name", "unknown"))
            return False
    for field in HOURLY_FIELDS:
        if field not in raw.get("hourly", {}):
            logger.warning("Missing hourly field '%s'", field)
            return False
    return True


def _clamp_or_null(value: Optional[float], lo: float, hi: float) -> Optional[float]:
    if value is None:
        return None
    if lo <= value <= hi:
        return value
    logger.warning("Value %s out of range [%s, %s], nulling", value, lo, hi)
    return None


def transform(raw: dict) -> list[dict]:
    if not validate_raw(raw):
        return []

    hourly = raw["hourly"]
    location = raw["location_name"]
    records = []

    times = hourly["time"]
    temps = hourly["temperature_2m"]
    humidities = hourly["relative_humidity_2m"]
    winds = hourly["wind_speed_10m"]
    precips = hourly["precipitation"]

    for i, ts in enumerate(times):
        try:
            parsed_time = datetime.fromisoformat(ts)
        except ValueError:
            logger.warning("Invalid timestamp '%s', skipping", ts)
            continue

        records.append({
            "location": location,
            "timestamp": parsed_time,
            "temperature_c": _clamp_or_null(temps[i] if i < len(temps) else None, TEMP_MIN, TEMP_MAX),
            "humidity_pct": _clamp_or_null(humidities[i] if i < len(humidities) else None, HUMIDITY_MIN, HUMIDITY_MAX),
            "wind_speed_kmh": _clamp_or_null(winds[i] if i < len(winds) else None, WIND_MIN, WIND_MAX),
            "precipitation_mm": precips[i] if i < len(precips) else None,
        })

    logger.info("Transformed %d records for %s", len(records), location)
    return records


def transform_all(raw_list: list[dict]) -> list[dict]:
    all_records = []
    for raw in raw_list:
        all_records.extend(transform(raw))
    logger.info("Total transformed records: %d", len(all_records))
    return all_records
