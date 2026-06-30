# Standard Library
import asyncio
import os
import random

# Third-Party Libraries
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

LOGIN_API = os.environ["LOGIN_API"]
LOGIN_URL = os.environ["LOGIN_URL"]
SCHEDULE_URL = os.environ["SCHEDULE_URL"]
STORAGE_STATE_PATH = "browser_state.json"


# Helper function: simulate human-like pause for a random duration
async def human_pause(min_s, max_s):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def _playwright_login(user_number: str, user_password: str) -> dict:
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
                await asyncio.sleep(random.uniform(0.06, 0.1))
            await human_pause(0.3, 0.8)
            for char in user_password:
                await password.press_sequentially(char)
                await asyncio.sleep(random.uniform(0.08, 0.12))
            await human_pause(0.4, 1.0)

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
