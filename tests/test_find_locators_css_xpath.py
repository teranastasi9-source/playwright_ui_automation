import logging

from config import (
    AUTOMATIONTESTING_INDEX_URL,
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_LOGIN_URL,
)
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_css_locators_via_id(page: Page):
    """Verify a field can be located and filled using a CSS id selector."""
    logger.info("Given the demo login page\n\tWhen I locate the email field via a CSS id selector"
                "\n\tThen the value I typed is present before submitting\n")

    # Navigate to URL
    page.goto(AUTOMATIONTESTING_INDEX_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Define CSS locator for email field via id (#email)
    email_txt_box = page.wait_for_selector('#email')

    # Enter 'test@gmail.com' email into email locator
    email_txt_box.type('test@gmail.com')

    # Verify the value was actually entered before submitting
    assert email_txt_box.input_value() == 'test@gmail.com'

    # Define CSS locator for login button via id (#enterimg) and click it
    button_login = page.wait_for_selector('#enterimg')
    button_login.click()


def test_css_locators_via_attribute(page: Page):
    """Verify login succeeds using CSS attribute selectors to locate the username/password/submit fields."""
    logger.info("Given the OrangeHRM login page\n\tWhen I log in using CSS attribute selectors"
                "\n\tThen I land on the dashboard\n")

    # Navigate to URL
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Define CSS locator for username via attribute and type it in
    username = page.wait_for_selector('input[name="username"]')
    username.type(ORANGEHRM_ADMIN_USERNAME)

    # Define CSS locator for password via attribute and type it in
    password = page.wait_for_selector('input[type="password"]')
    password.type(ORANGEHRM_ADMIN_PASSWORD)

    # Define CSS locator for the submit button via attribute and click it
    login_button = page.wait_for_selector('button[type="submit"]')
    login_button.click()

    # Verify the login actually succeeded and landed on the dashboard
    page.wait_for_url('**/dashboard/**')
    expect(page).to_have_title("OrangeHRM")


def test_css_locators_via_xpath(page: Page):
    """Verify elements can be located with several XPath strategies (text, contains) on the password-reset flow."""
    logger.info("Given the OrangeHRM login page\n\tWhen I navigate to 'Forgot your password?' via XPath locators"
                "\n\tThen the password-reset page and its fields are located correctly\n")

    # Navigate to URL
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Define relative XPath '//' locator for the 'Forgot Your Password?' link and click it
    # using text() - //tagname[text()='']
    # Verified against the live site (2026-08-03): the exact wording/casing is
    # "Forgot Your Password? " (capital Y) - it previously read "Forgot your
    # password? " (lowercase y), so this drifted from a real content change on
    # OrangeHRM's demo, not a code bug.
    forgot_your_password_button = page.wait_for_selector("//p[text()='Forgot Your Password? ']")
    forgot_your_password_button.click()

    # Verify we actually navigated to the password-reset request page
    page.wait_for_url('**/requestPasswordResetCode')

    # 'contains' -> //tagname[contains(@attribute, 'value')]
    # 'username' label - use locator() instead of wait_for_selector() here,
    # because expect() only works with Locator objects, not ElementHandle.
    # Verified against the live site (2026-08-03): both the label text and the
    # placeholder below are now lowercase "username" (previously "Username"/
    # placeholder containing "User") - same kind of real content drift as above.
    username_inscription = page.locator('//label[contains(text(), "username")]')
    expect(username_inscription).to_be_visible()

    # 'username' field, located via a partial-attribute XPath match
    username_field = page.locator('//input[contains(@placeholder, "user")]')
    expect(username_field).to_be_visible()
