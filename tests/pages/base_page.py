import re

from playwright.sync_api import Page, expect


class BasePage:
    """Shared navigation/interaction helpers reused by every page object."""

    def __init__(self, page: Page):
        self.page = page

    def goto_url(self, url: str):
        self.page.goto(rf"{url}")                   # Navigate to the webpage URL
        self.page.wait_for_load_state("load")

    def check_title(self, title: str):
        expect(self.page).to_have_title(re.compile(pattern=fr'{title}', flags=re.IGNORECASE))

    def is_visible(self, locator):
        expect(locator).to_be_visible()

    def is_enabled(self, locator):
        expect(locator).to_be_enabled()

    def click_button(self, button):
        self.is_visible(button)
        self.is_enabled(button)
        button.click()
