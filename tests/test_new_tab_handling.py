import logging

import pytest
from config import AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON, AUTOMATIONTESTING_WINDOWS_URL
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_new_tab_closes_without_affecting_original_tab(page: Page):
    """Verify a link opens a new tab, and closing that tab leaves only the original one."""
    logger.info("Given a page with a link that opens a new tab\n\tWhen I click it and then close the new tab"
                "\n\tThen only the original tab remains\n")

    # Navigate to the page
    page.goto(AUTOMATIONTESTING_WINDOWS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)
    context = page.context

    # Find "Click" button via XPath and click it -> new tab will be opened
    with context.expect_page() as new_page_info:
        page.wait_for_selector('//a[@target="_blank"]/button').click()
    new_page = new_page_info.value
    new_page.wait_for_load_state("load")

    # Verify a second tab actually opened
    assert len(context.pages) == 2

    # Switch to new page (child) and verify it navigated somewhere
    new_page.bring_to_front()
    assert new_page.url != page.url

    # Close only the new_page tab
    new_page.close()

    # Verify only the original tab remains
    assert len(context.pages) == 1

    # Switch back to parent tab
    page.bring_to_front()
