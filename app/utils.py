# Standard Library
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass

# Local Application Imports
from config_loader import load_config

NZ_TZ = ZoneInfo("Pacific/Auckland")  # set NZ timezone
DEFAULT_START = "06:00"
DEFAULT_END = "23:00"
DEFAULT_LOCATION = "bond_crescent"
LOCATION_IDS = {
    "bond_crescent": "1",
    "corinthian_drive": "2",
}


def is_near_target() -> bool:
    # Convert string into datetime object
    target_time = "00:00:00"
    target_time = datetime.strptime(target_time, "%H:%M:%S").time()
    now = datetime.now(NZ_TZ)

    # Combine current date with target time
    run_at = datetime.combine(
        now.date(),
        target_time,
        tzinfo=NZ_TZ,
    )

    # If the target time has already passed today, schedule for tomorrow
    if run_at <= now:
        run_at += timedelta(days=1)

    wait_time = run_at - now
    return wait_until_target(wait_time)


def wait_until_target(wait_time: timedelta) -> None:
    # If the wait time is more than 61 seconds, exit
    if wait_time > timedelta(seconds=61):
        print(f"⚠ wait time exceeds 61 seconds\n")
        return False

    print("time until project runs: ", str(wait_time))
    time.sleep(wait_time.total_seconds())  # sleep until the target time

    print(f"app starting at: {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}\n")
    return True


@dataclass
class BookingCriteria:
    date: str
    start_time: str
    end_time: str
    location_id: str
    location_name: str
    price: int


def fetch_criteria() -> BookingCriteria | None:
    config = load_config()

    # Fetch user's booking preferences, add 1 day buffer
    now = datetime.now(NZ_TZ)
    day = (now + timedelta(weeks=3, days=1)).strftime("%A").lower()  # e.g. 'monday'
    date = (now + timedelta(weeks=3, days=1)).date().isoformat()  # e.g. '2024-07-15'

    day_schedule = config["schedule"].get(
        day
    )  # e.g. {'start': '18:00', 'end': '20:00'}
    if not day_schedule:
        print(f"no booking scheduled for {day}")
        return None

    return BookingCriteria(
        date=date,
        start_time=day_schedule.get("start", DEFAULT_START),
        end_time=day_schedule.get("end", DEFAULT_END),
        location_id=LOCATION_IDS[day_schedule.get("location", DEFAULT_LOCATION)],
        location_name=(
            "bond_crescent"
            if day_schedule.get("location", DEFAULT_LOCATION) == "bond_crescent"
            else "corinthian_drive"
        ),
        price=config["price_per_court"] or 27,
    )
