import json
import logging
from pathlib import Path

import pytest
from config import (
    EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON,
    EXPANDTESTING_LOGIN_URL,
    EXPANDTESTING_VALID_PASSWORD,
    EXPANDTESTING_VALID_USERNAME,
)
from pages.demowebsite_login_page import LoginPage

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent / "test_data" / "data.json"
# The valid username/password in there mirror config.py's EXPANDTESTING_VALID_USERNAME/
# PASSWORD - duplicated because JSON fixtures can't import Python constants.

# NOTE: this site does not reveal which field was wrong (a deliberate,
# common security practice) unless the username field is left empty.
# Verified against the live site: both "wrong username" and "wrong
# password" (with the other field valid) render the SAME flash message,
# "Your password is invalid!". The page's own on-page documentation text
# claims a separate "Invalid username." message exists, but that text is
# never actually rendered by the login form itself - asserting against it
# was a false-positive bug (get_by_text matched that unrelated docs text
# instead of the real #flash banner).


def get_login_test_data() -> list[tuple[str, str, str]]:
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return [(item["username"], item["password"], item["expected_message"]) for item in data]


@pytest.mark.smoke
@pytest.mark.no_browsers("firefox", "webkit", reason=EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON)
def test_login_successful(login_page: LoginPage) -> None:
    """Verify a user can log in with valid credentials and reach the secure area."""
    logger.info("Given valid credentials\n\tWhen I log in\n\tThen I am redirected to the secure area\n")

    # Launch the browser and navigate to the login page URL
    login_page.goto_url(EXPANDTESTING_LOGIN_URL)

    # Verify that the 'login' page is displayed successfully
    login_page.check_page(url=r'.*/login', title="login")

    # Login with valid username and password
    login_page.login(username=EXPANDTESTING_VALID_USERNAME, password=EXPANDTESTING_VALID_PASSWORD)

    # Verify that the user is redirected to the /secure page
    login_page.check_page(url=r'.*/secure', title="secure")

    # Confirm the success message "You logged into a secure area!" is visible
    login_page.check_message(message="You logged into a secure area!")

    # Verify that a Logout button is displayed and click it
    login_page.click_button(login_page.logout_button)


@pytest.mark.no_browsers("firefox", "webkit", reason=EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON)
def test_login_invalid_username(login_page: LoginPage) -> None:
    """Verify logging in with an invalid username shows the real error message and keeps the user on /login."""
    logger.info("Given the login page\n\tWhen I log in with an invalid username and valid password"
                "\n\tThen an error message is shown and I remain on the login page\n")

    # Navigate to the login page URL
    login_page.goto_url(EXPANDTESTING_LOGIN_URL)

    # Verify that the 'login' page is displayed successfully
    login_page.check_page(url=r'.*/login', title="login")

    # Login with invalid username and valid password
    login_page.login(username="wrongUser", password=EXPANDTESTING_VALID_PASSWORD)

    # Verify that the real error message is displayed
    login_page.check_message(message="Your password is invalid!")

    # Ensure the user remains on the 'login' page
    login_page.check_page(url=r'.*/login', title="login")


@pytest.mark.no_browsers("firefox", "webkit", reason=EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON)
def test_login_invalid_password(login_page: LoginPage) -> None:
    """Verify logging in with an invalid password shows the real error message and keeps the user on /login."""
    logger.info("Given the login page\n\tWhen I log in with a valid username and invalid password"
                "\n\tThen an error message is shown and I remain on the login page\n")

    # Launch the browser and navigate to the login page URL
    login_page.goto_url(EXPANDTESTING_LOGIN_URL)

    # Verify that the 'login' page is displayed successfully
    login_page.check_page(url=r'.*/login', title="login")

    # Login with valid username and invalid password
    login_page.login(username=EXPANDTESTING_VALID_USERNAME, password="WrongPassword")

    # Verify that the real error message is displayed
    login_page.check_message(message="Your password is invalid!")

    # Ensure the user remains on the 'login' page
    login_page.check_page(url=r'.*/login', title="login")


@pytest.mark.parametrize("username,password,expected_message", get_login_test_data())
@pytest.mark.no_browsers("firefox", "webkit", reason=EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON)
def test_login_with_various_credentials(login_page: LoginPage, username, password, expected_message) -> None:
    """Verify each username/password combination in data.json produces its expected login outcome."""
    logger.info(f"Given the login page\n\tWhen I log in with username='{username}'"
                f"\n\tThen the message '{expected_message}' is displayed\n")

    # Launch the browser and navigate to the login page URL
    login_page.goto_url(EXPANDTESTING_LOGIN_URL)

    # Verify that the 'login' page is displayed successfully
    login_page.check_page(url=r'.*/login', title="login")

    # Login with the parametrized username and password
    login_page.login(username, password)

    # Verify the message that matches this specific combination of credentials
    login_page.check_message(message=expected_message)

    # Only a successful login reaches the secure area and shows a Logout button
    if expected_message == "You logged into a secure area!":
        login_page.click_button(login_page.logout_button)
