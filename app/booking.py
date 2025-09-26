# Standard Library
import os
from datetime import date

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()

# booking_date = str(date.today())
booking_date = "2025-10-13"


def get_court_schedule(session: requests.Session, location: str):
    # Fetch request payload
    url = os.getenv("COURT_SCHEDULE") + booking_date

    # Make fetch court availability GET request
    response = session.get(url)
    data = response.json()

    # Check if fetch court availability was successful
    if data.get("status") != "success":
        raise Exception("FETCH COURT AVAILABILITY FAILED")

    # Extract stadium specific court availability
    if location == "corinthian_drive":
        data = data["data"].get("2").get("courts")  # corinthian drive stadium
    else:
        data = data["data"].get("1").get("courts")  # bond crescent stadium and others

    print(f"fetch court availability successful ({booking_date})")
    return data


def find_court(data: dict):
    booking_info = {
        "booking_id": "",
        "date": booking_date,
        "gst": "",
        "subtotal": "",
        "total": "",
        "user_id": "",
        # remaining values to be filled in this function
        "court_id": None,
        "court_name": "",
        "start_time": "",
        "end_time": "",
        "price": None,
    }
    best_length = 0

    for court_number, court_info in data.items():
        current_length = 0
        current_start = None

        for slot in court_info.get("timetable"):
            if slot.get("status") == "Available":
                if current_length == 0:
                    current_start = slot.get("start_time")
                current_length += 1

                if current_length > best_length:
                    booking_info.update(
                        {
                            "court_id": int(court_number),
                            "start_time": current_start,
                            "end_time": slot["end_time"],
                        }
                    )
                    best_length = current_length
            else:
                current_length = 0
                current_start = None

    booking_info["court_name"] = "Court " + str(booking_info.get("court_id"))
    booking_info["price"] = best_length * 27

    print(f"\nlongest availability: {best_length} slots/hours")
    print(
        f"court: {booking_info.get("court_id")}, starting at {booking_info.get("start_time")}, ending at {booking_info.get("end_time")}"
    )

    return booking_info


def book_court(session: requests.Session, booking_info: dict):
    # Fetch request_one payload
    url_one = os.getenv("BOOKING_URL")

    # Make booking_create POST request
    response_one = session.post(url_one, json=booking_info)
    data_one = response_one.json()

    # Check if booking_create was successful
    if data_one.get("status") != "success":
        raise Exception("BOOKING CREATE FAILED")

    print("\n")
    print(data_one)  # temp
    booking_id = str(data_one["data"].get("id"))

    #######

    # Fetch request_two payload
    url_two = os.getenv("CHECKOUT_URL") + booking_id

    # Make booking_checkout GET request
    response_two = session.get(url_two)
    data_two = response_two.json()

    # Check if booking_checkout was successful
    if data_two.get("status") != "success":
        raise Exception("BOOKING CHECKOUT FAILED")

    print("\n")
    print(data_two)  # temp

    #######
    # TODO: VERIFY BOOKING PRICE IN URL 1 AND URL 2 ARE THE SAME - If yes, url 2 may be redundant
    # temp condition to verify TODO
    if int(data_one["data"].get("total")) != data_two["data"].get("current_price"):
        raise Exception("BOOKING PRICES ARE NOT THE SAME")
    else:
        print("booking prices for both urls are the same")

    return data_one["data"].get("user_id"), data_one["data"].get(
        "id"
    )  # returns user_id and booking_id as integers


def pay_court(session: requests.Session, user_id: int, booking_id: int):
    url = os.getenv("PAYMENT_URL") + f"{user_id}/{booking_id}"
    print(url)

    response = session.get(url)
    
    # content type is text/html; charset=UTF-8
    print(response.text)

    return
