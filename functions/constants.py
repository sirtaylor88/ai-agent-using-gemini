"""Common constants and enums."""

from enum import Enum

MAX_CHARS = 10000


class ErrorSuffixes(Enum):
    """Common error suffixes."""

    OUTSIDE_WORKING_DIR = "as it is outside the permitted working directory"
