"""Tests for record processing and analysis functions."""

from datetime import datetime

from better_timetagger_cli.lib.records import (
    check_record_tags_match,
    create_record_key,
    get_tag_stats,
    get_tags_from_description,
    get_total_time,
    merge_by_key,
    post_process_records,
    round_records,
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


def test_merge_by_key_updates_existing_records():
    """Replace existing records with updated versions."""
    original: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#work original",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#meeting original",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        },
    ]

    updated: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640999000,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#work updated",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    result = merge_by_key(updated, original)

    assert len(result) == 2
    assert result[0]["key"] == "abc123"
    assert result[0]["ds"] == "#work updated"
    assert result[1]["key"] == "def456"
    assert result[1]["ds"] == "#meeting original"


def test_merge_by_key_adds_new_records():
    """Add new records that weren't in original list."""
    original: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    updated: list[Record] = [
        {
            "key": "xyz999",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#new",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    result = merge_by_key(updated, original)

    assert len(result) == 2
    assert result[0]["key"] == "abc123"
    assert result[1]["key"] == "xyz999"


def test_merge_by_key_with_empty_updates():
    """Return original records when no updates provided."""
    original: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    result = merge_by_key([], original)

    assert len(result) == 1
    assert result[0]["key"] == "abc123"


def test_merge_by_key_with_empty_original():
    """Return updated records when original is empty."""
    updated: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    result = merge_by_key(updated, [])

    assert len(result) == 1
    assert result[0]["key"] == "abc123"


def test_merge_by_key_preserves_order():
    """Preserve order of original list with updates appended."""
    original: list[Record] = [
        {
            "key": "first",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#1",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        },
        {
            "key": "second",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#2",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        },
    ]

    updated: list[Record] = [
        {
            "key": "third",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640998800,
            "ds": "#3",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 3600,
        }
    ]

    result = merge_by_key(updated, original)

    assert result[0]["key"] == "first"
    assert result[1]["key"] == "second"
    assert result[2]["key"] == "third"


def test_post_process_records_sorts_by_t2():
    """Sort records by t2 in descending order by default."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records)

    assert len(result) == 2
    assert result[0]["key"] == "def456"  # Higher t2 first
    assert result[1]["key"] == "abc123"


def test_post_process_records_filters_by_tags_any():
    """Filter records by tags using 'any' mode."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work #project",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records, tags=["#work"], tags_match="any")

    assert len(result) == 1
    assert result[0]["key"] == "abc123"


def test_post_process_records_filters_by_tags_all():
    """Filter records by tags using 'all' mode."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work #project",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records, tags=["#work", "#project"], tags_match="all")

    assert len(result) == 1
    assert result[0]["key"] == "abc123"


def test_post_process_records_excludes_hidden_by_default():
    """Exclude hidden records by default."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "HIDDEN #work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records)

    assert len(result) == 1
    assert result[0]["key"] == "abc123"


def test_post_process_records_includes_hidden_when_requested():
    """Include hidden records when hidden=True."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "HIDDEN #work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records, hidden=True)

    assert len(result) == 1
    assert result[0]["key"] == "def456"


def test_post_process_records_filters_running_records():
    """Filter to show only running records."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995300,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995200,  # Running: t1 == t2
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        },
    ]

    result = post_process_records(records, running=True)

    assert len(result) == 1
    assert result[0]["key"] == "def456"


def test_post_process_records_computes_running_and_duration():
    """Compute _running and _duration fields."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 0,
        }
    ]

    result = post_process_records(records)

    assert result[0]["_running"] is False
    assert result[0]["_duration"] == 600  # 10 minutes


def test_round_records_rounds_timestamps():
    """Round record timestamps to specified interval."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995320,  # 00:02:00
            "t2": 1640995920,  # 00:12:00
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,  # 10 minutes
        }
    ]

    result = round_records(records, round_to=5)

    assert result[0]["t1"] == 1640995200  # Rounded to 00:00:00
    assert result[0]["t2"] == 1640995800  # t1 + rounded duration (10 min)
    assert result[0]["_duration"] == 600  # Duration rounded to 10 minutes


def test_round_records_preserves_duration_logic():
    """Round duration separately then apply to rounded start time."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995260,  # 00:01:00
            "t2": 1640995560,  # 00:06:00
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,  # 5 minutes
        }
    ]

    result = round_records(records, round_to=15)

    assert result[0]["t1"] == 1640995200  # Rounded to 00:00:00
    assert result[0]["t2"] == 1640995200  # t1 + 0 (duration rounds to 0)
    assert result[0]["_duration"] == 0  # 5 min rounds to 0 with 15-min interval


def test_round_records_with_multiple_records():
    """Round multiple records independently."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995920,
            "t2": 1640996820,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 900,
        },
    ]

    result = round_records(records, round_to=5)

    assert len(result) == 2
    assert result[0]["t1"] == 1640995200
    assert result[0]["_duration"] == 600
    assert result[1]["t1"] == 1640995800  # Rounded from 1640995920
    assert result[1]["_duration"] == 900


def test_round_records_preserves_other_fields():
    """Preserve all fields except t1, t2, and _duration."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995320,
            "t2": 1640995920,
            "ds": "#work #project",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    result = round_records(records, round_to=5)

    assert result[0]["key"] == "abc123"
    assert result[0]["mt"] == 1640995200
    assert result[0]["ds"] == "#work #project"
    assert result[0]["st"] == 1640995200.0
    assert result[0]["_running"] is False


def test_get_total_time_calculates_duration_in_range():
    """Calculate total time for records within time range."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,  # 00:00:00
            "t2": 1640995800,  # 00:10:00
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    total = get_total_time(records, start=1640995200, end=1640996000)

    assert total == 600  # 10 minutes


def test_get_total_time_with_partial_overlap():
    """Calculate time only for overlapping portion."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,  # 00:00:00
            "t2": 1640995800,  # 00:10:00
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    # Range only covers first 5 minutes
    total = get_total_time(records, start=1640995200, end=1640995500)

    assert total == 300  # 5 minutes


def test_get_total_time_with_datetime_inputs():
    """Accept datetime objects as start and end."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    start = datetime.fromtimestamp(1640995200)
    end = datetime.fromtimestamp(1640996000)

    total = get_total_time(records, start=start, end=end)

    assert total == 600


def test_get_total_time_with_multiple_records():
    """Sum time across multiple records."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996100,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    total = get_total_time(records, start=1640995200, end=1640996200)

    assert total == 900  # 15 minutes total


def test_get_total_time_excludes_records_outside_range():
    """Exclude records that don't overlap with range."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640996000,  # Starts after range ends
            "t2": 1640996300,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    # Range ends before second record starts
    total = get_total_time(records, start=1640995200, end=1640996000)

    assert total == 600  # Only first record


def test_get_tag_stats_counts_occurrences_and_duration():
    """Calculate occurrence count and total duration for each tag."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work #project",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996100,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    stats = get_tag_stats(records)

    assert stats["#work"] == (2, 900)  # 2 occurrences, 900 seconds total
    assert stats["#project"] == (1, 600)  # 1 occurrence, 600 seconds


def test_get_tag_stats_sorts_by_duration():
    """Return tags sorted by total duration in descending order."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "#low-priority",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996400,
            "ds": "#high-priority",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
    ]

    stats = get_tag_stats(records)

    keys = list(stats.keys())
    assert keys[0] == "#high-priority"  # Higher duration first
    assert keys[1] == "#low-priority"


def test_get_tag_stats_with_no_tags():
    """Return empty dict when no tags present."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "no tags here",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    stats = get_tag_stats(records)

    assert stats == {}


def test_get_tag_stats_with_empty_records():
    """Return empty dict for empty record list."""
    stats = get_tag_stats([])

    assert stats == {}


def test_get_tag_stats_aggregates_same_tag():
    """Aggregate stats for same tag across multiple records."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995500,
            "ds": "#work meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995500,
            "t2": 1640995800,
            "ds": "#work coding",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
        {
            "key": "ghi789",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996400,
            "ds": "#work review",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
    ]

    stats = get_tag_stats(records)

    assert stats["#work"] == (3, 1200)  # 3 occurrences, 1200 seconds total
