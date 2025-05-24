import importlib
import importlib.metadata

import better_timetagger_cli


def test_version() -> None:
    """Package metadata matches ___version__."""
    assert better_timetagger_cli.__version__ == importlib.metadata.version("better-timetagger-cli")
