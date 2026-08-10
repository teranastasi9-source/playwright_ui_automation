from config import (
    ORANGEHRM_ADD_ENTITLEMENT_URL,
    ORANGEHRM_ADD_LEAVE_TYPE_URL,
    ORANGEHRM_APPLY_LEAVE_URL,
    ORANGEHRM_DEFINE_LEAVE_PERIOD_URL,
)
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class LeavePage(BasePage):
    """Leave pages - period/type configuration and entitlements (Admin), applying (ESS)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.save_button = page.get_by_role("button", name="Save")
        self.confirm_button = page.get_by_role("button", name="Confirm")
        self.apply_button = page.get_by_role("button", name="Apply")
        self.my_leave_tab = page.get_by_text("My Leave", exact=True)

    def field(self, label: str) -> Locator:
        return self.page.locator(".oxd-input-group", has_text=label).locator("input")

    def _fill_date(self, label: str, iso_date: str) -> None:
        # A plain .fill() on these OXD date inputs appends to their existing value instead of
        # replacing it (verified directly) - .fill("") first, then .type(), then Escape to
        # dismiss the calendar popover without it re-touching the value.
        date_field = self.field(label)
        date_field.click()
        date_field.fill("")
        date_field.type(iso_date)
        self.page.keyboard.press("Escape")

    def _select_dropdown_option(self, option_text: str) -> None:
        self.page.locator("text=-- Select --").first.click()
        self.page.get_by_role("option", name=option_text, exact=True).click()

    def _wait_for_save(self) -> None:
        # These are Vue SPA saves, not full page navigations - wait_for_load_state("load")
        # resolves before the save actually completes server-side (verified directly on
        # AddEmployeePage's save; applied defensively here too). The success toast is the
        # real completion signal.
        self.page.get_by_text("Successfully Saved").wait_for(state="visible")

    def define_leave_period(self) -> None:
        # Just saves the already-defaulted current-year period - safe to call more than
        # once, re-saving the same period is a verified no-op, not an error.
        self.goto_url(ORANGEHRM_DEFINE_LEAVE_PERIOD_URL)
        self.click_button(self.save_button)
        self._wait_for_save()

    def add_leave_type(self, name: str) -> None:
        self.goto_url(ORANGEHRM_ADD_LEAVE_TYPE_URL)
        self.field("Name").fill(name)
        self.click_button(self.save_button)
        self._wait_for_save()

    def add_entitlement(self, employee_search_text: str, employee_full_name: str, leave_type: str, days: int) -> None:
        # employee_search_text is what's typed into the autocomplete (e.g. a first name);
        # employee_full_name is the exact suggestion clicked.
        self.goto_url(ORANGEHRM_ADD_ENTITLEMENT_URL)

        employee_input = self.field("Employee Name")
        employee_input.fill(employee_search_text)
        self.page.get_by_text(employee_full_name, exact=True).wait_for(state="visible")
        self.page.get_by_text(employee_full_name, exact=True).click()

        self._select_dropdown_option(leave_type)
        self.field("Entitlement").fill(str(days))

        self.click_button(self.save_button)
        # OrangeHRM confirms before overwriting an employee's existing (here: zero) entitlement.
        self.click_button(self.confirm_button)
        self._wait_for_save()

    def apply_leave(self, leave_type: str, iso_date: str) -> None:
        self.goto_url(ORANGEHRM_APPLY_LEAVE_URL)
        self._select_dropdown_option(leave_type)
        self._fill_date("From Date", iso_date)
        self._fill_date("To Date", iso_date)
        self.click_button(self.apply_button)
        self._wait_for_save()

    def my_leave_row(self, iso_date: str) -> Locator:
        self.click_button(self.my_leave_tab)
        self.page.wait_for_load_state("load")
        return self.page.locator("div.oxd-table-card", has_text=iso_date)
