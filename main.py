# Standard Library
import os
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from app.booking import book_court, find_court, get_court_schedule, pay_court
from app.user import fetch_user_detail, login, logout
from app.utils import wait_until



# temp
import requests


def main():

    

    print("automated court booker !")
    # temp placement of new pre-fetch. TODO: tidy main file.
    public_session = requests.Session()
    public_schedule = get_court_schedule(
        public_session, user_location, date, user_start_time, user_end_time
    )
    print(
        f"[DEBUG] public fetch reached here at {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}"
    )
    # temp end

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print(
        f"[DEBUG] login reached here at {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}"
    )

    print("\n_____BOOKING ATTEMPT_____")
    # Future version: consider removing - it is extra overhead
    fetch_user_detail(session, "credit_balance")  # balance before booking

    wait_until()

    print(
        f"[DEBUG] booking reached here at {datetime.now(ZoneInfo('Pacific/Auckland')).isoformat()}"
    )

    # schedule = get_court_schedule(
    #     session, user_location, date, user_start_time, user_end_time
    # )
    booking_info = find_court(
        public_schedule, date, price
    )  # TODO: move this before midnight

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
    # Future version: consider removing - it is extra overhead
    fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        print("Waiting 10 seconds before logout...")
        time.sleep(10)

    logout(session)
    print("Booking attempt/s completed. Exiting.")


if __name__ == "__main__":
    main()
