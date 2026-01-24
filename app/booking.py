# Standard Library
import os
import re

# Third-Party Libraries
import requests
from dotenv import load_dotenv


if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()


def get_court_schedule(
    session: requests.Session,
    location: str,
    date: str,
    user_start_time: str,
    user_end_time: str,
) -> dict:
    # Fetch request payload
    url = f"{os.getenv('COURT_SCHEDULE')}{date}"

    # Make fetch court availability GET request
    response = session.get(url, timeout=15)
    data = response.json()

    # Check if fetch court availability was successful
    if data.get("status") != "success":
        raise Exception("FETCH COURT AVAILABILITY FAILED")

    # Extract stadium specific court availability
    if location == "corinthian_drive":
        data = data["data"]["2"]["courts"]  # corinthian drive
    else:
        data = data["data"]["1"]["courts"]  # bond crescent

    # Filter courts only within the desired time range
    if user_start_time and user_end_time:
        for court_data in data.values():
            timetable = court_data["timetable"]

            court_data["timetable"] = [
                slot
                for slot in timetable
                if user_start_time <= slot["start_time"] < user_end_time
            ]

    print(f"\nfetch court availability successful ({date})")
    return data


def find_court(data: dict, date: str, price: int) -> dict | None:
    booking_info = {
        "booking_id": "",
        "date": date,
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
    booking_info["price"] = best_length * price

    print(f"longest availability: {best_length} slots/hours")
    print(
        f"court: {booking_info['court_id']}, starting at {booking_info['start_time']}, ending at {booking_info['end_time']}"
    )

    return booking_info


def book_court(session: requests.Session, booking_info: dict) -> tuple[int | int]:
    # Fetch request_one payload
    url = os.getenv("BOOKING_URL")

    # Make booking_create POST request
    response = session.post(url, json=booking_info, timeout=15)
    data = response.json()

    # Check if booking_create was successful
    if data.get("status") != "success":
        raise Exception("CREATE BOOKING FAILED")

    return (
        data["data"]["user_id"],
        data["data"]["id"],
    )  # returns user_id and booking_id as integers


# Helper function: extract payment error message from HTML response
def extract_payment_error(text: str) -> str:
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


def pay_court(session: requests.Session, user_id: int, booking_id: int) -> None:
    # Fetch request payload
    url = f"{os.getenv('PAYMENT_URL')}{user_id}/{booking_id}"

    # Make court payment GET request; Response Content-Type: text/html; charset=UTF-8
    response = session.get(url, timeout=15)

    # Check if court payment was successful
    if "Payment Success" not in response.text:
        error_message = extract_payment_error(response.text)
        raise Exception(error_message or "Unknown payment error")

    print("court payment successful - check email for confirmation/receipt")

    return
