# Standard Library
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Local Application Imports
from app.booking import book_court, find_court, get_court_schedule, pay_court
from app.user import fetch_user_detail, login, logout, create_session
from app.utils import is_near_target, fetch_criteria


def main():
    print("========== AUTOMATED COURT BOOKER ==========\n")
    criteria = fetch_criteria()

    public_session = create_session()
    public_schedule = get_court_schedule(public_session, criteria)
    booking_info = find_court(public_schedule, criteria.date, criteria.price)

    session = login()
    fetch_user_detail(session, "credit_balance")

    if not is_near_target():
        logout(session)
        sys.exit()

    # Main booking logic
    while booking_info is not None:
        try:
            user_id, booking_id = book_court(session, booking_info)
            pay_court(session, user_id, booking_id)
            schedule = get_court_schedule(session, criteria)
            booking_info = find_court(schedule, criteria.date, criteria.price)
        except Exception as e:
            print(f"Error: {e}")
            break

    fetch_user_detail(session, "credit_balance")

    logout(session)


if __name__ == "__main__":
    main()
