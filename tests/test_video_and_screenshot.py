import logging
import os
from pathlib import Path

import pytest
from config import (
    AUTOMATIONTESTING_ALERTS_URL,
    ORANGEHRM_ADMIN_PASSWORD,
    ORANGEHRM_ADMIN_USERNAME,
    ORANGEHRM_LOGIN_URL,
    ORANGEHRM_NAV_TIMEOUT_MS,
)
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Browser, Page

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "reports" / "test-results"


def test_screenshot(page: Page, browser_name: str):
    """Verify both a viewport screenshot and a full-page screenshot are actually written to disk."""
    logger.info("Given the Alerts demo page\n\tWhen I take a viewport and a full-page screenshot"
                "\n\tThen both image files exist on disk with content\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Launch the browser and navigate to the Alerts demo page
    page.goto(AUTOMATIONTESTING_ALERTS_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Namespaced by browser + xdist worker: with parallel execution (pytest-xdist, or
    # --browser passed more than once), several of these can run at the same time and would
    # otherwise overwrite each other's screenshot mid-write.
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    screenshot_path = RESULTS_DIR / f"screenshot_1_{browser_name}_{worker_id}.png"
    full_page_screenshot_path = RESULTS_DIR / f"screenshot_2_{browser_name}_{worker_id}.png"

    # Do and save a screenshot under the provided path
    page.screenshot(path=screenshot_path)
    # Do and save a screenshot under the provided path for the full page
    page.screenshot(path=full_page_screenshot_path, full_page=True)

    # Verify both screenshots were actually written to disk
    assert screenshot_path.exists() and screenshot_path.stat().st_size > 0
    assert full_page_screenshot_path.exists() and full_page_screenshot_path.stat().st_size > 0


@pytest.mark.slow
def test_video_recording_saved_to_disk(browser: Browser):
    """Verify a login flow recorded on video actually produces a non-empty video file."""
    logger.info("Given a browser context with video recording enabled\n\tWhen I log in on OrangeHRM"
                "\n\tThen a video file is saved to disk with content\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initiate video recording and the path where it has to be stored
    context = browser.new_context(record_video_dir=str(RESULTS_DIR))
    page = context.new_page()

    # Launch the browser and navigate to the login page
    page.goto(ORANGEHRM_LOGIN_URL)
    page.wait_for_load_state("load")

    # Fill in the login form
    page.get_by_placeholder("Username").fill(ORANGEHRM_ADMIN_USERNAME)
    page.get_by_placeholder("Password").fill(ORANGEHRM_ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url('**/dashboard/**', timeout=ORANGEHRM_NAV_TIMEOUT_MS)

    # Get the video
    video = page.video
    context.close()  # video file is only finalized once the context closes

    # Verify the video was actually recorded and saved to disk
    video_path = Path(video.path())
    assert video_path.exists() and video_path.stat().st_size > 0
