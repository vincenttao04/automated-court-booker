# Standard Library
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()
# NZ_TZ = ZoneInfo("Pacific/Auckland")
# now_nz = datetime.now(NZ_TZ)
# BOOKING_DATE = now_nz.date() + timedelta(weeks=3)

BOOKING_DATE = "2025-11-17"  # temp, testing purposes only
# times must be in "HH:MM" 24-hour format (i.e. "09:00", not "9:00")
START_TIME = "12:00"
END_TIME = "23:00"
PRICE_PER_COURT = 27  # price tier required: Community Member (Peak)


def get_court_schedule(session: requests.Session, location: str) -> dict:
    # Fetch request payload
    url = f"{os.getenv('COURT_SCHEDULE')}{BOOKING_DATE}"

    # Make fetch court availability GET request
    response = session.get(url)
    data = response.json()

    # Check if fetch court availability was successful
    if data.get("status") != "success":
        raise Exception("FETCH COURT AVAILABILITY FAILED")

    # Extract stadium specific court availability
    if location == "corinthian_drive":
        data = data["data"]["2"]["courts"]  # corinthian drive stadium
    else:
        data = data["data"]["1"]["courts"]  # bond crescent stadium and others

    # Filter courts only within the desired time range
    if START_TIME and END_TIME:
        for court_data in data.values():
            timetable = court_data["timetable"]

            court_data["timetable"] = [
                slot
                for slot in timetable
                if START_TIME <= slot["start_time"] < END_TIME
            ]

    print(f"fetch court availability successful ({BOOKING_DATE})")
    print(data["1"]["timetable"][0]["start_time"])
    return data


def find_court(data: dict) -> dict | None:
    booking_info = {
        "booking_id": "",
        "date": BOOKING_DATE,
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

        for slot in court_info["timetable"]:
            if slot["status"] == "Available":
                if current_length == 0:
                    current_start = slot["start_time"]
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

    # Check if any court availability was found
    if best_length == 0:
        print("\nno available courts found")
        return None

    booking_info["court_name"] = f"Court {booking_info['court_id']}"
    booking_info["price"] = best_length * PRICE_PER_COURT

    print(f"\nlongest availability: {best_length} slots/hours")
    print(
        f"court: {booking_info['court_id']}, starting at {booking_info["start_time"]}, ending at {booking_info["end_time"]}"
    )

    return booking_info


def book_court(session: requests.Session, booking_info: dict) -> tuple[int | int]:
    # Fetch request_one payload
    url = os.getenv("BOOKING_URL")

    # Make booking_create POST request
    response = session.post(url, json=booking_info)
    data = response.json()

    # Check if booking_create was successful
    if data.get("status") != "success":
        raise Exception("CREATE BOOKING FAILED")

    print("\n")
    print(data)

    return (
        data["data"]["user_id"],
        data["data"]["id"],
    )  # returns user_id and booking_id as integers


def pay_court(session: requests.Session, user_id: int, booking_id: int) -> None:
    # Fetch request payload
    url = f"{os.getenv('PAYMENT_URL')}{user_id}/{booking_id}"

    # Make court payment GET request
    response = session.get(url)

    # Content-Type: text/html; charset=UTF-8
    print(response.text)

    # Check if court payment was successful
    if "Payment Success" not in response.text:
        raise Exception("COURT PAYMENT FAILED")

    print("\ncourt payment successful - check email for confirmation/receipt")

    return
