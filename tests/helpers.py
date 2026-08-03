from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def dismiss_cookie_consent_if_present(page: Page, timeout: int = 3000) -> None:
    """Dismiss demo.automationtesting.in's Funding Choices cookie-consent dialog.

    Verified across all three engines on 2026-08-03: the dialog is present in the DOM in
    Chromium too, but only actually rendered/blocking in Firefox and WebKit - so this is a
    no-op there and a real, necessary step here. Call it right after navigating to any
    demo.automationtesting.in page, before interacting with anything else on it.
    """
    consent_button = page.get_by_role("button", name="Consent", exact=True)
    try:
        consent_button.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError:
        return
    consent_button.click()
