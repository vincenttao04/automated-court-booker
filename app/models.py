# Standard Library
from dataclasses import dataclass


@dataclass
class BookingCriteria:
    date: str
    start_time: str
    end_time: str
    location_id: str
    location_name: str
    price: int
