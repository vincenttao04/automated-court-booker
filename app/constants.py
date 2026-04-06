# Standard Library
from zoneinfo import ZoneInfo

NZ_TZ = ZoneInfo("Pacific/Auckland")  # set NZ timezone
TARGET_TIME = "00:00:00"  # HH:MM:SS, 24-hour format
WEEKS_IN_ADVANCE = 3
DEFAULT_START = "06:00"
DEFAULT_END = "23:00"
DEFAULT_LOCATION = "bond_crescent"
LOCATION_IDS = {
    "bond_crescent": "1",
    "corinthian_drive": "2",
}
