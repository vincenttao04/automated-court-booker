# Standard Library
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from app.booking import book_court, find_court, get_court_schedule, pay_court
from app.user import fetch_user_detail, login, logout

from config_loader import load_config


def main():
    config = load_config()

    # Fetch user's booking preferences
    now = datetime.now(ZoneInfo("Pacific/Auckland"))
    day = (now + timedelta(weeks=3)).strftime("%A").lower()  # e.g. 'monday'
    date = (now + timedelta(weeks=3)).date().isoformat()  # e.g. '2024-07-15'

    schedule = config["schedule"].get(day)  # e.g. {'start': '18:00', 'end': '20:00'}
    if not schedule:
        print(f"No booking scheduled for {day}. Exiting.")
        return

    user_start_time = schedule.get("start") or "06:00"
    user_end_time = schedule.get("end") or "23:00"
    user_location = schedule.get("location") or config["locations"][0]

    price = config["price_per_court"]  # e.g. 27

    print("automated court booker !")
    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print(
        f"[DEBUG] reached here at {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}"
    )

    print("\n_____BOOKING ATTEMPT_____")
    fetch_user_detail(session, "credit_balance")  # balance before booking

    schedule = get_court_schedule(
        session, user_location, date, user_start_time, user_end_time
    )
    booking_info = find_court(schedule, date, price)

    while booking_info is not None:
        try:
            user_id, booking_id = book_court(session, booking_info)
            pay_court(session, user_id, booking_id)
            schedule = get_court_schedule(
                session, user_location, date, user_start_time, user_end_time
            )
            booking_info = find_court(schedule, date, price)
        except Exception as e:
            print(f"Error: {e}")
            break

    print("\n_____BOOKING COMPLETED_____")
    fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        print("Waiting 10 seconds before logout...")
        time.sleep(10)

    logout(session)
    print("Booking attempt/s completed. Exiting.")


if __name__ == "__main__":
    main()
