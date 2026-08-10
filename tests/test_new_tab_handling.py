import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_new_tab_closes_without_affecting_original_tab(page: Page, qa_playground_url: str):
    """
    Test verifies opening a link in a new tab and closing it leaves the original tab's own
    state untouched.

    Test Steps:
    1. Navigate to the New tab page and type text into its notes field.
    2. Click the button that opens a link in a new tab.
    3. Switch to the new tab and check its content.
    4. Close the new tab.
    5. Switch back to the original tab.

    Expected results:
    Opening the link creates a second tab showing the real "Alerts" page content. Closing it
    leaves exactly one tab open, and the original tab's notes field still holds the text that
    was typed before the new tab was ever opened.
    """
    logger.info("Given a page with unsaved notes typed in\n\tWhen I open a link in a new tab, read it, and close it"
                "\n\tThen the original tab still has the notes I typed, unaffected by the new tab\n")

    # Navigate to the page
    page.goto(f"{qa_playground_url}/new_tab.html")
    page.wait_for_load_state("load")
    context = page.context

    # Type something in the original tab before ever opening a new one
    notes_field = page.locator("#notes")
    notes_field.fill("Remember to check the Alerts page")

    # Find "Click" button via XPath and click it -> new tab will be opened
    with context.expect_page() as new_page_info:
        page.locator('//a[@target="_blank"]/button').click()
    new_page = new_page_info.value
    new_page.wait_for_load_state("load")

    # Verify a second tab actually opened
    assert len(context.pages) == 2

    # Switch to the new tab and verify it actually shows real, specific content -
    # not just that its URL differs from the original tab's
    new_page.bring_to_front()
    expect(new_page.get_by_role("heading", name="Alerts")).to_be_visible()

    # Close only the new_page tab
    new_page.close()

    # Verify only the original tab remains
    assert len(context.pages) == 1

    # Switch back to the original tab and verify its own state actually survived untouched -
    # the real point of "closes without affecting the original tab", not just the tab count
    page.bring_to_front()
    expect(notes_field).to_have_value("Remember to check the Alerts page")
