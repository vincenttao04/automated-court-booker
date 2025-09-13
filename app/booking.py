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

    if location == "corinthian_drive":
        print(data["data"].get("2").get("courts"))
    else:
        print(data["data"].get("1").get("courts"))

    print("fetch court availability successful")
    return
