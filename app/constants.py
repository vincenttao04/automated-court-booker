# Standard Library
from enum import StrEnum
from zoneinfo import ZoneInfo

NZ_TZ = ZoneInfo("Pacific/Auckland")  # set NZ timezone

TARGET_TIME = "00:00:00"  # HH:MM:SS, 24-hour format
WEEKS_IN_ADVANCE = 3

DEFAULT_START = "06:00"
DEFAULT_END = "23:00"


class Location(StrEnum):
    BOND_CRESCENT = "bond_crescent"
    CORINTHIAN_DRIVE = "corinthian_drive"


LOCATION_IDS = {
    Location.BOND_CRESCENT: "1",
    Location.CORINTHIAN_DRIVE: "2",
}

DEFAULT_LOCATION = Location.BOND_CRESCENT


class Priority(StrEnum):
    EARLIEST = "earliest"
    LONGEST = "longest"


DEFAULT_PRIORITY = Priority.EARLIEST
