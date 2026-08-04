import base64
import os

import pytest
from config import (
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_LOGIN_URL,
    ORANGEHRM_NAV_TIMEOUT_MS,
)
from pages.demowebsite_login_page import LoginPage
from pages.google_search_page import GooglePage
from pytest_html import extras


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Name the HTML report and log file after the browser(s) actually under
    test, so running --browser=firefox after --browser=chromium doesn't
    silently overwrite the previous run's report - each browser (or
    combination, if several are passed together) gets its own file in
    reports/. Only kicks in when --html/--log-file weren't explicitly
    passed on the command line, so an explicit override still wins.
    """
    browsers = config.getoption("browser") or ["chromium"]
    suffix = "_".join(sorted(set(browsers)))

    raw_args = " ".join(config.invocation_params.args)
    if "--html" not in raw_args:
        config.option.htmlpath = f"reports/report_{suffix}.html"
    if "--log-file" not in raw_args:
        config.option.log_file = f"reports/test_logs_{suffix}.log"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Skip a test on browser engines it's marked as not supported on, instead
    of letting it run and fail there every time with a confusing,
    browser-specific error.

    Usage: @pytest.mark.no_browsers("firefox", "webkit", reason="...").
    Deliberately not pytest-playwright's own built-in `skip_browser` marker:
    that one only accepts a single browser name per decorator, and stacking
    two of them on the same test doesn't combine - get_closest_marker only
    ever returns the closest one, so the first would silently be ignored.
    """
    marker = item.get_closest_marker("no_browsers")
    if marker is not None and hasattr(item, "callspec"):
        browser_name = item.callspec.params.get("browser_name")
        if browser_name in marker.args:
            reason = marker.kwargs.get("reason", f"Not supported on {browser_name}")
            pytest.skip(reason)

    # Same idea as no_browsers above, but scoped to CI only - for a site that
    # works fine on these browsers from a normal/local connection, but not
    # from GitHub Actions' datacenter IP ranges specifically (verified
    # 2026-08-04: identical tests, same browsers, 28/28 passed locally on
    # Firefox+WebKit; only fail with connection timeouts when run via CI).
    # Usage: @pytest.mark.no_browsers_in_ci("firefox", "webkit", reason="...").
    ci_marker = item.get_closest_marker("no_browsers_in_ci")
    if ci_marker is not None and hasattr(item, "callspec") and os.environ.get("CI") == "true":
        browser_name = item.callspec.params.get("browser_name")
        if browser_name in ci_marker.args:
            reason = ci_marker.kwargs.get("reason", f"Not supported on {browser_name} in CI")
            pytest.skip(reason)


@pytest.fixture
def login_page(page):
    """Ready-to-use LoginPage POM bound to the current test's page."""
    return LoginPage(page)


@pytest.fixture
def google_page(page):
    """Ready-to-use GooglePage POM bound to the current test's page."""
    return GooglePage(page)


@pytest.fixture(scope="session")
def orangehrm_admin_storage_state(browser):
    """
    Log into OrangeHRM once per test session and capture the resulting
    storage_state (cookies etc.), instead of repeating the UI login flow
    in every single test that needs to be authenticated.
    """
    context = browser.new_context()
    page = context.new_page()
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")
    page.get_by_placeholder("Username").fill(ORANGEHRM_ADMIN_USERNAME)
    page.get_by_placeholder("Password").fill(ORANGEHRM_ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/dashboard/**", timeout=ORANGEHRM_NAV_TIMEOUT_MS)

    state = context.storage_state()
    context.close()
    return state


@pytest.fixture
def orangehrm_admin_page(browser, orangehrm_admin_storage_state):
    """
    An already-authenticated OrangeHRM page, built from the session-scoped
    storage_state above. Each test still gets its own fresh BrowserContext
    (isolation is preserved), it just skips redoing the login UI steps.
    """
    context = browser.new_context(storage_state=orangehrm_admin_storage_state)
    page = context.new_page()
    yield page
    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the HTML report for any test that fails during its call phase."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("orangehrm_admin_page")
        if page is not None:
            try:
                screenshot_b64 = base64.b64encode(page.screenshot()).decode("ascii")
            except Exception:
                # Best-effort only - e.g. the page/browser may already be
                # closed as part of why the test failed. A failed screenshot
                # attempt should never mask the real test failure.
                pass
            else:
                report_extras = getattr(report, "extras", [])
                report_extras.append(extras.image(screenshot_b64, name="Screenshot on failure"))
                report.extras = report_extras
