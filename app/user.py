# Standard Library
import os
import time

# Third-Party Libraries
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from app.browser import browser_login

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
    url = os.getenv("USER_DATA_API")
    if not url:
        raise RuntimeError("FETCH USER DETAIL FAILED: Missing env variables")

    # Make fetch user detail GET request
    response = session.get(url, timeout=15)
    data = response.json()

    # Check if fetch user detail was successful
    if data.get("status") != "success":
        raise Exception(
            f"FETCH USER DETAIL FAILED: {data.get('message', 'Unknown error')}"
        )

    print(f"{field}: {data['data'].get(field)}")
    return


def login() -> requests.Session:
    # Fetch request payload
    user_number = os.getenv("USER_NUMBER")
    user_password = os.getenv("USER_PASSWORD")

    if not user_number or not user_password:
        raise RuntimeError("Login: Missing env variables")

    data = browser_login(user_number, user_password)

    # Create request session
    session = create_session()
    # Update session headers with authentication token
    session.headers.update(
        {
            "Authorization": f"{data['data'].get('token_type')} {data['data'].get('access_token')}"
        }
    )

    print(f"login successful: {user_number}")
    fetch_user_detail(session, "credit_balance")
    print("")

    return session


def logout(session: requests.Session) -> None:
    fetch_user_detail(session, "credit_balance")

    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        print("waiting 10 seconds before logging out...")
        time.sleep(10)

    # Fetch request payload
    url = os.getenv("LOGOUT_API")
    if not url:
        raise RuntimeError("Logout: Missing env variables")

    payload = {"device_id": DEVICE_ID}

    # Make logout POST request
    response = session.post(url, json=payload, timeout=15)
    data = response.json()

    # Check if logout was successful
    if data.get("status") != "success":
        raise Exception(f"LOGOUT FAILED: {data.get('message', 'Unknown error')}")

    print(f"logout successful: {os.getenv('USER_NUMBER')}\n")
    return
