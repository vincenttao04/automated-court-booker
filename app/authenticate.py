import requests
import os
from dotenv import load_dotenv

load_dotenv()


def login():
    # Fetch request payload
    url = os.getenv("LOGIN_URL")
    payload = {
        "number": os.getenv("LOGIN_NUMBER"),
        "password": os.getenv("LOGIN_PASSWORD"),
        "device_id": "Badminton-Test-ABC-001",
    }
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://book.bnh.org.nz",
        "Referer": "https://book.bnh.org.nz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    }

    # Instantiate request session
    session = requests.Session()

    # Make authentication/login POST request
    response = session.post(url, json=payload, headers=headers)
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

    print(f"{os.getenv('LOGIN_NUMBER')} login successful")
    return session


def logout(session: requests.Session):
    # Fetch request payload
    url = os.getenv("LOGOUT_URL")
    payload = {"device_id": "Badminton-Test-ABC-001"}
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://book.bnh.org.nz",
        "Referer": "https://book.bnh.org.nz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    }

    # Make authentication/logout POST request
    response = session.post(url, json=payload, headers=headers)
    data = response.json()

    # Check if logout was successful
    if data.get("status") != "success":
        raise Exception("LOGOUT FAILED")

    print(f"{os.getenv('LOGIN_NUMBER')} logout successful")
    return
