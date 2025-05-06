from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from app.services.report_service import (acknowledge_event_by_id,
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


def test_fetch_unacknowledged_events(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"event_id": "E123", "region": "Taipei", "level": "L2"}
    ]
    result = fetch_unacknowledged_events("Taipei")
    assert result == [{"event_id": "E123", "region": "Taipei", "level": "L2"}]
    mock_cursor.execute.assert_called_once()


def test_acknowledge_event_by_id_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {"id": "E123"}
    result = acknowledge_event_by_id("E123")
    assert result is True
    mock_cursor.execute.assert_called()


def test_acknowledge_event_by_id_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = acknowledge_event_by_id("E123")
    assert result is False


def test_update_event_status_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1
    result = update_event_status("E123", True, True)
    assert result is True
    mock_cursor.execute.assert_called()


def test_update_event_status_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0
    result = update_event_status("E123", True, True)
    assert result is False


def test_mark_event_as_repaired_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {"create_at": datetime.now()}
    result = mark_event_as_repaired("E123")
    assert result is True
    mock_cursor.execute.assert_called()


def test_mark_event_as_repaired_failure(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = mark_event_as_repaired("E123")
    assert result is False