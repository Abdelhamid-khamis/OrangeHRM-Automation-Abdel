"""
API Test: Recruitment Candidates
Covers: Add candidate via API → assert created → Delete → assert removed
"""
import logging

import pytest

from api.client import OrangeHRMApiClient
from utils.helpers import generate_username

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestCandidatesApi:

    def test_add_and_delete_candidate(self, api_client: OrangeHRMApiClient) -> None:
        """
        1. Add a candidate via POST /api/v2/recruitment/candidates
        2. Assert the response contains expected fields
        3. Delete the candidate via DELETE
        4. Assert the candidate no longer appears in the list
        """
        first_name = "Auto"
        last_name = generate_username("Candidate")
        email = f"{last_name.lower()}@example.com"

        # ── Step 1-2: Add candidate ───────────────────────────────────────
        candidate = api_client.add_candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        assert candidate["id"] is not None, "Candidate ID should not be None"
        assert candidate["firstName"] == first_name
        assert candidate["lastName"] == last_name
        logger.info(f"Created candidate id={candidate['id']} email={email} ✓")

        candidate_id = candidate["id"]

        # ── Step 3-4: Delete and verify ───────────────────────────────────
        api_client.delete_candidate(candidate_id)

        remaining_ids = [c["id"] for c in api_client.get_candidates()]
        assert candidate_id not in remaining_ids, (
            f"Candidate {candidate_id} should have been deleted but still appears"
        )
        logger.info(f"Candidate {candidate_id} successfully deleted ✓")

    def test_add_candidate_returns_correct_structure(
        self, api_client: OrangeHRMApiClient
    ) -> None:
        """Ensure the API response structure is as expected."""
        last_name = generate_username("Struct")
        candidate = api_client.add_candidate(
            first_name="Structure",
            last_name=last_name,
            email=f"{last_name.lower()}@example.com",
        )

        required_fields = {"id", "firstName", "lastName"}
        missing = required_fields - candidate.keys()
        assert not missing, f"Response missing fields: {missing}"

        # Cleanup
        api_client.delete_candidate(candidate["id"])
        logger.info("Structure test passed and cleaned up ✓")
