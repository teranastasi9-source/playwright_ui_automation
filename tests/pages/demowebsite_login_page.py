import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page for the practice.expandtesting.com demo site (login form + secure-area landing)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.get_by_role("textbox", name="Username")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.password_field = page.get_by_label("Password")
        self.login_button   = page.get_by_role("button", name="Login")
        self.logout_button  = page.get_by_role("link", name="Logout")

    def check_url(self, url:str):
        expect(self.page).to_have_url(re.compile(pattern=fr'{url}', flags=re.IGNORECASE))

    def check_page(self, url, title):
        self.check_url(url)
        self.check_title(title)

    def enter_username(self, username:str):
        self.username_input.fill(username)

    def enter_password(self, password:str):
        self.is_visible(self.password_field)
        self.is_enabled(self.password_input)
        self.password_input.fill(password)

    def login(self, username:str, password:str):
        self.enter_username(username=username)
        self.enter_password(password=password)
        self.click_button(button=self.login_button)

    def check_message(self, message:str):
        # The site renders both success and error banners inside #flash.
        # Matching free text anywhere on the page (get_by_text) previously
        # produced false positives, because the page also contains static
        # documentation text that happens to contain phrases like
        # "Invalid username." unrelated to the actual flash message.
        expect(self.page.locator("#flash")).to_contain_text(message)
