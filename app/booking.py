import os
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def book_court():
    return True


def fetch_court_availability(session: requests.Session):
    request_date = str(date.today())
    url = os.getenv("COURT_AVAILABILITY") + request_date

    response = session.get(url)

    print(response.json())
