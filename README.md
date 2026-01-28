# automated-court-booker

future improvements

1. have an option to combine bond and c. drive data together for the bot to book courts at both stadiums.
2. add optional start and/or end time for algorithm so it only books within certain time constraints - speeds up convergence time as well. make this an iterative booking process to find the longest continuous sequence within the given time frame.
3. credit balance checker - have 3 different statuses (correspond to the 3 different pricing tiers) - calculates and checks if my credit balance is sufficient for the booking request (concurrent, not sequential - otherwise it will increase execution time)
4. test cases - important to test if my optimisation is working or not

open new (restart) terminal to open virtual environment

testing

- `python -m pytest -v`
- `python -m pytest -v -s` -> with output printed

run

- `python main.py`

change booking preferences using /config.yaml (local dev only)

| Situation         | Command                                       |
| ----------------- | --------------------------------------------- |
| Local development | `pip install -r requirements-dev.txt`         |
| Lambda build      | `pip install -r requirements.txt -t package/` |

---

# Automated Court Booker

This project automates the process of checking court availability and booking courts based on predefined preferences.

The program:

- Loads booking preferences from a configuration file
- Determines the target booking date and day
- Fetches court availability from an external booking system
- Selects the longest available time slot that matches the user’s preferences
- Books and pays for courts automatically (when available)

The logic is designed to run once per day and exit early if no booking is scheduled for that day.

---

## Features

- Automatic date and day calculation
- Config-driven booking preferences
- Finds the longest contiguous available court slot
- Safe early exit when no schedule is configured
- Clear logging for debugging and monitoring
- Designed for unattended execution

---

## Project Structure

(tbc.)

## Configuration

Booking preferences are defined in `config.yaml`, including:

- Preferred locations
- Price per court
- Weekly schedule with optional start/end times

If no schedule is provided for a given day, the program exits without making any external requests.

---

## Notes

- This project assumes valid credentials and API endpoints are provided via environment variables.
- Logging is currently done using simple `print()` statements for clarity.
- The codebase is structured to allow future extensions such as scheduling, monitoring, or deployment automation.

---

## Status

This project is under active development.
