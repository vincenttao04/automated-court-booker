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
- [AWS Deployment - Lambda \& EventBridge](#aws-deployment---lambda--eventbridge)
  - [1. Packaging the Lambda Application](#1-packaging-the-lambda-application)
    - [Build the deployment package](#build-the-deployment-package)
    - [What the scripts do](#what-the-scripts-do)
  - [2. Uploading to AWS Lambda](#2-uploading-to-aws-lambda)
  - [3. Environment Variables](#3-environment-variables)
  - [4. Scheduling the Lambda Execution](#4-scheduling-the-lambda-execution)
    - [Scheduler Configuration](#scheduler-configuration)
  - [5. Verifying the Deployment](#5-verifying-the-deployment)
  - [6. Cost and Free Tier Usage](#6-cost-and-free-tier-usage)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [AWS Deployment](#aws-deployment)
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
- **Deployment Ready**: Structured for deployment on AWS Lambda and Amazon EventBridge for autonomous, unattended execution
- **Credit Balance Tracking**: Retrieves and reports account credit balance before and after bookings
- **Comprehensive Testing**: Includes a pytest test suite covering core booking and user logic

## Tech Stack

### Core Language

- **Python 3.14+** — Primary language used for automation, scheduling logic, and API interactions

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

- **AWS Lambda & Amazon EventBridge** — Serverless execution for autonomous, scheduled bookings
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
├── build-lambda.ps1         # PowerShell script to build the Lambda deployment package
├── build-lambda.sh          # Bash script to build the Lambda deployment package
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

- Python 3.14 or higher
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
   USER_NUMBER="your_user_number"
   USER_PASSWORD="your_user_password"

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

## AWS Deployment - Lambda & EventBridge

This project is deployed as a scheduled AWS Lambda function that runs automatically using Amazon EventBridge Scheduler. The deployment uses a ZIP-based Lambda package built locally and uploaded to AWS.

### 1. Packaging the Lambda Application

AWS Lambda runs on a Linux environment, so the deployment ZIP must be created with proper structure. Two build scripts are provided to create the Lambda deployment package (`build-lambda.sh`, `build-lambda.ps1`) - choose the one that matches your environment.

#### Build the deployment package

**Option A: Using Bash - `build-lambda.sh`**

**Requirements:**

- Python + pip available on PATH
- `zip` command installed
- Bash shell (Git Bash on Windows, native on macOS/Linux)

From the project root:

```bash
# Make script executable (one-time, macOS/Linux only)
chmod +x build-lambda.sh

# Run the build script
./build-lambda.sh
```

**Option B: Using PowerShell - `build-lambda.ps1`**

**Requirements:**

- Python + pip available on PATH
- PowerShell 5.1+ (Windows) or PowerShell 7+ (pwsh on any platform)

From the project root:

```powershell
# Windows PowerShell 5.1
powershell -ExecutionPolicy Bypass -File build-lambda.ps1

# OR PowerShell 7+ (pwsh) - Windows
pwsh build-lambda.ps1

# OR PowerShell 7+ (pwsh) - macOS/Linux
chmod +x build-lambda.ps1  # Make script executable (one-time only)
./build-lambda.ps1
```

#### What the scripts do

Both scripts perform the same operations:

1. Clean old artifacts (removes existing `package/` directory and `lambda.zip`)
2. Create a fresh `package/` directory
3. Install Python dependencies from `requirements.txt` into `package/`
4. Copy project files (`app/`, `main.py`, `handler.py`, `config_loader.py`, `config.yaml`) to `package/`
5. Remove `__pycache__` folders and `bin/` directory (reduces ZIP size)
6. Create `lambda.zip` with the packaged application

After running either script, `lambda.zip` will be created in the project root and is ready to upload to AWS Lambda.

### 2. Uploading to AWS Lambda

1. **Create a new AWS Lambda function**
2. **Choose the following settings:**
   - Runtime: Python 3.14 or higher
   - Architecture: `arm64`
3. **Upload the generated `lambda.zip`**
4. **Set the handler:**
   ```
   handler.lambda_handler
   ```
5. **Configure resources:**
   - Memory: 512 MB
   - Timeout: 30–60 seconds

This project uses ZIP-based deployment. Inline code edits in the AWS console may not save and deploy correctly.

### 3. Environment Variables

In production, the Lambda function does not use the `.env` file. The `.env` file is used only for local development. All secrets and endpoints must be provided via AWS Lambda Environment Variables.

Configure the following environment variables in:

```
Lambda → Configuration → Environment variables
```

**Required variables:**
Do not include quotes or comments in AWS environment variable values.

```
USER_NUMBER
USER_PASSWORD
LOGIN_URL
LOGOUT_URL
USER_DATA
COURT_SCHEDULE
BOOKING_URL
PAYMENT_URL
```

**Optional variables:**

```
CONFIG_URL  # S3 URL for hosted config.yaml (if using remote config)
```

### 4. Scheduling the Lambda Execution

The Lambda function is triggered automatically using **Amazon EventBridge Scheduler**.

#### Scheduler Configuration

1. Navigate to **Amazon EventBridge → Schedules**
2. Click **Create schedule**
3. Configure the schedule:
   - **Schedule name**: `automated-court-booker` (or your preferred name)
   - **Schedule type**: Recurring schedule
   - **Cron expression:**
     ```
     cron(0 0 * * ? *)
     ```
     _(Runs once per day at midnight)_
   - **Time zone**: Select your local time zone (e.g., `Pacific/Auckland` for New Zealand)
   - **Flexible time window**: Disabled

4. **Select target:**
   - **Target API**: AWS Lambda Invoke
   - **Lambda function**: Select the deployed AWS Lambda function
   - **Input**: Empty JSON object `{}`

5. **Review and create**

This configuration triggers the Lambda once per day at midnight (local time). Daylight saving time is handled automatically by EventBridge.

### 5. Verifying the Deployment

To verify the deployment:

**Option 1: Create a test schedule**

1. Create a temporary one-time schedule in EventBridge
2. Set it to trigger within a few minutes
3. Monitor CloudWatch Logs for execution

**Option 2: Use Lambda Test feature**

1. Navigate to your Lambda function in the AWS Console
2. Go to the **Test** tab
3. Create a new test event with an empty payload:
   ```json
   {}
   ```
4. Click **Test**

**Check CloudWatch Logs** for:

- Successful execution
- Correct New Zealand timestamps
- Expected output messages

**Expected output on a booking day:**

```
automated court booker !

_____LOGIN ATTEMPT_____
loading remote config

123456 login successful

_____BOOKING ATTEMPT_____

Credit Balance: 108

fetch court availability successful (2025-02-19)
longest availability: 2 slots/hours
court: 3, starting at 19:00, ending at 21:00
court payment successful - check email for confirmation/receipt
...
```

### 6. Cost and Free Tier Usage

This project runs well within AWS free tier limits:

- **AWS Lambda**: 1 invocation per day
- **EventBridge Scheduler**: 1 scheduled trigger per day
- **Execution time**: ~1–3 seconds per run
- **CloudWatch Logs**: Minimal log storage

**Monthly estimates (assuming 1 execution per day):**

- Lambda invocations: ~30/month (Free tier: 1M requests/month)
- Compute time: ~90 seconds/month (Free tier: 400,000 GB-seconds/month)
- EventBridge rules: 1 rule (Free tier: Always free for rules)

Under normal usage, the deployment should incur no AWS charges and stay well within the free tier.

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

### AWS Deployment

**Issue: "No module named 'app'" error**

- Ensure `lambda.zip` was created using the custom PowerShell or GitBash scripts provided (`build-lambda.ps1`, `build-lambda.sh`)
- Verify the ZIP contains the `app/` directory at the root level

**Issue: Environment variables not working**

- Check for quotes or extra whitespace in values
- Ensure variable names match exactly (case-sensitive)

**Issue: Scheduler not triggering**

- Verify the EventBridge schedule is in "Enabled" state
- Check the time zone matches your location
- Review EventBridge execution history

**Issue: Timeout errors**

- Increase Lambda timeout to 60 seconds
- Check internet connectivity from Lambda VPC (if using VPC)
- Verify API endpoints are accessible from AWS region

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
