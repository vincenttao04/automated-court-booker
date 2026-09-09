# Standard Library
import asyncio
from datetime import datetime, timedelta
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
from app.constants import NZ_TZ, PREWARM_LEAD_SECONDS
from app.models import BookingInformation
from app.utils import check_status

if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
LOGIN_API = os.getenv("LOGIN_API")
SCHEDULE_URL = os.getenv("SCHEDULE_URL")
BOOKING_API = os.getenv("BOOKING_API")
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")

_cached_user_agent: str | None = None


# Helper function: sleep until a given moment, returning immediately if it has passed
async def sleep_until(moment: datetime) -> None:
    remaining = (moment - datetime.now(NZ_TZ)).total_seconds()
    if remaining > 0:
        await asyncio.sleep(remaining)


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


# Helper function: simulate human-like typing by pressing keys sequentially
async def human_type(locator: Locator, text: str, min_s: float, max_s: float) -> None:
    for char in text:
        await locator.press_sequentially(char)
        await human_pause(min_s, max_s)


async def _playwright_login(
    user_number: str, user_password: str, user_agent: str
) -> dict:
    if not LOGIN_API or not LOGIN_URL or not SCHEDULE_URL or not CHROME_PROFILE_PATH:
        raise RuntimeError(
            "PLAYWRIGHT LOGIN FAILED: missing env variable(s) - LOGIN_API, LOGIN_URL, SCHEDULE_URL and/or CHROME_PROFILE_PATH"
        )

    async with async_playwright() as p:
        # Persistent Chrome profile provides the browsing identity reCAPTCHA v3 scores on
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE_PATH,
            headless=True,
            channel="chrome",
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            user_agent=user_agent,
        )
        # A persistent context opens with a page already; reuse it instead of adding a blank tab
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(30_000)  # 30 seconds

        try:
            # Warm up session - visit home page first before login
            print("browser: warming up session")
            await page.goto(
                SCHEDULE_URL,
                wait_until="networkidle",
            )
            await human_pause(1.0, 1.75)

            # Navigate to login page
            print("browser: navigating to login page")
            await page.goto(
                LOGIN_URL,
                wait_until="networkidle",
            )

            # Wait for fields to exist before filling in credentials
            number = page.locator('input[type="text"]')
            password = page.locator('input[type="password"]')

            # Fill in credentials with human-like typing and behaviour
            print("browser: entering credentials")
            await human_pause(0.8, 1.4)
            await human_type(number, user_number, 0.05, 0.12)
            await human_pause(0.5, 1.0)
            await human_type(password, user_password, 0.08, 0.2)
            await human_pause(1.0, 1.6)

            # Capture the login API response
            print("browser: submitting login")
            async with page.expect_response(
                lambda r: r.url == LOGIN_API and r.request.method == "POST",
            ) as response_info:
                await page.click('button[type="submit"]')

            response = await response_info.value
            login_response_data = await response.json()

        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"PLAYWRIGHT LOGIN FAILED: timed out - {e}")

        finally:
            await context.close()
            print("")

    if not login_response_data:
        raise RuntimeError("PLAYWRIGHT LOGIN FAILED: no API response captured")

    # Check if login was successful
    check_status(login_response_data, "PLAYWRIGHT LOGIN")

    return login_response_data


def browser_login(user_number: str, user_password: str) -> dict:
    return asyncio.run(_playwright_login(user_number, user_password, get_user_agent()))


async def _playwright_book_court(
    booking_info: BookingInformation, user_agent: str, target: datetime | None
) -> str:
    if not BOOKING_API or not SCHEDULE_URL or not CHROME_PROFILE_PATH:
        raise RuntimeError(
            "PLAYWRIGHT BOOK COURT FAILED: missing env variable(s) - BOOKING_API, SCHEDULE_URL and/or CHROME_PROFILE_PATH"
        )

    async with async_playwright() as p:
        # Hold off launching so the loaded page and minted reCAPTCHA token stays fresh
        if target is not None:
            await sleep_until(target - timedelta(seconds=PREWARM_LEAD_SECONDS))

        # Persistent Chrome profile provides the browsing identity reCAPTCHA v3 scores on
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE_PATH,
            headless=True,
            channel="chrome",
            viewport={"width": 1280, "height": 800},
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
            user_agent=user_agent,
        )
        # A persistent context opens with a page already; reuse it instead of adding a blank tab
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(30_000)  # 30 seconds

        try:
            # Build booking info page URL
            encoded_data = urllib.parse.quote(
                json.dumps(asdict(booking_info), separators=(",", ":"))
            )
            url = f"{SCHEDULE_URL}/payment/booking-info?data={encoded_data}"

            # The page renders client-side from the URL, so it can be loaded before the
            # booking window opens; only the Continue click is validated server-side
            print("browser: loading booking page")
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('button:has-text("Continue")')

            if target is None:
                await human_pause(0.2, 0.35)
            else:
                spare = (target - datetime.now(NZ_TZ)).total_seconds()
                print(f"browser: ready with {spare:.4f}s to spare")
                await sleep_until(target)

            # Capture the create booking API response
            print("browser: creating booking")
            async with page.expect_response(
                lambda r: r.url == BOOKING_API and r.request.method == "POST",
            ) as response_info:
                await page.click('button:has-text("Continue")')

            response = await response_info.value
            data = await response.json()

            check_status(data, "CREATE BOOKING")

            # Navigate to the payment page and click the "Pay Now" button
            print("browser: proceeding to payment")
            await page.wait_for_selector('button:has-text("Pay Now")', timeout=30_000)
            await human_pause(0.2, 0.35)

            await page.click('button:has-text("Pay Now")')

            await page.wait_for_load_state("networkidle")
            await human_pause(0.2, 0.35)

            payment_page_html = await page.content()

            # Extract signed URL from HTML
            match = re.search(r'data-url="([^"]+)"', payment_page_html)
            if not match:
                raise RuntimeError(
                    "COURT PAYMENT FAILED: could not find signed payment URL"
                )

            signed_payment_url = match.group(1).replace("&amp;", "&")
            print("browser: payment url retrieved")
            return signed_payment_url

        except PlaywrightTimeoutError as e:
            raise RuntimeError(f"PLAYWRIGHT BOOK COURT FAILED: timed out - {e}")

        finally:
            await context.close()
            print("")


def browser_book_court(
    booking_info: BookingInformation, target: datetime | None
) -> str:
    return asyncio.run(_playwright_book_court(booking_info, get_user_agent(), target))
