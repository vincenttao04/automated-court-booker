# Standard Library
import os
from datetime import date

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()


def get_court_schedule(session: requests.Session, location: str):
    # Fetch request payload
    # request_date = str(date.today())
    request_date = "2025-10-13"
    url = os.getenv("COURT_SCHEDULE") + request_date

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

    print(f"fetch court availability successful ({request_date})")
    return data


def find_court(data: dict):
    booking_info = {
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
    payload_one = {
        **booking_info,
        "booking_id": "",
        "date": "2025-10-13",
        "gst": "",
        "subtotal": "",
        "total": "",
        "user_id": "",
    }

    # Make booking_create POST request
    response_one = session.post(url_one, json=payload_one)
    data_one = response_one.json()

    # Check if booking_create was successful
    if data_one.get("status") != "success":
        raise Exception("BOOKING CREATE FAILED")

    print(data_one)  # temp
    booking_id = str(data_one["data"].get("id"))

    #######

    # Fetch request_two payload
    url_two = os.getenv("CHECKOUT_URL") + booking_id

    # Make booking_checkout GET request
    response_two = session.get(url_two)
    data_two = response_two.json()

    # Check if booking_checkout was successful
    if data_one.get("status") != "success":
        raise Exception("BOOKING CHECKOUT FAILED")

    print(data_two)  # temp
