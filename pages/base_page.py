import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BasePage:
    """Common helpers shared by all page objects."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> None:
        logger.info(f"Navigating to {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def click(self, selector: str) -> None:
        logger.info(f"Clicking: {selector}")
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        logger.info(f"Filling '{selector}' with '{value}'")
        self.page.locator(selector).fill(value)

    def select_dropdown_option(self, dropdown_locator, option_text: str) -> None:
        """Click an oxd-select dropdown and choose an option by visible text."""
        dropdown_locator.click()
        self.page.locator(
            f".oxd-select-dropdown [role='option']:has-text('{option_text}')"
        ).click()
