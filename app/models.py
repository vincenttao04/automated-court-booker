# Standard Library
from dataclasses import dataclass

# Local Application Imports
from constants import LOCATION_IDS, Location, Priority


@dataclass
class BookingCriteria:
    date: str
    start_time: str
    end_time: str
    location: Location
    priority: Priority
    price: int

    @property
    def location_id(self) -> str:
        return LOCATION_IDS[self.location]

    @property
    def location_name(self) -> str:
        return self.location.value


@dataclass
class BookingInformation:
    date: str
    court_id: str = ""
    court_name: str = ""
    start_time: str = ""
    end_time: str = ""
    price: int = 0
    # Remaining values are required but not used in the booking process
    booking_id: str = ""
    gst: str = ""
    subtotal: str = ""
    total: str = ""
    user_id: str = ""
    member_count: int = 0
    member_total: str = ""
    non_member_count: int = 0
    non_member_total: str = ""
