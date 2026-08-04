import logging

import pytest
from config import AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON, AUTOMATIONTESTING_SELECTABLE_URL
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_hover_opens_dropdown_and_dblclick_works(page: Page):
    """Verify hovering over "SwitchTo" opens its dropdown, and double-click works on the same element."""
    logger.info("Given the demo page\n\tWhen I hover over 'SwitchTo' and click 'Frames'"
                "\n\tThen the dropdown opens and double-click also works\n")

    # Navigate to the page
    page.goto(AUTOMATIONTESTING_SELECTABLE_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Find "SwitchTo" button location and call hover() method
    # (keep a cursor on "SwitchTo" element -> dropdown list pops up)
    page.wait_for_selector('//a[text()="SwitchTo"]').hover()

    # Verify the hover actually opened the "Frames" dropdown entry
    # (locator(), not wait_for_selector(), because expect() requires a Locator, not an ElementHandle)
    frames_link = page.locator('//a[text()="Frames"]')
    expect(frames_link).to_be_visible()

    # Select "Frames" and click it
    frames_link.click()

    # Double-click on element (no proper location as example)
    page.wait_for_selector('//a[text()="SwitchTo"]').dblclick()
