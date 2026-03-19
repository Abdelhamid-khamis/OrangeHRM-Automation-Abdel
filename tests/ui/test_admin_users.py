"""
UI Test — Admin User Management
Covers all 13 steps from the QA assessment task.
"""
import logging

import pytest
from playwright.sync_api import Page

from pages.admin_page import AdminPage
from config.settings import DEFAULT_PASSWORD
from utils.helpers import generate_username

logger = logging.getLogger(__name__)


@pytest.mark.ui
class TestAdminUserManagement:

    def test_add_search_delete_user(self, logged_in_page: Page) -> None:
        """
        Steps:
        1.  Navigate to OrangeHRM                   (handled by logged_in_page fixture)
        2.  Login as Admin / admin123               (handled by logged_in_page fixture)
        3.  Login as Admin / admin123               ^^^
        4.  Click Login button                      ^^^
        5.  Click Admin tab in the left menu
        6.  Get the number of records found
        7.  Click Add
        8.  Fill required user details (dynamic username)
        9.  Click Save
        10. Verify records increased by 1
        11. Search for the new user by username
        12. Delete the new user
        13. Verify records decreased by 1
        """
        admin = AdminPage(logged_in_page)
        username = generate_username()
        logger.info(f"Test username: '{username}'")

        # ── Steps 1–4: Login is handled by the logged_in_page fixture ──────

        # ── Step 5: Click Admin tab (navigate to Admin users list) ─────────
        admin.goto()
        admin.cleanup_stale_test_users()  # remove orphans from previous failed runs

        # ── Step 6: Capture initial record count ───────────────────────────
        initial_count = admin.get_record_count()
        logger.info(f"Initial count: {initial_count}")

        # ── Steps 7–9: Add new user ─────────────────────────────────────────
        admin.click_add()
        admin.fill_user_form(username=username, password=DEFAULT_PASSWORD)
        admin.save_user()

        # ── Step 10: Verify count increased by 1 ────────────────────────────
        count_after_add = admin.get_record_count()
        assert count_after_add == initial_count + 1, (
            f"Expected {initial_count + 1} records after add, got {count_after_add}"
        )
        logger.info(f"Count after add: {count_after_add} ✓")

        # ── Step 11: Search for the newly created user ───────────────────────
        admin.search_by_username(username)
        search_count = admin.get_record_count()
        assert search_count == 1, (
            f"Expected exactly 1 result for '{username}', got {search_count}"
        )
        logger.info(f"Search result count: {search_count} ✓")

        # ── Step 12: Delete the user ─────────────────────────────────────────
        admin.delete_user_from_results(username)

        # ── Step 13: Reset search, verify count decreased by 1 ───────────────
        admin.reset_search()
        count_after_delete = admin.get_record_count()
        assert count_after_delete == initial_count, (
            f"Expected {initial_count} records after delete, got {count_after_delete}"
        )
        logger.info(f"Count after delete: {count_after_delete} ✓")
