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

    print(url)
    print(payload)

    return True
