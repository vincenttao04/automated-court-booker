# Standard Library
import os
import re
from dataclasses import asdict

# Third-Party Libraries
import requests
from dotenv import load_dotenv

# Local Application Imports
from app.constants import Priority
from app.models import BookingCriteria, BookingInformation

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()


# Helper function: clean and filter court schedule data based on booking criteria
def process_court_schedule(data: dict, criteria: BookingCriteria) -> dict:
    # Extract stadium specific court availability
    data = data["data"][criteria.location_id]["courts"]

    # Filter courts only within the desired time range
    if criteria.start_time and criteria.end_time:
        for court_data in data.values():
            timetable = court_data["timetable"]

            court_data["timetable"] = [
                slot
                for slot in timetable
                if criteria.start_time <= slot["start_time"] < criteria.end_time
            ]

    return data


# Helper function: extract payment error message from HTML response
def extract_payment_error(text: str) -> str | None:
    if not text:
        return None

    # Use regex to find the error message within the HTML content
    match = re.search(
        r'<div class="text-xl font-bold[^"]*">\s*(.*?)\s*</div>',
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:
        return " ".join(match.group(1).split())

    return None


# Helper function: identify courts based on user's priority preference
def identify_courts(data: dict, criteria: BookingCriteria) -> BookingInformation | None:
    print("identifying courts based on priority:", criteria.priority.value)
    return PRIORITY_HANDLER[criteria.priority](data, criteria.date, criteria.price)


def get_court_schedule(
    session: requests.Session,
    criteria: BookingCriteria,
) -> dict:
    # Fetch request payload
    url = f"{os.getenv('COURT_SCHEDULE_API')}{criteria.date}"

    # Make fetch court availability GET request
    response = session.get(url, timeout=15)
    data = response.json()

    # Check if fetch court availability was successful
    if data.get("status") != "success":
        raise Exception("FETCH COURT AVAILABILITY FAILED")

    print(
        f"fetch court schedule: {criteria.location_name}, {criteria.date}, between {criteria.start_time} and {criteria.end_time}"
    )

    return process_court_schedule(data, criteria)


def identify_earliest_courts(
    data: dict, date: str, price: int
) -> BookingInformation | None:
    search_index = 0
    max_slots = len(next(iter(data.values()))["timetable"])

    while search_index < max_slots:
        found_available = False

        for court_info in data.values():
            if court_info["timetable"][search_index]["status"] == "Available":
                found_available = True
                break

        if found_available:
            break

        search_index += 1

    # Check if any court availability was found
    if search_index == max_slots:
        print("no available courts found\n")
        return None

    booking_info = BookingInformation(date)
    best_length = 0

    for court_number, court_info in data.items():
        timetable = court_info["timetable"]

        # Court must be available at the beginning of the search window
        if timetable[search_index]["status"] != "Available":
            continue

        current_length = 0
        court_name = court_info["court"][
            "name"
        ]  # note court_id and court_name mistmatch for corinthian_drive

        start_time = timetable[search_index]["start_time"]
        end_time = start_time

        # Count contiguous availability from the start of the timetable
        for slot in timetable[search_index:]:
            if slot["status"] != "Available":
                break

            current_length += 1
            end_time = slot["end_time"]

        if current_length > best_length:
            booking_info.court_id = court_number
            booking_info.court_name = court_name
            booking_info.start_time = start_time
            booking_info.end_time = end_time

            best_length = current_length

    booking_info.price = best_length * price

    print(f"longest availability: {best_length} slots/hours")
    print(
        f"{booking_info.court_name.lower()}, between {booking_info.start_time} and {booking_info.end_time}\n"
    )

    return booking_info


def identify_longest_courts(
    data: dict, date: str, price: int
) -> BookingInformation | None:
    booking_info = BookingInformation(date)
    best_length = 0

    for court_number, court_info in data.items():
        current_length = 0
        current_start = ""
        court_name = court_info["court"][
            "name"
        ]  # note court_id and court_name mistmatch for corinthian_drive

        for slot in court_info["timetable"]:
            if slot["status"] == "Available":
                if current_length == 0:
                    current_start = slot["start_time"]
                current_length += 1

                if current_length > best_length:
                    booking_info.court_id = court_number
                    booking_info.court_name = court_name
                    booking_info.start_time = current_start
                    booking_info.end_time = slot["end_time"]

                    best_length = current_length
            else:
                current_length = 0
                current_start = ""

    # Check if any court availability was found
    if best_length == 0:
        print("no available courts found\n")
        return None

    booking_info.price = best_length * price

    print(f"longest availability: {best_length} slots/hours")
    print(
        f"{booking_info.court_name.lower()}, between {booking_info.start_time} and {booking_info.end_time}\n"
    )

    return booking_info


PRIORITY_HANDLER = {
    Priority.EARLIEST: identify_earliest_courts,
    Priority.LONGEST: identify_longest_courts,
}


def book_court(
    session: requests.Session, booking_info: BookingInformation
) -> tuple[int, int]:
    # Fetch request_one payload
    url = os.getenv("BOOKING_API")
    if not url:
        raise RuntimeError("Book Court: Missing env variables")

    # Make booking_create POST request
    response = session.post(url, json=asdict(booking_info), timeout=15)
    data = response.json()

    # Check if booking_create was successful
    if data.get("status") != "success":
        raise Exception("CREATE BOOKING FAILED")

    return (
        data["data"]["user_id"],
        data["data"]["id"],
    )  # returns user_id and booking_id as integers


def pay_court(
    session: requests.Session, user_id: int, booking_id: int, count: int
) -> None:
    # Fetch request payload
    url = f"{os.getenv('PAYMENT_API')}{user_id}/{booking_id}"

    # Make court payment GET request; Response Content-Type: text/html; charset=UTF-8
    response = session.get(url, timeout=15)

    # Check if court payment was successful
    if "Payment Success" not in response.text:
        error_message = extract_payment_error(response.text)
        raise Exception(error_message or "Unknown payment error")

    print(
        f"({count}) court payment successful - check email for confirmation/receipt\n"
    )

    return


def book_all_available(
    session: requests.Session,
    criteria: BookingCriteria,
    booking_info: BookingInformation | None,
):
    count = 1
    while booking_info is not None:
        try:
            user_id, booking_id = book_court(session, booking_info)
            pay_court(session, user_id, booking_id, count)
            schedule = get_court_schedule(session, criteria)
            booking_info = identify_courts(schedule, criteria)
            count += 1
        except Exception as e:
            print(f"Error: {e}")
            break
