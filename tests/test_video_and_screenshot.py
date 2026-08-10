import logging
import os
from pathlib import Path

from playwright.sync_api import Browser, Page

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "reports" / "test-results"


def test_screenshot(page: Page, browser_name: str, qa_playground_url: str):
    """
    Test verifies both a viewport screenshot and a full-page screenshot are actually written
    to disk.

    Test Steps:
    1. Navigate to the Alerts page.
    2. Take a viewport screenshot, saved to a browser/worker-namespaced path.
    3. Take a full-page screenshot, saved to a different browser/worker-namespaced path.

    Expected results:
    Both screenshot files exist on disk with non-zero size.
    """
    logger.info("Given the Alerts page\n\tWhen I take a viewport and a full-page screenshot"
                "\n\tThen both image files exist on disk with content\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Launch the browser and navigate to the Alerts page
    page.goto(f"{qa_playground_url}/alerts.html")
    page.wait_for_load_state("load")

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


def test_video_recording_saved_to_disk(browser: Browser, qa_playground_url: str):
    """
    Test verifies a short recorded interaction actually produces a non-empty video file.

    Test Steps:
    1. Open a new browser context with video recording enabled.
    2. Navigate to the Playground index and click through to the Alerts page.
    3. Trigger a plain alert box and accept it.
    4. Close the context so the video is finalized.

    Expected results:
    The alert's captured message is "I am an alert box!", and the resulting video file exists
    on disk with non-zero size.
    """
    logger.info("Given a browser context with video recording enabled\n\tWhen I navigate the"
                " playground and trigger an alert\n\tThen a video file is saved to disk with content\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initiate video recording and the path where it has to be stored
    context = browser.new_context(record_video_dir=str(RESULTS_DIR))
    page = context.new_page()

    # Navigate the playground and trigger an alert, so there's real recorded interaction
    page.goto(f"{qa_playground_url}/index.html")
    page.wait_for_load_state("load")
    page.get_by_role("link", name="Alerts").click()
    page.wait_for_load_state("load")

    captured_messages = []

    def handle_dialog(dialog):
        captured_messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", handle_dialog)
    page.locator('//div[@id="OKTab"]/button').click()
    assert captured_messages[0] == "I am an alert box!"

    # Get the video
    video = page.video
    context.close()  # video file is only finalized once the context closes

    # Verify the video was actually recorded and saved to disk
    video_path = Path(video.path())
    assert video_path.exists() and video_path.stat().st_size > 0
