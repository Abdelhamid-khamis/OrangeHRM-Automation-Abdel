import logging
import re

from playwright.sync_api import Page

from pages.base_page import BasePage
from config.settings import BASE_URL

logger = logging.getLogger(__name__)


class AdminPage(BasePage):
    """Page object for Admin > User Management > Users."""

    URL = f"{BASE_URL}/web/index.php/admin/viewSystemUsers"

    def __init__(self, page: Page):
        super().__init__(page)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def goto(self) -> None:
        """Navigate directly to the Admin users list page."""
        self.navigate(self.URL)
        self._wait_for_table()
        self._wait_for_record_count()

    # ------------------------------------------------------------------
    # Record count
    # ------------------------------------------------------------------

    def get_record_count(self) -> int:
        """
        Read and return the integer from '(N) Record(s) Found'.
        Returns 0 when OrangeHRM shows 'No Records Found' instead of a count.
        """
        self._wait_for_record_count()
        # No-results state: OrangeHRM shows "No Records Found" with no count element
        if self.page.locator("span, p").filter(has_text="No Records Found").count() > 0:
            logger.info("Record count: 0 (No Records Found)")
            return 0
        locator = self.page.locator("span, p").filter(
            has_text=re.compile(r"\(\d+\) Record")
        ).first
        text = locator.text_content(timeout=5_000)
        match = re.search(r"\((\d+)\)", text)
        if not match:
            raise ValueError(f"Cannot parse record count from: '{text}'")
        count = int(match.group(1))
        logger.info(f"Record count: {count}")
        return count

    # ------------------------------------------------------------------
    # Add user
    # ------------------------------------------------------------------

    def click_add(self) -> None:
        # codegen: button label is " Add" (leading space is part of the icon+text)
        self.page.get_by_role("button", name=" Add").click()
        self.page.wait_for_selector("input[placeholder='Type for hints...']", timeout=10_000)

    def fill_user_form(
        self,
        username: str,
        password: str,
        user_role: str = "ESS",
        employee_query: str = "a",
        status: str = "Enabled",
    ) -> None:
        """
        Fill the Add System User form.
        All selectors are taken directly from the Playwright codegen recording.
        """
        logger.info(f"Filling user form: username='{username}'")

        # --- User Role dropdown (first .oxd-select-text on the page) ---
        self.page.locator(".oxd-select-text").first.click()
        self.page.get_by_role("option", name=user_role).click()

        # --- Employee Name autocomplete ---
        # codegen: click → ArrowDown → fill → ArrowDown → ArrowDown → Enter
        emp = self.page.get_by_placeholder("Type for hints...")
        emp.fill(employee_query)
        # The dropdown initially shows "Searching..." — wait for real results
        real_option = self.page.locator(".oxd-autocomplete-option").filter(
            has_not_text="Searching"
        ).first
        real_option.wait_for(state="visible", timeout=10_000)
        real_option.click()

        # --- Status dropdown ---
        # codegen: filter div by exact text "-- Select --", pick nth(2)
        self.page.locator("div").filter(
            has_text=re.compile(r"^-- Select --$")
        ).nth(2).click()
        self.page.get_by_role("option", name=status).click()

        # --- Username: codegen confirmed textbox nth(2) ---
        self.page.get_by_role("textbox").nth(2).fill(username)

        # --- Password / Confirm Password: textbox nth(3) and nth(4) ---
        self.page.get_by_role("textbox").nth(3).fill(password)
        self.page.get_by_role("textbox").nth(4).fill(password)

    def save_user(self) -> None:
        self.page.get_by_role("button", name="Save").click()
        # Wait for redirect back to the users list
        self._wait_for_table()
        self._wait_for_record_count()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_by_username(self, username: str) -> None:
        logger.info(f"Searching for username='{username}'")
        # codegen: on the list page the username search input is textbox nth(1)
        self.page.get_by_role("textbox").nth(1).fill(username)
        self.page.get_by_role("button", name="Search").click()
        self._wait_for_table()

    def reset_search(self) -> None:
        """Clear all search filters. Uses a full page reload for reliability —
        clicking the Reset button has a race condition where the old state
        is briefly still visible before the new count loads."""
        self.goto()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_user_from_results(self, username: str) -> None:
        """
        Delete the user row matching username from the current table view.
        Scopes the delete-icon click to the specific row to avoid hitting
        the wrong user when multiple rows are present.
        """
        logger.info(f"Deleting user '{username}'")
        row = self.page.locator(".oxd-table-row").filter(has_text=username)
        # Target the trash icon button explicitly — OrangeHRM orders delete(0) before edit(1)
        row.locator("button:has(.bi-trash)").click()
        # codegen: confirm button label is " Yes, Delete" (leading space)
        self.page.get_by_role("button", name=" Yes, Delete").click()
        self._wait_for_table()

    # ------------------------------------------------------------------
    # Test hygiene
    # ------------------------------------------------------------------

    def cleanup_stale_test_users(self, prefix: str = "auto_user_") -> None:
        """
        Delete any leftover test users from previous failed runs.
        Always ends with a full page reload so the caller gets a clean state.
        """
        logger.info(f"Cleaning up stale test users with prefix='{prefix}'")
        self.search_by_username(prefix)
        count = self.get_record_count()
        if count == 0:
            logger.info("No stale test users found")
        else:
            logger.info(f"Found {count} stale test user(s) — deleting")
            for _ in range(count):
                row = self.page.locator(".oxd-table-row").nth(1)  # always first data row
                row.locator("button:has(.bi-trash)").click()
                self.page.get_by_role("button", name=" Yes, Delete").click()
                self._wait_for_table()
            logger.info("Stale test users cleaned up")
        # Full reload — ensures no search filter is active before caller reads count
        self.goto()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _wait_for_table(self) -> None:
        """Wait until the table body is in the DOM.
        It is visible when records exist and hidden when 0 results — both are valid."""
        self.page.wait_for_selector(".oxd-table-body", state="attached", timeout=15_000)

    def _wait_for_record_count(self) -> None:
        """Wait until search results are fully loaded.
        Accepts either '(N) Record(s) Found' or 'No Records Found'."""
        self.page.locator("span, p").filter(
            has_text=re.compile(r"\(\d+\) Record|No Records Found")
        ).first.wait_for(state="visible", timeout=10_000)
