# Standard Library
import sys

# Local Application Imports
from app.booking import find_court, get_court_schedule, book_all_available
from app.user import login, logout, create_session
from app.utils import is_near_target, fetch_criteria


def main():
    print("========== AUTOMATED COURT BOOKER ==========\n")
    criteria = fetch_criteria()

    if criteria is not None:
        public_session = create_session()
        public_schedule = get_court_schedule(public_session, criteria)
        booking_info = find_court(public_schedule, criteria.date, criteria.price)

        if booking_info is None:
            print("================= FINISH =================")
            sys.exit()

        session = login()

        if not is_near_target():
            logout(session)
            print("================== FINISH ==================")
            sys.exit()

        book_all_available(session, criteria, booking_info)

        logout(session)

    print("================= FINISH =================")


if __name__ == "__main__":
    main()
