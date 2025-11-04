from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from better_timetagger_cli.lib.csv import records_to_csv


def test_convert_records_to_csv(sample_records, monkeypatch):
    """Convert basic sample records to CSV format with proper headers and data."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records, utc=True)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#project #backend\tWorking on #project #backend"
    assert lines[2] == "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\t#team\tMeeting with #team"
    assert lines[3] == "ghi789\t2022-01-01T00:00:00Z\t\t#task\tCurrently working on #task"


def test_convert_empty_records_list_to_csv(monkeypatch):
    """Convert empty records list to CSV with only headers."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv([], utc=True)

    assert result == "key\tstart\tstop\ttags\tdescription"


def test_convert_completed_records_to_csv(completed_records, monkeypatch):
    """Convert basic sample records to CSV format with proper headers and data."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(completed_records, utc=True)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#project #backend\tWorking on #project #backend"
    assert lines[2] == "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\t#team\tMeeting with #team"


def test_convert_running_record_to_csv(running_records, monkeypatch):
    """Convert running record to CSV with empty stop time."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(running_records, utc=True)

    lines = result.split("\n")
    assert lines[0] == "key\tstart\tstop\ttags\tdescription"
    assert lines[1] == "ghi789\t2022-01-01T00:00:00Z\t\t#task\tCurrently working on #task"


def test_convert_records_with_whitespace_cleanup(monkeypatch):
    """Convert records with multiple whitespace characters to CSV with cleaned whitespace."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "test\t\nkey", "t1": 1640995200, "t2": 1640998800, "_running": False, "ds": "Description\twith\n\nmultiple   spaces"}]

    result = records_to_csv(records, utc=True)

    lines = result.split("\n")
    assert "test key" in lines[1]  # Tab and newline should be replaced with single space
    assert "Description with multiple spaces" in lines[1]  # Multiple spaces normalized


def test_use_windows_newlines_on_windows_platform(sample_records, monkeypatch):
    """Use Windows newlines when running on Windows platform."""
    monkeypatch.setattr("sys.platform", "win32")

    result = records_to_csv(sample_records, utc=True)

    assert "\r\n" in result
    assert result.count("\r\n") == 3  # Header + 3 data lines = 3 newlines


def test_use_unix_newlines_on_non_windows_platform(sample_records, monkeypatch):
    """Use Unix newlines when running on non-Windows platform."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records, utc=True)

    assert "\r\n" not in result
    assert result.count("\n") == 3  # Header + 2 data lines = 3 newlines


def test_handle_records_with_zero_timestamps(monkeypatch):
    """Handle records with zero timestamps correctly."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "zero_time", "t1": 0, "t2": 0, "_running": False, "ds": "Zero timestamp test"}]

    result = records_to_csv(records, utc=True)

    lines = result.split("\n")
    assert "1970-01-01T00:00:00Z" in lines[1]  # Unix epoch


def test_convert_records_without_tags_in_description(monkeypatch):
    """Convert records without tags in description to CSV with empty tags field."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [{"key": "no_tags", "t1": 1640995200, "t2": 1640998800, "_running": False, "ds": "Simple description without tags"}]

    result = records_to_csv(records, utc=True)

    lines = result.split("\n")
    fields = lines[1].split("\t")
    assert fields[3] == ""  # Tags field should be empty


def test_convert_single_record_to_csv(monkeypatch):
    """Convert single record to CSV format."""
    monkeypatch.setattr("sys.platform", "linux")

    record = {"key": "single", "t1": 1640995200, "t2": 1640998800, "ds": "Single record #test", "_running": False, "_duration": 3600}

    result = records_to_csv([record], utc=True)

    lines = result.split("\n")
    assert len(lines) == 2  # Header + 1 data line
    assert lines[1] == "single\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\t#test\tSingle record #test"


def test_preserve_field_order_in_csv_output(sample_records, monkeypatch):
    """Preserve correct field order in CSV output."""
    monkeypatch.setattr("sys.platform", "linux")

    result = records_to_csv(sample_records, utc=True)

    lines = result.split("\n")
    header_fields = lines[0].split("\t")
    assert header_fields == ["key", "start", "stop", "tags", "description"]

    # Verify data fields match header order
    data_fields = lines[1].split("\t")
    assert len(data_fields) == 5


@pytest.mark.parametrize(
    "local_timezone",
    [
        timezone.utc,  # UTC
        ZoneInfo("America/New_York"),  # EST (UTC-5)
        ZoneInfo("Asia/Tokyo"),  # JST (UTC+9)
    ],
)
def test_utc_true_always_outputs_utc_regardless_of_local_timezone(monkeypatch, local_timezone):
    """Verify utc=True always outputs UTC timestamps with 'Z' suffix regardless of local timezone."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [
        {
            "key": "test123",
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640998800,  # 2022-01-01 01:00:00 UTC
            "ds": "Test record #test",
            "_running": False,
        }
    ]

    # Mock datetime.now() with the specified local timezone
    mock_dt = datetime(2022, 1, 1, 12, 0, 0, tzinfo=local_timezone)
    monkeypatch.setattr(
        "better_timetagger_cli.lib.csv.datetime",
        type(
            "MockDatetime",
            (),
            {
                "fromtimestamp": lambda ts, tz: datetime.fromtimestamp(ts, tz=tz),
                "now": lambda: mock_dt,
            },
        ),
    )

    result = records_to_csv(records, utc=True)
    lines = result.split("\n")

    # Should always output UTC timestamps with 'Z' suffix regardless of local timezone
    assert "2022-01-01T00:00:00Z" in lines[1]
    assert "2022-01-01T01:00:00Z" in lines[1]


@pytest.mark.parametrize(
    "timezone_name,expected_start,expected_stop",
    [
        ("America/New_York", "2021-12-31T19:00:00-05:00", "2021-12-31T20:00:00-05:00"),  # EST (UTC-5)
        ("Asia/Tokyo", "2022-01-01T09:00:00+09:00", "2022-01-01T10:00:00+09:00"),  # JST (UTC+9)
        ("Europe/Paris", "2022-01-01T01:00:00+01:00", "2022-01-01T02:00:00+01:00"),  # CET (UTC+1)
    ],
)
def test_utc_false_outputs_local_timezone(monkeypatch, timezone_name, expected_start, expected_stop):
    """Verify utc=False outputs timestamps in the specified local timezone."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [
        {
            "key": "test123",
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640998800,  # 2022-01-01 01:00:00 UTC
            "ds": "Test record #test",
            "_running": False,
        }
    ]

    # Mock datetime.now() to return the specified timezone
    tz = ZoneInfo(timezone_name)
    mock_dt = datetime(2022, 1, 1, 12, 0, 0, tzinfo=tz)

    # Create a mock that properly handles the .astimezone() call
    class MockNowResult:
        def astimezone(self):
            return mock_dt

    class MockDatetime:
        @staticmethod
        def fromtimestamp(ts, tz):
            return datetime.fromtimestamp(ts, tz=tz)

        @staticmethod
        def now():
            return MockNowResult()

    monkeypatch.setattr("better_timetagger_cli.lib.csv.datetime", MockDatetime)

    result = records_to_csv(records, utc=False)
    lines = result.split("\n")

    assert expected_start in lines[1]
    assert expected_stop in lines[1]


def test_utc_false_different_outputs_across_timezones(monkeypatch):
    """Verify utc=False produces different outputs for different local timezones."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [
        {
            "key": "test123",
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640998800,  # 2022-01-01 01:00:00 UTC
            "ds": "Test record #test",
            "_running": False,
        }
    ]

    # Get result in EST
    est_tz = ZoneInfo("America/New_York")
    mock_dt_est = datetime(2022, 1, 1, 12, 0, 0, tzinfo=est_tz)

    class MockNowResultEST:
        def astimezone(self):
            return mock_dt_est

    class MockDatetimeEST:
        @staticmethod
        def fromtimestamp(ts, tz):
            return datetime.fromtimestamp(ts, tz=tz)

        @staticmethod
        def now():
            return MockNowResultEST()

    monkeypatch.setattr("better_timetagger_cli.lib.csv.datetime", MockDatetimeEST)
    result_est = records_to_csv(records, utc=False)

    # Get result in JST
    jst_tz = ZoneInfo("Asia/Tokyo")
    mock_dt_jst = datetime(2022, 1, 1, 12, 0, 0, tzinfo=jst_tz)

    class MockNowResultJST:
        def astimezone(self):
            return mock_dt_jst

    class MockDatetimeJST:
        @staticmethod
        def fromtimestamp(ts, tz):
            return datetime.fromtimestamp(ts, tz=tz)

        @staticmethod
        def now():
            return MockNowResultJST()

    monkeypatch.setattr("better_timetagger_cli.lib.csv.datetime", MockDatetimeJST)
    result_jst = records_to_csv(records, utc=False)

    # Get result in CET
    cet_tz = ZoneInfo("Europe/Paris")
    mock_dt_cet = datetime(2022, 1, 1, 12, 0, 0, tzinfo=cet_tz)

    class MockNowResultCET:
        def astimezone(self):
            return mock_dt_cet

    class MockDatetimeCET:
        @staticmethod
        def fromtimestamp(ts, tz):
            return datetime.fromtimestamp(ts, tz=tz)

        @staticmethod
        def now():
            return MockNowResultCET()

    monkeypatch.setattr("better_timetagger_cli.lib.csv.datetime", MockDatetimeCET)
    result_cet = records_to_csv(records, utc=False)

    # All results should be different when utc=False
    assert result_est != result_jst
    assert result_jst != result_cet
    assert result_est != result_cet


def test_utc_parameter_defaults_to_false(monkeypatch):
    """Verify that utc parameter defaults to False (local time)."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [
        {
            "key": "test123",
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "Test record #test",
            "_running": False,
        }
    ]

    # Mock a non-UTC timezone
    mock_dt = datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    monkeypatch.setattr(
        "better_timetagger_cli.lib.csv.datetime",
        type(
            "MockDatetime",
            (),
            {
                "fromtimestamp": lambda ts, tz: datetime.fromtimestamp(ts, tz=tz),
                "now": lambda: mock_dt,
            },
        ),
    )

    # Call without utc parameter
    result_default = records_to_csv(records)
    # Call with utc=False explicitly
    result_false = records_to_csv(records, utc=False)

    # Both should produce the same output
    assert result_default == result_false


def test_utc_false_handles_running_records_correctly(monkeypatch):
    """Verify utc=False handles running records (empty stop time) correctly."""
    monkeypatch.setattr("sys.platform", "linux")

    records = [
        {
            "key": "running123",
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640995200,
            "ds": "Running task #task",
            "_running": True,
        }
    ]

    # Mock JST timezone
    jst_tz = ZoneInfo("Asia/Tokyo")
    mock_dt_jst = datetime(2022, 1, 1, 12, 0, 0, tzinfo=jst_tz)

    # Create a mock that properly handles the .astimezone() call
    class MockNowResult:
        def astimezone(self):
            return mock_dt_jst

    class MockDatetime:
        @staticmethod
        def fromtimestamp(ts, tz):
            return datetime.fromtimestamp(ts, tz=tz)

        @staticmethod
        def now():
            return MockNowResult()

    monkeypatch.setattr("better_timetagger_cli.lib.csv.datetime", MockDatetime)

    result = records_to_csv(records, utc=False)
    lines = result.split("\n")

    # Start time should be in JST
    assert "2022-01-01T09:00:00+09:00" in lines[1]
    # Stop time should be empty for running records
    fields = lines[1].split("\t")
    assert fields[2] == ""  # stop field should be empty
