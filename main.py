# Local Application Imports
from app.booking import book_all_available, find_court, get_court_schedule
from app.scheduler import fetch_criteria, is_near_target
from app.user import create_session, login, logout


def main():
    print("========== AUTOMATED COURT BOOKER ==========\n")
    criteria = fetch_criteria()

    if criteria is not None:
        public_session = create_session()
        public_schedule = get_court_schedule(public_session, criteria)
        booking_info = find_court(public_schedule, criteria.date, criteria.price)

        if booking_info is None:
            print("================= FINISH =================")
            return

        session = login()

        if not is_near_target():
            logout(session)
            print("================== FINISH ==================")
            return

        book_all_available(session, criteria, booking_info)

        logout(session)

    print("================= FINISH =================")
    return


if __name__ == "__main__":
    main()
