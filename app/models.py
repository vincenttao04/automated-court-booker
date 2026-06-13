# Standard Library
from dataclasses import dataclass

# Local Application Imports
from constants import Priority


@dataclass
class BookingCriteria:
    date: str
    start_time: str
    end_time: str
    location_id: str
    location_name: str
    priority: Priority
    price: int
