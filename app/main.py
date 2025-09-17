from user import login, logout, fetch_user_detail
from booking import (
    book_court,
    fetch_court_availability,
    identify_longest_available_courts,
)


def main():

    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print("\n_____BOOKING ATTEMPT_____")

    fetch_user_detail(session, "credit_balance")

    data = fetch_court_availability(session, "bond_crescent")
    identify_longest_available_courts(data)

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
