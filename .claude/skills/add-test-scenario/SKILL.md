---
name: add-test-scenario
description: Add a new Playwright test to this project following its established conventions (config-driven URLs, POM, docstrings, Given/When/Then logging, verified assertions). Use when asked to add, write, or scaffold a new test case in playwright_ui_automation.
---

# Add a test scenario

This project has a specific, deliberate set of conventions (see `CLAUDE.md` for the full
review checklist). When adding a new test, follow this recipe instead of writing something
ad hoc.

## 1. Decide where things go

- **Target URL**: add a named constant to `tests/config.py` (grouped under the relevant
  site's comment block). Never hardcode a bare URL string inside a test file.
- **Repeated interactions** (locators reused across more than one test, e.g. a login form,
  an admin page with several actions): add or extend a Page Object in `tests/pages/`,
  inheriting from `BasePage`. One-off, single-use interactions can stay inline in the test.
- **New Page Object**: give the class a one-line docstring stating which page/site it
  represents (see the existing classes in `tests/pages/` for the exact tone).
- **Test file**: grouped by the feature/site under test, `tests/test_<topic>.py` (e.g. all
  login scenarios in `test_login.py`, all Job Titles scenarios in `test_job_titles.py`) -
  add a new test function to the matching file rather than creating a near-duplicate one, but
  don't pile in scenarios against an unrelated feature/site just because a file happens to
  exist.

## 2. Verify before you assert - this is the most important step

Before writing any assertion about what a page/API is supposed to show or return, **check
it for real** first. Do not guess or assume from memory:

- Write a tiny throwaway script using `sync_playwright()` (or `requests`/`curl` for an API)
  against the real target, and actually look at the output.
- This applies to error messages, response shapes, element text, status codes, timing
  behavior - anything you're about to bake into an assertion or a comment.
- This project has at least one real, historical bug that happened specifically because
  this step was skipped (see `tests/pages/demowebsite_login_page.py`'s `check_message`
  comment, and the module-level comment near the top of `tests/test_login.py` for the full
  story). Don't repeat it.

## 3. Write the test

- Function name: describe what it verifies (business behavior), not the technique used -
  `test_login_shows_error_for_invalid_password`, not `test_login_2`.
- Docstring: every test function uses this exact three-part structure, stating only what the
  test currently checks - never a change-history narrative ("replaces the previous
  version...", "used to do X instead of Y"). That belongs in the commit message, not in a
  docstring every future reader has to read past. The same goes for any README/documentation
  update that comes with the test: describe the current behavior, not a narrated history of
  what it used to be.
  ```python
  def test_login_shows_error_for_invalid_password(login_page):
      """
      Test verifies an error message is shown for a login attempt with a valid username but
      wrong password.

      Test Steps:
      1. Navigate to the login page.
      2. Enter a valid username with an incorrect password.
      3. Click the Login button.

      Expected results:
      The page displays the "Your password is invalid!" error message, and the user is not
      logged in.
      """
  ```
  "Test verifies" states the business behavior, not the technique. "Test Steps" lists the
  concrete actions taken, in order - matching what the test body actually does, not an
  idealized version of it. "Expected results" states what should be observably true
  afterward - the same thing the test's assertions check, in plain language. Keep each line
  within the project's 120-char limit (ruff `E501` applies inside docstrings too).
- Add `logger = logging.getLogger(__name__)` at module level if not already present, and a
  single `logger.info(...)` call at the top of the test body narrating it as Given/When/Then,
  e.g.:
  ```python
  logger.info("Given the login page\n\tWhen I log in with an invalid password"
              "\n\tThen an error message is shown\n")
  ```
- Prefer semantic locators (`get_by_role`, `get_by_label`, `get_by_placeholder`,
  `get_by_text`) over raw CSS/XPath, unless the test is specifically demonstrating a
  locator strategy (see `test_find_locators_css_xpath.py`).
- Prefer `expect(locator).to_...()` over a bare `assert` on a locator - better failure
  messages and built-in auto-waiting.
- No `time.sleep()` / arbitrary `wait_for_timeout()` - wait on a real condition.
- If the test creates data on a shared/public demo instance, make the data uniquely named
  (e.g. embed a timestamp) and clean it up at the end of the test (see
  `test_job_titles.py::test_job_title_create_and_delete`). If the shared site's own state is
  too unreliable to assert against at all, consider mocking the network response instead (see
  the same file's mocked-API tests).
- Add the right marker if it fits: `@pytest.mark.smoke` (fast, high-value),
  `@pytest.mark.api` (no browser involved), `@pytest.mark.slow` (heavier/multi-step).
- **Cover the negative/error path too, not just the happy path** - a feature isn't verified
  just because valid input works. Add a case for invalid input, a rejected/unauthorized
  request, or an error response, alongside the success scenario (see `test_login.py`'s
  invalid-username/invalid-password tests next to its successful-login test, and
  `test_job_titles.py::test_job_titles_list_handles_api_error` next to the happy-path mocked
  response). If the real backend can't produce the negative case on demand, mock it instead
  of skipping it (same file, same pattern).

## 4. Verify it actually works

1. `ruff check .` from the project root - fix anything it flags.
2. Run just the new test: `pytest tests/test_<topic>.py -v`.
3. Run the full suite once: `pytest tests` - confirm no regressions.
4. If the new test targets a third-party demo site, run it at least twice a few seconds
   apart before trusting a single green result - some of the demo sites used in this project
   are known to be occasionally slow or flaky (see `triage-test-failure` skill).
