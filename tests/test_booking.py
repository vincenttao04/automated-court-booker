import pytest

from app.booking import find_court, PRICE_PER_COURT


@pytest.fixture
def test_court_data():
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
                    "user_name": "Club",
                },
                {
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "11:00",
                    "end_time": "12:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "12:00",
                    "end_time": "13:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "13:00",
                    "end_time": "14:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "14:00",
                    "end_time": "15:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "15:00",
                    "end_time": "16:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "16:00",
                    "end_time": "17:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "17:00",
                    "end_time": "18:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
            ],
        },
    }


def test_find_court_returns_longest_available(test_court_data):
    result = find_court(test_court_data)

    assert result is not None
    assert result["court_id"] == 1
    assert result["court_name"] == "Court 1"
    assert result["start_time"] == "12:00"
    assert result["end_time"] == "16:00"
    assert result["price"] == PRICE_PER_COURT * 4

    for slot in test_court_data["1"]["timetable"]:
        if result["start_time"] <= slot["start_time"] < result["end_time"]:
            slot["status"] = "Booked"

    result = find_court(test_court_data)

    assert result is not None
    assert result["court_id"] == 1
    assert result["court_name"] == "Court 1"
    assert result["start_time"] == "06:00"
    assert result["end_time"] == "08:00"
    assert result["price"] == PRICE_PER_COURT * 2


def test_find_court_returns_none_when_no_availability(test_court_data):
    for slot in test_court_data["1"]["timetable"]:
        if slot.get("status") == "Available":
            slot["status"] = "Booked"

    result = find_court(test_court_data)
    assert result is None
