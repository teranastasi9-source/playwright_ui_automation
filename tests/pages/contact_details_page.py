from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class ContactDetailsPage(BasePage):
    """My Info > Contact Details tab - always the currently logged-in user's own record."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.my_info_link = page.get_by_text("My Info", exact=True)
        self.contact_details_tab = page.get_by_text("Contact Details", exact=True)
        self.save_button = page.get_by_role("button", name="Save")

    def field(self, label: str) -> Locator:
        return self.page.locator(".oxd-input-group", has_text=label).locator("input")

    def open(self) -> None:
        # Via the nav menu, not a direct URL - always routes to the current user's own
        # record, so no employee number needs to be known/passed in.
        self.click_button(self.my_info_link)
        self.page.wait_for_load_state("load")

        # Opening this tab kicks off an async GET that populates the form from the server.
        # Filling fields before it resolves is a real race, not a hypothetical one - verified
        # directly: the GET response handler overwrites whatever was just typed back to the
        # (for a brand-new employee, empty) server state, and a save right after silently
        # persists empty fields. wait_for_load_state("load") does not wait for this - it's an
        # in-page API call, not a navigation.
        with self.page.expect_response(lambda r: "contact-details" in r.url and r.request.method == "GET"):
            self.click_button(self.contact_details_tab)
        self.page.wait_for_load_state("load")

    def update_city_and_mobile(self, city: str, mobile: str) -> None:
        # .press("Tab") after each fill forces a blur - without it, filling Mobile second
        # discards City's unsaved value back to whatever was last loaded from the server
        # (verified directly: a Vue reactivity race, not a Playwright issue - the DOM shows
        # the typed value until the next field's own re-render silently reverts it).
        city_field = self.field("City")
        city_field.fill(city)
        city_field.press("Tab")

        mobile_field = self.field("Mobile")
        mobile_field.fill(mobile)
        mobile_field.press("Tab")

        self.click_button(self.save_button)
        # Vue SPA save, not a full page navigation - wait for the real completion signal
        # rather than trusting wait_for_load_state("load") (verified elsewhere in this
        # project's OrangeHRM pages that it resolves too early for this kind of save).
        self.page.get_by_text("Successfully Updated").wait_for(state="visible")
