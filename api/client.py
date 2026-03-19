"""
OrangeHRM API client.

Authentication note
-------------------
OrangeHRM is a Vue.js SPA — the login form (including its CSRF token) is
rendered by JavaScript, so the token is NOT available in the raw HTML
returned by a plain requests.get().

The reliable solution is to perform the login through a real browser
(Playwright), then extract the resulting session cookie and inject it into
the requests Session.  This approach requires no CSRF token handling and
works regardless of framework internals.
"""

import logging

import requests
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class OrangeHRMApiClient:
    """Reusable HTTP client for the OrangeHRM REST API."""

    CANDIDATES_URL = "/web/index.php/api/v2/recruitment/candidates"

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._authenticate(username, password)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self, username: str, password: str) -> None:
        """
        Login via a headless Playwright browser, then transfer the
        resulting session cookie into the requests Session.

        Why Playwright?  OrangeHRM renders its login form (including the
        CSRF _token input) with JavaScript, so a plain requests.get()
        returns an empty HTML shell with no token to extract.
        """
        logger.info("Authenticating via headless browser (SPA login)...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(f"{self.base_url}/web/index.php/auth/login")
            page.get_by_placeholder("Username").fill(username)
            page.get_by_placeholder("Password").fill(password)
            page.get_by_role("button", name="Login").click()
            page.wait_for_selector(".oxd-main-menu", timeout=15_000)

            # Transfer all browser cookies to the requests session
            for cookie in context.cookies():
                self.session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie["domain"].lstrip("."),
                )
            browser.close()

        logger.info("API client authenticated successfully")

    # ------------------------------------------------------------------
    # Candidates API
    # ------------------------------------------------------------------

    def add_candidate(
        self,
        first_name: str,
        last_name: str,
        email: str,
        middle_name: str = "",
        contact_number: str = "",
    ) -> dict:
        """
        POST /api/v2/recruitment/candidates
        Returns the created candidate dict with at least: id, firstName, lastName, email.

        Note: the API rejects a 'notes' field (returns 422) — omit it.
        """
        url = f"{self.base_url}{self.CANDIDATES_URL}"
        payload = {
            "firstName": first_name,
            "middleName": middle_name,
            "lastName": last_name,
            "email": email,
            "contactNumber": contact_number,
            "keywords": "",
            "dateOfApplication": None,
            "consentToKeepData": False,
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        candidate = response.json()["data"]
        logger.info(f"Candidate created — id={candidate['id']}, email={email}")
        return candidate

    def delete_candidate(self, candidate_id: int) -> None:
        """
        DELETE /api/v2/recruitment/candidates  body: {"ids": [id]}
        """
        url = f"{self.base_url}{self.CANDIDATES_URL}"
        response = self.session.delete(url, json={"ids": [candidate_id]})
        response.raise_for_status()
        logger.info(f"Candidate {candidate_id} deleted")

    def get_candidates(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        GET /api/v2/recruitment/candidates
        Returns list of candidate dicts.
        """
        url = f"{self.base_url}{self.CANDIDATES_URL}"
        params = {
            "limit": limit,
            "offset": offset,
            "sortField": "candidate.dateOfApplication",
            "sortOrder": "DESC",
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["data"]
