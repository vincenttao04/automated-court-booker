# Standard Library
import sys
from datetime import datetime

# Local Application Imports
from app.booking import book_all_available, get_court_schedule, identify_courts
from app.scheduler import fetch_criteria, is_near_target
from app.user import create_session, login, logout


def main():
    print(
        f"{datetime.now().strftime("%a %d %B %H:%M:%S")}"
    )  # format example: Mon 03 August 19:09:29
    print("======== AUTOMATED COURT BOOKER ========\n")

    criteria = fetch_criteria()

    if criteria is not None:
        public_session = create_session()
        public_schedule = get_court_schedule(public_session, criteria)
        booking_info = identify_courts(public_schedule, criteria)

        if booking_info is None:
            print("================ FINISH ================")
            return

        session = login()

        if not is_near_target():
            logout(session)
            print("================= FINISH =================")
            return

        book_all_available(session, criteria, booking_info)

        logout(session)

    print("================ FINISH ================")
    return


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
