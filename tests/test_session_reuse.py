import logging

from config import ORANGEHRM_DASHBOARD_URL, ORANGEHRM_JOB_TITLES_URL
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

# Both tests below use the `orangehrm_admin_page` fixture (see conftest.py):
# neither one fills in a username/password or clicks "Login" itself. The
# fixture logs in ONCE per test session, captures the resulting
# storage_state, and hands each test a fresh BrowserContext built from that
# state. That gives two things at once, which is the actual point of this
# pattern:
#   - speed: the (slow) UI login flow only runs once for the whole session,
#     not once per test that needs to be authenticated;
#   - isolation: each test still gets its own brand-new BrowserContext, so
#     tests can't leak state into one another - this is NOT the same as
#     sharing one browser/context/page across tests.


def test_dashboard_reachable_via_reused_session(orangehrm_admin_page: Page) -> None:
    """Verify the dashboard is reachable directly, without logging in, by reusing a stored session."""
    logger.info("Given a session captured once by the orangehrm_admin_page fixture"
                "\n\tWhen I navigate straight to the dashboard\n\tThen it loads without redirecting to login\n")

    # Launch the browser and navigate to the dashboard URL
    orangehrm_admin_page.goto(ORANGEHRM_DASHBOARD_URL)
    orangehrm_admin_page.wait_for_load_state("load")

    # If the reused session weren't valid, this would have redirected to /auth/login instead
    expect(orangehrm_admin_page).to_have_url(ORANGEHRM_DASHBOARD_URL)
    expect(orangehrm_admin_page.get_by_text("Time at Work")).to_be_visible()


def test_job_titles_reachable_via_reused_session(orangehrm_admin_page: Page) -> None:
    """Verify the Job Titles admin page is reachable directly, without logging in, by reusing a stored session."""
    logger.info("Given a session captured once by the orangehrm_admin_page fixture"
                "\n\tWhen I navigate straight to the Job Titles page\n\tThen it loads without redirecting to login\n")

    # Launch the browser and navigate to the job titles URL
    orangehrm_admin_page.goto(ORANGEHRM_JOB_TITLES_URL)
    orangehrm_admin_page.wait_for_load_state("load")

    # If the reused session weren't valid, this would have redirected to /auth/login instead
    expect(orangehrm_admin_page).to_have_url(ORANGEHRM_JOB_TITLES_URL)
    expect(orangehrm_admin_page.get_by_role("heading", name="Job Titles")).to_be_visible()
