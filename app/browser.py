# Standard Library
import asyncio

# Third-Party Libraries
from playwright.async_api import async_playwright, Response
from playwright_stealth import Stealth

BOOKING_FRONTEND = "https://book.bnh.org.nz"
LOGIN_API_PATH = "/api/v1/auth/login"


async def _playwright_login(user_number: str, user_password: str) -> dict:
    login_response_data: dict = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

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

        # Capture the login API response
        async def handle_response(response: Response) -> None:
            if LOGIN_API_PATH in response.url and response.request.method == "POST":
                try:
                    login_response_data.update(await response.json())
                except Exception:
                    pass

        page.on("response", handle_response)

        # Navigate to login page and fill credentials
        await page.goto(f"{BOOKING_FRONTEND}/auth/login", wait_until="networkidle")
        await page.fill('input[type="text"]', user_number)
        await page.fill('input[type="password"]', user_password)
        await page.click('button[type="submit"]')

        # Wait for the login API call to complete
        await page.wait_for_timeout(3000)

        await context.close()
        await browser.close()

    if not login_response_data:
        raise Exception("PLAYWRIGHT LOGIN: no API response captured")

    return login_response_data


def browser_login(user_number: str, user_password: str) -> dict:
    return asyncio.run(_playwright_login(user_number, user_password))
