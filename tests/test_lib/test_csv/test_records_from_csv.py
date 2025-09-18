from datetime import datetime, timezone

import pytest

from better_timetagger_cli.lib.csv import records_from_csv


def test_parse_csv_with_tab_separator(csv_with_tab_separator):
    """Parse CSV file using tab separator."""

    records = records_from_csv(iter(csv_with_tab_separator))

    assert len(records) == 2
    assert records[0]["key"] == "abc123"
    assert records[0]["t1"] == 1640995200
    assert records[0]["t2"] == 1640998800
    assert records[0]["ds"] == "Working on #project #backend"
    assert records[0]["_running"] is False
    assert records[0]["_duration"] == 3600


def test_parse_csv_with_comma_separator(csv_with_comma_separator):
    """Parse CSV file using comma separator."""

    records = records_from_csv(iter(csv_with_comma_separator))

    assert len(records) == 2
    assert records[0]["key"] == "abc123"
    assert records[1]["key"] == "def456"


def test_parse_csv_with_semicolon_separator(csv_with_semicolon_separator):
    """Parse CSV file using semicolon separator."""

    records = records_from_csv(iter(csv_with_semicolon_separator))

    assert len(records) == 2
    assert records[0]["key"] == "abc123"
    assert records[1]["key"] == "def456"


def test_parse_csv_with_running_record(csv_with_running_record, mock_now):
    """Parse CSV file containing running record with empty stop time."""

    records = records_from_csv(iter(csv_with_running_record))

    assert len(records) == 1
    record = records[0]
    assert record["key"] == "ghi789"
    assert record["t1"] == 1640995200  # 2022-01-01T00:00:00Z
    assert record["t2"] == 1640995200  # Same as t1 since stop was empty
    assert record["_running"] is True
    assert record["_duration"] == mock_now - 1640995200  # Duration from start to now


def test_parse_csv_with_mixed_records(csv_with_mixed_records, mock_now):
    """Parse CSV file containing both completed and running records."""

    records = records_from_csv(iter(csv_with_mixed_records))

    assert len(records) == 3
    # First record: completed
    assert records[0]["_running"] is False
    assert records[0]["_duration"] == 3600
    # Second record: running
    assert records[1]["_running"] is True
    assert records[1]["_duration"] == mock_now - records[1]["t1"]
    # Third record: completed
    assert records[2]["_running"] is False


def test_parse_csv_with_extra_columns(csv_with_extra_columns):
    """Parse CSV file with extra columns beyond required ones."""

    records = records_from_csv(iter(csv_with_extra_columns))

    assert len(records) == 1
    assert records[0]["key"] == "abc123"
    assert records[0]["ds"] == "Working on #project #backend"


def test_parse_csv_with_whitespace_handling(csv_with_whitespace):
    """Parse CSV file with extra whitespace that gets stripped."""

    records = records_from_csv(iter(csv_with_whitespace))

    assert len(records) == 1
    record = records[0]
    assert record["key"] == "abc123"  # Whitespace stripped
    assert record["ds"] == "Working on #project #backend"  # Whitespace stripped


def test_parse_empty_csv_file(empty_csv):
    """Parse CSV file containing only headers."""

    records = records_from_csv(iter(empty_csv))

    assert len(records) == 0


def test_filter_records_by_timestamp_range(csv_with_mixed_records):
    """Filter records by timestamp range using integer timestamps."""

    # Filter to only include records during or after 2022-01-01T01:30:00Z (1641001800)
    start_filter = 1641001800
    records = records_from_csv(iter(csv_with_mixed_records), start=start_filter)

    # Should include def456 (starts at 01:40:00) and ghi789 (starts at 02:00:00)
    assert len(records) == 2
    assert all(record["t2"] >= start_filter for record in records)


def test_filter_records_by_datetime_range(csv_with_mixed_records):
    """Filter records by datetime range using datetime objects."""

    start_dt = datetime(2022, 1, 1, 1, 30, tzinfo=timezone.utc)
    end_dt = datetime(2022, 1, 1, 2, 30, tzinfo=timezone.utc)

    records = records_from_csv(iter(csv_with_mixed_records), start=start_dt, end=end_dt)

    # Should include def456 (01:40-02:40) and ghi789 (02:00-running)
    assert len(records) == 2


def test_filter_records_excludes_records_outside_range(csv_with_mixed_records):
    """Filter records excluding those outside the specified range."""

    # Very narrow window that should exclude all records
    start_filter = 1641010000  # Way after all test records
    records = records_from_csv(iter(csv_with_mixed_records), start=start_filter)

    assert len(records) == 0


def test_abort_on_missing_required_headers(malformed_csv_missing_header, monkeypatch):
    """Abort parsing when required header fields are missing."""
    mock_now = 1641000000
    monkeypatch.setattr("better_timetagger_cli.lib.timestamps.now_timestamp", lambda: mock_now)

    with pytest.raises(SystemExit):
        list(records_from_csv(iter(malformed_csv_missing_header)))


def test_abort_on_inconsistent_column_count(malformed_csv_wrong_column_count, monkeypatch):
    """Abort parsing when line has wrong number of columns."""
    mock_now = 1641000000
    monkeypatch.setattr("better_timetagger_cli.lib.timestamps.now_timestamp", lambda: mock_now)

    with pytest.raises(SystemExit):
        list(records_from_csv(iter(malformed_csv_wrong_column_count)))


def test_abort_on_invalid_date_format(malformed_csv_invalid_date, monkeypatch):
    """Abort parsing when date format is invalid."""
    mock_now = 1641000000
    monkeypatch.setattr("better_timetagger_cli.lib.timestamps.now_timestamp", lambda: mock_now)

    with pytest.raises(SystemExit):
        list(records_from_csv(iter(malformed_csv_invalid_date)))


def test_set_correct_metadata_fields(csv_with_tab_separator, mock_now):
    """Set correct metadata fields for imported records."""

    records = records_from_csv(iter(csv_with_tab_separator))

    for record in records:
        assert record["mt"] == mock_now  # Modified time set to now
        assert record["st"] == 0  # Start time offset
        assert "_running" in record
        assert "_duration" in record


def test_handle_carriage_return_line_endings():
    """Handle CSV with Windows-style carriage return line endings."""

    csv_with_crlf = [
        "key\tstart\tstop\ttags\tdescription\r\n",
        "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\tproject\tWorking\r\n",
    ]

    records = records_from_csv(iter(csv_with_crlf))

    assert len(records) == 1
    assert records[0]["key"] == "abc123"


def test_convert_z_timezone_to_iso_format(csv_with_tab_separator):
    """Convert Z timezone suffix to proper ISO format for datetime parsing."""

    records = records_from_csv(iter(csv_with_tab_separator))

    # Verify timestamps are correctly parsed from Z format
    assert records[0]["t1"] == 1640995200  # 2022-01-01T00:00:00Z
    assert records[0]["t2"] == 1640998800  # 2022-01-01T01:00:00Z


def test_calculate_duration_for_completed_records(csv_with_tab_separator):
    """Calculate correct duration for completed records."""

    records = records_from_csv(iter(csv_with_tab_separator))

    for record in records:
        if not record["_running"]:
            expected_duration = record["t2"] - record["t1"]
            assert record["_duration"] == expected_duration


def test_calculate_duration_for_running_records(csv_with_running_record, mock_now):
    """Calculate correct duration for running records from start to now."""

    records = records_from_csv(iter(csv_with_running_record))

    record = records[0]
    assert record["_running"] is True
    expected_duration = mock_now - record["t1"]
    assert record["_duration"] == expected_duration
