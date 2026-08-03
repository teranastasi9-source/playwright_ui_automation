import logging
from pathlib import Path

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

# NOTE: the classic public iframe demo for this (the-internet.herokuapp.com/iframe)
# is currently broken for reasons entirely outside this project's control: its
# embedded TinyMCE editor is served from a paid CDN plan that has hit its free
# monthly usage cap, so the editor loads read-only ("no more editor loads
# available this month"). Rather than chase yet another third-party demo that
# can rot the same way, this test uses a tiny, fully self-contained local HTML
# fixture - guaranteed stable, and it's still a real iframe/frame_locator
# scenario (a common real-world pattern: WYSIWYG editors, payment widgets,
# embedded dashboards, etc. all commonly live inside an iframe).
IFRAME_DEMO_PATH = Path(__file__).resolve().parent.parent / "test_data" / "iframe_demo.html"


def test_typed_text_is_reflected_inside_iframe(page: Page) -> None:
    """Verify text typed into an editable area inside an iframe is actually reflected inside that frame."""
    logger.info("Given a page with an editable area inside an iframe\n\tWhen I type text into it"
                "\n\tThen the frame's content reflects the new text\n")

    # Navigate to URL
    page.goto(IFRAME_DEMO_PATH.as_uri())
    page.wait_for_load_state("load")

    # Content inside an <iframe> lives in a separate document - page.locator()
    # can't see into it. frame_locator() is how Playwright scopes a locator to
    # the frame's content.
    notes_frame = page.frame_locator("#notes-frame")
    editable_area = notes_frame.locator("#editable-area")

    # Verify the editable area is visible and contains the expected text
    expect(editable_area).to_be_visible()
    expect(editable_area).to_have_text("Start typing your notes here...")

    # Type text into the editable area
    editable_area.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("Hello from Playwright!")

    # Verify the state actually changed inside the iframe, not just that we clicked something
    expect(editable_area).to_have_text("Hello from Playwright!")
