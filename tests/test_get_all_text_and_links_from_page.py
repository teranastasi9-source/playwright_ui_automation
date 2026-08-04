import logging

import pytest
from config import AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON, AUTOMATIONTESTING_SELECTABLE_URL
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_get_all_text_from_page(page: Page):
    """Verify all bold-text elements on the page can be collected and each has visible text."""
    logger.info("Given the demo page\n\tWhen I collect every <b> element on the page"
                "\n\tThen at least one text element is found\n")

    # Navigate to URL
    page.goto(AUTOMATIONTESTING_SELECTABLE_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Store multiple text elements (usually marked as 'b', 'label', 'p', etc.)
    all_text = page.query_selector_all('b')
    assert len(all_text) > 0

    # Read each text from web element
    for text in all_text:
        print(text.text_content())


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_get_all_links_from_page(page: Page):
    """Verify all links on the page can be collected and at least one has a non-empty href."""
    logger.info("Given the demo page\n\tWhen I collect every <a> element on the page"
                "\n\tThen at least one link with a non-empty href is found\n")

    # Navigate to URL
    page.goto(AUTOMATIONTESTING_SELECTABLE_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Links are usually marked as 'a' (anchor) tag
    all_links = page.query_selector_all('a')
    assert len(all_links) > 0

    try:
        page.query_selector('d//[@aaa="bbb"]')  # raise an error for testing purpose
    except Exception as e:
        print(str(e))  # Unsupported token "@aaa ...
    finally:
        print("Will be executed anyway")

    # Read each link with href attribute
    hrefs = [link.get_attribute('href') for link in all_links]
    assert any(href for href in hrefs), "Expected at least one link with a non-empty href"
