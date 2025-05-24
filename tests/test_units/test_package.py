import importlib
import importlib.metadata
import subprocess
import sys

import better_timetagger_cli


def test_package_version() -> None:
    """Package metadata matches ___version__."""
    assert better_timetagger_cli.__version__ == importlib.metadata.version("better-timetagger-cli")


def test_package_entrypoint() -> None:
    """Test that __main__ executes the CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "better_timetagger_cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.output
    assert "Options:" in result.output
    assert "Commands:" in result.output
    assert "-h, --help" in result.output
    assert "--version" in result.output
