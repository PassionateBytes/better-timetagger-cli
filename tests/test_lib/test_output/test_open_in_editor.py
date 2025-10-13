"""Tests for the open_in_editor function."""

import pytest

from better_timetagger_cli.lib.output import open_in_editor


# Fixtures
@pytest.fixture
def mock_subprocess_call(monkeypatch):
    """Mock subprocess.call to track calls without executing."""
    calls = []

    def mock_call(args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return 0

    monkeypatch.setattr("subprocess.call", mock_call)
    return calls


@pytest.fixture
def mock_stderr(monkeypatch):
    """Mock stderr.print to capture output."""
    messages = []

    def mock_print(msg, *args, **kwargs):
        messages.append({"msg": msg, "style": kwargs.get("style")})

    monkeypatch.setattr("better_timetagger_cli.lib.output.stderr.print", mock_print)
    return messages


@pytest.fixture
def mock_platform(monkeypatch):
    """Return a function to mock sys.platform."""

    def set_platform(platform: str):
        monkeypatch.setattr("sys.platform", platform)

    return set_platform


# Tests for explicit editor
def test_open_with_explicit_editor(mock_subprocess_call):
    """Use the specified editor when provided."""
    open_in_editor("/path/to/file.txt", editor="vim")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("vim", "/path/to/file.txt")
    assert mock_subprocess_call[0]["kwargs"] == {}


def test_open_with_explicit_editor_full_path(mock_subprocess_call):
    """Use the specified editor with full path."""
    open_in_editor("/path/to/file.txt", editor="/usr/bin/emacs")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("/usr/bin/emacs", "/path/to/file.txt")


def test_explicit_editor_overrides_platform(mock_subprocess_call, mock_platform):
    """Explicit editor overrides platform-specific behavior."""
    for platform in ["darwin", "win32", "linux"]:
        mock_platform(platform)
        mock_subprocess_call.clear()

        open_in_editor("/path/to/file.txt", editor="nano")

        assert len(mock_subprocess_call) == 1
        assert mock_subprocess_call[0]["args"] == ("nano", "/path/to/file.txt")


# Tests for macOS
def test_open_on_macos(mock_subprocess_call, mock_platform):
    """Use 'open' command on macOS."""
    mock_platform("darwin")

    open_in_editor("/path/to/file.txt")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("open", "/path/to/file.txt")
    assert mock_subprocess_call[0]["kwargs"] == {}


def test_open_on_macos_with_spaces(mock_subprocess_call, mock_platform):
    """Handle file paths with spaces on macOS."""
    mock_platform("darwin")

    open_in_editor("/path/to/my file.txt")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("open", "/path/to/my file.txt")


# Tests for Windows
def test_open_on_windows_without_spaces(mock_subprocess_call, mock_platform):
    """Use 'start' command on Windows for paths without spaces."""
    mock_platform("win32")

    open_in_editor("C:\\path\\to\\file.txt")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("start", "C:\\path\\to\\file.txt")
    assert mock_subprocess_call[0]["kwargs"] == {"shell": True}


def test_open_on_windows_with_spaces(mock_subprocess_call, mock_platform):
    """Use 'start ""' command on Windows for paths with spaces."""
    mock_platform("win32")

    open_in_editor("C:\\path\\to\\my file.txt")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("start", "", "C:\\path\\to\\my file.txt")
    assert mock_subprocess_call[0]["kwargs"] == {"shell": True}


def test_windows_platform_variations(mock_subprocess_call, mock_platform):
    """Handle different Windows platform strings."""
    for platform in ["win32", "win64", "windows"]:
        mock_platform(platform)
        mock_subprocess_call.clear()

        open_in_editor("file.txt")

        assert len(mock_subprocess_call) == 1
        assert mock_subprocess_call[0]["args"][0] == "start"


# Tests for Linux
def test_open_on_linux_with_xdg(mock_subprocess_call, mock_platform):
    """Use xdg-open on Linux when available."""
    mock_platform("linux")

    open_in_editor("/path/to/file.txt")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("xdg-open", "/path/to/file.txt")
    assert mock_subprocess_call[0]["kwargs"] == {}


def test_open_on_linux_without_xdg(mock_subprocess_call, mock_platform, monkeypatch):
    """Fall back to EDITOR env var when xdg-open is not available."""
    mock_platform("linux")

    # Mock subprocess.call to raise FileNotFoundError for xdg-open
    def mock_call_with_error(args, **kwargs):
        mock_subprocess_call.append({"args": args, "kwargs": kwargs})
        if args[0] == "xdg-open":
            raise FileNotFoundError("xdg-open not found")
        return 0

    monkeypatch.setattr("subprocess.call", mock_call_with_error)
    monkeypatch.setenv("EDITOR", "vim")

    open_in_editor("/path/to/file.txt")

    # Should have tried xdg-open first, then vim
    assert len(mock_subprocess_call) == 2
    assert mock_subprocess_call[0]["args"] == ("xdg-open", "/path/to/file.txt")
    assert mock_subprocess_call[1]["args"] == ("vim", "/path/to/file.txt")


def test_open_on_linux_without_xdg_default_editor(mock_subprocess_call, mock_platform, monkeypatch):
    """Use nano as default when xdg-open unavailable and EDITOR not set."""
    mock_platform("linux")

    # Mock subprocess.call to raise FileNotFoundError for xdg-open
    def mock_call_with_error(args, **kwargs):
        mock_subprocess_call.append({"args": args, "kwargs": kwargs})
        if args[0] == "xdg-open":
            raise FileNotFoundError("xdg-open not found")
        return 0

    monkeypatch.setattr("subprocess.call", mock_call_with_error)
    monkeypatch.delenv("EDITOR", raising=False)

    open_in_editor("/path/to/file.txt")

    # Should have tried xdg-open first, then nano
    assert len(mock_subprocess_call) == 2
    assert mock_subprocess_call[1]["args"] == ("nano", "/path/to/file.txt")


def test_linux_platform_variations(mock_subprocess_call, mock_platform):
    """Handle different Linux platform strings."""
    for platform in ["linux", "linux2", "linux3"]:
        mock_platform(platform)
        mock_subprocess_call.clear()

        open_in_editor("file.txt")

        assert len(mock_subprocess_call) == 1
        assert mock_subprocess_call[0]["args"][0] == "xdg-open"


# Tests for unsupported platforms
def test_unsupported_platform(mock_subprocess_call, mock_platform, mock_stderr):
    """Show warning message on unsupported platforms."""
    mock_platform("freebsd")

    open_in_editor("/path/to/file.txt")

    # Should not call subprocess
    assert len(mock_subprocess_call) == 0

    # Should print warning
    assert len(mock_stderr) == 1
    assert "Unsupported platform: freebsd" in mock_stderr[0]["msg"]
    assert "Please open the file manually" in mock_stderr[0]["msg"]
    assert mock_stderr[0]["style"] == "yellow"


def test_unsupported_platform_variations(mock_subprocess_call, mock_platform, mock_stderr):
    """Handle various unsupported platforms."""
    for platform in ["aix", "sunos", "netbsd", "openbsd", "unknown"]:
        mock_platform(platform)
        mock_subprocess_call.clear()
        mock_stderr.clear()

        open_in_editor("file.txt")

        assert len(mock_subprocess_call) == 0
        assert len(mock_stderr) == 1
        assert f"Unsupported platform: {platform}" in mock_stderr[0]["msg"]


# Edge cases
def test_empty_file_path(mock_subprocess_call, mock_platform):
    """Handle empty file path."""
    mock_platform("darwin")

    open_in_editor("")

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("open", "")


def test_special_characters_in_path(mock_subprocess_call, mock_platform):
    """Handle special characters in file path."""
    mock_platform("linux")

    special_path = '/path/to/file\'s & "special" (chars).txt'
    open_in_editor(special_path)

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("xdg-open", special_path)


def test_unicode_in_path(mock_subprocess_call, mock_platform):
    """Handle Unicode characters in file path."""
    mock_platform("darwin")

    unicode_path = "/path/to/файл-文件.txt"
    open_in_editor(unicode_path)

    assert len(mock_subprocess_call) == 1
    assert mock_subprocess_call[0]["args"] == ("open", unicode_path)


# Return value tests
def test_subprocess_return_code_ignored(mock_subprocess_call, mock_platform, monkeypatch):
    """Function completes regardless of subprocess return code."""
    mock_platform("darwin")

    # Mock subprocess.call to return error code
    def mock_call_with_error(args, **kwargs):
        mock_subprocess_call.append({"args": args, "kwargs": kwargs})
        return 1  # Error code

    monkeypatch.setattr("subprocess.call", mock_call_with_error)

    # Should not raise exception
    open_in_editor("/path/to/file.txt")

    assert len(mock_subprocess_call) == 1
