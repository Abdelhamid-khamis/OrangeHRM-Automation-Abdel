"""
UI Test: Admin User Management
Covers: Add user → verify count → search → delete → verify count
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
        End-to-end scenario:
        1. Navigate to Admin > Users
        2. Record initial user count
        3. Add a new user with a dynamically generated username
        4. Verify the count increased by 1
        5. Search for the newly created user — expect exactly 1 result
        6. Delete the user from search results
        7. Verify the total count returned to the initial value
        """
        admin = AdminPage(logged_in_page)
        username = generate_username()

        # ── Step 1-2: Navigate and capture initial count ──────────────────
        admin.goto()
        initial_count = admin.get_record_count()
        logger.info(f"Initial record count: {initial_count}")

        # ── Step 3: Add a new user ─────────────────────────────────────────
        admin.click_add()
        admin.fill_user_form(username=username, password=DEFAULT_PASSWORD)
        admin.save_user()

        # ── Step 4: Verify count increased by 1 ───────────────────────────
        count_after_add = admin.get_record_count()
        assert count_after_add == initial_count + 1, (
            f"Expected {initial_count + 1} records after add, got {count_after_add}"
        )
        logger.info(f"Count after add: {count_after_add} ✓")

        # ── Step 5: Search for the new user ───────────────────────────────
        admin.search_by_username(username)
        search_count = admin.get_record_count()
        assert search_count == 1, (
            f"Expected 1 search result for '{username}', got {search_count}"
        )
        logger.info(f"Search result count: {search_count} ✓")

        # ── Step 6: Delete the user ────────────────────────────────────────
        admin.delete_user_from_results(username)

        # ── Step 7: Reset search and verify count returned to initial ─────
        admin.reset_search()
        count_after_delete = admin.get_record_count()
        assert count_after_delete == initial_count, (
            f"Expected {initial_count} records after delete, got {count_after_delete}"
        )
        logger.info(f"Count after delete: {count_after_delete} ✓")
