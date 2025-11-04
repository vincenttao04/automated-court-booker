import os
import time

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
                {
                    "start_time": "18:00",
                    "end_time": "19:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
            ],
        },
        "2": {
            "court": {"id": 2, "name": "Court 2"},
            "timetable": [
                {
                    "start_time": "06:00",
                    "end_time": "07:00",
                    "status": "Booked",
                    "user_name": "Club",
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
                {
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "status": "Available",
                    "user_name": None,
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
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "13:00",
                    "end_time": "14:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "14:00",
                    "end_time": "15:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
                {
                    "start_time": "15:00",
                    "end_time": "16:00",
                    "status": "Booked",
                    "user_name": "Club",
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
                {
                    "start_time": "18:00",
                    "end_time": "19:00",
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
                    "user_name": "Club",
                },
                {
                    "start_time": "07:00",
                    "end_time": "08:00",
                    "status": "Booked",
                    "user_name": "Club",
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
                    "status": "Available",
                    "user_name": None,
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
                    "status": "Booked",
                    "user_name": "Club",
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
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "17:00",
                    "end_time": "18:00",
                    "status": "Available",
                    "user_name": None,
                },
                {
                    "start_time": "18:00",
                    "end_time": "19:00",
                    "status": "Booked",
                    "user_name": "Club",
                },
            ],
        },
    }


def test_booking_env_variables_exist():
    required_env_variables = ["COURT_SCHEDULE", "BOOKING_URL", "PAYMENT_URL"]

    for var in required_env_variables:
        value = os.getenv(var)
        assert value, f"Missing environment variable: {var}"


# Helper function
def simulate_booking(test_court_data: dict, result: dict | None) -> None:
    if result is None:
        return

    for court in test_court_data.values():
        for slot in court.get("timetable"):
            if result["start_time"] <= slot["start_time"] < result["end_time"]:
                slot["status"] = "Booked"

    return result


def test_find_court_returns_all_available_sequences(test_court_data):
    start_time = time.perf_counter()

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 1
    assert result["court_name"] == "Court 1"
    assert result["start_time"] == "12:00"
    assert result["end_time"] == "16:00"
    assert result["price"] == PRICE_PER_COURT * 4
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 2
    assert result["court_name"] == "Court 2"
    assert result["start_time"] == "07:00"
    assert result["end_time"] == "11:00"
    assert result["price"] == PRICE_PER_COURT * 4
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 3
    assert result["court_name"] == "Court 3"
    assert result["start_time"] == "16:00"
    assert result["end_time"] == "18:00"
    assert result["price"] == PRICE_PER_COURT * 2
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 1
    assert result["court_name"] == "Court 1"
    assert result["start_time"] == "06:00"
    assert result["end_time"] == "07:00"
    assert result["price"] == PRICE_PER_COURT * 1
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 2
    assert result["court_name"] == "Court 2"
    assert result["start_time"] == "18:00"
    assert result["end_time"] == "19:00"
    assert result["price"] == PRICE_PER_COURT * 1
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is not None
    assert result["court_id"] == 3
    assert result["court_name"] == "Court 3"
    assert result["start_time"] == "11:00"
    assert result["end_time"] == "12:00"
    assert result["price"] == PRICE_PER_COURT * 1
    simulate_booking(test_court_data, result)

    result = find_court(test_court_data)
    assert result is None

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\n[test_find_court_returns_all_available_sequences] {duration:.6f} seconds")


def test_find_court_returns_none_when_no_availability(test_court_data):
    start_time = time.perf_counter()

    for court in test_court_data.values():
        for slot in court.get("timetable"):
            if slot.get("status") == "Available":
                slot["status"] = "Booked"

    result = find_court(test_court_data)
    assert result is None

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"\n[test_find_court_returns_none_when_no_availability] {duration:.6f} seconds"
    )
