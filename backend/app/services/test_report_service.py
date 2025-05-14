from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from app.services.report_service import (acknowledge_event_by_id,
                                         auto_close_unprocessed_events,
                                         fetch_acknowledged_events,
                                         fetch_closed_events,
                                         fetch_in_process_events,
                                         fetch_unacknowledged_events,
                                         mark_event_as_repaired,
                                         update_event_status)


@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("app.services.report_service.get_mysql_connection", return_value=mock_conn)
    return mock_conn, mock_cursor

# fetch_unacknowledged_events
def test_fetch_unacknowledged_events(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "114097-tp", "region": "Taipei", "level": "L2"}
    ]
    result = fetch_unacknowledged_events("Taipei")
    assert result == [{"event_id": "114097-tp", "region": "Taipei", "level": "L2"}]
    mock_cursor.execute.assert_called_once()

def test_fetch_unacknowledged_events_invalid_location(mock_db_connection):
    result = fetch_unacknowledged_events("InvalidLocation")
    assert result == {"message": "Invalid location"}

# acknowledge_event_by_id
def test_acknowledge_event_by_id_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {"id": "114097-tp"}
    result = acknowledge_event_by_id("114097-tp")
    assert result is True
    mock_cursor.execute.assert_called()

def test_acknowledge_event_by_id_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = acknowledge_event_by_id("114097-tp")
    assert result is False

# fetch_acknowledged_events
def test_fetch_acknowledged_events(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "114097-tp", "region": "Taipei", "level": "L2", "ack_time": datetime.now()}
    ]
    result = fetch_acknowledged_events("Taipei")
    assert len(result) == 1
    assert result[0]["event_id"] == "114097-tp"
    mock_cursor.execute.assert_called_once()

# update_event_status
def test_update_event_status_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1
    result = update_event_status("114097-tp", True, True)
    assert result is True
    mock_cursor.execute.assert_called()

def test_update_event_status_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0
    result = update_event_status("114097-tp", True, True)
    assert result is False

# fetch_in_process_events
def test_fetch_in_process_events(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "114097-tp", "region": "Taipei", "level": "L2", "is_operation_active": True}
    ]
    result = fetch_in_process_events("Taipei")
    assert len(result) == 1
    assert result[0]["event_id"] == "114097-tp"
    mock_cursor.execute.assert_called_once()

# mark_event_as_repaired
def test_mark_event_as_repaired_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {"create_at": datetime.now()}
    result = mark_event_as_repaired("114097-tp")
    assert result is True
    mock_cursor.execute.assert_called()

def test_mark_event_as_repaired_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = mark_event_as_repaired("114097-tp")
    assert result is False

# fetch_closed_events
def test_fetch_closed_events(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "114097-tp", "region": "Taipei", "level": "L2", "process_time": 30}
    ]
    result = fetch_closed_events("Taipei")
    assert len(result) == 1
    assert result[0]["event_id"] == "114097-tp"
    mock_cursor.execute.assert_called_once()

def test_fetch_closed_events_unprocessed(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "114097-tp", "region": "Taipei", "level": "L2", "process_time": -1}
    ]
    result = fetch_closed_events("Taipei")
    assert len(result) == 1
    assert result[0]["process_time"] == "未處理"
    mock_cursor.execute.assert_called_once()

# auto_close_unprocessed_events
def test_auto_close_unprocessed_events_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [{"id": "114097-tp"}]
    mock_cursor.rowcount = 1
    result = auto_close_unprocessed_events()
    assert result == 1
    mock_cursor.execute.assert_called()

def test_auto_close_unprocessed_events_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = []
    result = auto_close_unprocessed_events()
    assert result == 0
    mock_cursor.execute.assert_called()