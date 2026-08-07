# Standard Library
import builtins
import sys
from datetime import datetime

# Local Application Imports
from app.booking import book_all_available, get_court_schedule, identify_courts
from app.scheduler import fetch_criteria, is_near_target
from app.user import create_session, login, logout

# Helper function: override the built-in print function to include timestamps for better logging
# Useful for Windows Task Scheduler, does not auto timestamp execution output like AWS Lambda's CloudWatch Logs
_original_print = print


def _timestamped_print(*args, **kwargs):
    if args and args[0] == "":
        _original_print(
            *args, **kwargs
        )  # keep blank-line spacers clean, no timestamp clutter
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _original_print(f"[{timestamp}]", *args, **kwargs)


builtins.print = _timestamped_print


def main():
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
