from config import ORANGEHRM_NAV_TIMEOUT_MS
from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class JobTitlesPage(BasePage):
    """Admin > Job > Job Titles page (OrangeHRM demo)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.add_button = page.get_by_role("button", name="Add")
        self.save_button = page.get_by_role("button", name="Save")
        self.confirm_delete_button = page.get_by_role("button", name="Yes, Delete")

    def job_title_row(self, title: str) -> Locator:
        return self.page.locator("div.oxd-table-card", has_text=title)

    def add_job_title(self, title: str, description: str) -> None:
        self.click_button(self.add_button)

        title_group = self.page.locator(".oxd-input-group", has_text="Job Title")
        description_group = self.page.locator(".oxd-input-group", has_text="Job Description")
        title_group.locator("input").fill(title)
        description_group.locator("textarea").fill(description)

        self.click_button(self.save_button)
        self.page.wait_for_url("**/viewJobTitleList", timeout=ORANGEHRM_NAV_TIMEOUT_MS)

        # The list re-fetches over the network after the redirect, so wait
        # for the new row itself rather than trusting the URL change alone.
        self.job_title_row(title).first.wait_for(state="visible", timeout=ORANGEHRM_NAV_TIMEOUT_MS)

    def delete_job_title(self, title: str) -> None:
        row = self.job_title_row(title).first
        row.get_by_role("button").first.click()  # trash icon is the first action button in the row
        self.click_button(self.confirm_delete_button)
        expect(self.job_title_row(title)).to_have_count(0)
