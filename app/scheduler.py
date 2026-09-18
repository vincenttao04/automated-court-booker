# Standard Library
from datetime import datetime, timedelta

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
    MAX_WAIT_SECONDS,
)
from app.models import BookingCriteria


# Resolve the next target time, or None if it is too far away to be worth waiting for.
# Does not sleep; the wait happens in browser.py so the booking page can be loaded first.
def resolve_target() -> datetime | None:
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

    if wait_time > timedelta(seconds=MAX_WAIT_SECONDS):
        print(f"[error] wait time exceeds {MAX_WAIT_SECONDS} seconds\n")
        return None

    print("time until target:", str(wait_time))
    return run_at


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
