"""Tests for the styled_padded function."""

from rich.text import Text

from better_timetagger_cli.lib.output import styled_padded


def test_value_needs_padding():
    """Pad value to specified width."""
    result = styled_padded(42, width=5)
    assert isinstance(result, Text)
    assert str(result) == "00042"


def test_value_no_padding_needed():
    """Return value without padding when it exceeds width."""
    result = styled_padded(123456, width=3)
    assert str(result) == "123456"


def test_exact_width():
    """Handle value that matches width exactly."""
    result = styled_padded(12345, width=5)
    assert str(result) == "12345"


def test_custom_padding_character():
    """Use custom padding character."""
    result = styled_padded(42, width=5, padding=" ")
    assert str(result) == "   42"


def test_string_value():
    """Handle string values."""
    result = styled_padded("test", width=8)
    assert str(result) == "0000test"


def test_default_width():
    """Use default width of 5."""
    result = styled_padded(1)
    assert str(result) == "00001"
