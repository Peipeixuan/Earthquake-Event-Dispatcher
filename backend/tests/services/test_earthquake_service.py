import re
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from app.services.earthquake_service import (determine_level,
                                             fetch_all_simulated_earthquakes,
                                             generate_simulated_earthquake_id,
                                             get_alert_suppress_time_from_db,
                                             process_earthquake_and_locations)


def normalize_sql(sql):
    # Remove all whitespace characters for comparison
    return re.sub(r'\s+', '', sql)

@pytest.fixture
def mock_db_connection(mocker):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Set up the lastrowid property for the cursor
    mock_cursor.lastrowid = 123

    # Mock the get_mysql_connection function globally for the main function
    mocker.patch("app.services.earthquake_service.get_mysql_connection", return_value=mock_conn)
    
    # Mock the get_alert_suppress_time_from_db function directly
    mocker.patch("app.services.earthquake_service.get_alert_suppress_time_from_db", return_value=30)

    return mock_conn, mock_cursor

@pytest.fixture
def mock_request():
    # Mock the input request object
    class MockEarthquake:
        def __init__(self):
            # 確保在現在時間 10 分鐘之後，避免觸發 "太早模擬" 的錯誤
            self.earthquake_id = "114097"
            self.earthquake_time = (
                datetime.now(ZoneInfo("Asia/Taipei"))
            ).strftime("%Y-%m-%dT%H:%M:%S")
            self.center = "嘉義縣政府東南東方  30.8  公里 (位於嘉義縣大埔鄉)"
            self.latitude = 24.5
            self.longitude = 121.8
            self.magnitude = 4.5
            self.depth = 10.0
            self.is_demo = True

    class MockLocation:
        def __init__(self, location, intensity):
            self.location = location
            self.intensity = intensity

    class MockRequest:
        earthquake = MockEarthquake()
        locations = [
            MockLocation("Taipei", 1),
            MockLocation("Hsinchu", 2),
            MockLocation("Taichung", 3),
            MockLocation("Tainan", 5)
        ]

    return MockRequest()

# determine_level
def test_determine_level():
    assert determine_level(1, 4.5) == "L1"
    assert determine_level(2, 5.0) == "L2"
    assert determine_level(3, 3.0) == "L2"
    assert determine_level(0, 3.0) == "NA"

# get_alert_suppress_time_from_db
def test_get_alert_suppress_time_from_db(mocker):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("app.services.earthquake_service.get_mysql_connection", return_value=mock_conn)

    # Mock the query result
    mock_cursor.fetchone.return_value = {"value": "45"}

    # Call the function
    result = get_alert_suppress_time_from_db()

    # Assertions
    assert result == 45
    mock_cursor.execute.assert_called_once_with(
        "SELECT value FROM settings WHERE name = %s", ("alert_suppress_time",)
    )
    mock_conn.close.assert_called_once()

def test_get_alert_suppress_time_from_db_default(mocker):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("app.services.earthquake_service.get_mysql_connection", return_value=mock_conn)

    # Mock the query result to return None
    mock_cursor.fetchone.return_value = None

    # Call the function
    result = get_alert_suppress_time_from_db()

    # Assertions
    assert result == 30  # Default value
    mock_cursor.execute.assert_called_once_with(
        "SELECT value FROM settings WHERE name = %s", ("alert_suppress_time",)
    )
    mock_conn.close.assert_called_once()

# generate_simulated_earthquake_id
def test_generate_simulated_earthquake_id(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"max_id": 100000123}

    result = generate_simulated_earthquake_id(mock_conn)
    assert result == 100000124

    # Compare normalized SQL strings
    called_sql = mock_cursor.execute.call_args[0][0]
    expected_sql = "SELECT MAX(id) as max_id FROM earthquake WHERE id >= 100000000"
    assert normalize_sql(called_sql) == normalize_sql(expected_sql)

def test_generate_simulated_earthquake_id_default(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"max_id": None}

    result = generate_simulated_earthquake_id(mock_conn)
    assert result == 100000001

    called_sql = mock_cursor.execute.call_args[0][0]
    expected_sql = "SELECT MAX(id) as max_id FROM earthquake WHERE id >= 100000000"
    assert normalize_sql(called_sql) == normalize_sql(expected_sql)
    
# process_earthquake_and_locations
def test_process_earthquake_and_locations(mock_db_connection, mock_request):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.side_effect = [{"count": 0}, {"count": 0}]
    result = process_earthquake_and_locations(mock_request)
    assert result is True
    assert mock_cursor.execute.call_count > 0

# fetch_all_simulated_earthquakes
def test_fetch_all_simulated_earthquakes(mock_db_connection):
    """
    Test fetching all simulated earthquakes from the database.
    """
    mock_conn, mock_cursor = mock_db_connection
    current_time = datetime.now(ZoneInfo("Asia/Taipei"))
    mock_cursor.fetchall.side_effect = [
        [
            {
                "id": 1,
                "earthquake_time": current_time,
                "center": "嘉義縣政府東南東方  30.8  公里 (位於嘉義縣大埔鄉)",
                "latitude": 24.5,
                "longitude": 121.8,
                "magnitude": 4.5,
                "depth": 10.0,
                "is_demo": True,
            }
        ],
        [
            {"location": "Taipei", "intensity": 1},
            {"location": "Hsinchu", "intensity": 2},
        ],
    ]
    
    result = fetch_all_simulated_earthquakes()
    
    assert len(result) == 1
    assert result[0]["earthquake"]["center"] == "嘉義縣政府東南東方  30.8  公里 (位於嘉義縣大埔鄉)"
    assert len(result[0]["locations"]) == 2
    assert result[0]["locations"][0]["location"] == "Taipei"