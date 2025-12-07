import time
from datetime import datetime, timedelta

from app.user import login, logout, fetch_user_detail
from app.booking import book_court, find_court, get_court_schedule, pay_court
from config_loader import load_config


def main():

    print("@@@@@@@@@@@@@@@@@@@@@ PRE RUN @@@@@@@@@@@@@@@@@@@@")
    config = load_config()
    day = (datetime.now() + timedelta(weeks=3)).strftime("%A").lower()
    date = (datetime.now() + timedelta(weeks=3)).date()

    print(date)  # temp
    print(day)  # temp

    schedule = config["schedule"].get(day)
    print(schedule)  # temp

    if schedule:
        user_start_time = schedule.get("start")
        user_end_time = schedule.get("end")

        if user_start_time is None:
            user_start_time = "06:00"

        if user_end_time is None:
            user_end_time = "23:00"

        print(user_start_time)  # temp
        print(user_end_time)  # temp

    location = config["locations"][0]
    print(location)

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

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
    schedule = get_court_schedule(
        session, location, date, user_start_time, user_end_time
    )
    booking_info = find_court(schedule, date)

    print(booking_info)

    # while booking_info is not None:
    #     try:
    #         user_id, booking_id = book_court(session, booking_info)
    #         pay_court(session, user_id, booking_id)
    #         schedule = get_court_schedule(session, location, date, user_start_time, user_end_time)
    #         booking_info = find_court(schedule, date)
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         break

    # end_time = time.perf_counter()
    # duration = end_time - start_time
    # print(f"\n[BOOKING] {duration:.6f} seconds")

    # print("\n_____BOOKING COMPLETED_____")
    # fetch_user_detail(session, "credit_balance")  # balance after booking

    print("\n_____LOGOUT ATTEMPT_____")
    logout(session)


if __name__ == "__main__":
    main()
