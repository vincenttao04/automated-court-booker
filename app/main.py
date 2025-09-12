from user import login, logout, fetch_user_detail
from booking import book_court, fetch_court_availability


def main():

    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print("\n_____BOOKING ATTEMPT_____")
    # booking_success = book_court()
    # if booking_success:
    #     print("booking is successful")
    # else:
    #     print("booking is unsuccessful")

    fetch_court_availability(session, "bond_crescent")

    fetch_user_detail(session, "credit_balance")

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
