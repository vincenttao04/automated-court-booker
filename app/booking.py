import os
import requests

from datetime import date
from dotenv import load_dotenv

load_dotenv()


def book_court():
    return True


def fetch_court_availability(session: requests.Session, location: str):
    request_date = str(date.today())
    url = os.getenv("COURT_AVAILABILITY") + request_date

    response = session.get(url)
    data = response.json()

    if location == "corinthian_drive":
        print(data["data"].get("2").get("courts"))
    else:
        print(data["data"].get("1").get("courts"))

    return
