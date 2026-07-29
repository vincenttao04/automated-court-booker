# Standard Library
import asyncio
import os
import random

# Third-Party Libraries
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from dotenv import load_dotenv

# Local Application Imports
from app.utils import check_status

import json
import urllib.parse

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()

LOGIN_API = os.getenv("LOGIN_API")
LOGIN_URL = os.getenv("LOGIN_URL")
SCHEDULE_URL = os.getenv("SCHEDULE_URL")
STORAGE_STATE_PATH = "browser_state.json"

BOOKING_CONFIRM_PATH = "/payment/booking-confirm"
BOOKING_API_PATH = "/api/v1/bookings/create"


# Helper function: simulate human-like pause for a random duration
async def human_pause(min_s: float, max_s: float) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


async def _playwright_login(user_number: str, user_password: str) -> dict:
    if not LOGIN_API or not LOGIN_URL or not SCHEDULE_URL:
        raise RuntimeError(
            "PLAYWRIGHT LOGIN FAILED: missing env variable(s) - LOGIN_API, LOGIN_URL and/or SCHEDULE_URL"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")

        # Realistic browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            storage_state=(
                STORAGE_STATE_PATH if os.path.exists(STORAGE_STATE_PATH) else None
            ),
        )

        page = await context.new_page()
        page.set_default_timeout(30_000)  # 30 seconds

        try:
            # Warm up session - visit home page first before login
            await page.goto(
                SCHEDULE_URL,
                wait_until="networkidle",
            )
            await human_pause(1.5, 2.5)

            # Navigate to login page
            await page.goto(
                LOGIN_URL,
                wait_until="networkidle",
            )

            # Wait for fields to exist before filling in credentials
            number = page.locator('input[type="text"]')
            password = page.locator('input[type="password"]')

            # Fill in credentials with human-like typing and behaviour
            await human_pause(0.5, 1.2)
            for char in user_number:
                await number.press_sequentially(char)
                await human_pause(0.06, 0.1)
            await human_pause(0.3, 0.8)
            for char in user_password:
                await password.press_sequentially(char)
                await human_pause(0.08, 0.12)
            await human_pause(0.4, 1.0)

            # Capture the login API response
            async with page.expect_response(
                lambda r: r.url == LOGIN_API and r.request.method == "POST",
            ) as response_info:
                await page.click('button[type="submit"]')

            response = await response_info.value
            login_response_data = await response.json()

        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"PLAYWRIGHT LOGIN FAILED: timed out - {e}")

        finally:
            await context.storage_state(path=STORAGE_STATE_PATH)
            await context.close()
            await browser.close()

    if not login_response_data:
        raise RuntimeError("PLAYWRIGHT LOGIN FAILED: no API response captured")

    # Check if login was successful
    check_status(login_response_data, "PLAYWRIGHT LOGIN")

    return login_response_data


def browser_login(user_number: str, user_password: str) -> dict:
    return asyncio.run(_playwright_login(user_number, user_password))


BOOKING_INFO_PATH = "/payment/booking-info"


async def _playwright_book_court(booking_info) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            storage_state=(
                STORAGE_STATE_PATH if os.path.exists(STORAGE_STATE_PATH) else None
            ),
        )

        page = await context.new_page()
        page.set_default_timeout(30_000)

        try:
            # Build booking info page URL
            encoded_data = urllib.parse.quote(
                json.dumps(booking_info, separators=(",", ":"))
            )
            url = f"{SCHEDULE_URL}{BOOKING_INFO_PATH}?data={encoded_data}"

            await page.goto(url, wait_until="networkidle")
            await human_pause(1.5, 2.5)

            # Capture the create booking API response
            async with page.expect_response(
                lambda r: BOOKING_API_PATH in r.url and r.request.method == "POST",
            ) as response_info:
                await page.click('button:has-text("Continue")')

            response = await response_info.value
            data = await response.json()

            check_status(data, "CREATE BOOKING")

            user_id = data["data"]["user_id"]
            booking_id = data["data"]["id"]

            ##
            payment_api = os.getenv("PAYMENT_API")
            payment_url = f"{payment_api}?user_id={user_id}&order_id={booking_id}"

            payment_page_html = await page.evaluate(
                """
                async (url) => {
                    const res = await fetch(url);
                    return await res.text();
                }
            """,
                payment_url,
            )

            print(f"payment page response: {payment_page_html[:500]}")  # temporary

            # Extract signed URL from HTML
            import re

            match = re.search(r'data-url="([^"]+)"', payment_page_html)
            if not match:
                raise RuntimeError(
                    "COURT PAYMENT FAILED: could not find signed payment URL"
                )

            signed_payment_url = match.group(1).replace("&amp;", "&")
            print(f"signed url found: {signed_payment_url[:50]}...")

            return signed_payment_url

        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"PLAYWRIGHT BOOK COURT: timed out - {e}")

        finally:
            await context.storage_state(path=STORAGE_STATE_PATH)
            await context.close()
            await browser.close()


def browser_book_court(booking_info: dict) -> str:
    return asyncio.run(_playwright_book_court(booking_info))


#### TODO: CHECK IF BROWSWER STATE IS OKAY? HEADLESS CHROME - DOES IT HAVE TO OPEN, WILL IT WORK IN AWS?
#### TODO: clean up codebase, refactor everything as necessary. redeploy to aws, check other files needed to upload to s3 bucket (cookies?), make pipeline for github to aws auto deploy?
