import logging

import pytest
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


@pytest.mark.smoke
def test_webtable_content_matches_expected_data(page: Page, qa_playground_url: str):
    """
    Test verifies the customers table has the expected shape (rows/columns) and exact cell
    content.

    Test Steps:
    1. Navigate to the Table page.
    2. Read the customers table's row count, cell count, and every cell's text.

    Expected results:
    The table has 7 rows and 18 cells, and the cell content matches the expected 6 companies
    with their contact name and country, in order.
    """
    logger.info("Given the Table page\n\tWhen I read the customers table"
                "\n\tThen its shape and content match the expected data\n")

    # Launch the browser and navigate to the Table page
    page.goto(f"{qa_playground_url}/table.html")
    page.wait_for_load_state("load")

    # Find selector for whole table
    table = page.locator('//table[@id="customers"]')

    # Find number of rows of that table via 'tr' (table rows)
    all_rows = table.locator('tr')
    assert all_rows.count() == 7

    # Find number of cells of that table via 'td' (table data)
    all_columns = table.locator('td')
    assert all_columns.count() == 18

    table_data = []
    for row in all_rows.all():
        row_data = row.locator('td')
        for data in row_data.all():
            table_data.append(data.text_content())

    # Verify the actual table content, not just its shape
    assert table_data == [
        'Google', 'Maria Anders', 'Germany',
        'Meta', 'Francisco Chang', 'Mexico',
        'Microsoft', 'Roland Mendel', 'Austria',
        'Island Trading', 'Helen Bennett', 'UK',
        'Adobe', 'Yoshi Tannamuri', 'Canada',
        'Amazon', 'Giovanni Rovelli', 'Italy',
    ]


def test_searching_filters_table_to_matching_rows(page: Page, qa_playground_url: str):
    """
    Test verifies searching the table filters to only matching rows, and clearing the search
    restores all rows.

    Test Steps:
    1. Navigate to the Table page.
    2. Search for "Canada", a term matching exactly one row.
    3. Search for "Wakanda", a term matching no row.
    4. Clear the search box.

    Expected results:
    Before any search, all 6 rows (18 cells) are visible. Searching "Canada" leaves only the
    Adobe/Yoshi Tannamuri/Canada row visible. Searching "Wakanda" leaves zero rows visible.
    Clearing the search restores all 18 cells.
    """
    logger.info("Given the Table page\n\tWhen I search for a country matching one row, then a term matching none"
                "\n\tThen only the actually matching rows stay visible each time, and clearing restores all rows\n")

    page.goto(f"{qa_playground_url}/table.html")
    page.wait_for_load_state("load")

    search_box = page.locator("#table-search")
    visible_data_rows = page.locator("#customers tr:visible td")

    # Given: nothing searched yet - all 6 rows (18 cells) visible
    expect(visible_data_rows).to_have_count(18)

    # When: searching for a country that matches exactly one row
    search_box.fill("Canada")

    # Then: only that row stays visible
    expect(visible_data_rows).to_have_count(3)
    assert [cell.text_content() for cell in visible_data_rows.all()] == ["Adobe", "Yoshi Tannamuri", "Canada"]

    # When: searching for a term that matches no row
    search_box.fill("Wakanda")

    # Then: no rows are visible
    expect(visible_data_rows).to_have_count(0)

    # When: clearing the search
    search_box.fill("")

    # Then: all rows are visible again
    expect(visible_data_rows).to_have_count(18)
