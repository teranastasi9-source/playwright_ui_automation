import json
import logging
import time

import pytest
from config import (
    ORANGEHRM_JOB_TITLES_API_URL,
    ORANGEHRM_JOB_TITLES_API_URL_PATTERN,
    ORANGEHRM_JOB_TITLES_URL,
)
from pages.job_titles_page import JobTitlesPage
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

# This is the SAME public/shared demo page used by the mocked-API tests below,
# approached from the opposite angle. Instead of mocking the network
# response, this test creates and cleans up its own real data.
MOCKED_JOB_TITLES_RESPONSE = {
    "data": [
        {
            "id": 9001,
            "title": "Mocked Job Title A",
            "description": "First mocked description",
            "note": None,
            "jobSpecification": {"id": None, "filename": None, "fileType": None, "fileSize": None},
        },
        {
            "id": 9002,
            "title": "Mocked Job Title B",
            "description": "Second mocked description",
            "note": None,
            "jobSpecification": {"id": None, "filename": None, "fileType": None, "fileSize": None},
        },
    ],
    "meta": {"total": 2},
    "rels": [],
}


@pytest.mark.slow
def test_job_title_create_and_delete(orangehrm_admin_page: Page) -> None:
    """
    Verify a Job Title can be created with unique data, appears correctly in the UI, and is cleaned up afterward.

    End-to-end CRUD check against OrangeHRM's Admin > Job > Job Titles page.

    Replaces the previous version of this test, which was a Playwright
    Codegen recording of a live Google search -> otomoto.pl flow. That
    approach was unreliable for automated regression testing: it depended
    on Google not showing a bot-check page, on Google's search results
    staying identical over time, and on mutating real state on someone
    else's production site. This version instead:
      - targets a stable, purpose-built demo application,
      - creates its OWN uniquely-named test data instead of asserting
        against shared, publicly-editable demo content (other visitors
        constantly add unrelated entries to this public demo's data), and
      - cleans up after itself, so repeated runs don't leave junk behind
        on the shared demo instance.

    Login itself is handled by the `orangehrm_admin_page` fixture (see
    conftest.py), which reuses a storage_state captured once per test
    session instead of repeating the UI login here.
    """
    logger.info("Given the OrangeHRM Job Titles page\n\tWhen I create a uniquely-named Job Title"
                "\n\tThen it appears in the list with the correct data, and can be deleted again\n")

    unique_title = f"Playwright QA Test Title {int(time.time())}"
    description = "Created by an automated Playwright test - safe to delete."

    job_titles_page = JobTitlesPage(orangehrm_admin_page)
    job_titles_page.goto_url(ORANGEHRM_JOB_TITLES_URL)

    job_titles_page.add_job_title(unique_title, description)

    # Verify both the title AND description were actually saved, not just that some row appeared
    new_row = job_titles_page.job_title_row(unique_title).first
    row_text = new_row.inner_text()
    assert unique_title in row_text
    assert "Created by an automated Playwright test" in row_text

    job_titles_page.delete_job_title(unique_title)


def test_job_titles_list_renders_mocked_api_response(orangehrm_admin_page: Page) -> None:
    """Verify the Job Titles list renders exactly the data returned by its API, using a fully mocked response."""
    logger.info("Given a mocked Job Titles API response\n\tWhen I load the Job Titles page"
                "\n\tThen it renders exactly the mocked rows, not the real shared demo data\n")

    # Mock the API response
    orangehrm_admin_page.route(
        ORANGEHRM_JOB_TITLES_API_URL_PATTERN,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCKED_JOB_TITLES_RESPONSE),
        ),
    )

    # Go to job titles page
    orangehrm_admin_page.goto(ORANGEHRM_JOB_TITLES_URL)
    orangehrm_admin_page.wait_for_load_state("load")

    # The list must show EXACTLY the mocked rows - nothing from the real, shared demo data leaked through
    expect(orangehrm_admin_page.get_by_text("Mocked Job Title A")).to_be_visible()
    expect(orangehrm_admin_page.get_by_text("Mocked Job Title B")).to_be_visible()
    expect(orangehrm_admin_page.get_by_text("(2) Records Found")).to_be_visible()


def test_job_titles_list_handles_api_error(orangehrm_admin_page: Page) -> None:
    """
    Verify the page doesn't crash/hang when its data API fails. This is the
    kind of negative scenario that's slow, unreliable, or simply impossible
    to trigger reliably against a real backend - mocking is what makes it
    practical to test at all.
    """
    logger.info("Given a mocked 500 error from the Job Titles API\n\tWhen I load the Job Titles page"
                "\n\tThen the page itself still renders instead of crashing\n")

    # Mock the API response
    orangehrm_admin_page.route(
        ORANGEHRM_JOB_TITLES_API_URL_PATTERN,
        lambda route: route.fulfill(status=500, content_type="application/json", body="{}"),
    )

    # Go to job titles page
    orangehrm_admin_page.goto(ORANGEHRM_JOB_TITLES_URL)
    orangehrm_admin_page.wait_for_load_state("load")

    # The page itself (nav, "Add" button, page header) must still render even
    # though the data call failed - the app shouldn't crash into a blank page
    expect(orangehrm_admin_page.get_by_role("heading", name="Job Titles")).to_be_visible()
    expect(orangehrm_admin_page.get_by_role("button", name="Add")).to_be_visible()


@pytest.mark.slow
def test_job_title_created_via_api_is_visible_in_ui(orangehrm_admin_page: Page) -> None:
    """
    Verify a Job Title created directly via the API is correctly rendered in the UI.

    Hybrid API+UI check: create the record directly through OrangeHRM's real
    internal REST API (bypassing the "Add Job Title" form entirely), then
    verify it actually renders in the UI.

    `orangehrm_admin_page.request` is an APIRequestContext that shares
    cookies with the browser context behind `orangehrm_admin_page` - no
    separate login or manual cookie handling is needed to authenticate the
    API call.

    This is the kind of test that's normally used to set up state fast (via
    API) while still asserting on the thing users actually see (the UI), and
    it exercises both layers of the same feature in one scenario.
    """
    logger.info("Given an authenticated API session\n\tWhen I create a Job Title via a direct API call"
                "\n\tThen it appears correctly in the OrangeHRM UI\n")

    unique_title = f"Playwright Hybrid API Test {int(time.time())}"

    # Create job title via API
    response = orangehrm_admin_page.request.post(
        ORANGEHRM_JOB_TITLES_API_URL,
        data={
            "title": unique_title,
            "description": "Created via API, verified via UI",
            "specification": None,
            "note": "",
        },
    )

    # Verify API response
    assert response.ok, f"API creation failed: {response.status} {response.text()}"
    created_id = response.json()["data"]["id"]
    assert created_id is not None

    # Go to job titles page
    job_titles_page = JobTitlesPage(orangehrm_admin_page)
    job_titles_page.goto_url(ORANGEHRM_JOB_TITLES_URL)

    # Verify job title is visible in UI
    row = job_titles_page.job_title_row(unique_title)
    expect(row).to_be_visible()
    expect(row).to_contain_text("Created via API, verified via UI")

    # Cleanup: delete the job title via UI
    job_titles_page.delete_job_title(unique_title)
