import logging
import time

import pytest
from config import API_MAX_RESPONSE_TIME_MS, REQRES_API_BASE_URL

logger = logging.getLogger(__name__)


@pytest.fixture
def api_request_context(playwright):
    """Reqres.in HTTP client shared by the GET/POST tests below."""
    request = playwright.request.new_context(extra_http_headers={
        "Accept": "application/json",
        "Authorization": "Bearer ",
        "x-api-key": "reqres_ffe9d830c25a45a09229981fc71ae2e7",
    })
    yield request
    request.dispose()


@pytest.mark.api
@pytest.mark.smoke
def test_get_users_returns_expected_records(api_request_context):
    """Verify a GET request to the users endpoint returns 200, expected records, within the response-time budget."""
    logger.info("Given the reqres.in fake REST API\n\tWhen I request page 2 of users"
                "\n\tThen I receive the expected user records within the response-time budget\n")

    # Send a GET request to the given URL, timing it like a simple non-functional check
    start_time = time.time()
    response = api_request_context.get(url=f"{REQRES_API_BASE_URL}/users?page=2")
    response_time_ms = (time.time() - start_time) * 1000
    print(f"\nResponse time: {response_time_ms:.0f}ms")

    # Verify response status
    assert response.status == 200

    # Verify the response came back within budget (see config.py for the verified baseline)
    assert response_time_ms < API_MAX_RESPONSE_TIME_MS, \
        f"Response took {response_time_ms:.0f}ms, expected under {API_MAX_RESPONSE_TIME_MS}ms"

    # Print the raw response as a text
    print(f"\nRaw response: {response.text()}")

    # Print the response as bytes
    print(f"\nResponse in bytes: {response.body()}")

    # Print the converted response body to Python dict
    print(f"\nConverted response body to Python dict: {response.json()}")

    # Convert response body to Python dict
    json_data = response.json()

    # Verify some response data
    assert json_data["data"][3]["first_name"] == "Byron"
    assert json_data["data"][4]["last_name"] == "Edwards"


@pytest.mark.api
@pytest.mark.smoke
def test_create_user_returns_201(api_request_context):
    """Verify a POST request to the users endpoint creates a resource, returns 201, within the response-time budget."""
    logger.info("Given the reqres.in fake REST API\n\tWhen I POST a new user"
                "\n\tThen the API responds with 201 Created within the response-time budget\n")

    # Send a POST request to the given URL, timing it like a simple non-functional check
    start_time = time.time()
    response = api_request_context.post(url=f"{REQRES_API_BASE_URL}/users",
                                        data={"name": "Alice", "job": "Engineer"})
    response_time_ms = (time.time() - start_time) * 1000
    print(f"\nResponse time: {response_time_ms:.0f}ms")

    # Verify response status
    assert response.status == 201

    # Verify the response came back within budget (see config.py for the verified baseline)
    assert response_time_ms < API_MAX_RESPONSE_TIME_MS, \
        f"Response took {response_time_ms:.0f}ms, expected under {API_MAX_RESPONSE_TIME_MS}ms"

    # Print the raw response as a text
    print(f"\nRaw response: {response.text()}")

    # Print the response as bytes
    print(f"\nResponse in bytes: {response.body()}")

    # Print the converted response body to Python dict
    print(f"\nConverted response body to Python dict: {response.json()}")
