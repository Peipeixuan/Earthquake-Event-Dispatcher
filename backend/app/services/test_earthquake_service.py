from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from app.services.earthquake_service import (determine_level,
                                             process_earthquake_and_locations)


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
        earthquake_id = "EQ123"
        earthquake_time = "2025-05-01T12:00:00"
        center = "Demo Center"
        latitude = 24.5
        longitude = 121.8
        magnitude = 4.5
        depth = 10.0
        is_demo = True

    class MockLocation:
        def __init__(self, location, intensity):
            self.location = location
            self.intensity = intensity

    class MockRequest:
        earthquake = MockEarthquake()
        locations = [
            MockLocation("臺北南港", "3級"),
            MockLocation("新竹寶山", "2級"),
        ]

    return MockRequest()

def test_determine_level():
    assert determine_level("3級", 4.5) == "L2"
    assert determine_level("1級", 4.5) == "L1"
    assert determine_level("NA", 4.5) == "NA"
    assert determine_level("1級", 5.0) == "L2"

def test_process_earthquake_and_locations_success(mock_db_connection, mock_request):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.side_effect = [{"count": 0}, {"count": 0}]
    result = process_earthquake_and_locations(mock_request)
    assert result is True
    assert mock_cursor.execute.call_count > 0


def test_process_earthquake_and_locations_alert_suppressed(mock_db_connection, mock_request):
    mock_conn, mock_cursor = mock_db_connection

    # Mock the database cursor behavior to simulate an existing alert
    mock_cursor.fetchone.side_effect = [
        {"count": 1},  # For alert suppression check (first location)
        {"count": 0},  # For second location
    ]

    # Call the function
    result = process_earthquake_and_locations(mock_request)

    # Assertions
    assert result is True
    assert mock_cursor.execute.call_count > 0

    # Verify that the event's trigger_alert is set to 0 due to suppression
    mock_cursor.execute.assert_any_call(
        """
                INSERT INTO event (id, location_eq_id, create_at, region, level, trigger_alert, ack, is_damage, is_operation_active, is_done)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
        ("EQ123-tp", 123, mock.ANY, "臺北南港", "L2", 0, 0, 0, 0, 0),
    )


def test_process_earthquake_and_locations_db_error(mock_db_connection, mock_request):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception("Database error")
    result = process_earthquake_and_locations(mock_request)
    assert result is False
    mock_conn.rollback.assert_called_once()