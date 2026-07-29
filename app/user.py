# Standard Library
import os
import time

# Third-Party Libraries
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter

# Local Application Imports
from app.browser import browser_login, get_user_agent
from app.utils import check_status

DEVICE_ID = "Badminton-Test-ABC-001"

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()


def create_session():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://book.bnh.org.nz",
        "Referer": "https://book.bnh.org.nz/",
        "User-Agent": get_user_agent(),
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
        raise RuntimeError(
            "FETCH USER DETAIL FAILED: missing env variable(s) - USER_DATA_API"
        )

    # Make fetch user detail GET request
    try:
        response = session.get(url, timeout=15)
    except requests.RequestException as e:
        raise RuntimeError(f"FETCH USER DETAIL FAILED: network error - {e}")

    data = response.json()

    # Check if fetch user detail was successful
    check_status(data, "FETCH USER DETAIL")

    print(f"{field}: {data['data'].get(field)}")
    return


def login() -> requests.Session:
    # Fetch request payload
    user_number = os.getenv("USER_NUMBER")
    user_password = os.getenv("USER_PASSWORD")

    if not user_number or not user_password:
        raise RuntimeError(
            "LOGIN FAILED: missing env variable(s) - USER_NUMBER and/or USER_PASSWORD"
        )

    data = {}

    # Login with browser automation; retry once if it fails
    for attempt in range(1, 3):
        try:
            data = browser_login(user_number, user_password)
            break
        except Exception as e:
            print(f"login attempt {attempt} failed: {e}")
            if attempt == 2:
                raise RuntimeError(f"LOGIN FAILED after 2 attempts: {e}")

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
        raise RuntimeError("LOGOUT FAILED: missing env variable(s) - LOGOUT_API")

    payload = {"device_id": DEVICE_ID}

    # Make logout POST request
    try:
        response = session.post(url, json=payload, timeout=15)
    except requests.RequestException as e:
        raise RuntimeError(f"LOGOUT FAILED: network error - {e}")

    data = response.json()

    # Check if logout was successful
    check_status(data, "LOGOUT")

    print(f"logout successful: {os.getenv('USER_NUMBER')}\n")
    return
