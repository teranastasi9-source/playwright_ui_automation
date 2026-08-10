import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def test_clearing_cookies_forgets_the_remembered_user(page: Page, qa_playground_url: str):
    """
    Test verifies "Remember me" persists the user's email via a cookie, and clearing cookies
    forgets it again.

    Test Steps:
    1. Navigate to the login form with no cookies set.
    2. Fill in an email, check "Remember me", and submit.
    3. Reload the page.
    4. Clear cookies and reload the page again.

    Expected results:
    Before login, no "remembered_email" cookie exists and the welcome-back message is hidden.
    After submitting with "Remember me" checked, the cookie is set and reloading pre-fills the
    email with a visible welcome-back message. After clearing cookies and reloading again, no
    cookie remains, the email field is empty, and the welcome-back message is hidden again.
    """
    logger.info("Given a user who logs in with 'Remember me' checked"
                "\n\tWhen the page is reloaded, then cookies are cleared and it's reloaded again"
                "\n\tThen the site remembers the user after the first reload, and forgets them after\n")

    email = "returning.user@example.com"

    # Given: a first-time visit - nothing remembered yet
    page.goto(f"{qa_playground_url}/login_form.html")
    page.wait_for_load_state("load")
    expect(page.locator("#welcome-back")).to_be_hidden()
    assert page.context.cookies() == []

    # When: the user logs in with 'Remember me' checked
    page.locator("#email").fill(email)
    page.locator("#remember-me").check()
    page.locator("#enterimg").click()

    # Then: a cookie is actually set for it - not just assumed from the checkbox being ticked
    cookies = page.context.cookies()
    assert any(cookie["name"] == "remembered_email" for cookie in cookies)

    # And: reloading the page remembers the user, driven by that cookie
    page.reload()
    page.wait_for_load_state("load")
    expect(page.locator("#email")).to_have_value(email)
    expect(page.locator("#welcome-back")).to_contain_text(f"Welcome back, {email}")

    # When: cookies are cleared and the page is reloaded again
    page.context.clear_cookies()
    page.reload()
    page.wait_for_load_state("load")

    # Then: the site has genuinely forgotten the user - not just that the cookie API returns empty
    assert page.context.cookies() == []
    expect(page.locator("#email")).to_have_value("")
    expect(page.locator("#welcome-back")).to_be_hidden()
