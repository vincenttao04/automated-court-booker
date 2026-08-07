# Standard Library
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from app.config_loader import load_config
from app.constants import (
    DEFAULT_END,
    DEFAULT_LOCATION,
    DEFAULT_PRIORITY,
    DEFAULT_START,
    Location,
    NZ_TZ,
    Priority,
    TARGET_TIME,
    WEEKS_IN_ADVANCE,
    DAYS_IN_ADVANCE,
)
from app.models import BookingCriteria


def wait_until_target(wait_time: timedelta) -> bool:
    # If the wait time is more than 121 seconds, exit
    if wait_time > timedelta(seconds=121):
        print(f"[error] wait time exceeds 121 seconds\n")
        return False

    print("time until project runs: ", str(wait_time))
    time.sleep(wait_time.total_seconds())  # sleep until the target time

    print(
        f"app starting at: {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}\n"
    )
    return True


def is_near_target() -> bool:
    # Convert string into datetime object
    target_time = datetime.strptime(TARGET_TIME, "%H:%M:%S").time()
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


def fetch_criteria() -> BookingCriteria | None:
    config = load_config()

    schedule = config.get("schedule")
    if schedule is None:
        raise RuntimeError("LOAD CONFIG FAILED: missing 'schedule' key in config")

    # Fetch user's booking preferences, add 1 day buffer
    now = datetime.now(NZ_TZ)
    day = (
        (now + timedelta(weeks=WEEKS_IN_ADVANCE, days=DAYS_IN_ADVANCE))
        .strftime("%A")
        .lower()
    )  # e.g. 'monday'
    date = (
        (now + timedelta(weeks=WEEKS_IN_ADVANCE, days=DAYS_IN_ADVANCE))
        .date()
        .isoformat()
    )  # e.g. '2024-07-15'

    day_schedule = schedule.get(day)  # e.g. {'start': '18:00', 'end': '20:00'}
    if not day_schedule:
        print(f"no booking scheduled for {day}")
        return None

    return BookingCriteria(
        date=date,
        start_time=day_schedule.get("start", DEFAULT_START),
        end_time=day_schedule.get("end", DEFAULT_END),
        location=Location(day_schedule.get("location", DEFAULT_LOCATION)),
        priority=Priority(day_schedule.get("priority", DEFAULT_PRIORITY)),
        price=config.get("price_per_court") or 27,
    )
