import logging

from config import PLUS2NET_AJAX_URL
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def test_selecting_category_returns_matching_subcategories(page: Page):
    """Verify selecting a category in the AJAX dropdown returns the matching subcategories from the backend."""
    logger.info("Given the AJAX dropdown demo page\n\tWhen I select 'Fruits' in the category dropdown"
                "\n\tThen the backend returns the matching subcategories\n")

    page.goto(PLUS2NET_AJAX_URL)
    page.wait_for_load_state("load")

    # Find selector for 'Category' dropdown list (colors)
    category_dropdown = page.locator('//select[@id="s1"]')

    # Select "Fruits" (value=1) and wait for the AJAX call it triggers,
    # then verify the backend actually returned the expected subcategories
    with page.expect_response(lambda response: 'dd-ajax.php' in response.url) as response_info:
        category_dropdown.select_option(value='1')

    response = response_info.value
    assert response.status == 200

    subcategories = [item["subcategory"] for item in response.json()["data"]]
    assert subcategories == ["Mango", "Banana", "Orange", "Apple"]
