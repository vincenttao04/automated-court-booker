from user import login, logout, fetch_user_detail
from booking import (
    book_court,
    get_court_schedule,
    find_court,
)


def main():

    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    session = login()

    print("\n_____BOOKING ATTEMPT_____")

    fetch_user_detail(session, "credit_balance")

    data = get_court_schedule(session, "bond_crescent")
    find_court(data)

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
