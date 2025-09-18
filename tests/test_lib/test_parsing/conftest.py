from datetime import datetime

import click
import pytest


@pytest.fixture
def mock_click_context():
    """Create a mock Click context."""
    return click.Context(click.Command("test"))


@pytest.fixture
def mock_click_param():
    """Create a mock Click parameter."""
    return click.Option(["--tags"], multiple=True)


@pytest.fixture
def mock_abort(monkeypatch):
    """Mock abort function to capture error messages."""
    abort_info = {"called": False, "message": ""}

    def _mock_abort(msg):
        abort_info["called"] = True
        abort_info["message"] = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.parsing.abort", _mock_abort)
    return abort_info


@pytest.fixture
def mock_datetime_today(monkeypatch):
    """Mock datetime.today() to return a fixed date."""
    fixed_today = datetime(2024, 3, 15, 10, 30, 45)

    class MockDateTime(datetime):
        @classmethod
        def today(cls):
            return fixed_today

    monkeypatch.setattr("better_timetagger_cli.lib.parsing.datetime", MockDateTime)
    return fixed_today


@pytest.fixture
def mock_parsedatetime(monkeypatch):
    """Mock parsedatetime.Calendar for controlled testing."""

    class MockContext:
        def __init__(self, has_date=False, has_time=False):
            self.hasDate = has_date
            self.hasTime = has_time

    class MockCalendar:
        def __init__(self, version=None):
            self.parse_results = {}

        def set_result(self, input_str, parsed_time, has_date=False, has_time=False):
            self.parse_results[input_str] = (parsed_time, MockContext(has_date, has_time))

        def parse(self, input_str):
            if input_str in self.parse_results:
                return self.parse_results[input_str]
            # Default to failed parse (no date, no time)
            return (None, MockContext(False, False))

    mock_cal = MockCalendar()

    class MockParsedatetime:
        VERSION_CONTEXT_STYLE = 1  # Mock constant

        @staticmethod
        def Calendar(version=None):  # noqa: N802
            return mock_cal

    monkeypatch.setattr("better_timetagger_cli.lib.parsing.parsedatetime", MockParsedatetime)
    return mock_cal
