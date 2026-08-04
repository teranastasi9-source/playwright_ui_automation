import logging

import pytest
from config import AUTOMATIONTESTING_ALERTS_URL, AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def _make_dialog_handler(captured: list, response_text: str):
    """Return a dialog handler that records the dialog message and answers the prompt."""
    def handle_dialog(dialog):
        captured.append(dialog.message)
        dialog.accept(prompt_text=response_text)
    return handle_dialog


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_select_alertbox_with_ok(page: Page):
    """Verify a plain alert() dialog shows the expected message and is auto-accepted."""
    logger.info("Given the Alerts demo page\n\tWhen I trigger a plain alert box"
                "\n\tThen its message matches the expected text\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_ALERTS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Register the dialog handler BEFORE the click that triggers the alert
    captured_messages = []
    page.on("dialog", _make_dialog_handler(captured_messages, ""))

    # Find "click the button to display an alert box:" button via XPath referring to button`s parent and Click it
    page.wait_for_selector('//div[@id="OKTab"]/button').click()
    # Note: playwright automatically accepts the alert box (it's the only option for a plain alert())

    # Verify the received message matches the expected one
    assert captured_messages[0] == "I am an alert box!"


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_select_alertbox_with_ok_cancel(page: Page):
    """Verify a confirm() dialog ("Alert with OK & Cancel") shows the expected message."""
    logger.info("Given the Alerts demo page\n\tWhen I trigger a confirm box"
                "\n\tThen its message matches the expected text\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_ALERTS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Find "Alert with OK & Cancel" button via XPath and Click it
    alert_with_ok_cancel = page.wait_for_selector('//a[@href="#CancelTab"]')
    alert_with_ok_cancel.click()

    # Register the dialog handler BEFORE triggering it, so the click below
    # blocks until the dialog is handled and the message is captured
    captured_messages = []
    page.on("dialog", _make_dialog_handler(captured_messages, "I have just typed new message"))

    # Find "click the button to display a confirm box" button via XPath and Click it
    confirm_box = page.wait_for_selector('//div[@id="CancelTab"]/button')
    confirm_box.click()

    # Verify the received message matches the expected one
    assert captured_messages[0] == "Press a Button !"


@pytest.mark.no_browsers_in_ci("firefox", "webkit", reason=AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON)
def test_select_alertbox_with_textbox(page: Page):
    """Verify a prompt() dialog ("Alert with TextBox") shows the expected message and accepts input."""
    logger.info("Given the Alerts demo page\n\tWhen I trigger the prompt box and answer it"
                "\n\tThen its message matches the expected text\n")

    # Launch the browser and navigate to the login page URL
    page.goto(AUTOMATIONTESTING_ALERTS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Find "Alert with TextBox" button via XPath and Click it
    page.wait_for_selector('//a[@href="#Textbox"]').click()

    # Register the dialog handler BEFORE the click that triggers the prompt box
    captured_messages = []
    page.on("dialog", _make_dialog_handler(captured_messages, "I have just typed new message"))

    # Find "click the button to display the prompt box" button via XPath and Click it
    page.wait_for_selector('//div[@id="Textbox"]/button').click()

    # Verify the received message matches the expected one
    assert captured_messages[0] == "Please enter your name"
