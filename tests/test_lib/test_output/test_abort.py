import pytest

from better_timetagger_cli.lib.output import abort


def test_abort(capsys):
    """Exit with code 1 and print to stderr."""

    with pytest.raises(SystemExit) as exc_info:
        abort("Test error message")

    captured = capsys.readouterr()
    assert captured.err == "Test error message\n"
    assert exc_info.value.code == 1
