import logging

import pytest
from config import (
    AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON,
    AUTOMATIONTESTING_INDEX_URL,
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_LOGIN_URL,
)
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_css_locators_via_id(page: Page):
    """Verify a field can be located and filled using a CSS id selector."""
    logger.info("Given the demo login page\n\tWhen I locate the email field via a CSS id selector"
                "\n\tThen the value I typed is present before submitting\n")

    # Navigate to URL
    page.goto(AUTOMATIONTESTING_INDEX_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Define CSS locator for email field via id (#email)
    email_txt_box = page.locator('#email')

    # Enter 'test@gmail.com' email into email locator
    email_txt_box.type('test@gmail.com')

    # Verify the value was actually entered before submitting
    expect(email_txt_box).to_have_value('test@gmail.com')

    # Define CSS locator for login button via id (#enterimg) and click it
    button_login = page.locator('#enterimg')
    button_login.click()


def test_css_locators_via_attribute(page: Page):
    """Verify login succeeds using CSS attribute selectors to locate the username/password/submit fields."""
    logger.info("Given the OrangeHRM login page\n\tWhen I log in using CSS attribute selectors"
                "\n\tThen I land on the dashboard\n")

    # Navigate to URL
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Define CSS locator for username via attribute and type it in
    username = page.locator('input[name="username"]')
    username.type(ORANGEHRM_ADMIN_USERNAME)

    # Define CSS locator for password via attribute and type it in
    password = page.locator('input[type="password"]')
    password.type(ORANGEHRM_ADMIN_PASSWORD)

    # Define CSS locator for the submit button via attribute and click it
    login_button = page.locator('button[type="submit"]')
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
    # Verified live (2026-08-03) that this text's casing actually flips between visits -
    # "Forgot your password?" and "Forgot Your Password?" have both been observed within the
    # same session, presumably inconsistent server instances/edge nodes behind this demo. A
    # case-sensitive exact match broke as soon as it flipped, so this uses XPath's translate()
    # to lowercase both sides before comparing - same fix applied to the two locators below,
    # which showed the identical flip-flopping behavior for "username".
    lower = "translate(%s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    forgot_your_password_button = page.locator(
        f"//p[contains({lower % '.'}, 'forgot your password')]"
    )
    forgot_your_password_button.click()

    # Verify we actually navigated to the password-reset request page
    page.wait_for_url('**/requestPasswordResetCode')

    # 'contains' -> //tagname[contains(@attribute, 'value')]
    # 'username' label - use locator() instead of wait_for_selector() here,
    # because expect() only works with Locator objects, not ElementHandle.
    username_inscription = page.locator(f"//label[contains({lower % '.'}, 'username')]")
    expect(username_inscription).to_be_visible()

    # 'username' field, located via a partial-attribute XPath match
    username_field = page.locator(f"//input[contains({lower % '@placeholder'}, 'user')]")
    expect(username_field).to_be_visible()
