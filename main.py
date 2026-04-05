# Standard Library
import sys

# Local Application Imports
from app.booking import find_court, get_court_schedule, book_all_available
from app.user import fetch_user_detail, login, logout, create_session
from app.utils import is_near_target, fetch_criteria


def main():
    print("========== AUTOMATED COURT BOOKER ==========\n")
    criteria = fetch_criteria()

    if criteria is not None:
        public_session = create_session()
        public_schedule = get_court_schedule(public_session, criteria)
        booking_info = find_court(public_schedule, criteria.date, criteria.price)

        if booking_info is None:
            print("\npre-fetch: no available courts found")
            print("================= FINISH =================\n")
            sys.exit()

        session = login()
        fetch_user_detail(session, "credit_balance")

        if not is_near_target():
            logout(session)
            print("================== FINISH ==================\n")
            sys.exit()

        book_all_available(session, criteria, booking_info)

        fetch_user_detail(session, "credit_balance")

        logout(session)

    print("================= FINISH =================\n")


if __name__ == "__main__":
    main()
