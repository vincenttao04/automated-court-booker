from authenticate import login
from booking import book_court

def main():
    print("automated court booker !")

    print("\n_____LOGIN ATTEMPT_____")
    login_success = login()
    if login_success:
        print("login is successful")
    else: 
        print("login is unsuccessful")

    print("\n_____BOOKING ATTEMPT_____")
    booking_success = book_court()
    if booking_success:
        print("booking is successful")
    else: 
        print("booking is unsuccessful")

if __name__ == "__main__":
    main()
