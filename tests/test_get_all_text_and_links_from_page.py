import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def test_get_all_text_from_page(page: Page, qa_playground_url: str):
    """
    Test verifies searching highlights only the matching statements, and updates correctly
    as the search term changes.

    Test Steps:
    1. Navigate to the Links & text page.
    2. Search for a term that appears in all three statements.
    3. Search for a term that matches only one statement.
    4. Search for a term with no matches.

    Expected results:
    Nothing is highlighted before any search. Searching "statement" highlights all three
    occurrences. Searching "two" highlights only that one match, with the previous search's
    highlights cleared. Searching a nonexistent term leaves nothing highlighted.
    """
    logger.info("Given the Links & text page's highlight search box"
                "\n\tWhen I search for a term matching several statements, then one, then none"
                "\n\tThen only the statements that actually match are highlighted each time\n")

    # Navigate to URL
    page.goto(f"{qa_playground_url}/links_and_text.html")
    page.wait_for_load_state("load")

    search_box = page.locator("#highlight-search")
    highlight_button = page.locator("#highlight-button")
    highlighted = page.locator("#content b")

    # Given: nothing is highlighted before any search has been made
    assert highlighted.count() == 0

    # When: searching for a term that appears in all three statements
    search_box.fill("statement")
    highlight_button.click()

    # Then: all three are highlighted, each containing the search term
    assert highlighted.count() == 3
    for text in highlighted.all():
        assert text.text_content().lower() == "statement"

    # When: searching for a term that matches only one statement
    search_box.fill("two")
    highlight_button.click()

    # Then: only that one is highlighted now - the previous search's highlights are gone
    assert highlighted.count() == 1
    assert highlighted.first.text_content().lower() == "two"

    # When: searching for a term with no matches
    search_box.fill("nonexistent")
    highlight_button.click()

    # Then: nothing is highlighted
    assert highlighted.count() == 0


def test_get_all_links_from_page(page: Page, qa_playground_url: str):
    """
    Test verifies the page's own content links are collected with the correct destination and
    label for each.

    Test Steps:
    1. Navigate to the Links & text page.
    2. Collect every content link (scoped to the page's own list, excluding the shared nav bar).

    Expected results:
    Exactly 3 content links are found, with hrefs and link text matching the page's actual
    content exactly.
    """
    logger.info("Given the Links & text page\n\tWhen I collect every content link on the page"
                "\n\tThen each one has the expected destination and label\n")

    # Navigate to URL
    page.goto(f"{qa_playground_url}/links_and_text.html")
    page.wait_for_load_state("load")

    # Scoped to the content links only - the nav bar's own links repeat on every Playground
    # page and aren't what this page's content is about
    content_links = page.locator("ul li a")
    assert content_links.count() == 3

    hrefs = [link.get_attribute("href") for link in content_links.all()]
    texts = [link.text_content() for link in content_links.all()]

    # Verify the actual destinations and labels, not just that some links exist
    assert hrefs == [
        "https://example.com/one",
        "https://example.com/two",
        "https://example.com/three",
    ]
    assert texts == ["Example link one", "Example link two", "Example link three"]
