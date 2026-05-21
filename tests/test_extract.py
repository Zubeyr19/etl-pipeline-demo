import pytest
from unittest.mock import patch, MagicMock
from src.extract import fetch_weather_data, extract_all


MOCK_RESPONSE = {
    "latitude": 55.6761,
    "longitude": 12.5683,
    "hourly": {
        "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
        "temperature_2m": [2.5, 3.1],
        "relative_humidity_2m": [80.0, 78.0],
        "wind_speed_10m": [12.0, 10.5],
        "precipitation": [0.0, 0.1],
    },
}


def _make_mock_response(data):
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = data
    return mock


@patch("src.extract.requests.get")
def test_fetch_weather_data_success(mock_get):
    mock_get.return_value = _make_mock_response(MOCK_RESPONSE.copy())
    location = {"name": "Copenhagen", "latitude": 55.6761, "longitude": 12.5683}
    result = fetch_weather_data(location)
    assert result is not None
    assert result["location_name"] == "Copenhagen"
    assert "hourly" in result


@patch("src.extract.requests.get")
def test_fetch_weather_data_timeout(mock_get):
    import requests as req
    mock_get.side_effect = req.exceptions.Timeout()
    location = {"name": "Copenhagen", "latitude": 55.6761, "longitude": 12.5683}
    result = fetch_weather_data(location)
    assert result is None


@patch("src.extract.requests.get")
def test_fetch_weather_data_http_error(mock_get):
    import requests as req
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = req.exceptions.HTTPError("500")
    mock_get.return_value = mock_response
    location = {"name": "Copenhagen", "latitude": 55.6761, "longitude": 12.5683}
    result = fetch_weather_data(location)
    assert result is None


@patch("src.extract.fetch_weather_data")
def test_extract_all_partial_failure(mock_fetch):
    mock_fetch.side_effect = [MOCK_RESPONSE.copy(), None, MOCK_RESPONSE.copy()]
    results = extract_all()
    assert len(results) == 2


@patch("src.extract.fetch_weather_data")
def test_extract_all_full_failure(mock_fetch):
    mock_fetch.return_value = None
    results = extract_all()
    assert results == []
