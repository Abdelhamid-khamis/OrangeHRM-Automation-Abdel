import logging

import pytest
from playwright.sync_api import Page

from config.settings import CREDENTIALS, BASE_URL, VIEWPORT
from pages.login_page import LoginPage
from api.client import OrangeHRMApiClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------------------------------
# Playwright browser configuration
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default Playwright context args."""
    return {**browser_context_args, "viewport": VIEWPORT}


# ---------------------------------------------------------------------------
# UI fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Return a Playwright Page that is already authenticated."""
    login = LoginPage(page)
    login.goto()
    login.login(CREDENTIALS["username"], CREDENTIALS["password"])
    return page


# ---------------------------------------------------------------------------
# API fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_client() -> OrangeHRMApiClient:
    """Return an authenticated API client (shared across the test session)."""
    return OrangeHRMApiClient(
        base_url=BASE_URL,
        username=CREDENTIALS["username"],
        password=CREDENTIALS["password"],
    )
