from user import login, logout, fetch_user_detail
from booking import book_court, find_court, get_court_schedule, pay_court


def main():

    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print("\n_____BOOKING ATTEMPT_____")

    fetch_user_detail(session, "credit_balance")  # balance before booking

    schedule = get_court_schedule(session, "bond_crescent")

    booking_info = find_court(schedule)

    while booking_info is not None:
        user_id, booking_id = book_court(session, booking_info)
        pay_court(session, user_id, booking_id)

    print("\nno available courts found")

    print("\n_____BOOKING COMPLETED_____")
    fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
