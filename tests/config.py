"""Named URLs for the third-party demo sites used across the test suite.

Centralising them here means a dead/changed demo site only needs updating
in one place instead of being hunted down across every test file.
"""

# expandtesting.com - login flow demos
EXPANDTESTING_LOGIN_URL = "https://practice.expandtesting.com/login"
# The one account this demo site actually authenticates - also duplicated in
# test_data/data.json's parametrize cases, since JSON fixtures can't import
# from here. Keep both in sync if this ever changes.
EXPANDTESTING_VALID_USERNAME = "practice"
EXPANDTESTING_VALID_PASSWORD = "SuperSecretPassword!"
# Verified 2026-08-03 via a controlled, browser-isolated repro (see "Cross-browser
# testing" in README.md): this login form fingerprints Firefox/WebKit-driven requests
# and misreports "Your username is invalid!" regardless of what was actually
# submitted. Chromium is unaffected. Not a code bug, not fixable by a retry.
EXPANDTESTING_LOGIN_BROWSER_LIMITATION_REASON = (
    "practice.expandtesting.com's login form misreports errors for Firefox/WebKit-driven "
    "requests (bot-detection fingerprinting) - see README.md's 'Cross-browser testing'"
)

# demo.automationtesting.in - assorted UI widget demos
AUTOMATIONTESTING_ALERTS_URL = "https://demo.automationtesting.in/Alerts.html"
AUTOMATIONTESTING_SELECTABLE_URL = "https://demo.automationtesting.in/Selectable.html"
AUTOMATIONTESTING_REGISTER_URL = "https://demo.automationtesting.in/Register.html"
AUTOMATIONTESTING_FILEUPLOAD_URL = "https://demo.automationtesting.in/FileUpload.html"
AUTOMATIONTESTING_WINDOWS_URL = "https://demo.automationtesting.in/Windows.html"
AUTOMATIONTESTING_INDEX_URL = "https://demo.automationtesting.in/Index.html"
# Verified 2026-08-04 across two separate CI runs: every test hitting this site
# reliably times out on Page.goto()/wait_for_selector() on Firefox/WebKit when run
# via GitHub Actions (never on Chromium, in the same runs) - but the identical
# tests, same browsers, pass 28/28 when run locally from a normal connection.
# Points at demo.automationtesting.in itself (or infra in front of it) treating
# non-Chromium traffic from datacenter IP ranges differently, not a code bug.
AUTOMATIONTESTING_CI_BROWSER_LIMITATION_REASON = (
    "demo.automationtesting.in reliably times out for Firefox/WebKit specifically when run "
    "from GitHub Actions' datacenter IPs (28/28 pass locally on the same browsers) - see "
    "README.md's 'Cross-browser testing'"
)

# OrangeHRM public demo instance
ORANGEHRM_LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
ORANGEHRM_DASHBOARD_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index"
ORANGEHRM_JOB_TITLES_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/admin/viewJobTitleList"
ORANGEHRM_JOB_TITLES_API_URL_PATTERN = "**/api/v2/admin/job-titles**"
ORANGEHRM_JOB_TITLES_API_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/api/v2/admin/job-titles"
ORANGEHRM_ADMIN_USERNAME = "Admin"
ORANGEHRM_ADMIN_PASSWORD = "admin123"
# How long to wait for a post-login/post-save redirect on this demo instance -
# shared by conftest.py and pages/job_titles_page.py.
ORANGEHRM_NAV_TIMEOUT_MS = 15000

# techlistic.com - static HTML table demo
TECHLISTIC_WEBTABLE_URL = "https://www.techlistic.com/2017/02/automate-demo-web-table-with-selenium.html"

# plus2net.com - AJAX dropdown demo
PLUS2NET_AJAX_URL = "https://www.plus2net.com/php_tutorial/ajax_drop_down_list-demo.php"

# the-internet.herokuapp.com (Dave Haeffner / Sauce Labs) - stable, well-known
# QA practice site. Replaces demo.imacros.net, which stopped resolving
# entirely (verified 2026-08-01: ERR_NAME_NOT_RESOLVED).
THE_INTERNET_DOWNLOAD_URL = "https://the-internet.herokuapp.com/download"

# reqres.in - public fake REST API used for API-level tests
REQRES_API_BASE_URL = "https://reqres.in/api"

# Non-functional check: fail if a request takes noticeably longer than its
# normal, verified latency (typically 20-150ms). 2000ms leaves headroom for
# network/CI variance while still catching a genuinely broken/slow response.
API_MAX_RESPONSE_TIME_MS = 2000

# Google
GOOGLE_URL = "https://google.com"
GOOGLE_NO_REDIRECT_URL = "https://google.com/ncr"
