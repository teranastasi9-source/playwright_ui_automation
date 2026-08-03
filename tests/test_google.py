import logging

import pytest
from config import GOOGLE_NO_REDIRECT_URL, GOOGLE_URL
from pages.google_search_page import GooglePage
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def test_google_homepage_title_contains_google(page: Page):
    """Verify google.com loads and its page title contains 'Google'."""
    logger.info("Given google.com\n\tWhen the page loads\n\tThen the title contains 'Google'\n")

    # Navigate to URL
    page.goto(GOOGLE_URL)
    page.wait_for_load_state("load")

    # Verify page title contains 'Google'
    title = page.title()
    print(f"Page title: {title}")
    assert "Google" in title, f"Expected title: 'Google'; Received title: {title}"


@pytest.mark.smoke
def test_search_results_title_contains_playwright(page: Page, google_page: GooglePage):
    """Verify searching for 'Playwright Python' on Google returns results with 'Playwright' in the page title."""
    logger.info("Given the Google homepage\n\tWhen I search for 'Playwright Python'"
                "\n\tThen the results page title contains 'Playwright'\n")

    # Navigate to URL
    google_page.goto_url(GOOGLE_NO_REDIRECT_URL)

    # Handle cookie pop up from Google. If not found, it skips it with message
    try:
        google_page.cookie_button.click(timeout=3000)
    except Exception:
        print("No pop up to accept")

    # Enter 'Playwright Python' into search field
    google_page.enter_search(search="Playwright Python")

    # Click 'Enter' on the keyboard to start searching
    page.keyboard.press("Enter")

    # Verify the page title contains the word 'Playwright'
    google_page.check_title(title="Playwright")
