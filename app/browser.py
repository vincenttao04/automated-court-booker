# Standard Library
import asyncio
import json
import os
import random
import re
import urllib.parse
from dataclasses import asdict

# Third-Party Libraries
from dotenv import load_dotenv
from playwright.async_api import (
    async_playwright,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
)

# Local Application Imports
from app.models import BookingInformation
from app.utils import check_status

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
LOGIN_API = os.getenv("LOGIN_API")
SCHEDULE_URL = os.getenv("SCHEDULE_URL")
BOOKING_API = os.getenv("BOOKING_API")
STORAGE_STATE_PATH = "browser_state.json"

_cached_user_agent: str | None = None


# Helper function: fetch the corrected user agent string
# Removes the "Headless" token from default user agent reported by Playwright
async def _fetch_user_agent() -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")
        context = await browser.new_context()
        page = await context.new_page()
        raw_ua = await page.evaluate("navigator.userAgent")
        await context.close()
        await browser.close()
    return raw_ua.replace("HeadlessChrome/", "Chrome/")


# Helper function: get the cached user agent string, or fetch it if not cached
def get_user_agent() -> str:
    global _cached_user_agent
    if _cached_user_agent is None:
        _cached_user_agent = asyncio.run(_fetch_user_agent())
    return _cached_user_agent


# Helper function: simulate human-like pause for a random duration
async def human_pause(min_s: float, max_s: float) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


# TODO
# Helper function: simulate human-like typing by pressing keys sequentially
async def human_type(locator: Locator, text: str, min_s: float, max_s: float) -> None:
    for char in text:
        await locator.press_sequentially(char)
        await human_pause(min_s, max_s)


async def _playwright_login(
    user_number: str, user_password: str, user_agent: str
) -> dict:
    if not LOGIN_API or not LOGIN_URL or not SCHEDULE_URL:
        raise RuntimeError(
            "PLAYWRIGHT LOGIN FAILED: missing env variable(s) - LOGIN_API, LOGIN_URL and/or SCHEDULE_URL"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")

        # Realistic browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            storage_state=(
                STORAGE_STATE_PATH if os.path.exists(STORAGE_STATE_PATH) else None
            ),
            user_agent=user_agent,
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
            await human_type(number, user_number, 0.06, 0.1)
            await human_pause(0.3, 0.8)
            await human_type(password, user_password, 0.08, 0.12)
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
    return asyncio.run(_playwright_login(user_number, user_password, get_user_agent()))


async def _playwright_book_court(
    booking_info: BookingInformation, user_agent: str
) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")

        # Realistic browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            storage_state=(
                STORAGE_STATE_PATH if os.path.exists(STORAGE_STATE_PATH) else None
            ),
            user_agent=user_agent,
        )

        page = await context.new_page()
        page.set_default_timeout(30_000)  # 30 seconds

        try:
            # Build booking info page URL
            encoded_data = urllib.parse.quote(
                json.dumps(asdict(booking_info), separators=(",", ":"))
            )
            url = f"{SCHEDULE_URL}/payment/booking-info?data={encoded_data}"

            # Navigate to booking create page
            await page.goto(url, wait_until="networkidle")
            await human_pause(1.5, 2.5)

            # Capture the create booking API response
            async with page.expect_response(
                lambda r: r.url == BOOKING_API and r.request.method == "POST",
            ) as response_info:
                await page.click('button:has-text("Continue")')

            response = await response_info.value
            data = await response.json()

            check_status(data, "CREATE BOOKING")

            # Navigate to the payment page and click the "Pay Now" button
            await page.wait_for_selector('button:has-text("Pay Now")', timeout=30_000)
            await human_pause(1.0, 2.0)
            await page.click('button:has-text("Pay Now")')

            await page.wait_for_load_state("networkidle")
            await human_pause(1.0, 2.0)

            payment_page_html = await page.content()

            # Extract signed URL from HTML
            match = re.search(r'data-url="([^"]+)"', payment_page_html)
            if not match:
                raise RuntimeError(
                    "COURT PAYMENT FAILED: could not find signed payment URL"
                )

            signed_payment_url = match.group(1).replace("&amp;", "&")
            return signed_payment_url

        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"PLAYWRIGHT BOOK COURT: timed out - {e}")

        finally:
            await context.storage_state(path=STORAGE_STATE_PATH)
            await context.close()
            await browser.close()


def browser_book_court(booking_info: BookingInformation) -> str:
    return asyncio.run(_playwright_book_court(booking_info, get_user_agent()))
