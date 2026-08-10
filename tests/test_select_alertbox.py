import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def _make_dialog_handler(captured: list, response_text: str):
    """Return a dialog handler that records the dialog message and accepts it."""
    def handle_dialog(dialog):
        captured.append(dialog.message)
        dialog.accept(prompt_text=response_text)
    return handle_dialog


def _make_dismiss_handler(captured: list):
    """Return a dialog handler that records the dialog message and dismisses (cancels) it."""
    def handle_dialog(dialog):
        captured.append(dialog.message)
        dialog.dismiss()
    return handle_dialog


def test_select_alertbox_with_ok(page: Page, qa_playground_url: str):
    """
    Test verifies a plain alert() dialog shows the expected message and is auto-accepted.

    Test Steps:
    1. Navigate to the Alerts page.
    2. Register a dialog handler that records the dialog's message.
    3. Click the button that triggers a plain alert box.

    Expected results:
    The captured dialog message is exactly "I am an alert box!".
    """
    logger.info("Given the Alerts page\n\tWhen I trigger a plain alert box"
                "\n\tThen its message matches the expected text\n")

    # Launch the browser and navigate to the Alerts page
    page.goto(f"{qa_playground_url}/alerts.html")
    page.wait_for_load_state("load")

    # Register the dialog handler BEFORE the click that triggers the alert
    captured_messages = []
    page.on("dialog", _make_dialog_handler(captured_messages, ""))

    # Find "click the button to display an alert box:" button via XPath referring to button`s parent and Click it
    page.locator('//div[@id="OKTab"]/button').click()
    # Note: playwright automatically accepts the alert box (it's the only option for a plain alert())

    # Verify the received message matches the expected one
    assert captured_messages[0] == "I am an alert box!"


def test_confirming_deletion_removes_item_but_canceling_keeps_it(page: Page, qa_playground_url: str):
    """
    Test verifies accepting the confirm dialog actually deletes the item, and canceling
    leaves it in place.

    Test Steps:
    1. Navigate to the Alerts page and open the "Alert with OK & Cancel" tab.
    2. Click Delete on the sample item, then dismiss (Cancel) the confirmation.
    3. Click Delete again, then accept the confirmation this time.

    Expected results:
    The confirm dialog's message is "Press a Button !". After canceling, the item is still
    visible. After confirming, the item is hidden - actually removed, not coincidentally
    still rendered.
    """
    logger.info("Given the Alerts page's item list\n\tWhen I cancel the delete confirmation, then confirm it"
                "\n\tThen the item survives the cancel, and is actually removed after confirming\n")

    # Launch the browser and navigate to the Alerts page
    page.goto(f"{qa_playground_url}/alerts.html")
    page.wait_for_load_state("load")

    # Find "Alert with OK & Cancel" button via XPath and Click it
    page.locator('//a[@href="#CancelTab"]').click()

    item = page.locator("#sample-item")
    delete_button = item.locator("button")

    # Given: the item is there before anything happens
    expect(item).to_be_visible()

    # When: clicking Delete but dismissing (Cancel) the confirmation
    captured_messages = []
    page.once("dialog", _make_dismiss_handler(captured_messages))
    delete_button.click()

    # Then: the confirm message is right, and the item is still there - canceling must not delete it
    assert captured_messages[0] == "Press a Button !"
    expect(item).to_be_visible()

    # When: clicking Delete again and accepting the confirmation this time
    page.once("dialog", _make_dialog_handler(captured_messages, ""))
    delete_button.click()

    # Then: the item is actually gone, not just coincidentally still rendered
    expect(item).to_be_hidden()


def test_confirming_prompt_shows_personalized_greeting(page: Page, qa_playground_url: str):
    """
    Test verifies accepting the prompt with a name shows a personalized greeting, and
    canceling shows nothing.

    Test Steps:
    1. Navigate to the Alerts page and open the "Alert with TextBox" tab.
    2. Click the prompt button, then dismiss (Cancel) the prompt.
    3. Click the prompt button again, then accept it with the name "Ada".

    Expected results:
    The prompt's message is "Please enter your name". After canceling, no greeting is shown.
    After answering with "Ada", the greeting is visible and reads exactly "Hello, Ada!".
    """
    logger.info("Given the Alerts page's name prompt\n\tWhen I cancel the prompt, then answer it with a name"
                "\n\tThen no greeting appears after canceling, and the right one appears after answering\n")

    # Launch the browser and navigate to the Alerts page
    page.goto(f"{qa_playground_url}/alerts.html")
    page.wait_for_load_state("load")

    # Find "Alert with TextBox" button via XPath and Click it
    page.locator('//a[@href="#Textbox"]').click()

    prompt_button = page.locator('//div[@id="Textbox"]/button')
    greeting = page.locator("#greeting")

    # When: triggering the prompt but dismissing (Cancel) it
    captured_messages = []
    page.once("dialog", _make_dismiss_handler(captured_messages))
    prompt_button.click()

    # Then: the prompt message is right, and no greeting appears - canceling must not show one
    assert captured_messages[0] == "Please enter your name"
    expect(greeting).to_be_hidden()

    # When: triggering the prompt again and answering it with a name this time
    page.once("dialog", _make_dialog_handler(captured_messages, "Ada"))
    prompt_button.click()

    # Then: the greeting actually reflects the name that was typed, not just any greeting
    expect(greeting).to_be_visible()
    expect(greeting).to_have_text("Hello, Ada!")
