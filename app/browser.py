# Standard Library
import asyncio
import os
import random

# Third-Party Libraries
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

STORAGE_STATE_PATH = "browser_state.json"


async def _playwright_login(user_number: str, user_password: str) -> dict:
    LOGIN_API = os.getenv("LOGIN_API")
    SCHEDULE_URL = os.getenv("SCHEDULE_URL")
    LOGIN_URL = os.getenv("LOGIN_URL")

    if not LOGIN_API or not SCHEDULE_URL or not LOGIN_URL:
        raise RuntimeError("Missing env variables")

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
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # Navigate to login page
            await page.goto(
                LOGIN_URL,
                wait_until="networkidle",
            )

            # Wait for fields to exist before filling in credentials
            await page.wait_for_selector('input[type="text"]')
            await page.wait_for_selector('input[type="password"]')

            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.type(
                'input[type="text"]', user_number, delay=random.randint(60, 120)
            )
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await page.type(
                'input[type="password"]', user_password, delay=random.randint(60, 120)
            )
            await asyncio.sleep(random.uniform(0.4, 1.0))

            # Capture the login API response
            async with page.expect_response(
                lambda r: r.url == LOGIN_API and r.request.method == "POST",
            ) as response_info:
                await page.click('button[type="submit"]')

            response = await response_info.value
            login_response_data = await response.json()

        except PlaywrightTimeoutError as e:
            raise Exception(f"PLAYWRIGHT LOGIN FAILED: timed out - {e}")

        finally:
            await context.storage_state(path=STORAGE_STATE_PATH)
            await context.close()
            await browser.close()

    if not login_response_data:
        raise Exception("PLAYWRIGHT LOGIN FAILED: no API response captured")

    # Check if login was successful
    if login_response_data.get("status") != "success":
        raise Exception(
            f"LOGIN FAILED: {login_response_data.get('message', 'Unknown error')}"
        )

    return login_response_data


def browser_login(user_number: str, user_password: str) -> dict:
    return asyncio.run(_playwright_login(user_number, user_password))
