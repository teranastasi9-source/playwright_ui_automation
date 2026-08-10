import logging

import pytest
from axe_playwright_python.sync_playwright import Axe
from config import ORANGEHRM_DASHBOARD_URL
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

HIGH_IMPACT = {"critical", "serious"}


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Self-hosted OrangeHRM's Dashboard has real, verified critical/serious axe-core "
        "violations - button-name (two icon-only buttons with no accessible name), "
        "color-contrast (8 elements below the minimum ratio), html-has-lang (<html> has no "
        "lang attribute), and list (a <ul> contains a non-<li> child). These are upstream "
        "defects in OrangeHRM's own markup, not something this suite's code can fix. "
        "strict=True: if a future OrangeHRM image release fixes them, this test starts "
        "unexpectedly passing and fails loudly instead of silently - a nudge to remove "
        "this marker rather than let it rot."
    ),
)
def test_dashboard_has_no_high_impact_accessibility_violations(orangehrm_admin_page: Page):
    """
    Test verifies an axe-core scan of the authenticated Dashboard finds no critical/serious
    accessibility violations.

    Test Steps:
    1. Navigate to the Dashboard as an authenticated Admin.
    2. Wait for its async widgets to finish loading.
    3. Run an axe-core accessibility scan against the rendered page.

    Expected results:
    The scan reports zero violations with "critical" or "serious" impact.
    """
    logger.info("Given the authenticated OrangeHRM Dashboard\n\tWhen I run an axe-core accessibility scan against it"
                "\n\tThen it reports no critical or serious violations\n")

    # Navigate to the Dashboard and let its async widgets (attendance, quick launch,
    # employee distribution) finish loading before scanning - a scan mid-render would
    # miss real issues in content that hasn't rendered yet.
    orangehrm_admin_page.goto(ORANGEHRM_DASHBOARD_URL)
    orangehrm_admin_page.wait_for_load_state("networkidle")

    results = Axe().run(orangehrm_admin_page)
    high_impact_violations = [v for v in results.response["violations"] if v["impact"] in HIGH_IMPACT]

    # Report body lists exactly which rules failed, on which elements, and why - not just
    # a bare pass/fail - so a real failure (a genuinely new regression) is actionable
    # straight from the pytest output, without re-running the scan by hand to find out.
    assert high_impact_violations == [], f"High-impact accessibility violations found:\n{results.generate_report()}"
