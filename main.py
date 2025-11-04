import time

from app.user import login, logout, fetch_user_detail
from app.booking import book_court, find_court, get_court_schedule, pay_court


def main():

    print("automated court booker !")

    start_time = time.perf_counter()
    print("\n_____LOGIN ATTEMPT_____")
    session = login()
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\n[LOGIN] {duration:.6f} seconds")

    print("\n_____BOOKING ATTEMPT_____")
    fetch_user_detail(session, "credit_balance")  # balance before booking

    start_time = time.perf_counter()
    schedule = get_court_schedule(session, "bond_crescent")
    booking_info = find_court(schedule)

    while booking_info is not None:
        try:
            user_id, booking_id = book_court(session, booking_info)
            pay_court(session, user_id, booking_id)
            schedule = get_court_schedule(session, "bond_crescent")
            booking_info = find_court(schedule)
        except Exception as e:
            print(f"Error: {e}")
            break
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\n[BOOKING] {duration:.6f} seconds")

    print("\n_____BOOKING COMPLETED_____")
    fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
