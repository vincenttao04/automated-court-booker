# Standard Library
import os
from datetime import date

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()


def book_court():
    return True


def fetch_court_availability(session: requests.Session, location: str):
    # Fetch request payload
    request_date = str(date.today())
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


def identify_longest_available_courts(data: str):
    best = {
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

                if current > best.get("length"):
                    best.update(
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

    best["court_name"] = "Court" + str(best.get("court_id"))

    print(f"\nLongest availability: {best.get("length")} slots/hours")
    print(
        f"Court: {best.get("court_id")}, starting at {best.get("start_time")}, ending at {best.get("end_time")}"
    )

    return
