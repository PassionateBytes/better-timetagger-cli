"""Tests for record processing and analysis functions."""

from better_timetagger_cli.lib.records import (
    check_record_tags_match,
    create_record_key,
    get_tags_from_description,
)
from better_timetagger_cli.lib.types import Record


def test_create_record_key_returns_string():
    """Return a string value."""
    result = create_record_key()

    assert isinstance(result, str)


def test_create_record_key_default_length():
    """Return string with default length of 8 characters."""
    result = create_record_key()

    assert len(result) == 8


def test_create_record_key_custom_length():
    """Return string with custom length."""
    result = create_record_key(length=12)

    assert len(result) == 12


def test_create_record_key_uses_valid_characters():
    """Return string containing only valid alphanumeric characters."""
    result = create_record_key()

    valid_chars = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    assert all(char in valid_chars for char in result)


def test_create_record_key_generates_unique_values():
    """Generate different values on successive calls."""
    keys = [create_record_key() for _ in range(100)]

    # All keys should be unique
    assert len(keys) == len(set(keys))


def test_check_record_tags_match_with_no_tags():
    """Return True when no tags are provided."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, None, "any")

    assert result is True


def test_check_record_tags_match_any_with_one_match():
    """Return True when 'any' mode and one tag matches."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, ["#work", "#meeting"], "any")

    assert result is True


def test_check_record_tags_match_any_with_no_match():
    """Return False when 'any' mode and no tags match."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, ["#meeting", "#personal"], "any")

    assert result is False


def test_check_record_tags_match_all_with_all_matching():
    """Return True when 'all' mode and all tags match."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, ["#work", "#project"], "all")

    assert result is True


def test_check_record_tags_match_all_with_partial_match():
    """Return False when 'all' mode and only some tags match."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, ["#work", "#meeting"], "all")

    assert result is False


def test_check_record_tags_match_all_with_no_match():
    """Return False when 'all' mode and no tags match."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    result = check_record_tags_match(record, ["#meeting", "#personal"], "all")

    assert result is False


def test_get_tags_from_description_with_multiple_tags():
    """Extract multiple tags from description."""
    description = "#work #project documentation for #client"

    result = get_tags_from_description(description)

    assert result == ["#work", "#project", "#client"]


def test_get_tags_from_description_with_no_tags():
    """Return empty list when no tags present."""
    description = "just some regular text without tags"

    result = get_tags_from_description(description)

    assert result == []


def test_get_tags_from_description_with_empty_string():
    """Return empty list for empty string."""
    result = get_tags_from_description("")

    assert result == []


def test_get_tags_from_description_with_single_tag():
    """Extract single tag from description."""
    description = "Working on #documentation today"

    result = get_tags_from_description(description)

    assert result == ["#documentation"]


def test_get_tags_from_description_with_special_characters():
    """Extract tags containing numbers and underscores."""
    description = "#project_123 #work-2024 #test_case"

    result = get_tags_from_description(description)

    assert result == ["#project_123", "#work-2024", "#test_case"]
