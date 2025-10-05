from user import login, logout, fetch_user_detail
from booking import book_court, find_court, get_court_schedule, pay_court


def main():

    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print("\n_____BOOKING ATTEMPT_____")

    fetch_user_detail(session, "credit_balance")  # balance before booking

    data = get_court_schedule(session, "bond_crescent")

    data = find_court(data)

    if data is not None:
        user_id, booking_id = book_court(session, data)
        # pay_court(session, user_id, booking_id)
    else:
        print("no available courts found")

    print("\n_____BOOKING COMPLETED_____")
    fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
