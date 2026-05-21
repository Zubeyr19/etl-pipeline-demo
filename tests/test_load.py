import pytest
from datetime import datetime
from sqlalchemy import create_engine
from src.load import init_db, load_records, WeatherRecord


def make_records(n=3):
    return [
        {
            "location": "Copenhagen",
            "timestamp": datetime(2024, 1, 1, hour=i),
            "temperature_c": 2.5 + i,
            "humidity_pct": 80.0,
            "wind_speed_kmh": 10.0,
            "precipitation_mm": 0.0,
        }
        for i in range(n)
    ]


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    init_db(eng)
    return eng


def test_load_inserts_records(engine):
    records = make_records(3)
    inserted = load_records(records, engine)
    assert inserted == 3


def test_load_skips_duplicates(engine):
    records = make_records(2)
    load_records(records, engine)
    inserted_second = load_records(records, engine)
    assert inserted_second == 0


def test_load_partial_duplicates(engine):
    first_batch = make_records(2)
    second_batch = make_records(4)
    load_records(first_batch, engine)
    inserted = load_records(second_batch, engine)
    assert inserted == 2


def test_load_empty_list(engine):
    inserted = load_records([], engine)
    assert inserted == 0


def test_load_preserves_values(engine):
    from sqlalchemy.orm import Session
    records = [
        {
            "location": "Aarhus",
            "timestamp": datetime(2024, 6, 15, 12),
            "temperature_c": 22.3,
            "humidity_pct": 55.0,
            "wind_speed_kmh": 8.5,
            "precipitation_mm": 0.0,
        }
    ]
    load_records(records, engine)
    with Session(engine) as session:
        row = session.query(WeatherRecord).filter_by(location="Aarhus").first()
        assert row is not None
        assert row.temperature_c == pytest.approx(22.3)
        assert row.humidity_pct == pytest.approx(55.0)
