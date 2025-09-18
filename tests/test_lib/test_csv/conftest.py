from typing import Any

import pytest


@pytest.fixture
def completed_records() -> list[dict[str, Any]]:
    """Provide completed records for testing."""
    return [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640998800,  # 2022-01-01 01:00:00 UTC
            "ds": "Working on #project #backend",
            "_running": False,
            "_duration": 3600,  # 1 hour
        },
        {
            "key": "def456",
            "mt": 1641001200,
            "t1": 1641001200,  # 2022-01-01 01:40:00 UTC
            "t2": 1641004800,  # 2022-01-01 02:40:00 UTC
            "ds": "Meeting with #team",
            "_running": False,
            "_duration": 3600,  # 1 hour
        },
    ]


@pytest.fixture
def running_records() -> list[dict[str, Any]]:
    """Provide running records for testing."""
    return [
        {
            "key": "ghi789",
            "mt": 1640995200,
            "t1": 1640995200,  # 2022-01-01 00:00:00 UTC
            "t2": 1640995200,  # identical to t1 since it's running
            "ds": "Currently working on #task",
            "_running": True,
            "_duration": 5400,
        },
    ]


@pytest.fixture
def sample_records(completed_records, running_records) -> list[dict[str, Any]]:
    """A sample of records including both completed and running."""
    return [*completed_records, *running_records]


@pytest.fixture
def csv_with_tab_separator() -> list[str]:
    """Provide CSV data with tab separator."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\tproject backend\tWorking on #project #backend",
        "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\tteam\tMeeting with #team",
    ]


@pytest.fixture
def csv_with_comma_separator() -> list[str]:
    """Provide CSV data with comma separator."""
    return [
        "key,start,stop,tags,description",
        "abc123,2022-01-01T00:00:00Z,2022-01-01T01:00:00Z,project backend,Working on #project #backend",
        "def456,2022-01-01T01:40:00Z,2022-01-01T02:40:00Z,team,Meeting with #team",
    ]


@pytest.fixture
def csv_with_semicolon_separator() -> list[str]:
    """Provide CSV data with semicolon separator."""
    return [
        "key;start;stop;tags;description",
        "abc123;2022-01-01T00:00:00Z;2022-01-01T01:00:00Z;project backend;Working on #project #backend",
        "def456;2022-01-01T01:40:00Z;2022-01-01T02:40:00Z;team;Meeting with #team",
    ]


@pytest.fixture
def csv_with_running_record() -> list[str]:
    """Provide CSV data with a running record (empty stop time)."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "ghi789\t2022-01-01T00:00:00Z\t\ttask\tCurrently working on #task",
    ]


@pytest.fixture
def csv_with_mixed_records() -> list[str]:
    """Provide CSV data with both completed and running records."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\tproject backend\tWorking on #project #backend",
        "ghi789\t2022-01-01T02:00:00Z\t\ttask\tCurrently working on #task",
        "def456\t2022-01-01T01:40:00Z\t2022-01-01T02:40:00Z\tteam\tMeeting with #team",
    ]


@pytest.fixture
def csv_with_extra_columns() -> list[str]:
    """Provide CSV data with extra columns beyond required ones."""
    return [
        "key\tstart\tstop\ttags\tdescription\textra_field",
        "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\tproject backend\tWorking on #project #backend\textra_data",
    ]


@pytest.fixture
def csv_with_whitespace() -> list[str]:
    """Provide CSV data with extra whitespace that should be stripped."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "  abc123  \t  2022-01-01T00:00:00Z  \t  2022-01-01T01:00:00Z  \t  project backend  \t  Working on #project #backend  ",
    ]


@pytest.fixture
def malformed_csv_missing_header() -> list[str]:
    """Provide CSV data missing required header fields."""
    return [
        "key\tstart\ttags\tdescription",  # Missing 'stop' column
        "abc123\t2022-01-01T00:00:00Z\tproject\tWorking on project",
    ]


@pytest.fixture
def malformed_csv_wrong_column_count() -> list[str]:
    """Provide CSV data with inconsistent column count."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "abc123\t2022-01-01T00:00:00Z\t2022-01-01T01:00:00Z\tproject",  # Missing description
    ]


@pytest.fixture
def malformed_csv_invalid_date() -> list[str]:
    """Provide CSV data with invalid date format."""
    return [
        "key\tstart\tstop\ttags\tdescription",
        "abc123\tinvalid-date\t2022-01-01T01:00:00Z\tproject\tWorking on project",
    ]


@pytest.fixture
def empty_csv() -> list[str]:
    """Provide CSV data with only headers."""
    return [
        "key\tstart\tstop\ttags\tdescription",
    ]


@pytest.fixture
def mock_now(monkeypatch):
    """Mock the current timestamp to a fixed value."""
    mock_now = 1641000000
    monkeypatch.setattr("better_timetagger_cli.lib.csv.now_timestamp", lambda: mock_now)
    return mock_now
