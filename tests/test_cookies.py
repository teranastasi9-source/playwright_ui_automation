import logging

import pytest
from config import AUTOMATIONTESTING_ALERTS_URL, AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_cookies_can_be_read_and_cleared(page: Page):
    """Verify browser cookies can be read and cleared for the current page."""
    logger.info("Given a page with cookies set\n\tWhen I clear all cookies"
                "\n\tThen no cookies remain for the context\n")

    # Navigate to URL
    page.goto(AUTOMATIONTESTING_ALERTS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Get all cookies from the opened page
    my_cookies = page.context.cookies()
    assert isinstance(my_cookies, list)

    # Clear all cookies
    page.context.clear_cookies()

    # Verify all cookies were actually cleared
    assert page.context.cookies() == []
