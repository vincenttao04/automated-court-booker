import pytest

from app.booking import find_court


@pytest.fixture
def mock_court_data():
    return {
        "1": {
            "court": {"id": 1, "name": "Court 1"},
            "timetable": [
                {
                    "start_time": "06:00",
                    "end_time": "07:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "07:00",
                    "end_time": "08:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "08:00",
                    "end_time": "09:00",
                    "status": "Booked",
                    "user_name": "Morning Club",
                },
                {
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "status": "Available",
                    "user_name": None,
                },
            ],
        },
        "2": {
            "court": {"id": 2, "name": "Court 2"},
            "timetable": [
                {
                    "start_time": "06:00",
                    "end_time": "07:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "07:00",
                    "end_time": "08:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "08:00",
                    "end_time": "09:00",
                    "status": "Available",
                    "user_name": None,
                },
            ],
        },
        "3": {
            "court": {"id": 3, "name": "Court 3"},
            "timetable": [
                {
                    "start_time": "06:00",
                    "end_time": "07:00",
                    "status": "Booked",
                    "user_name": "League",
                },
                {
                    "start_time": "07:00",
                    "end_time": "08:00",
                    "status": "Booked",
                    "user_name": "League",
                },
            ],
        },
    }


def test_find_court_returns_longest_available(mock_court_data):
    result = find_court(mock_court_data)

    assert result is not None
    # Court 2 has 3 consecutive available slots, the longest streak
    assert result["court_id"] == 2
    assert result["start_time"] == "06:00"
    assert result["end_time"] == "09:00"
    assert result["price"] == 27 * 3  # PRICE_PER_COURT * 3 hours


def test_find_court_returns_none_when_no_availability():
    data = {
        "1": {
            "court": {"id": 1, "name": "Court 1"},
            "timetable": [
                {"start_time": "06:00", "end_time": "07:00", "status": "Booked"},
                {"start_time": "07:00", "end_time": "08:00", "status": "Booked"},
            ],
        }
    }

    result = find_court(data)
    assert result is None
