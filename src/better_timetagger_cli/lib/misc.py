"""
# Miscellaneous utilities.
"""

from time import time


def now_timestamp() -> int:
    """
    Get the current time as epoch timestamp.

    Returns:
        The current timestamp as an integer.
    """

    return int(time())


def round_timestamp(timestamp: int | float, round_to: int) -> int:
    """
    Round a timestamp to a specific interval.

    Args:
        timestamp: The timestamp to round.
        round_to: Rounding interval in minutes.

    Returns:
        The rounded timestamp as an integer.
    """
    round_to_seconds = round_to * 60
    return round(timestamp / round_to_seconds) * round_to_seconds
