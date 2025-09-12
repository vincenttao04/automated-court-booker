from user import login, logout, fetch_user_details
from booking import book_court


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

    fetch_user_details(session, "credit_balance")

    logout(session)


if __name__ == "__main__":
    main()
