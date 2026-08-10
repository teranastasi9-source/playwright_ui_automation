import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_filling_and_submitting_registration_form_shows_matching_summary(page: Page, qa_playground_url: str):
    """
    Test verifies filling out the registration form and submitting it shows a summary
    matching exactly what was selected.

    Test Steps:
    1. Navigate to the Dropdowns page.
    2. Select "Python" from the Skills dropdown.
    3. Check the "FeMale" radio button.
    4. Check the "Cricket" and "Football" checkboxes, leaving "Hockey" unchecked.
    5. Click the submit button.

    Expected results:
    Before any selection, the dropdown is empty, no radio/checkbox is checked, and the
    summary is hidden. Each control reflects its own selection immediately (dropdown value,
    checked/unchecked radios and checkboxes) before submitting. After submitting, the summary
    reads exactly "Skills: Python | Gender: FeMale | Sports: Cricket, Football" - correctly
    omitting Hockey, which was never checked.
    """
    logger.info("Given the Registration form\n\tWhen I select a skill, a gender, and some sports, then submit"
                "\n\tThen the summary shown reflects exactly what was selected - and what wasn't\n")

    # Launch the browser and navigate to the Dropdowns page
    page.goto(f"{qa_playground_url}/dropdowns.html")
    page.wait_for_load_state("load")

    dropdown_select = page.locator('//select[@id="Skills"]')
    female_radio = page.locator('//input[@value="FeMale"]')
    male_radio = page.locator('//input[@value="Male"]')
    cricket_checkbox = page.locator('//input[@value="Cricket"]')
    football_checkbox = page.locator('//input[@value="Football"]')
    hockey_checkbox = page.locator('//input[@value="Hockey"]')
    submit_button = page.locator("#submit-registration")
    summary = page.locator("#summary")

    # Given: nothing filled in yet
    expect(dropdown_select).to_have_value("")
    expect(female_radio).not_to_be_checked()
    expect(male_radio).not_to_be_checked()
    expect(cricket_checkbox).not_to_be_checked()
    expect(summary).to_be_hidden()

    # When: selecting a skill in the dropdown
    dropdown_select.select_option(label="Python")
    expect(dropdown_select).to_have_value("Python")

    # When: selecting a gender - radio buttons in the same group are mutually exclusive
    female_radio.check()
    expect(female_radio).to_be_checked()
    expect(male_radio).not_to_be_checked()

    # When: checking two of the three sports, deliberately leaving Hockey unchecked -
    # checkboxes, unlike radio buttons, don't affect each other
    cricket_checkbox.check()
    football_checkbox.check()
    expect(cricket_checkbox).to_be_checked()
    expect(football_checkbox).to_be_checked()
    expect(hockey_checkbox).not_to_be_checked()

    # When: submitting the form
    submit_button.click()

    # Then: the summary reflects exactly what was selected - including that Hockey was not,
    # proving the submitted data actually matches every individual selection above
    expect(summary).to_be_visible()
    expect(summary).to_have_text("Skills: Python | Gender: FeMale | Sports: Cricket, Football")
