# Standard Library
import asyncio
import random

# Third-Party Libraries
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from playwright_stealth import Stealth

BOOKING_FRONTEND = "https://book.bnh.org.nz"
LOGIN_API_PATH = "/api/v1/auth/login"
TIMEOUT_MS = 30_000


async def _playwright_login(user_number: str, user_password: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")

        # Realistic browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-NZ",
            timezone_id="Pacific/Auckland",
        )

        page = await context.new_page()

        # Stealth masks headless signals
        await Stealth().apply_stealth_async(page)

        try:
            # Navigate to login page
            await page.goto(
                f"{BOOKING_FRONTEND}/auth/login",
                wait_until="networkidle",
                timeout=TIMEOUT_MS,
            )

            # Wait for fields to exist before filling in credentials
            await page.wait_for_selector('input[type="text"]', timeout=TIMEOUT_MS)
            await page.wait_for_selector('input[type="password"]', timeout=TIMEOUT_MS)

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
                lambda r: LOGIN_API_PATH in r.url and r.request.method == "POST",
                timeout=TIMEOUT_MS,
            ) as response_info:
                await page.click('button[type="submit"]')

            response = await response_info.value
            login_response_data = await response.json()

        except PlaywrightTimeoutError as e:
            raise Exception(f"PLAYWRIGHT LOGIN: timed out - {e}")

        finally:
            await context.close()
            await browser.close()

    if not login_response_data:
        raise Exception("PLAYWRIGHT LOGIN: no API response captured")

    return login_response_data


def browser_login(user_number: str, user_password: str) -> dict:
    return asyncio.run(_playwright_login(user_number, user_password))
