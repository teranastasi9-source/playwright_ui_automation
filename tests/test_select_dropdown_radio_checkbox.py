import logging

from config import AUTOMATIONTESTING_REGISTER_URL
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def test_select_dropdown(page: Page):
    """Verify selecting an option in the Skills dropdown updates its value from empty to the chosen option."""
    logger.info("Given the Register demo page\n\tWhen I select 'Python' in the Skills dropdown"
                "\n\tThen the dropdown value changes from empty to 'Python'\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_REGISTER_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Find the location of dropdown
    dropdown_select = page.query_selector('//select[@id="Skills"]')

    # Verify state BEFORE the action: nothing selected yet
    assert dropdown_select.input_value() == ""

    # Use select_option() method to define particular option
    dropdown_select.select_option(label='Python')

    # Verify state AFTER the action
    assert dropdown_select.input_value() == 'Python'


def test_select_radio_button(page: Page):
    """Radio button (round shape) - just one option can be enabled (ex. Male or Female or Other)"""
    logger.info("Given the Register demo page\n\tWhen I select the 'FeMale' radio button"
                "\n\tThen it becomes checked and 'Male' stays unchecked\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_REGISTER_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Find both radio buttons in the same group via Xpath
    female_radio = page.query_selector('//input[@value="FeMale"]')
    male_radio = page.query_selector('//input[@value="Male"]')

    # Verify state BEFORE the action: neither option is pre-selected
    assert not female_radio.is_checked()
    assert not male_radio.is_checked()

    # Select the female radio button
    female_radio.check()

    # Verify state AFTER the action: selecting one option deselects the other
    assert female_radio.is_checked()
    assert not male_radio.is_checked()


def test_select_checkbox_button(page: Page):
    """Checkbox button (square shape) - multiple options can be enabled (ex. Remote and Hybrid, but not on-site)"""
    logger.info("Given the Register demo page\n\tWhen I check the 'Cricket' checkbox"
                "\n\tThen it becomes checked\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_REGISTER_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Select checkbox button via Xpath
    checkbox_button = page.query_selector('//input[@value="Cricket"]')

    # Verify state BEFORE the action: unchecked by default
    assert not checkbox_button.is_checked()

    # Select the checkbox
    checkbox_button.check()

    # Verify state AFTER the action
    assert checkbox_button.is_checked()
