import requests
import os
from dotenv import load_dotenv

load_dotenv()


def login():

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

    session = requests.Session()

    response = session.post(url, json=payload, headers=headers)

    print("---")
    print("HTTP Status Code:", response.status_code)
    print("HTTP Headers:", response.headers)
    print("HTTP Response Body:", response.json())
    print("---")

    data = response.json()

    print("status:", data.get("status"))
    print("code:", data.get("code"))
    print("message:", data.get("message"))
    print("error:", data.get("error"))

    print("---")

    token_type = data["data"].get("token_type")
    access_token = data["data"].get("access_token")
    print("token_type:", token_type)
    print("access_token:", access_token)

    session.headers.update({"Authorization": f"{token_type} {access_token}"})

    print("---")

    print("Session headers updated")

    return True
