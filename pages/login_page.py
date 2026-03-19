import logging

from playwright.sync_api import Page

from pages.base_page import BasePage
from config.settings import BASE_URL

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    URL = f"{BASE_URL}/web/index.php/auth/login"

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> None:
        self.navigate(self.URL)

    def login(self, username: str, password: str) -> None:
        logger.info(f"Logging in as '{username}'")
        self.page.get_by_placeholder("Username").fill(username)
        self.page.get_by_placeholder("Password").fill(password)
        self.page.get_by_role("button", name="Login").click()
        # Wait for the left nav menu — only present after successful login
        self.page.wait_for_selector(".oxd-main-menu", timeout=15_000)
        logger.info("Login successful")
