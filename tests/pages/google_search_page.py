from playwright.sync_api import Page

from pages.base_page import BasePage


class GooglePage(BasePage):
    """Google search homepage: search box, cookie-consent handling, and results title."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.cookie_button = page.get_by_role(role="button", name="Accept all")
        self.search_combobox = page.get_by_role(role="combobox", name="Search")

    def enter_search(self, search:str):
        self.search_combobox.fill(search)
