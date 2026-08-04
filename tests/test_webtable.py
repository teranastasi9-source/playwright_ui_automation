import logging

import pytest
from config import TECHLISTIC_WEBTABLE_URL
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


@pytest.mark.smoke
def test_webtable_content_matches_expected_data(page: Page):
    """Verify the customers table has the expected shape (rows/columns) and exact cell content."""
    logger.info("Given the web table demo page\n\tWhen I read the customers table"
                "\n\tThen its shape and content match the expected data\n")

    # Launch the browser and navigate to the web table demo page
    page.goto(TECHLISTIC_WEBTABLE_URL)
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
