# Standard Library
import os
from datetime import date

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()


def book_court():
    return True


def get_court_schedule(session: requests.Session, location: str):
    # Fetch request payload
    # request_date = str(date.today())
    request_date = "2025-10-13"
    url = os.getenv("COURT_AVAILABILITY") + request_date

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
        "court_id": "",
        "court_name": "",
        "start_time": "",
        "end_time": "",
        "length": 0,  # TEMP
    }

    for court_number, court_info in data.items():
        current = 0
        current_start = None

        for slot in court_info.get("timetable"):
            if slot.get("status") == "Available":
                if current == 0:
                    current_start = slot.get("start_time")
                current += 1

                if current > booking_info.get("length"):
                    booking_info.update(
                        {
                            "court_id": court_number,
                            "start_time": current_start,
                            "end_time": slot["end_time"],
                            "length": current,  # TEMP
                        }
                    )
            else:
                current = 0
                current_start = None

    booking_info["court_name"] = "Court" + str(booking_info.get("court_id"))

    print(f"\nLongest availability: {booking_info.get("length")} slots/hours")
    print(
        f"Court: {booking_info.get("court_id")}, starting at {booking_info.get("start_time")}, ending at {booking_info.get("end_time")}"
    )

    return
