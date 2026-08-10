import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_hover_opens_dropdown_and_dblclick_works(page: Page, qa_playground_url: str):
    """
    Test verifies hovering reveals the dropdown, selecting an entry updates the page, and
    double-click changes the element's own color.

    Test Steps:
    1. Navigate to the Hover menu page.
    2. Hover over "SwitchTo".
    3. Click "Frames" from the dropdown that appears.
    4. Double-click "SwitchTo".

    Expected results:
    Before any interaction, no status text is shown and "SwitchTo" has no inline color.
    Hovering makes the "Frames" entry visible. Clicking it updates the status text to "You
    selected: Frames". Double-clicking "SwitchTo" changes its own color to purple.
    """
    logger.info("Given the Hover menu page\n\tWhen I hover over 'SwitchTo', select 'Frames', and double-click it"
                "\n\tThen the selection is reflected on the page, and the double-click changes its color\n")

    # Navigate to the page
    page.goto(f"{qa_playground_url}/hover_menu.html")
    page.wait_for_load_state("load")

    switch_to_link = page.locator('//a[text()="SwitchTo"]')
    frames_link = page.locator('//a[text()="Frames"]')
    status = page.locator("#selection-status")

    # Given: nothing selected yet, and the link's color hasn't been changed
    expect(status).to_have_text("")
    assert switch_to_link.evaluate("el => el.style.color") == ""

    # Find "SwitchTo" button location and call hover() method
    # (keep a cursor on "SwitchTo" element -> dropdown list pops up)
    switch_to_link.hover()

    # Verify the hover actually opened the "Frames" dropdown entry
    expect(frames_link).to_be_visible()

    # Select "Frames" and click it
    frames_link.click()

    # Verify the selection is actually reflected on the page, not just that the click
    # didn't error - a real user expects some feedback from picking a menu entry
    expect(status).to_have_text("You selected: Frames")

    # Double-click on element (no proper location as example)
    switch_to_link.dblclick()

    # Verify the double-click actually did something to the element, not just that it
    # didn't error
    assert switch_to_link.evaluate("el => el.style.color") == "purple"
