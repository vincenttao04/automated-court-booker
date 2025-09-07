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

    print(url)
    print(payload)
    print(headers)

    return True
