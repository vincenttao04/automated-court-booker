# Standard Library
from dataclasses import dataclass

# Local Application Imports
from constants import Location, LOCATION_IDS, Priority


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
