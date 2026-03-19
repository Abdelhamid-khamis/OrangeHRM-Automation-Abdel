import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class OrangeHRMApiClient:
    """Reusable HTTP client for OrangeHRM API using session-based auth."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._authenticate(username, password)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _authenticate(self, username: str, password: str) -> None:
        """Login via the web form to obtain a session cookie."""
        login_url = f"{self.base_url}/web/index.php/auth/login"
        validate_url = f"{self.base_url}/web/index.php/auth/validate"

        # Step 1: GET login page to extract CSRF token
        response = self.session.get(login_url)
        response.raise_for_status()

        token = self._extract_csrf_token(response.text)
        logger.info("Extracted CSRF token for login")

        # Step 2: POST credentials
        payload = {"username": username, "password": password, "_token": token}
        response = self.session.post(validate_url, data=payload, allow_redirects=True)
        response.raise_for_status()

        if "dashboard" not in response.url:
            raise RuntimeError("Authentication failed — check credentials")

        logger.info("API client authenticated successfully")

    def _extract_csrf_token(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        token_input = soup.find("input", {"name": "_token"})
        if not token_input:
            raise RuntimeError("CSRF token not found on login page")
        return token_input["value"]

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------

    def add_candidate(
        self,
        first_name: str,
        last_name: str,
        email: str,
        middle_name: str = "",
        contact_number: str = "",
    ) -> dict:
        """Add a candidate and return the created resource."""
        url = f"{self.base_url}/web/index.php/api/v2/recruitment/candidates"
        payload = {
            "firstName": first_name,
            "middleName": middle_name,
            "lastName": last_name,
            "email": email,
            "contactNumber": contact_number,
            "keywords": "",
            "dateOfApplication": None,
            "notes": "",
            "consentToKeepData": False,
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Candidate created: {data['data']['id']}")
        return data["data"]

    def delete_candidate(self, candidate_id: int) -> None:
        """Delete a candidate by ID."""
        url = f"{self.base_url}/web/index.php/api/v2/recruitment/candidates"
        response = self.session.delete(url, json={"ids": [candidate_id]})
        response.raise_for_status()
        logger.info(f"Candidate {candidate_id} deleted")

    def get_candidates(self, limit: int = 50, offset: int = 0) -> list:
        """Return a list of candidates."""
        url = f"{self.base_url}/web/index.php/api/v2/recruitment/candidates"
        params = {"limit": limit, "offset": offset, "sortField": "candidate.dateOfApplication", "sortOrder": "DESC"}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()["data"]
