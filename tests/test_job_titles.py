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

# This is the SAME self-hosted OrangeHRM page used by the mocked-API tests below,
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
    Test verifies a Job Title can be created with unique data, appears correctly in the UI,
    and is cleaned up afterward - an end-to-end CRUD check against OrangeHRM's Admin > Job >
    Job Titles page.

    Test Steps:
    1. Navigate to the Job Titles page as an authenticated Admin.
    2. Add a Job Title with a uniquely-timestamped title and a description.
    3. Delete that same Job Title.

    Expected results:
    A row for the new title appears containing both the exact title and description that
    were entered - not just any new row. The title creates its own uniquely-named data rather
    than asserting against pre-existing content, so repeated runs never collide.
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
    """
    Test verifies the Job Titles list renders exactly the data returned by its API, using a
    fully mocked response.

    Test Steps:
    1. Mock the Job Titles API to return two fixed, known rows.
    2. Navigate to the Job Titles page.

    Expected results:
    Both mocked titles ("Mocked Job Title A", "Mocked Job Title B") are visible, and the
    "(2) Records Found" count matches the mocked data - nothing from the real instance's own
    data leaks through.
    """
    logger.info("Given a mocked Job Titles API response\n\tWhen I load the Job Titles page"
                "\n\tThen it renders exactly the mocked rows, not the real instance data\n")

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

    # The list must show EXACTLY the mocked rows - nothing from the real instance data leaked through
    expect(orangehrm_admin_page.get_by_text("Mocked Job Title A")).to_be_visible()
    expect(orangehrm_admin_page.get_by_text("Mocked Job Title B")).to_be_visible()
    expect(orangehrm_admin_page.get_by_text("(2) Records Found")).to_be_visible()


def test_job_titles_list_handles_api_error(orangehrm_admin_page: Page) -> None:
    """
    Test verifies the page doesn't crash or hang when its data API fails - a negative
    scenario that's slow, unreliable, or simply impossible to trigger on demand against a
    real backend, which is what makes mocking it worthwhile.

    Test Steps:
    1. Mock the Job Titles API to return a 500 error.
    2. Navigate to the Job Titles page.

    Expected results:
    The page's own chrome (the "Job Titles" heading and the "Add" button) still renders
    despite the failed data call, instead of the app crashing into a blank page.
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
    Test verifies a Job Title created directly via the API is correctly rendered in the UI -
    a hybrid API+UI check that creates the record through OrangeHRM's real internal REST API
    (bypassing the "Add Job Title" form entirely), then verifies it in the UI.

    Test Steps:
    1. POST a uniquely-titled Job Title directly to the internal Job Titles API.
    2. Navigate to the Job Titles page in the UI.
    3. Delete that same Job Title via the UI.

    Expected results:
    The API response is successful with a generated id. The UI then shows a row for that
    exact title containing the description that was posted, proving the API-created record
    renders correctly - not just that the API call itself succeeded.
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
