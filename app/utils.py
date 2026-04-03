# Standard Library
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from config_loader import load_config

NZ_TZ = ZoneInfo("Pacific/Auckland")  # set NZ timezone


def wait_until() -> None:
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

    # If the wait time is more than 61 seconds, exit
    wait_time = run_at - now
    if wait_time > timedelta(seconds=61):
        sys.exit(f"Wait time exceeds 61 seconds ({run_at}). Exiting.")

    print("[DEBUG] Time until project runs: ", str(wait_time))
    time.sleep(wait_time.total_seconds())  # sleep until the target time

    return


def fetch_preferences() -> dict:
    config = load_config()

    # Fetch user's booking preferences, add 1 day buffer
    now = datetime.now(NZ_TZ)
    day = (
        (now + timedelta(weeks=3) + timedelta(days=1)).strftime("%A").lower()
    )  # e.g. 'monday'
    date = (
        (now + timedelta(weeks=3) + timedelta(days=1)).date().isoformat()
    )  # e.g. '2024-07-15'

    schedule = config["schedule"].get(day)  # e.g. {'start': '18:00', 'end': '20:00'}
    if not schedule:
        print(f"No booking scheduled for {day}. Exiting.")
        return

    start_time = schedule.get("start") or "06:00"
    end_time = schedule.get("end") or "23:00"
    location = schedule.get("location") or config["locations"][0]

    price = config["price_per_court"]  # e.g. 27

    return {
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "location": location,
        "price": price,
    }
