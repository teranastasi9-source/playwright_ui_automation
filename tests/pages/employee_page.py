from config import ORANGEHRM_ADD_EMPLOYEE_URL
from playwright.sync_api import Page

from pages.base_page import BasePage


class AddEmployeePage(BasePage):
    """PIM > Add Employee page - creates an employee record and, optionally, its own login."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input = page.get_by_placeholder("First Name")
        self.last_name_input = page.get_by_placeholder("Last Name")
        # OrangeHRM's own toggle to create a system login for the employee being added,
        # in the same step - revealed only after switching it on (see username_input etc.).
        self.create_login_toggle = page.locator(".oxd-switch-input")
        self.username_input = page.locator(".oxd-input-group", has_text="Username").locator("input")
        self.password_input = page.locator('input[type="password"]').first
        self.confirm_password_input = page.locator('input[type="password"]').last
        self.save_button = page.get_by_role("button", name="Save")

    def goto(self) -> None:
        self.goto_url(ORANGEHRM_ADD_EMPLOYEE_URL)

    def create_employee_with_login(self, first_name: str, last_name: str, username: str, password: str) -> None:
        # OrangeHRM auto-assigns the ESS (Employee Self Service) role to logins created
        # this way - verified directly, there's no separate role picker here.
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.click_button(self.create_login_toggle)

        self.username_input.fill(username)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)

        self.click_button(self.save_button)
        # This is a Vue SPA save, not a full page navigation - wait_for_load_state("load")
        # resolves before the save actually completes server-side (verified directly: without
        # this, an immediate logout+login-as-the-new-user race loses the save). The success
        # toast is the real completion signal.
        self.page.get_by_text("Successfully Saved").wait_for(state="visible")
