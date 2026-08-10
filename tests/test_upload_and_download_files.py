import logging
import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def test_upload_file(page: Page, qa_playground_url: str):
    """
    Test verifies a local file can be selected via the file input and is registered by the
    browser.

    Test Steps:
    1. Navigate to the Upload/Download page.
    2. Select a local file via the file input.

    Expected results:
    The file input's own file list shows exactly the uploaded file's name.
    """
    logger.info("Given the Upload/Download page\n\tWhen I select a local file via the file input"
                "\n\tThen the browser registers the correct file name\n")

    # Launch the browser and navigate to the Upload/Download page
    page.goto(f"{qa_playground_url}/upload_download.html")
    page.wait_for_load_state("load")

    # Define path to the file that will be uploaded
    file_to_be_uploaded = TEST_DATA_DIR / "file_to_be_uploaded.txt"

    # Find "Browse..." button via XPath
    browse_button = page.locator('//input[@id="input-4"]')

    # Upload the file
    browse_button.set_input_files(str(file_to_be_uploaded))

    # Verify the browser actually registered the selected file
    uploaded_file_name = browse_button.evaluate("el => el.files.length ? el.files[0].name : null")
    assert uploaded_file_name == file_to_be_uploaded.name


@pytest.mark.slow
def test_download_file(page: Page, browser_name: str, qa_playground_url: str):
    """
    Test verifies clicking a download link actually saves the expected file to disk.

    Test Steps:
    1. Navigate to the Upload/Download page.
    2. Click the "some-file.txt" download link.
    3. Save the resulting download to a browser/worker-namespaced path.

    Expected results:
    The download's suggested filename is "some-file.txt", and the saved file exists on disk
    with non-zero size.
    """
    logger.info("Given the Upload/Download page\n\tWhen I click the 'some-file.txt' download link"
                "\n\tThen the file is saved to disk with content\n")

    # Launch the browser and navigate to the Upload/Download page
    page.goto(f"{qa_playground_url}/upload_download.html")
    page.wait_for_load_state("load")

    # Namespaced by browser + xdist worker: with parallel execution, several of these can
    # save to disk at the same time and would otherwise overwrite each other's file mid-write.
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    downloaded_file_path = TEST_DATA_DIR / f"some-file_{browser_name}_{worker_id}.txt"

    download_link = page.get_by_role("link", name="some-file.txt", exact=True)
    expect(download_link).to_be_visible()

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


def test_uploaded_file_can_be_downloaded_back_with_same_content(page: Page, browser_name: str, qa_playground_url: str):
    """
    Test verifies a file that's uploaded can be downloaded back afterward with exactly the
    same content - a genuine round trip, not two unrelated actions that happen to both work.

    Test Steps:
    1. Navigate to the Upload/Download page.
    2. Upload a local file via the file input.
    3. Click the download link, which now offers that same uploaded file.
    4. Save the resulting download to a browser/worker-namespaced path.

    Expected results:
    After uploading, the download link's name matches the uploaded file's name (not the
    default sample). The downloaded file's content is byte-identical to the original
    uploaded file's content.
    """
    logger.info("Given the Upload/Download page\n\tWhen I upload a file and then download it back"
                "\n\tThen the downloaded file has exactly the content that was uploaded\n")

    # Launch the browser and navigate to the Upload/Download page
    page.goto(f"{qa_playground_url}/upload_download.html")
    page.wait_for_load_state("load")

    file_to_upload = TEST_DATA_DIR / "file_to_be_uploaded.txt"
    original_content = file_to_upload.read_text(encoding="utf-8")

    # Upload the file
    browse_button = page.locator('//input[@id="input-4"]')
    browse_button.set_input_files(str(file_to_upload))

    # Verify the download link now offers the file that was just uploaded, not the default sample
    download_link = page.get_by_role("link", name=file_to_upload.name, exact=True)
    expect(download_link).to_be_visible()

    # Namespaced by browser + xdist worker, same reasoning as test_download_file above -
    # "some-file" prefix so it matches the existing test_data/some-file*.txt gitignore entry.
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    downloaded_file_path = TEST_DATA_DIR / f"some-file-roundtrip_{browser_name}_{worker_id}.txt"

    # Click the download link and wait for the download to complete
    with page.expect_download() as download_info:
        download_link.click()

    download = download_info.value
    assert download.suggested_filename == file_to_upload.name
    download.save_as(downloaded_file_path)

    # Verify the downloaded content is exactly what was uploaded - a genuine round trip,
    # not just two unrelated actions that happen to both work
    assert downloaded_file_path.read_text(encoding="utf-8") == original_content
