from dataclasses import dataclass
from datetime import date
import os

from dotenv import load_dotenv


load_dotenv()


def _require_env(name: str) -> str:
    """Fetch a required environment variable or raise a helpful error."""
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value


@dataclass(frozen=True)
class ApiSettings:
    login_url: str = _require_env("LOGIN_URL")
    logout_url: str = _require_env("LOGOUT_URL")
    user_data_url: str = _require_env("USER_DATA")
    court_schedule_url: str = _require_env("COURT_SCHEDULE")
    booking_url: str = _require_env("BOOKING_URL")
    payment_url: str = _require_env("PAYMENT_URL")


@dataclass(frozen=True)
class UserCredentials:
    number: str = _require_env("USER_NUMBER")
    password: str = _require_env("USER_PASSWORD")


@dataclass
class BookingWindow:
    location: str = os.getenv("BOOKING_LOCATION", "bond_crescent")
    date: str = os.getenv("BOOKING_DATE", str(date.today()))
    start_time: str = os.getenv("BOOKING_START_TIME", "06:00")
    end_time: str = os.getenv("BOOKING_END_TIME", "23:00")


API = ApiSettings()
CREDENTIALS = UserCredentials()