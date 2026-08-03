import logging
import os
from pathlib import Path

import pytest
from config import AUTOMATIONTESTING_FILEUPLOAD_URL, THE_INTERNET_DOWNLOAD_URL
from helpers import dismiss_cookie_consent_if_present
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def test_upload_file(page: Page):
    """Verify a local file can be selected via the file input and is registered by the browser."""
    logger.info("Given the file upload demo page\n\tWhen I select a local file via the file input"
                "\n\tThen the browser registers the correct file name\n")

    # Launch the browser and navigate to the file upload demo page
    page.goto(AUTOMATIONTESTING_FILEUPLOAD_URL)
    page.wait_for_load_state("load")
    dismiss_cookie_consent_if_present(page)

    # Define path to the file that will be uploaded
    file_to_be_uploaded = TEST_DATA_DIR / "file_to_be_uploaded.txt"

    # Find "Browse..." button via XPath
    browse_button = page.wait_for_selector('//input[@id="input-4"]')

    # Upload the file
    browse_button.set_input_files(str(file_to_be_uploaded))

    # Verify the browser actually registered the selected file
    uploaded_file_name = browse_button.evaluate("el => el.files.length ? el.files[0].name : null")
    assert uploaded_file_name == file_to_be_uploaded.name


@pytest.mark.slow
@pytest.mark.flaky(reruns=2, reruns_delay=5)
def test_download_file(page: Page, browser_name: str):
    """Verify clicking a download link actually saves the expected file to disk."""
    logger.info("Given the file download demo page\n\tWhen I click the 'some-file.txt' download link"
                "\n\tThen the file is saved to disk with content\n")

    # Launch the browser and navigate to the file download demo page
    page.goto(THE_INTERNET_DOWNLOAD_URL)
    page.wait_for_load_state("load")

    # Namespaced by browser + xdist worker: with parallel execution, several of these can
    # save to disk at the same time and would otherwise overwrite each other's file mid-write.
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    downloaded_file_path = TEST_DATA_DIR / f"some-file_{browser_name}_{worker_id}.txt"

    # the-internet.herokuapp.com runs on a free Heroku dyno that can be slow
    # to "wake up" after being idle - give the link extra time to become
    # interactive before clicking, instead of relying on the default timeout.
    # The @pytest.mark.flaky rerun above is a second layer for the rarer case
    # where the whole cold-start takes longer than even this budget.
    download_link = page.get_by_role("link", name="some-file.txt", exact=True)
    expect(download_link).to_be_visible(timeout=45000)

    # Click the "some-file.txt" download link and wait for the download to complete
    with page.expect_download() as download_info:
        download_link.click()

    # Get the downloaded file
    download = download_info.value
    assert download.suggested_filename == "some-file.txt"
    download.save_as(downloaded_file_path)

    # Verify the file was actually saved to disk
    assert downloaded_file_path.exists()
    assert downloaded_file_path.stat().st_size > 0
