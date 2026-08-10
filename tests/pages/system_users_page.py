from config import ORANGEHRM_SYSTEM_USERS_URL
from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class SystemUsersPage(BasePage):
    """Admin > User Management > System Users - used here only to clean up a test-created login."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.confirm_delete_button = page.get_by_role("button", name="Yes, Delete")

    def user_row(self, username: str) -> Locator:
        return self.page.locator("div.oxd-table-card", has_text=username)

    def delete_user(self, username: str) -> None:
        self.goto_url(ORANGEHRM_SYSTEM_USERS_URL)
        row = self.user_row(username).first
        row.get_by_role("button").first.click()  # trash icon is the first action button in the row
        self.click_button(self.confirm_delete_button)
        expect(self.user_row(username)).to_have_count(0)
