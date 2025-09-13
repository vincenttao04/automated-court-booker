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

    print("fetch court availability successful")
    return data


def identify_available_courts(data: str):
    longest_availability = 0
    best_court = None
    best_start = None
    best_end = None

    for court_number, court_info in data.items():
        current = 0
        current_start = None

        for slot in court_info.get("timetable"):
            if slot.get("status") == "Available":
                if current == 0:
                    current_start = slot.get("start_time")
                current += 1

                if current > longest_availability:
                    longest_availability = current
                    best_court = court_number
                    best_start = current_start
                    best_end = slot.get("end_time")
            else:
                current = 0
                current_start = None

    print(f"\nLongest availability: {longest_availability} slots")
    print(f"Court: {best_court}, starting at {best_start}, ending at {best_end}")

    return
