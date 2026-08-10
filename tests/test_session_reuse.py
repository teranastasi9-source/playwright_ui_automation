import logging

from config import ORANGEHRM_DASHBOARD_URL, ORANGEHRM_JOB_TITLES_URL
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_navigating_between_pages_stays_authenticated_via_reused_session(orangehrm_admin_page: Page) -> None:
    """
    Test verifies a reused session stays authenticated across real in-app navigation, not
    just a single direct page load.

    Test Steps:
    1. Load the Dashboard directly using the reused session.
    2. Navigate to Job Titles via the app's own Admin > Job > Job Titles nav menu.
    3. Navigate back to the Dashboard via the nav menu.

    Expected results:
    Every page loads directly at its expected URL with its expected content visible ("Time at
    Work" on the Dashboard, the "Job Titles" heading on that page) - none of the three hops
    redirect back to the login page, proving the reused session survives more than one hop.
    """
    logger.info("Given a session captured once by the orangehrm_admin_page fixture"
                "\n\tWhen I navigate through the app via its own nav menu - dashboard, then Job Titles, then back"
                "\n\tThen every page loads directly, with no redirect to login at any point\n")

    # Start on the dashboard - if the reused session weren't valid, this would redirect to /auth/login instead
    orangehrm_admin_page.goto(ORANGEHRM_DASHBOARD_URL)
    orangehrm_admin_page.wait_for_load_state("load")
    expect(orangehrm_admin_page).to_have_url(ORANGEHRM_DASHBOARD_URL)
    expect(orangehrm_admin_page.get_by_text("Time at Work")).to_be_visible()

    # Navigate to Job Titles via the app's own nav menu, not a direct URL - a real user
    # clicks through the UI, they don't type admin URLs by hand
    orangehrm_admin_page.get_by_text("Admin", exact=True).click()
    orangehrm_admin_page.wait_for_load_state("load")
    orangehrm_admin_page.get_by_text("Job", exact=True).click()
    orangehrm_admin_page.get_by_text("Job Titles", exact=True).click()
    orangehrm_admin_page.wait_for_load_state("load")

    # Still authenticated after that hop - landed on the real page, not bounced back to login
    expect(orangehrm_admin_page).to_have_url(ORANGEHRM_JOB_TITLES_URL)
    expect(orangehrm_admin_page.get_by_role("heading", name="Job Titles")).to_be_visible()

    # Navigate back to the Dashboard via the nav menu - proving the session survives more
    # than one hop, not just a single page load
    orangehrm_admin_page.get_by_text("Dashboard", exact=True).click()
    orangehrm_admin_page.wait_for_load_state("load")
    expect(orangehrm_admin_page).to_have_url(ORANGEHRM_DASHBOARD_URL)
    expect(orangehrm_admin_page.get_by_text("Time at Work")).to_be_visible()
