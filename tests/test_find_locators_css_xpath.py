import logging

from config import (
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_LOGIN_URL,
)
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_css_locators_via_id(page: Page, qa_playground_url: str):
    """
    Test verifies a field can be located and filled using a CSS id selector.

    Test Steps:
    1. Navigate to the Login form page.
    2. Locate the email field via the CSS id selector #email and type an email into it.
    3. Locate the login button via the CSS id selector #enterimg and click it.

    Expected results:
    The email field holds the typed value before the button is clicked.
    """
    logger.info("Given the Login form page\n\tWhen I locate the email field via a CSS id selector"
                "\n\tThen the value I typed is present before submitting\n")

    # Navigate to URL
    page.goto(f"{qa_playground_url}/login_form.html")
    page.wait_for_load_state("load")

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
    """
    Test verifies each login field is correctly targeted via a CSS attribute selector, not
    just that login succeeds.

    Test Steps:
    1. Navigate to the OrangeHRM login page.
    2. Locate the username field via input[name="username"] and type the admin username.
    3. Locate the password field via input[type="password"] and type the admin password.
    4. Locate the submit button via button[type="submit"] and click it.

    Expected results:
    The username field holds the typed value before submitting. The password field is a real
    masked input (type="password") and holds some non-empty value, without ever asserting its
    literal content. The submit button is enabled before being clicked, and clicking it lands
    on the Dashboard.
    """
    logger.info("Given the OrangeHRM login page\n\tWhen I fill each field via a CSS attribute selector"
                "\n\tThen each one actually received the value before I submit, and login succeeds\n")

    # Navigate to URL
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Define CSS locator for username via attribute, type it in, and verify it actually took -
    # the point is confirming the attribute selector found the right, unique element, not just
    # that login eventually succeeds (same discipline as test_css_locators_via_id's id selector).
    username = page.locator('input[name="username"]')
    username.type(ORANGEHRM_ADMIN_USERNAME)
    expect(username).to_have_value(ORANGEHRM_ADMIN_USERNAME)

    # Define CSS locator for password via attribute and type it in. Never assert the literal
    # value of a password field - confirm it actually received something instead, and that the
    # attribute selector found a real, masked password input rather than a lookalike text field.
    password = page.locator('input[type="password"]')
    password.type(ORANGEHRM_ADMIN_PASSWORD)
    expect(password).not_to_have_value("")
    assert password.get_attribute("type") == "password"

    # Define CSS locator for the submit button via attribute, verify it's actually clickable,
    # then click it
    login_button = page.locator('button[type="submit"]')
    expect(login_button).to_be_enabled()
    login_button.click()

    # Verify the login actually succeeded and landed on the dashboard
    page.wait_for_url('**/dashboard/**')
    expect(page).to_have_title("OrangeHRM")


def test_css_locators_via_xpath(page: Page):
    """
    Test verifies elements can be located with several XPath strategies (text, contains) on
    the password-reset flow.

    Test Steps:
    1. Navigate to the OrangeHRM login page.
    2. Locate and click "Forgot your password?" via an XPath contains() match.
    3. Locate the resulting page's heading via an XPath text() match.
    4. Locate the resulting page's explanatory notice via an XPath contains() match.

    Expected results:
    Clicking "Forgot your password?" navigates to /requestPasswordResetCode. Because this
    self-hosted instance has no SMTP configured, that page shows a "Reset Password" heading
    and a notice explaining email isn't configured, both visible and both located successfully
    with XPath.
    """
    logger.info("Given the OrangeHRM login page\n\tWhen I navigate to 'Forgot your password?' via XPath locators"
                "\n\tThen the password-reset page's content is located correctly\n")

    # Navigate to URL
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Define relative XPath '//' locator for the 'Forgot Your Password?' link and click it
    # using contains() - //tagname[contains(., 'text')]. Case-insensitive via translate() as
    # a general defensive habit for user-facing copy, even though this self-hosted, single,
    # controlled instance has no reason for its own text to drift between requests.
    lower = "translate(%s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    forgot_your_password_button = page.locator(
        f"//p[contains({lower % '.'}, 'forgot your password')]"
    )
    forgot_your_password_button.click()

    # Verify we actually navigated to the password-reset request page
    page.wait_for_url('**/requestPasswordResetCode')

    # This self-hosted instance has no SMTP configured, so the reset page shows an
    # explanatory notice instead of a username form - verified directly (see
    # test_data/qa_playground/ note in README re: verifying real behavior before asserting
    # on it). Still demonstrates the same two XPath strategies as before: text() via the
    # heading, contains() via the explanatory paragraph.
    reset_password_heading = page.locator(f"//h6[{lower % '.'} = 'reset password']")
    expect(reset_password_heading).to_be_visible()

    # Matches both the outer wrapper <p> and the inner text-bearing <p> (XPath's `.` aggregates
    # descendant text too) - .last narrows to the specific inner element actually holding it.
    not_configured_notice = page.locator(f"//p[contains({lower % '.'}, 'not configured to receive email')]").last
    expect(not_configured_notice).to_be_visible()
