import logging
import time

import pytest
from config import API_MAX_RESPONSE_TIME_MS

logger = logging.getLogger(__name__)


@pytest.fixture
def api_request_context(playwright):
    """HTTP client for the QA Playground's local users API (see conftest.py's qa_playground_url fixture)."""
    request = playwright.request.new_context(extra_http_headers={"Accept": "application/json"})
    yield request
    request.dispose()


@pytest.mark.api
@pytest.mark.smoke
def test_get_users_returns_seed_records(api_request_context, qa_playground_url: str):
    """
    Test verifies GET /api/users returns 200 with the expected seed records, within the
    response-time budget.

    Test Steps:
    1. Send a GET request to /api/users.
    2. Measure the response time.

    Expected results:
    The response status is 200, the response time is under the configured budget, and the
    seed records are present (Ada at the start of the list, Johnson at the end).
    """
    logger.info("Given the QA Playground's local users API\n\tWhen I request the users list"
                "\n\tThen I receive the expected seed records within the response-time budget\n")

    # Send a GET request to the given URL, timing it like a simple non-functional check
    start_time = time.time()
    response = api_request_context.get(url=f"{qa_playground_url}/api/users")
    response_time_ms = (time.time() - start_time) * 1000
    print(f"\nResponse time: {response_time_ms:.0f}ms")

    # Verify response status
    assert response.status == 200

    # Verify the response came back within budget (see config.py for the verified baseline)
    assert response_time_ms < API_MAX_RESPONSE_TIME_MS, \
        f"Response took {response_time_ms:.0f}ms, expected under {API_MAX_RESPONSE_TIME_MS}ms"

    # Verify the seed records are present, at both ends of the list
    users = response.json()["data"]
    assert users[0]["first_name"] == "Ada"
    assert users[4]["last_name"] == "Johnson"


@pytest.mark.api
@pytest.mark.smoke
def test_create_user_returns_201_with_generated_id(api_request_context, qa_playground_url: str):
    """
    Test verifies POST /api/users creates a resource with a generated id and returns 201,
    within the response-time budget.

    Test Steps:
    1. Send a POST request to /api/users with a name and job.
    2. Measure the response time.

    Expected results:
    The response status is 201, the response time is under the configured budget, and the
    created resource echoes the posted name/job with a generated id and createdAt timestamp.
    """
    logger.info("Given the QA Playground's local users API\n\tWhen I POST a new user"
                "\n\tThen the API responds with 201 Created and a generated id, within the response-time budget\n")

    # Send a POST request to the given URL, timing it like a simple non-functional check
    start_time = time.time()
    response = api_request_context.post(url=f"{qa_playground_url}/api/users",
                                        data={"name": "Alice Example", "job": "Engineer"})
    response_time_ms = (time.time() - start_time) * 1000
    print(f"\nResponse time: {response_time_ms:.0f}ms")

    # Verify response status
    assert response.status == 201

    # Verify the response came back within budget (see config.py for the verified baseline)
    assert response_time_ms < API_MAX_RESPONSE_TIME_MS, \
        f"Response took {response_time_ms:.0f}ms, expected under {API_MAX_RESPONSE_TIME_MS}ms"

    # Verify the created resource echoes the posted fields and has a generated id
    created_user = response.json()
    assert created_user["name"] == "Alice Example"
    assert created_user["job"] == "Engineer"
    assert created_user["id"] is not None
    assert created_user["createdAt"] is not None


@pytest.mark.api
def test_created_user_is_retrievable_afterward(api_request_context, qa_playground_url: str):
    """
    Test verifies a user created via POST is actually persisted, not just echoed back - a
    follow-up GET for that exact id returns the same data.

    Test Steps:
    1. Create a user via POST and capture the id the API generated for it.
    2. Send a fresh GET request for that exact id.

    Expected results:
    The GET response is 200, and its name/job match exactly what was posted, proving the
    resource was actually stored rather than just returned once in the POST response.
    """
    logger.info("Given a user created via POST\n\tWhen I GET that same user by id afterward"
                "\n\tThen the API returns the same data, proving it was actually persisted\n")

    # Create a user via POST and capture the id the API generated for it
    create_response = api_request_context.post(url=f"{qa_playground_url}/api/users",
                                                data={"name": "Bob Persisted", "job": "Tester"})
    assert create_response.status == 201
    created_user_id = create_response.json()["id"]

    # Fetch that exact user back by id - a fresh request, not the same response object
    get_response = api_request_context.get(url=f"{qa_playground_url}/api/users/{created_user_id}")
    assert get_response.status == 200
    fetched_user = get_response.json()["data"]
    assert fetched_user["name"] == "Bob Persisted"
    assert fetched_user["job"] == "Tester"


@pytest.mark.api
def test_get_nonexistent_user_returns_404(api_request_context, qa_playground_url: str):
    """
    Test verifies requesting a user id that doesn't exist returns 404, not a crash or a
    misleading 200.

    Test Steps:
    1. Send a GET request for a user id that was never created.

    Expected results:
    The response status is 404.
    """
    logger.info("Given a user id that doesn't exist\n\tWhen I GET that user"
                "\n\tThen the API responds with 404, not a crash or a misleading empty 200\n")

    response = api_request_context.get(url=f"{qa_playground_url}/api/users/999999")
    assert response.status == 404
