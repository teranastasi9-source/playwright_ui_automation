import logging
import time
from datetime import date, timedelta

from config import (
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_BASE_URL,
    ORANGEHRM_LOGIN_URL,
)
from pages.contact_details_page import ContactDetailsPage
from pages.employee_page import AddEmployeePage
from pages.leave_page import LeavePage
from pages.system_users_page import SystemUsersPage
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def _login(page: Page, username: str, password: str) -> None:
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/dashboard/**")


def _logout(page: Page) -> None:
    page.goto(f"{ORANGEHRM_BASE_URL}/web/index.php/auth/logout")
    page.wait_for_load_state("load")


def test_new_employee_updates_own_contact_details(page: Page) -> None:
    """
    Test verifies a newly onboarded employee can log in on their own credentials, update
    their own contact details, and that the change actually persists - a full multi-actor
    lifecycle, not just a single screen.

    Test Steps:
    1. As Admin, onboard a new employee with their own ESS login.
    2. Log out, then log in as that employee on their own credentials.
    3. Update the employee's own City and Mobile fields on the Contact Details tab.
    4. Log out, then log back in as that same employee (a fresh session, not the same
       just-saved form).
    5. Reopen the Contact Details tab.
    6. As Admin again, delete the employee's user account.

    Expected results:
    After the fresh re-login, the City and Mobile fields show the values that were saved in
    step 3, proving the update actually persisted rather than only appearing to save on the
    same page. The account is removed cleanly at the end.
    """
    logger.info("Given an Admin onboards a new employee with their own login"
                "\n\tWhen that employee logs in and updates their own contact details"
                "\n\tThen the change persists after a fresh login, and the account can be removed\n")

    unique = int(time.time())
    username = f"ess.contact.{unique}"
    password = "EssContact#2026"
    city = f"Testville{unique}"
    mobile = "+48123456789"

    # Admin onboards a new employee with an ESS login
    _login(page, ORANGEHRM_ADMIN_USERNAME, ORANGEHRM_ADMIN_PASSWORD)
    add_employee_page = AddEmployeePage(page)
    add_employee_page.goto()
    add_employee_page.create_employee_with_login("Contact", "Tester", username, password)
    _logout(page)

    # That employee logs in on their own credentials and updates their own contact details
    _login(page, username, password)
    contact_details_page = ContactDetailsPage(page)
    contact_details_page.open()
    contact_details_page.update_city_and_mobile(city, mobile)
    _logout(page)

    # Verify the change actually persisted - re-read after a fresh login and page load,
    # not just trusted from the still-open form that was just saved
    _login(page, username, password)
    contact_details_page = ContactDetailsPage(page)
    contact_details_page.open()
    expect(contact_details_page.field("City")).to_have_value(city)
    expect(contact_details_page.field("Mobile")).to_have_value(mobile)
    _logout(page)

    # Cleanup: Admin removes the account
    _login(page, ORANGEHRM_ADMIN_USERNAME, ORANGEHRM_ADMIN_PASSWORD)
    SystemUsersPage(page).delete_user(username)


def test_new_employee_applies_for_leave(page: Page) -> None:
    """
    Test verifies a newly onboarded employee can log in on their own credentials, apply for
    leave, and that the application actually appears in their own leave list - another full
    multi-actor lifecycle.

    Test Steps:
    1. As Admin, define the current leave period, add a new leave type, and onboard a new
       employee with their own ESS login.
    2. As Admin, grant that employee a 5-day entitlement for the new leave type.
    3. Log out, then log in as the new employee on their own credentials.
    4. Apply for leave of the new type, for a date two weeks out.
    5. As Admin again, delete the employee's user account.

    Expected results:
    The employee's own leave list shows the new application with a "Pending Approval" status
    - read from their own list, not just assumed from a "Successfully Saved" toast. The
    account is removed cleanly at the end.
    """
    logger.info("Given an Admin configures leave (period, type, entitlement) for a new employee"
                "\n\tWhen that employee applies for leave on their own credentials"
                "\n\tThen the application appears in their own leave list, and the account can be removed\n")

    unique = int(time.time())
    username = f"ess.leave.{unique}"
    password = "EssLeave#2026"
    leave_type = f"Annual Leave {unique}"
    employee_first_name = f"Leave{unique}"
    employee_full_name = f"{employee_first_name} Tester"
    # A couple of weeks out, not "today" - avoids any same-day edge case in how the leave
    # module treats the current date, and stays safely inside the current-year period
    # define_leave_period() sets up (see that method's own docstring for why re-defining
    # it here is safe even if it already exists).
    leave_date = (date.today() + timedelta(days=14)).isoformat()

    # Admin configures the leave module and onboards a new employee with an ESS login
    _login(page, ORANGEHRM_ADMIN_USERNAME, ORANGEHRM_ADMIN_PASSWORD)
    leave_page = LeavePage(page)
    leave_page.define_leave_period()
    leave_page.add_leave_type(leave_type)

    add_employee_page = AddEmployeePage(page)
    add_employee_page.goto()
    add_employee_page.create_employee_with_login(employee_first_name, "Tester", username, password)

    leave_page.add_entitlement(employee_first_name, employee_full_name, leave_type, days=5)
    _logout(page)

    # That employee applies for leave on their own credentials
    _login(page, username, password)
    leave_page = LeavePage(page)
    leave_page.apply_leave(leave_type, leave_date)

    # Verify the application actually appears in their own leave list, pending approval
    expect(leave_page.my_leave_row(leave_date)).to_contain_text("Pending Approval")
    _logout(page)

    # Cleanup: Admin removes the account
    _login(page, ORANGEHRM_ADMIN_USERNAME, ORANGEHRM_ADMIN_PASSWORD)
    SystemUsersPage(page).delete_user(username)
