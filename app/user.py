# Standard Library
import os
import time

# Third-Party Libraries
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter


DEVICE_ID = "Badminton-Test-ABC-001"

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()


def create_session():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://book.bnh.org.nz",
        "Referer": "https://book.bnh.org.nz/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    }

    # Instantiate request session
    session = requests.Session()

    # Create a connection pool adapter
    adapter = HTTPAdapter(pool_connections=5, pool_maxsize=5)

    # Mount it for both HTTP and HTTPS
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Update session headers
    session.headers.update(headers)

    return session


def fetch_user_detail(session: requests.Session, field: str) -> None:
    # Fetch request payload
    url = os.getenv("USER_DATA")

    # Make fetch user detail GET request
    response = session.get(url, timeout=15)
    data = response.json()

    # Check if fetch user detail was successful
    if data.get("status") != "success":
        raise Exception("FETCH USER DETAIL FAILED")

    print(f"{field}: {data['data'].get(field)}")
    return


def login() -> requests.Session:
    # Fetch request payload
    url = os.getenv("LOGIN_URL")

    if not os.getenv("USER_NUMBER") or not os.getenv("USER_PASSWORD"):
        raise RuntimeError("Missing USER_NUMBER or USER_PASSWORD env variables")

    payload = {
        "number": os.getenv("USER_NUMBER"),
        "password": os.getenv("USER_PASSWORD"),
        "device_id": DEVICE_ID,
    }

    # Create request session
    session = create_session()

    # Make login POST request
    response = session.post(url, json=payload, timeout=15)
    data = response.json()

    # Check if login was successful
    if data.get("status") != "success":
        raise Exception("LOGIN FAILED")

    # Update session headers with authentication token
    session.headers.update(
        {
            "Authorization": f"{data['data'].get('token_type')} {data['data'].get('access_token')}"
        }
    )

    print(f"login successful: {os.getenv('USER_NUMBER')}")
    fetch_user_detail(session, "credit_balance")
    print("")

    return session


def logout(session: requests.Session) -> None:
    fetch_user_detail(session, "credit_balance")

    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        print("waiting 10 seconds before logging out...")
        time.sleep(10)

    # Fetch request payload
    url = os.getenv("LOGOUT_URL")
    payload = {"device_id": DEVICE_ID}

    # Make logout POST request
    response = session.post(url, json=payload, timeout=15)
    data = response.json()

    # Check if logout was successful
    if data.get("status") != "success":
        raise Exception("LOGOUT FAILED")

    print(f"logout successful: {os.getenv('USER_NUMBER')}\n")
    return
