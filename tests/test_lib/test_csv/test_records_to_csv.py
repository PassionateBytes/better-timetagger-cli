from better_timetagger_cli.lib.csv import records_to_csv


def test_convert_records_to_csv(sample_records, monkeypatch):
    """Convert basic sample records to CSV format with proper headers and data."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#project #backend\tWorking on #project #backend"
    assert lines[2] == "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\t#team\tMeeting with #team"
    assert lines[3] == "ghi789\t2022-01-01T00:00:00Z\t\t#task\tCurrently working on #task"


def test_convert_empty_records_list_to_csv(monkeypatch):
    """Convert empty records list to CSV with only headers."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv([])

    assert result == "key\tstart\tstop\ttags\tdescription"


def test_convert_completed_records_to_csv(completed_records, monkeypatch):
    """Convert basic sample records to CSV format with proper headers and data."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(completed_records)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#project #backend\tWorking on #project #backend"
    assert lines[2] == "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\t#team\tMeeting with #team"


def test_convert_running_record_to_csv(running_records, monkeypatch):
    """Convert running record to CSV with empty stop time."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(running_records)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "ghi789\t2022-01-01T00:00:00Z\t\t#task\tCurrently working on #task"


def test_convert_records_with_whitespace_cleanup(monkeypatch):
    """Convert records with multiple whitespace characters to CSV with cleaned whitespace."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "test\t\nkey", "t1": 1640995200, "t2": 1640998800, "_running": False, "ds": "Description\twith\n\nmultiple   spaces"}]

    result = records_to_csv(records)

    lines = result.split("\n")
    assert "test key" in lines[1]  # Tab and newline should be replaced with single space
    assert "Description with multiple spaces" in lines[1]  # Multiple spaces normalized


def test_use_windows_newlines_on_windows_platform(sample_records, monkeypatch):
    """Use Windows newlines when running on Windows platform."""
    monkeypatch.setattr("sys.platform", "win32")

    result = records_to_csv(sample_records)

    assert "\r\n" in result
    assert result.count("\r\n") == 3  # Header + 3 data lines = 3 newlines


def test_use_unix_newlines_on_non_windows_platform(sample_records, monkeypatch):
    """Use Unix newlines when running on non-Windows platform."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records)

    assert "\r\n" not in result
    assert result.count("\n") == 3  # Header + 2 data lines = 3 newlines


def test_handle_records_with_zero_timestamps(monkeypatch):
    """Handle records with zero timestamps correctly."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "zero_time", "t1": 0, "t2": 0, "_running": False, "ds": "Zero timestamp test"}]

    result = records_to_csv(records)

    lines = result.split("\n")
    assert "1970-01-01T00:00:00Z" in lines[1]  # Unix epoch


def test_convert_records_without_tags_in_description(monkeypatch):
    """Convert records without tags in description to CSV with empty tags field."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "no_tags", "t1": 1640995200, "t2": 1640998800, "_running": False, "ds": "Simple description without tags"}]

    result = records_to_csv(records)

    lines = result.split("\n")
    fields = lines[1].split("\t")
    assert fields[3] == ""  # Tags field should be empty


def test_convert_single_record_to_csv(monkeypatch):
    """Convert single record to CSV format."""
    monkeypatch.setattr("sys.platform", "linux")

    record = {"key": "single", "t1": 1640995200, "t2": 1640998800, "ds": "Single record #test", "_running": False, "_duration": 3600}

    result = records_to_csv([record])

    lines = result.split("\n")
    assert len(lines) == 2  # Header + 1 data line
    assert lines[1] == "single\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#test\tSingle record #test"


def test_preserve_field_order_in_csv_output(sample_records, monkeypatch):
    """Preserve correct field order in CSV output."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records)

    lines = result.split("\n")
    header_fields = lines[0].split("\t")
    assert header_fields == ["key", "start", "stop", "tags", "description"]

    # Verify data fields match header order
    data_fields = lines[1].split("\t")
    assert len(data_fields) == 5
