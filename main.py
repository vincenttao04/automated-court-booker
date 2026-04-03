# Standard Library
import os
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from app.booking import book_court, find_court, get_court_schedule, pay_court
from app.user import fetch_user_detail, login, logout, create_session
from app.utils import wait_until, fetch_criteria


def main():
    print("========== AUTOMATED COURT BOOKER ==========\n")
    criteria = fetch_criteria()

    public_session = create_session()
    public_schedule = get_court_schedule(public_session, criteria)
    booking_info = find_court(public_schedule, criteria.date, criteria.price)

    session = login()
    fetch_user_detail(session, "credit_balance")

    wait_until()

    while booking_info is not None:
        try:
            user_id, booking_id = book_court(session, booking_info)
            pay_court(session, user_id, booking_id)
            schedule = get_court_schedule(session, criteria)
            booking_info = find_court(schedule, criteria.date, criteria.price)
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
