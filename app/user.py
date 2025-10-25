# Standard Library
import os
import time

# Third-Party Libraries
import requests
from dotenv import load_dotenv

load_dotenv()


def create_session():
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://book.bnh.org.nz",
        "Referer": "https://book.bnh.org.nz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    }

    # Instantiate request session
    session = requests.Session()

    # Update session headers
    session.headers.update(headers)

    return session


def login() -> None:
    # Fetch request payload
    url = os.getenv("LOGIN_URL")
    payload = {
        "number": os.getenv("USER_NUMBER"),
        "password": os.getenv("USER_PASSWORD"),
        "device_id": "Badminton-Test-ABC-001",
    }

    # Create request session
    session = create_session()

    # Make login POST request
    response = session.post(url, json=payload)
    data = response.json()

    # Check if login was successful
    if data.get("status") != "success":
        raise Exception("LOGIN FAILED")

    # Update session headers with authentication token
    session.headers.update(
        {
            "Authorization": f"{data["data"].get("token_type")} {data["data"].get("access_token")}"
        }
    )

    # TEMP: PRINT DEBUG INFO
    print("\nRate Limit Remaining:", response.headers.get("X-RateLimit-Remaining"))
    print("Response Status Code:", data.get("code"))
    print("Response Status:", data.get("status"))

    print(f"\n{os.getenv('USER_NUMBER')} login successful")
    return session


def logout(session: requests.Session) -> None:
    # TEMP: DELAY LOGOUT FUNCTION TO SIMULATE SESSION ACTIVITY
    print("\ntime delay: 10 seconds")
    time.sleep(10)

    # Fetch request payload
    url = os.getenv("LOGOUT_URL")
    payload = {"device_id": "Badminton-Test-ABC-001"}

    # Make logout POST request
    response = session.post(url, json=payload)
    data = response.json()

    # Check if logout was successful
    if data.get("status") != "success":
        raise Exception("LOGOUT FAILED")

    print(f"\n{os.getenv('USER_NUMBER')} logout successful")
    return


def fetch_user_detail(session: requests.Session, property: str) -> None:
    # Fetch request payload
    url = os.getenv("USER_DATA")

    # Make fetch user detail GET request
    response = session.get(url)
    data = response.json()

    # Check if fetch user detail was successful
    if data.get("status") != "success":
        raise Exception("FETCH USER DETAIL FAILED")

    property_label = property.title().replace("_", " ")
    print(f"\n{property_label}: {data["data"].get(property)}")
    return
