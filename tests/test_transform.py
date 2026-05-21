import pytest
from datetime import datetime
from src.transform import validate_raw, transform, transform_all


def make_raw(location="Copenhagen", times=None, temps=None, humidities=None, winds=None, precips=None):
    times = times or ["2024-01-01T00:00", "2024-01-01T01:00"]
    return {
        "location_name": location,
        "hourly": {
            "time": times,
            "temperature_2m": temps or [2.5, 3.1],
            "relative_humidity_2m": humidities or [80.0, 78.0],
            "wind_speed_10m": winds or [12.0, 10.5],
            "precipitation": precips or [0.0, 0.1],
        },
    }


def test_validate_raw_valid():
    assert validate_raw(make_raw()) is True


def test_validate_raw_missing_location():
    raw = make_raw()
    del raw["location_name"]
    assert validate_raw(raw) is False


def test_validate_raw_missing_hourly_field():
    raw = make_raw()
    del raw["hourly"]["temperature_2m"]
    assert validate_raw(raw) is False


def test_transform_returns_correct_count():
    raw = make_raw(times=["2024-01-01T00:00", "2024-01-01T01:00", "2024-01-01T02:00"])
    raw["hourly"]["temperature_2m"] = [1.0, 2.0, 3.0]
    raw["hourly"]["relative_humidity_2m"] = [70.0, 71.0, 72.0]
    raw["hourly"]["wind_speed_10m"] = [5.0, 6.0, 7.0]
    raw["hourly"]["precipitation"] = [0.0, 0.0, 0.1]
    records = transform(raw)
    assert len(records) == 3


def test_transform_parses_timestamp():
    records = transform(make_raw())
    assert isinstance(records[0]["timestamp"], datetime)


def test_transform_nulls_out_of_range_temp():
    raw = make_raw(temps=[999.0, 2.0])
    records = transform(raw)
    assert records[0]["temperature_c"] is None
    assert records[1]["temperature_c"] == 2.0


def test_transform_nulls_out_of_range_humidity():
    raw = make_raw(humidities=[150.0, 80.0])
    records = transform(raw)
    assert records[0]["humidity_pct"] is None


def test_transform_invalid_timestamp_skipped():
    raw = make_raw(times=["NOT-A-DATE", "2024-01-01T01:00"])
    records = transform(raw)
    assert len(records) == 1


def test_transform_invalid_raw():
    records = transform({"bad": "data"})
    assert records == []


def test_transform_all_aggregates():
    raw_list = [make_raw("Copenhagen"), make_raw("Aarhus")]
    records = transform_all(raw_list)
    assert len(records) == 4
    locations = {r["location"] for r in records}
    assert locations == {"Copenhagen", "Aarhus"}
