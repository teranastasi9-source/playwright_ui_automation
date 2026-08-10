import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_selecting_category_renders_matching_subcategories(page: Page, qa_playground_url: str):
    """
    Test verifies the rendered subcategory list matches the selected category, and updates
    correctly as the selection changes - not just that the backend returned the right data
    (a user never sees the raw response).

    Test Steps:
    1. Navigate to the AJAX dropdown page.
    2. Select "Fruits" from the category dropdown.
    3. Select "Vegetables" from the category dropdown.
    4. Reset the category dropdown back to its placeholder option.

    Expected results:
    Nothing is rendered before any category is selected. Selecting "Fruits" renders exactly
    its 4 subcategories; switching to "Vegetables" replaces them with its own 4 subcategories,
    not a merge of both. Resetting clears the list back to empty.
    """
    logger.info("Given the AJAX dropdown page\n\tWhen I select 'Fruits', then 'Vegetables', then reset the category"
                "\n\tThen the rendered subcategory list matches each selection, and clears on reset\n")

    page.goto(f"{qa_playground_url}/ajax_dropdown.html")
    page.wait_for_load_state("load")

    category_dropdown = page.locator("#s1")
    subcategories = page.locator("#subcategory-list li")

    # Given: nothing selected yet - no subcategories rendered
    assert subcategories.count() == 0

    # When: selecting 'Fruits', wait for the fetch() it triggers, then check what actually
    # rendered on the page - not the raw response, which a real user never sees
    with page.expect_response(lambda response: "dd-ajax-fruits.json" in response.url):
        category_dropdown.select_option(label="Fruits")
    expect(subcategories).to_have_count(4)
    assert [item.text_content() for item in subcategories.all()] == ["Mango", "Banana", "Orange", "Apple"]

    # When: switching to 'Vegetables'
    with page.expect_response(lambda response: "dd-ajax-vegetables.json" in response.url):
        category_dropdown.select_option(label="Vegetables")

    # Then: the list reflects the new category - the previous selection's items are gone
    expect(subcategories).to_have_count(4)
    assert [item.text_content() for item in subcategories.all()] == ["Carrot", "Potato", "Onion", "Spinach"]

    # When: resetting back to the placeholder option
    category_dropdown.select_option(label="Select category")

    # Then: the list is cleared, not left showing the last category's items
    expect(subcategories).to_have_count(0)
