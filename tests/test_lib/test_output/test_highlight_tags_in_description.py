"""Tests for the highlight_tags_in_description function."""

from better_timetagger_cli.lib.output import highlight_tags_in_description


def test_highlight_single_tag():
    """Wrap a single tag in markup."""
    result = highlight_tags_in_description("Working on #project")
    assert result == "Working on [underline]#project[/underline]"


def test_highlight_multiple_tags():
    """Wrap multiple tags in markup."""
    result = highlight_tags_in_description("Working on #project #feature")
    assert result == "Working on [underline]#project[/underline] [underline]#feature[/underline]"


def test_highlight_tags_with_custom_style():
    """Use custom style for tags."""
    result = highlight_tags_in_description("Working on #project", style="bold")
    assert result == "Working on [bold]#project[/bold]"


def test_no_tags():
    """Return unchanged string when no tags present."""
    result = highlight_tags_in_description("Working on something")
    assert result == "Working on something"


def test_remove_backslashes():
    """Remove backslashes from description."""
    result = highlight_tags_in_description("Working\\on #project")
    assert result == "Workingon [underline]#project[/underline]"


def test_tag_at_start():
    """Handle tag at the beginning of description."""
    result = highlight_tags_in_description("#project work")
    assert result == "[underline]#project[/underline] work"


def test_tag_at_end():
    """Handle tag at the end of description."""
    result = highlight_tags_in_description("Working on #project")
    assert result == "Working on [underline]#project[/underline]"


def test_tags_with_numbers():
    """Handle tags containing numbers."""
    result = highlight_tags_in_description("Task #bug123 fixed")
    assert result == "Task [underline]#bug123[/underline] fixed"


def test_tags_with_underscores_and_hyphens():
    """Handle tags with underscores and hyphens."""
    result = highlight_tags_in_description("Working on #project-name and #other_tag")
    assert result == "Working on [underline]#project-name[/underline] and [underline]#other_tag[/underline]"


def test_empty_string():
    """Handle empty string."""
    result = highlight_tags_in_description("")
    assert result == ""
