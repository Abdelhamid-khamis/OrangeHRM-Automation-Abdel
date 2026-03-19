import logging
import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from config.settings import BASE_URL

logger = logging.getLogger(__name__)


class AdminPage(BasePage):
    """Page object for Admin > User Management > Users."""

    URL = f"{BASE_URL}/web/index.php/admin/viewSystemUsers"

    # --- Main list page ---
    ADD_BUTTON = "button:has-text('Add')"
    RECORD_COUNT_TEXT = ".orangehrm-record-count"
    SEARCH_BUTTON = "button[type='submit']:has-text('Search')"
    RESET_BUTTON = "button[type='button']:has-text('Reset')"

    # --- Add/Edit user form ---
    SAVE_BUTTON = "button[type='submit']:has-text('Save')"
    EMPLOYEE_NAME_INPUT = "input[placeholder='Type for hints...']"
    AUTOCOMPLETE_OPTION = ".oxd-autocomplete-dropdown .oxd-autocomplete-option"

    # --- Confirm deletion dialog ---
    CONFIRM_DELETE_BUTTON = "button:has-text('Yes, Delete')"

    def __init__(self, page: Page):
        super().__init__(page)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def goto(self) -> None:
        self.navigate(self.URL)
        self._wait_for_table()

    # ------------------------------------------------------------------
    # Record count
    # ------------------------------------------------------------------

    def get_record_count(self) -> int:
        """Return the number shown in '(N) Record(s) Found'."""
        self._wait_for_table()
        text = self.page.locator(self.RECORD_COUNT_TEXT).text_content(timeout=10_000)
        match = re.search(r"\((\d+)\)", text)
        if not match:
            raise ValueError(f"Unexpected record count text: '{text}'")
        count = int(match.group(1))
        logger.info(f"Record count: {count}")
        return count

    # ------------------------------------------------------------------
    # Add user
    # ------------------------------------------------------------------

    def click_add(self) -> None:
        self.page.locator(self.ADD_BUTTON).click()
        self.page.wait_for_load_state("networkidle")

    def fill_user_form(
        self,
        username: str,
        password: str,
        user_role: str = "ESS",
        employee_name: str = "Admin",
        status: str = "Enabled",
    ) -> None:
        """Fill in all fields on the Add System User form."""
        logger.info(f"Filling user form for username='{username}'")

        # User Role dropdown (first .oxd-select-text on the page)
        self.select_dropdown_option(
            self.page.locator(".oxd-select-text").nth(0), user_role
        )

        # Employee Name (autocomplete)
        self.page.locator(self.EMPLOYEE_NAME_INPUT).fill(employee_name)
        self.page.locator(self.AUTOCOMPLETE_OPTION).first.click()

        # Status dropdown (second .oxd-select-text on the page)
        self.select_dropdown_option(
            self.page.locator(".oxd-select-text").nth(1), status
        )

        # Username — the input inside the form group labelled "Username"
        self._fill_form_field("Username", username)

        # Password fields
        self.page.locator("input[type='password']").nth(0).fill(password)
        self.page.locator("input[type='password']").nth(1).fill(password)

    def save_user(self) -> None:
        self.page.locator(self.SAVE_BUTTON).click()
        # After save we're redirected back to the users list
        self.page.wait_for_url("**/viewSystemUsers**", timeout=15_000)
        self._wait_for_table()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_by_username(self, username: str) -> None:
        logger.info(f"Searching for username='{username}'")
        self._fill_form_field("Username", username)
        self.page.locator(self.SEARCH_BUTTON).click()
        self._wait_for_table()

    def reset_search(self) -> None:
        self.page.locator(self.RESET_BUTTON).click()
        self._wait_for_table()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_user_from_results(self, username: str) -> None:
        """Delete the first row matching username in the current table view."""
        logger.info(f"Deleting user '{username}'")
        row = self.page.locator(".oxd-table-row").filter(has_text=username)
        # Delete icon is the second action button (pencil=0, trash=1)
        row.locator(".oxd-icon-button").nth(1).click()
        self.page.locator(self.CONFIRM_DELETE_BUTTON).click()
        self._wait_for_table()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _wait_for_table(self) -> None:
        """Wait until the results table is visible."""
        self.page.wait_for_selector(".oxd-table", timeout=15_000)

    def _fill_form_field(self, label: str, value: str) -> None:
        """Find the input inside the form group whose label contains `label`."""
        group = self.page.locator(
            f".oxd-form-group:has(.oxd-label:has-text('{label}'))"
        )
        group.locator("input").fill(value)
