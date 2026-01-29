# Automated Court Booker

A Python automation project that books courts at Badminton North Harbour facilities in Auckland, New Zealand. It searches for the longest contiguous available time slots that match user-defined preferences and completes the full booking and payment process end-to-end.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Core Language](#core-language)
  - [Key Libraries](#key-libraries)
  - [Time \& Date Handling](#time--date-handling)
  - [Testing Framework](#testing-framework)
  - [Configuration Tools](#configuration-tools)
  - [Deployment](#deployment)
  - [Development \& Tooling](#development--tooling)
  - [Version Control](#version-control)
- [How It Works](#how-it-works)
  - [Booking Algorithm](#booking-algorithm)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
- [Configuration](#configuration)
  - [config.yaml Options](#configyaml-options)
  - [Environment Variables](#environment-variables)
- [Testing](#testing)
- [AWS Lambda Deployment](#aws-lambda-deployment)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Author](#author)
- [Disclaimer](#disclaimer)
- [Acknowledgments](#acknowledgments)

## Features

- **Smart Scheduling**: Books courts up to three weeks in advance based on a configurable weekly schedule and user preferences
- **Intelligent Slot Detection**: Automatically finds the longest contiguous available time slot within user-defined start and end times, making multiple sequential bookings if required
- **Multi-Location Support**: Supports booking at both Bond Crescent and Corinthian Drive facilities
- **Flexible Time Preferences**: Define custom start and end time constraints for each day of the week
- **Automated Payment**: Completes court payments automatically using account credit
- **AWS Lambda Ready**: Structured for deployment on AWS Lambda for autonomous, unattended execution
- **Credit Balance Tracking**: Retrieves and reports account credit balance before and after bookings
- **Comprehensive Testing**: Includes a pytest test suite covering core booking and user logic

## Tech Stack

### Core Language

- **Python 3.9+** — Primary language used for automation, scheduling logic, and API interactions

### Key Libraries

- **requests** — Handles HTTP communication with the booking system APIs
- **PyYAML** — Loads and parses booking preferences from `config.yaml`
- **python-dotenv** — Manages environment variables for credentials and configuration

### Time & Date Handling

- **zoneinfo (stdlib)** — Ensures correct date calculations using the `Pacific/Auckland` timezone

### Testing Framework

- **pytest** — Test framework used for validating booking and user logic

### Configuration Tools

- **YAML** — Human-readable configuration for schedules, locations, and preferences
- **Environment Variables** — Secure handling of credentials and deployment settings

### Deployment

- **AWS Lambda** — Serverless execution for autonomous, scheduled bookings
- **ZIP-based deployment** — Lightweight packaging for Lambda compatibility

### Development & Tooling

- **Virtual environments (venv)** — Dependency isolation for local development
- **pip** — Python package management

### Version Control

- **Git / GitHub** — Source control and project hosting

## How It Works

1. **Date Calculation**: Determines the booking date up to three weeks in advance using the Pacific/Auckland timezone
2. **Config Loading**: Loads booking preferences from `config.yaml` (or a remote URL if configured)
3. **Schedule Check**: Checks whether booking is enabled for the calculated day of the week
4. **Authentication**: Logs in and establishes an authenticated session
5. **Availability Fetch**: Retrieves court availability for the target date and location
6. **Slot Finding**: Identifies the longest contiguous available time slot within user-defined start and end times
7. **Booking Loop**: Books all available slots that meet the criteria
8. **Payment**: Automatically completes payment using account credit
9. **Repeat**: Repeats availability checking and booking until no suitable courts remain
10. **Confirmation**: Displays the updated account credit balance
11. **Cleanup**: Logs out and closes the session

### Booking Algorithm

The project uses a sliding-window-style approach to find optimal court slots:

- Scans all courts within the configured time range
- Identifies the longest contiguous sequence of available time slots
- Books the entire sequence in a single booking transaction
- Continues searching for and booking additional suitable slots if available
- Stops once no further qualifying slots are found

## Project Structure

```
automated-court-booker/
├── app/
│   ├── booking.py           # Court availability, optimisation, booking, and payment logic
│   ├── user.py              # Authentication & user logic
│   └── __init__.py
│
├── tests/
│   ├── test_booking.py      # Booking logic tests
│   └── test_user.py         # User logic tests
│
├── config.yaml              # Booking preferences (local dev)
├── config_loader.py         # YAML config loader
├── handler.py               # AWS Lambda entry point
├── main.py                  # Main application entry point
├── requirements.txt         # Production / AWS Lambda dependencies
├── requirements-dev.txt     # Development & testing dependencies
├── .env.example             # Environment variables template
├── .gitignore
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Valid Badminton North Harbour account credentials

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/vincenttao04/automated-court-booker.git
   cd automated-court-booker
   ```

2. **Create and activate a virtual environment** (optional but recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   # For local development (includes pytest)
   pip install -r requirements-dev.txt

   # For production deployment (AWS Lambda)
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:

   ```env
   ## Login Credentials
   USER_NUMBER = "your_user_number"
   USER_PASSWORD = "your_user_password"

   ## API Endpoints (already configured)

   ## Optional: Remote config (for AWS Lambda deployment)
   CONFIG_URL = ""
   ```

5. **Configure booking preferences**

   Edit `config.yaml` to define your booking schedule and preferences

   ```yaml
   # Available locations
   locations:
     - bond_crescent
     - corinthian_drive

   price_per_court: 27

   # Weekly schedule (time in 24-hour format: "HH:MM")
   schedule:
     monday: null
     tuesday: null
     wednesday:
       start: "19:00"
       end: "21:00"
     thursday: null
     friday: null
     saturday: null
     sunday:
       start: "12:00"
       end: "19:00"
       location: "bond_crescent" # Optional: override default location
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

## Configuration

### config.yaml Options

| Field                     | Type      | Description                                               | Required |
| ------------------------- | --------- | --------------------------------------------------------- | -------- |
| `locations`               | list      | Available court locations (first location listed is used) | Yes      |
| `price_per_court`         | int       | Price per hour slot                                       | Yes      |
| `schedule`                | dict      | Weekly booking schedule by day                            | Yes      |
| `schedule.<day>`          | dict/null | Day-specific settings or `null` to skip booking           | Yes      |
| `schedule.<day>.start`    | string    | Preferred start time (24-hour format: "HH:MM")            | No       |
| `schedule.<day>.end`      | string    | Preferred end time (24-hour format: "HH:MM")              | No       |
| `schedule.<day>.location` | string    | Location override for specific day                        | No       |

**Time Format Notes:**

- Times must be in 24-hour format (e.g. `"19:00"`, not `"7:00 PM"`)
- Leading zeros are required (e.g. `"09:00"`)
- If `start` is omitted, defaults to `"06:00"`
- If `end` is omitted, defaults to `"23:00"`
- If a day is set to `null`, no booking attempt is made

### Environment Variables

See `.env.example` for all required variables. Key variables:

- `USER_NUMBER`: Your Badminton North Harbour account user number
- `USER_PASSWORD`: Your Badminton North Harbour account user password
- `CONFIG_URL`: (Optional) Remote YAML config URL for AWS Lambda deployment

## Testing

The project includes a comprehensive test suite using pytest:

```bash
# Run all tests
python -m pytest -v

# Run tests with output printed
python -m pytest -v -s

# Run a specific test file
python -m pytest tests/test_booking.py -v
```

## AWS Lambda Deployment

(coming soon)

## Troubleshooting

### Common Issues

**"LOGIN FAILED"**

- Verify that `USER_NUMBER` and `USER_PASSWORD` are correct
- Ensure the account is active and in good standing

**"No available courts found"**

- Adjust the preferred time range in `config.yaml`
- Check whether courts are already fully booked for the target date
- Verify the configured location is correct

**"FETCH COURT AVAILABILITY FAILED"**

- Check your internet connection
- Verify API endpoints are accessible
- Confirm the booking system is not undergoing maintenance

**"Payment Success" not found**

- Insufficient credit balance
- Payment processing error (check email for details)

## Limitations

- **Booking window constraints**: The application can only book courts within the venue’s allowed advance booking window (up to three weeks ahead). This is an external limitation.
- **Sequential execution**: Court availability is checked and booked sequentially to avoid double bookings. The application does not perform parallel booking attempts.
- **No retry or backoff logic**: If a booking, availability fetch, or payment step fails, the process exits without automatic retries.
- **Dependency on external system availability**: Successful booking depends on the stability and responsiveness of the Badminton North Harbour booking system. This is an external limitation.
- **Limited error recovery**: Partial failures (such as payment issues after booking) may require manual review via the confirmation email.

## Future Improvements

1. **Web dashboard**: Create a UI for managing preferences and viewing booking history
2. **Better error handling**: More granular error messages and retry logic

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Vincent Tao** - [@vincenttao04](https://github.com/vincenttao04)

## Disclaimer

This tool is designed for personal use to automate legitimate court bookings. Users are responsible for:

- Complying with Badminton North Harbour's terms of service
- Not abusing the booking system
- Ensuring bookings are actually used (not hoarding courts)
- Respecting fair usage policies

## Acknowledgments

- Badminton North Harbour for providing the booking platform
- The Python community for excellent libraries and tools

---

**Note**: This is an independent project and is not officially affiliated with or endorsed by Badminton North Harbour.
