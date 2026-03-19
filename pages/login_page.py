import logging

from playwright.sync_api import Page

from pages.base_page import BasePage
from config.settings import BASE_URL

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    URL = f"{BASE_URL}/web/index.php/auth/login"

    # Selectors
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    SUBMIT_BUTTON = "button[type='submit']"

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> None:
        self.navigate(self.URL)

    def login(self, username: str, password: str) -> None:
        logger.info(f"Logging in as '{username}'")
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.page.locator(self.SUBMIT_BUTTON).click()
        self.page.wait_for_url("**/dashboard**", timeout=15_000)
        logger.info("Login successful")
