"""Named URLs for the demo sites and self-hosted instances used across the test suite.

Centralising them here means a dead/changed demo site only needs updating
in one place instead of being hunted down across every test file.
"""

import os

# expandtesting.com - login flow demos
EXPANDTESTING_LOGIN_URL = "https://practice.expandtesting.com/login"
# The one account this demo site actually authenticates - also duplicated in
# test_data/data.json's parametrize cases, since JSON fixtures can't import
# from here. Keep both in sync if this ever changes.
EXPANDTESTING_VALID_USERNAME = "practice"
EXPANDTESTING_VALID_PASSWORD = "SuperSecretPassword!"
# Verified 2026-08-03, then re-verified 2026-08-05 (behavior had drifted - see git history):
# this login form fingerprints Firefox/WebKit-driven requests to /authenticate and rejects
# even genuinely valid credentials for those two engines specifically. Chromium is unaffected.
# Not a code bug, not fixable by a retry - test_login.py mocks around it for those two engines
# instead of skipping outright (see that file's mock_login_outcome_for_flaky_engines).

# Self-hosted OrangeHRM (see docker-compose.orangehrm.yml + orangehrm/ and "Self-hosted
# OrangeHRM" in README.md). ORANGEHRM_BASE_URL defaults to the port docker-compose.orangehrm.yml
# publishes; override it if that instance is reachable elsewhere (e.g. by service name on
# a shared Docker network - see README).
ORANGEHRM_BASE_URL = os.environ.get("ORANGEHRM_BASE_URL", "http://localhost:8300")
ORANGEHRM_LOGIN_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/auth/login"
ORANGEHRM_DASHBOARD_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/dashboard/index"
ORANGEHRM_JOB_TITLES_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/admin/viewJobTitleList"
ORANGEHRM_JOB_TITLES_API_URL_PATTERN = "**/api/v2/admin/job-titles**"
ORANGEHRM_JOB_TITLES_API_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/api/v2/admin/job-titles"
ORANGEHRM_ADD_EMPLOYEE_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/pim/addEmployee"
ORANGEHRM_SYSTEM_USERS_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/admin/viewSystemUsers"
ORANGEHRM_DEFINE_LEAVE_PERIOD_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/leave/defineLeavePeriod"
ORANGEHRM_ADD_LEAVE_TYPE_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/leave/defineLeaveType"
ORANGEHRM_ADD_ENTITLEMENT_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/leave/addLeaveEntitlement"
ORANGEHRM_APPLY_LEAVE_URL = f"{ORANGEHRM_BASE_URL}/web/index.php/leave/applyLeave"
ORANGEHRM_ADMIN_USERNAME = "Admin"
# Must satisfy both OrangeHRM's install-time password policy and its separate post-login
# weak-password check - see orangehrm/entrypoint.sh and docker-compose.orangehrm.yml, which
# set this same password when installing the instance. Keep both in sync if this changes.
ORANGEHRM_ADMIN_PASSWORD = "QaPlayground#2026"
# How long to wait for a post-login/post-save redirect on this instance -
# shared by conftest.py and pages/job_titles_page.py.
ORANGEHRM_NAV_TIMEOUT_MS = 15000

# Non-functional check: fail if a request takes noticeably longer than its
# normal, verified latency. 2000ms leaves headroom for CI variance while still
# catching a genuinely broken/slow response.
API_MAX_RESPONSE_TIME_MS = 2000
