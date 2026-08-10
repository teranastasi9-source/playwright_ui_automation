# Playwright UI Test Automation

[![Tests](https://github.com/teranastasi9-source/playwright_ui_automation/actions/workflows/tests.yml/badge.svg)](https://github.com/teranastasi9-source/playwright_ui_automation/actions/workflows/tests.yml)
![Tests](https://img.shields.io/badge/tests-40-brightgreen)
[![codecov](https://codecov.io/gh/teranastasi9-source/playwright_ui_automation/graph/badge.svg)](https://codecov.io/gh/teranastasi9-source/playwright_ui_automation)

Purpose: Python-based UI test automation framework built with [Playwright](https://playwright.dev/python/) and [pytest](https://docs.pytest.org/). Portfolio demonstration of UI automation, Page Object Model, and pytest best practices.

![CRUD test in action: creating, verifying, and deleting a Job Title on OrangeHRM](docs/job_titles_crud_demo.gif)
<sub>`test_job_title_create_and_delete` running headless, recorded at 10fps - creates a
uniquely-named Job Title, verifies it renders correctly, then deletes it again.</sub>

## Project Overview

| Aspect | Details |
|------|--------------------------------------------|
|**Tool**| Pytest + Playwright (`pytest-playwright`) |
|**Pattern**| Page Object Model, pytest fixtures, config-driven test data |
|**Test Types**| UI flows, API requests, network mocking, session reuse, hybrid API+UI, CRUD |
|**Auth**| Session reuse via `storage_state` (self-hosted OrangeHRM) |
|**Reports**| HTML via `pytest-html`, live logging via `log_cli` |

## This project demonstrates:
  - Page Object Model (`tests/pages/`, with a shared `BasePage`)
  - pytest fixtures for dependency injection (`login_page`, `orangehrm_admin_page`)
  - Data-driven tests via `@pytest.mark.parametrize`, reading cases from JSON
  - API testing with Playwright's `request` fixture
  - Network mocking with `page.route()` - a deterministic happy-path and an API-error scenario
  - Session reuse via `storage_state` - login once per test session, inject the resulting
    cookies into a fresh, isolated `BrowserContext` per test
  - A hybrid API+UI test: create data via a direct API call, verify it renders in the UI
  - A self-contained CRUD scenario that creates, verifies and cleans up its own test data
    instead of asserting against shared/mutable third-party demo content
  - iframe handling via `frame_locator()`
  - A deliberate, opt-in retry policy (`pytest-rerunfailures`) for a test with a known,
    understood external timing flake - not a blanket retry over the whole suite. Not
    currently applied to any test (see "Flaky test policy" below for why), but exercised
    and kept ready as infrastructure, the same way `no_browsers_in_ci` is
  - Cross-browser CI (Chromium/Firefox/WebKit matrix) - actually run and verified, surfacing
    a real per-engine site difference instead of just claiming `--browser` support works
  - Parallel execution (`pytest-xdist`) - actually run cross-browser under `-n auto`, which
    surfaced and fixed a real file-naming race between concurrently-running tests
  - File upload/download, dialogs, multiple tabs, cookies, screenshots/video recording,
    dropdowns/checkboxes/radio buttons, and CSS/XPath locator strategies
  - A self-built local test fixture app (`test_data/qa_playground/`, see "QA Playground"
    below) for generic UI-pattern tests, instead of depending on a dozen unrelated
    third-party sites for them
  - A self-hosted dependency (`docker-compose.orangehrm.yml`, see "Self-hosted OrangeHRM"
    below) for the tests that need a real, complex application - scripted end-to-end via
    that application's own unattended CLI installer, instead of depending on a shared
    public demo instance
  - Multi-actor lifecycle tests (`test_employee_lifecycle.py`) - an Admin provisions an
    account, a *different* logged-in role acts on it, the result is verified independently
    (a fresh login, not the same just-saved form state), and the account is removed again -
    not just single-actor, single-screen checks
  - Accessibility testing (`test_accessibility.py`, see "Accessibility testing" below) - an
    axe-core scan that found and documents real WCAG violations in self-hosted OrangeHRM,
    rather than a scan that always trivially passes
  - Documentation and reproducibility practices

## Project structure

![Architecture: test files -> fixtures -> Page Objects -> targets, plus the CI pipeline](docs/architecture.png)

```
playwright_ui_automation/
  .github/workflows/tests.yml   - CI: lint + smoke on push/PR, full suite nightly/manual
  .claude/skills/                - project-scoped Claude Code skills (see below)
  Dockerfile                       - optional containerized test run (see "Run tests in Docker")
  .dockerignore                     - keeps .git/caches out of the Docker build context
  docker-compose.orangehrm.yml      - self-hosted OrangeHRM (see "Self-hosted OrangeHRM" below)
  orangehrm/                        - Dockerfile + entrypoint.sh for the above
  .pre-commit-config.yaml            - runs ruff automatically before each commit (see "Linting")
  pytest.ini                       - pytest config (HTML report, live logging, markers)
  report_style.css               - custom theme applied to the pytest-html report
  requirements.txt                 - runtime dependencies
  requirements-dev.txt              - + ruff and pre-commit, for linting
  pyproject.toml                     - ruff config
  docs/architecture.png            - diagram above (tests -> fixtures -> Page Objects -> targets, + CI)
  docs/job_titles_crud_demo.gif    - CRUD test recording embedded at the top of this README
  docs/report_screenshot.png       - report screenshot embedded below, for a no-clone preview
  docs/github_actions.png          - CI run screenshot, embedded in "Cross-browser testing" below
  test_data/                          - JSON/CSV fixtures, sample upload file, local iframe fixture
  test_data/login_fixtures/           - minimal mocked login/secure pages (see "Cross-browser testing")
  test_data/qa_playground/            - self-built local test fixture app (see "QA Playground" below)
  reports/                             - committed HTML report + log per browser, + screenshots/video from the last run
  tests/
    conftest.py                       - shared fixtures (login_page, orangehrm_admin_page,
                                         qa_playground_url), plus a hook that attaches a screenshot to
                                         the HTML report on failure
    config.py                       - named URL constants for the remaining external demo sites/APIs
    pages/
      base_page.py                  - shared navigation/interaction helpers
      demowebsite_login_page.py
      job_titles_page.py
      employee_page.py, contact_details_page.py, leave_page.py,
      system_users_page.py          - used by test_employee_lifecycle.py's multi-actor flows
    test_*.py                       - one scenario/topic per file (see table below)
```

## Test scenarios overview

| File | Verifies |
|------|----------|
| `test_login.py` | Valid login, invalid username/password, and data-driven credential combinations (expandtesting.com) |
| `test_job_titles.py` | CRUD against a real backend; UI renders mocked API data / survives a mocked API error; data created via a direct API call is visible in the UI (self-hosted OrangeHRM) |
| `test_session_reuse.py` | A reused session stays authenticated across real in-app navigation between multiple pages, without repeating the login flow (self-hosted OrangeHRM) |
| `test_employee_lifecycle.py` | Two full multi-actor lifecycles - Admin onboards an employee with their own login, that employee acts on their own credentials (updates contact details / applies for leave), the result is independently verified, and the Admin removes the account again (self-hosted OrangeHRM) |
| `test_accessibility.py` | An axe-core scan of the authenticated Dashboard - documents real, verified critical/serious violations via a strict `xfail` rather than ignoring them (self-hosted OrangeHRM) |
| `test_iframe.py` | Typing into an editable area inside an iframe |
| `test_api_requests.py` | GET/POST requests against a small stateful REST API, including a created resource being retrievable afterward and a 404 for a nonexistent one (QA Playground) |
| `test_ajax.py` | The rendered subcategory list matches each category selected, and clears on reset (QA Playground) |
| `test_cookies.py` | A "Remember me" cookie persists the user across a reload, and clearing cookies forgets them again (QA Playground) |
| `test_find_locators_css_xpath.py` | CSS id selector (QA Playground) and CSS attribute/XPath locator strategies (self-hosted OrangeHRM) |
| `test_get_all_text_and_links_from_page.py` | Searching highlights only the matching statements, and updates correctly as the search term changes; collecting the page's content links with their exact destination and label (QA Playground) |
| `test_mouse_actions.py` | Hovering opens a dropdown, selecting an entry updates the page, and double-click changes the element's own color (QA Playground) |
| `test_new_tab_handling.py` | A link opened in a new tab shows real content, and closing it leaves the original tab's unsaved input untouched (QA Playground) |
| `test_select_alertbox.py` | Plain alert handling; confirm actually deletes only when accepted; prompt shows a personalized greeting only when answered (QA Playground) |
| `test_select_dropdown_radio_checkbox.py` | Filling out and submitting a registration form (dropdown, radio, checkboxes) shows a summary matching exactly what was selected (QA Playground) |
| `test_upload_and_download_files.py` | Uploading a file; downloading the default sample; a round trip - the file downloaded back after uploading has exactly the uploaded content (QA Playground) |
| `test_video_and_screenshot.py` | Screenshot and video-recording artifacts are saved to disk (QA Playground) |
| `test_webtable.py` | Exact table content; searching filters to only matching rows, and clearing restores all rows (QA Playground) |

## Prerequisites
- Python 3.11+ installed
- Docker, for the self-hosted OrangeHRM instance `test_job_titles.py`, `test_session_reuse.py`,
  `test_employee_lifecycle.py`, and two of `test_find_locators_css_xpath.py`'s tests need (see
  "Self-hosted OrangeHRM" below) - not required for the rest of the suite

## Test execution

### Clone the repository
```bash
git clone https://github.com/teranastasi9-source/playwright_ui_automation.git
```

### Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### Start self-hosted OrangeHRM
Only needed for the tests listed above - the rest of the suite runs without it.
```bash
docker compose -f docker-compose.orangehrm.yml up -d --build
```
Takes ~15-20s to finish installing (see "Self-hosted OrangeHRM" below for why); the OrangeHRM
tests will fail with a connection error if run before it's ready.

### Run specific test
```bash
pytest tests/test_login.py::test_login_successful -v
```

### Run all tests
```bash
pytest tests
```

## Run tests in Docker

An alternative to the local setup above: the included `Dockerfile` is based on the official
`mcr.microsoft.com/playwright/python` image, which ships with all three browser engines
already installed, so there's no local Python/pip/`playwright install` setup needed at all.

```bash
docker build -t playwright-ui-automation .
docker run --rm -v "$(pwd)/reports:/app/reports" playwright-ui-automation
```

The `-v` mount writes the HTML/log report back out to `reports/` on the host, so it's still
inspectable after the container exits. Pass extra pytest arguments after the image name, e.g.
`docker run --rm -v "$(pwd)/reports:/app/reports" playwright-ui-automation pytest tests -m smoke`.

On Windows Git Bash specifically, prefix the command with `MSYS_NO_PATHCONV=1` (e.g.
`MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd)/reports:/app/reports" ...`) - without it, Git
Bash's automatic path translation silently mangles the `$(pwd)` mount so the container runs fine
but the report never actually reaches the host (verified: the command exits 0 with no error, but
the host file's timestamp doesn't change). PowerShell/cmd and macOS/Linux shells aren't affected.

This is a local/manual convenience, not part of CI - the GitHub Actions workflow already runs
on a consistent `ubuntu-latest` runner, so containerizing it wouldn't add anything there (and
notably wouldn't fix the network-flakiness issues described in "Flaky test policy" below,
since a container on the same runner still egresses through the same IP).

This is a separate container from self-hosted OrangeHRM's (`docker-compose.orangehrm.yml`,
below) - running the OrangeHRM-dependent tests from inside *this* container too (rather than
running pytest directly on the host, which reaches OrangeHRM via `localhost:8300` with no
extra steps) means joining the same Docker network and pointing `ORANGEHRM_BASE_URL` at the
service name instead of `localhost`:
```bash
docker compose -f docker-compose.orangehrm.yml up -d --build
docker run --rm --network playwright_ui_automation_default \
  -e ORANGEHRM_BASE_URL=http://orangehrm \
  -v "$(pwd)/reports:/app/reports" playwright-ui-automation
```

## Useful debugging flags

These come from `pytest-playwright` itself, not anything custom in this project - handy when
a test fails and you want to see what actually happened:

```bash
pytest tests                       # headless by default
pytest tests --headed              # watch the browser locally instead
pytest tests --browser=firefox     # run against a specific engine (see "Cross-browser testing" below)
pytest tests --slowmo=500          # slow every action down by 500ms, easier to follow --headed
pytest tests --screenshot=on       # capture a screenshot after every test (not just failures)
pytest tests --video=on            # record a video of every test
pytest tests --tracing=on          # record a full Playwright trace (inspect with trace.playwright.dev)
```

`--screenshot`/`--video`/`--tracing` all default to `off` and save into `test-results/` at the
project root when enabled (a different folder from the committed `reports/test-results/` -
this one is gitignored, since it's meant for local debugging, not something to commit).
`--video`/`--tracing` also accept `retain-on-failure`, and `--screenshot` accepts
`only-on-failure`, to only keep the artifact for tests that actually failed.

## Markers

Six markers are registered in `pytest.ini`. Three of them let you run a meaningful subset
instead of the whole suite:

```bash
pytest tests -m smoke        # fast, high-value checks - good pre-merge/PR gate
pytest tests -m api          # API-only tests, no browser involved
pytest tests -m "not slow"   # skip the heavier multi-step/video tests
```

The other three aren't for browsing subsets - each drives its own behavior instead:
- `flaky` - opt-in reruns for a test with a known external timing flake. Not currently
  applied to any test; see "Flaky test policy" below for why.
- `no_browsers` - skips a test on specific browser engines with a known, understood
  per-engine limitation, on CI and locally alike; see "Cross-browser testing" below.
- `no_browsers_in_ci` - same idea, but only skips when the `CI` env var is `"true"` - for a
  site that works fine on those browsers locally, just not from GitHub Actions' datacenter
  IPs. Not currently applied to any test (the site that originally needed it was replaced by
  the local QA Playground, see below) - kept registered as ready-to-use infrastructure, since
  the underlying problem (a site behaving differently from CI's IP ranges) can resurface with
  any future external target.

## Flaky test policy

[pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures) is installed. Locally
and in the `smoke` CI job (the fast, strict pre-merge gate), reruns are **opt-in per test only**
- a global retry there would just as easily hide a real regression as a real flake. A test only
gets `@pytest.mark.flaky(reruns=N, reruns_delay=M)` once it has a *specific, understood*
external cause for occasional failure, documented in a comment next to the marker.

Not currently applied to any test. It used to be: `test_job_titles_list_renders_mocked_api_response`
and `test_job_titles_list_handles_api_error` (`test_job_titles.py`) both mocked the Job Titles
*API response*, but still navigated to the real, shared OrangeHRM demo site to load the page
itself, so they were exposed to that site's own occasional slowness regardless of the mock
(verified 2026-08-04: one of these timed out on `Page.goto` in CI, then passed immediately on
an unmodified re-run - an external-site blip, not a regression, see the `triage-test-failure`
skill). Once OrangeHRM became self-hosted (see "Self-hosted OrangeHRM" below), that root cause
was gone - verified directly with 10 consecutive reruns-disabled passes against the self-hosted
instance - so the markers were removed rather than left in place unnecessarily. The mechanism
stays installed and ready for the next test that has a real, specific, understood cause to use it.

Not every external-flakiness pattern in this suite gets this treatment: the one remaining
external site's known issue (`practice.expandtesting.com`'s Firefox/WebKit fingerprinting -
see "Third-party demo site still used" below and "Cross-browser testing" above) isn't a
timing issue a retry would fix, so it's handled at the root via mocking instead.

The `full-suite` CI job (nightly/manual only) is the one exception to "no blanket retry": it
runs with `--reruns 1 --reruns-delay 3` applied to the whole job (see `.github/workflows/tests.yml`).
That job's schedule trigger exists specifically to tolerate drift from the one third-party
demo site (`practice.expandtesting.com`) this suite still depends on, so a single job-wide
rerun for an ordinary, one-off site blip is consistent with what it's already for - verified 2026-08-04:
`test_mouse_actions` failed there once on Chromium, passed immediately on a plain local
re-run, and never reproduced again. A test's own `@pytest.mark.flaky(reruns=N)` still wins
over this job-wide default rather than stacking with it (pytest-rerunfailures' marker
precedence, not `append` mode).

## Linting

Code style is checked with [ruff](https://docs.astral.sh/ruff/) (config in `pyproject.toml`).

```bash
pip install -r requirements-dev.txt
ruff check .          # report issues
ruff check . --fix    # auto-fix what can be auto-fixed (import sorting, unused imports, ...)
```

A `.pre-commit-config.yaml` is included so the same check can run automatically before every
commit, instead of relying on remembering to run it (or waiting for CI to catch it):

```bash
pip install -r requirements-dev.txt
pre-commit install    # one-time, per clone - wires the git hook
```

From then on, `git commit` runs `ruff check` on the staged files first and blocks the commit if
it fails - the same rule CI enforces, just caught locally before it's pushed.

## Coverage

The two badges above answer different questions: `tests-40` is the count of test functions in
the suite (kept in sync by hand - see "Test scenarios overview"), while the Codecov badge
measures [`pytest-cov`](https://pytest-cov.readthedocs.io/) coverage of `tests/pages/` - the
Page Object Model - not of the application under test. OrangeHRM and
QA Playground aren't Python, so there's no app code for `coverage.py` to instrument; the
closest honest equivalent is this suite's own reusable framework code. A number here means
"this fraction of the POM's own methods are actually exercised by some test" - a POM method
nothing ever calls is dead code worth knowing about, which a flat test-count badge could
never show.

Collected on the `full-suite` job's chromium leg only (scope configured in
`[tool.coverage.run]`, `pyproject.toml`), uploaded to [Codecov](https://codecov.io) via
`codecov/codecov-action`.
Same freshness cadence as the full-suite report itself: it updates on the weekly schedule or
a manual `workflow_dispatch` run, not on every push - see "Third-party demo site still used"
below for why that job isn't run on every push in the first place.

To reproduce locally:

```bash
pytest tests --cov=tests/pages --cov-report=term-missing
```

One manual, one-time setup step this repo's CI can't do on its own: [enable the repo on
codecov.io](https://docs.codecov.com/docs/quick-start) and add the resulting token as this
repo's `CODECOV_TOKEN` secret (Settings > Secrets and variables > Actions). Until that's done,
the upload step no-ops (`fail_ci_if_error: false`) and the badge shows "unknown".

## Working with Claude Code

This project is read by [Claude Code](https://claude.com/claude-code) via `CLAUDE.md`
(a standing code-review checklist) and four custom project-scoped skills in
`.claude/skills/`:

- **`add-test-scenario`** - the exact recipe for adding a new test here: where URLs/POMs/
  test files go, the docstring + Given/When/Then logging convention, and - the most
  important step - verifying real site/API behavior before writing an assertion about it,
  instead of guessing.
- **`triage-test-failure`** - a decision process for telling a real regression apart from
  one of this project's known external-flakiness patterns (a demo site being down, slow to
  wake up, showing a bot-check page, or having its shared data edited by another visitor),
  with links to the actual past incidents each pattern is based on.
- **`create-bug-ticket`** - once a failure is triaged and confirmed real (not a flake), files
  it as a GitHub Issue on this repo: drafts the title/repro steps/expected-vs-actual for
  review first, then files via `gh issue create` - never auto-filed, and never for a failure
  that turned out to be one of the known external flakes above.
- **`write-commit-message`** - house style for commit messages: depth calibrated to the size of
  the change instead of a uniformly long template, with concrete before/after examples.

All four were written from real, repeated situations that came up while building this suite -
they're not aspirational, they're what "review it properly", "is this actually broken", "is
this worth a ticket", and "does this commit read like a person wrote it" looked like in
practice here.

**On authorship:** this project's code was written with Claude Code as an assistant,
including the QA Playground's HTML/CSS/JS pages (see "QA Playground" above) and the
self-hosted OrangeHRM setup - `Dockerfile`, `entrypoint.sh`, and `docker-compose.orangehrm.yml`
(see "Self-hosted OrangeHRM" above). The design decisions - what to test, which real problems
were worth solving (a shared demo instance's flakiness, nine-plus unrelated third-party
dependencies, thin single-actor tests), what quality bar to hold the code to (this file), and
which of Claude Code's proposals to accept, reject, or send back for another iteration - were
mine throughout.

## Expected output

After running, you should see:
  - Tests executed headless by default (add `--headed` to watch the browser locally)
  - An HTML report generated at `reports/report_<browser>.html` - e.g. `report_chromium.html`,
    or `report_firefox_webkit.html` if several `--browser` flags were passed in the same run.
    Named per browser so running a different `--browser` doesn't overwrite the previous run's
    report (see `conftest.py`'s `pytest_configure`); pass `--html=...` explicitly to override.
  - A matching text log at `reports/test_logs_<browser>.log`
  - Screenshots and a video recording saved under `reports/test-results/` (from `test_video_and_screenshot.py`)
  - Live log output in the console for each test's Given/When/Then narration (`log_cli` in `pytest.ini`)

**Live report:** all three of `full-suite`'s reports are redeployed to GitHub Pages after that
job runs - Mondays at 3:00 (schedule) or on-demand via `workflow_dispatch` in the Actions tab, not
on every push (`full-suite` itself only runs on schedule/manual dispatch, see
`.github/workflows/tests.yml`):
- [chromium](https://teranastasi9-source.github.io/playwright_ui_automation/) (also the site root)
- [firefox](https://teranastasi9-source.github.io/playwright_ui_automation/firefox.html)
- [webkit](https://teranastasi9-source.github.io/playwright_ui_automation/webkit.html)

Recent runs are also committed at `reports/report_chromium.html`, `reports/report_firefox.html`,
and `reports/report_webkit.html` so you can see results for all three engines - open any of them
directly in a browser.

![HTML test report](docs/report_screenshot.png)

## Parallel execution

[pytest-xdist](https://pytest-xdist.readthedocs.io/) is installed for distributing tests
across multiple worker processes:

```bash
pytest tests -n auto              # one worker per CPU core
pytest tests -n auto --browser=chromium --browser=firefox --browser=webkit   # all 3 browsers, in parallel
```

Verified locally: the full 40-test suite drops from ~150s sequential to ~40s with `-n auto`
(exact numbers depend on the machine's core count) - report generation, the
screenshot-on-failure hook, and the `flaky` reruns all still work correctly under `-n auto`,
since pytest-html and pytest-rerunfailures both support pytest-xdist.

Running multiple browsers in parallel surfaced one real correctness issue worth knowing
about: two tests (`test_screenshot`, `test_download_file`) wrote to a fixed filename on disk,
which is harmless sequentially (each run just overwrites the last) but becomes a genuine race
under parallel, multi-browser execution - two workers could write the same file at the same
time. Fixed by namespacing both filenames with the `browser_name` fixture and the
`PYTEST_XDIST_WORKER` env var pytest-xdist sets per worker.

Not wired into CI by default: the `smoke`/`full-suite` jobs here are small enough that the
extra worker-startup overhead isn't worth it, and spamming the one remaining third-party
demo site with many concurrent requests from CI's shared IP ranges is more likely to trip
anti-bot/rate protections (see "Cross-browser testing" below) than to meaningfully save
time. `-n auto` is documented here as a local, opt-in speed-up.

## Cross-browser testing

CI runs the full suite against **Chromium, Firefox, and WebKit** (a matrix job, scheduled
nightly and available on demand via `workflow_dispatch` - see `full-suite` in
`.github/workflows/tests.yml`) - all on `ubuntu-latest`, deliberately not a Windows/macOS
matrix too. Playwright drives the *browser engine*, not the host OS, and rendering behavior is
overwhelmingly a function of the engine, not what it happens to run on top of - a Chromium bug
is a Chromium bug on Ubuntu or Windows alike. For a suite that tests web pages loaded in a
browser, engine diversity is the dimension that actually matters; host-OS diversity would only
earn its cost for something genuinely OS-sensitive (a native desktop app, CLI path handling,
OS-level dialogs), which isn't the case here.

![GitHub Actions: Tests workflow run passing](docs/github_actions.png)

Locally:

```bash
pytest tests --browser=firefox
pytest tests --browser=webkit
pytest tests --browser=chromium --browser=firefox --browser=webkit   # all three in one run
```

Running this for real (not just documenting `--browser` and assuming it works) surfaced a
genuine, verified per-engine difference, not just a theoretical one:

- **`practice.expandtesting.com`'s login form** fingerprints Firefox/WebKit-driven requests to
  its `/authenticate` endpoint and rejects even genuinely valid credentials for those two
  engines specifically - Chromium is unaffected. Verified with a controlled repro isolating
  browser engine as the only variable. (A previous version of this note said it only
  "misreports a wrong username" - re-verified 2026-08-05 and found the real, current behavior
  is a hard rejection, not just a wrong message; site behavior on a public demo can drift, so
  don't trust an old verification note over a fresh check.) Since it's a real, one-sided site
  bug rather than a code bug or a timing issue, retrying it wouldn't help - but skipping
  outright would also mean zero coverage of `LoginPage`'s own code on two of the three engines.
  Instead, `test_login.py`'s `mock_login_outcome_for_flaky_engines()` intercepts the
  `POST /authenticate` request for Firefox/WebKit only and serves the same outcome Chromium
  legitimately gets (fixtures in `test_data/login_fixtures/`), so these tests verify our own
  login-flow code against a known-correct outcome instead of either skipping or asserting
  against the site's known-wrong behavior.

This project also has its own `no_browsers` marker (not pytest-playwright's built-in
`skip_browser`, which only accepts one browser name per decorator and doesn't combine when
stacked - `get_closest_marker` only ever returns the closest one) for cases where mocking
around a site issue isn't practical and skipping is the right call instead - see
`conftest.py`'s `pytest_runtest_setup` for how it's wired up.

A third pattern needed a different tool entirely, and is worth documenting even though the
site involved is no longer part of this suite. A previously-used third-party demo site
reliably timed out on `page.goto()`/`wait_for_selector()` for Firefox and WebKit specifically
when the full-suite matrix ran on GitHub Actions (confirmed across two separate CI runs,
14-15 failing tests each time, always this one site, never Chromium) - but the identical
tests, same browsers, passed 28/28 when run locally from a normal connection immediately
after. That pointed at the site (or infra in front of it) treating non-Chromium traffic from
datacenter IP ranges differently, not a real cross-browser incompatibility of the site's own
rendering and not a code bug - so unlike `no_browsers`, those tests stayed enabled locally,
just skipped on Firefox/WebKit *in CI specifically*, via `@pytest.mark.no_browsers_in_ci(...)`
(same mechanism as `no_browsers`, but the skip in `conftest.py` only fires when the `CI` env
var GitHub Actions sets is `"true"`). The tests that needed this were later rewritten to
target the self-built QA Playground instead (see below), which eliminates the problem at the
root rather than working around it - but the marker itself stays registered, since the
underlying "site behaves differently from CI's IPs" problem isn't specific to that one site.

Investigating this also turned up something unrelated but worth knowing: the shared public
OrangeHRM demo's login page text (e.g. "Forgot Your Password?") wasn't even *stable* - its
casing flipped between visits within the same session (verified directly, more than once),
likely inconsistent server instances/edge nodes behind that shared demo. An exact-match
locator there would pass today and break tomorrow for a reason that has nothing to do with
the test - one of several reasons OrangeHRM is now self-hosted instead (see "Self-hosted
OrangeHRM" below). `test_find_locators_css_xpath.py::test_css_locators_via_xpath` still
matches case-insensitively (XPath `translate()`) as a general defensive habit, even though a
single self-hosted instance has no reason to drift the way the shared demo did.

## QA Playground

Most of the UI-pattern tests (alerts/dialogs, tables, dropdowns/checkboxes/radio buttons,
hover menus, new-tab handling, cookies, an AJAX dropdown, file upload/download, CSS `id`
locators) don't actually need a real production application - they need a page with a
specific, known DOM structure to exercise a specific Playwright capability. Earlier versions
of this suite pointed each of those tests at a different, unrelated public demo site
(`automationtesting.in`, `techlistic.com`, `plus2net.com`, `the-internet.herokuapp.com`...),
which worked, but read like a checklist worked through site-by-site rather than a coherent
piece of engineering - and came with all the maintenance cost of nine-plus external
dependencies that can each independently go down, change their markup, or rate-limit CI.

`test_data/qa_playground/` replaces all of them with one small, self-built, connected app:
an `index.html` landing page with shared navigation, linking to one page per UI pattern
(`alerts.html`, `table.html`, `dropdowns.html`, `hover_menu.html`, `links_and_text.html`,
`new_tab.html`, `upload_download.html`, `login_form.html`, `ajax_dropdown.html`), sharing one
stylesheet. It's served over real HTTP (not `file://`, which some of the tests' fetch/cookie
behavior needs) by a session-scoped fixture in `conftest.py`, `qa_playground_url`: a
`ThreadingHTTPServer` bound to port `0` so the OS assigns a free port, started in a background
thread for the duration of the test session. Binding to port `0` rather than a fixed port
matters under `pytest-xdist` - each parallel worker process gets its own server instance and
would otherwise collide trying to bind the same fixed port.

The same server also backs a tiny, genuinely stateful REST API under `/api/users`
(`test_api_requests.py`) - a custom request handler layered on top of the static file
serving, backed by an in-memory store shared across requests for the session. A POSTed
user is actually persisted (a follow-up GET for that id returns it) and an unknown id
returns a real 404, not a canned response.

Rewriting these tests against the Playground only ever changed *where* they navigate
(`page.goto(f"{qa_playground_url}/alerts.html")` instead of a public URL) - every locator and
assertion is unchanged, since each Playground page was built to replicate the exact DOM
structure (element IDs, table content, link text) the existing tests already queried.

The Playground's HTML/CSS/JS pages themselves were generated with
[Claude Code](https://claude.com/claude-code) for this specific purpose (see "Working with
Claude Code" above) - static markup for a test fixture, not application code, is a
comfortable fit for AI assistance, especially since this project's focus is the test
automation around it, not front-end development itself.

## Self-hosted OrangeHRM

`test_job_titles.py`, `test_session_reuse.py`, `test_employee_lifecycle.py`, and two of
`test_find_locators_css_xpath.py`'s tests need a real, complex, multi-page application - CRUD,
session reuse, locator-strategy, and multi-actor lifecycle tests all get more value from
exercising a real app's markup than a page built for the test (unlike the QA Playground's
generic UI-pattern tests above). This suite used to point them at the shared public
`opensource-demo.orangehrmlive.com` instead, but that came with real, verified costs: other
visitors editing the shared Job Titles list, the demo's own occasional slowness triggering
reruns (see "Flaky test policy" above), and its login page text not even being stable
between visits (see "Cross-browser testing" above).

`test_employee_lifecycle.py` specifically exists to test *through a real user's eyes*, not
just an Admin's: an Admin onboards a new employee with their own login (OrangeHRM
auto-assigns the ESS role), that employee logs in on their own credentials and acts on
their own account (updates their own contact details, or applies for their own leave), the
result is verified independently (a fresh login and page load, not just the same
just-saved form state), and the Admin removes the account again - the same
create/verify/clean-up-after-yourself discipline `test_job_titles.py`'s CRUD test already
uses, applied to a multi-actor flow instead of a single-actor one.

`docker-compose.orangehrm.yml` + `orangehrm/` replace it with a dedicated, self-hosted
instance instead - two services, `orangehrm-db` (MariaDB) and `orangehrm` (the official
`orangehrm/orangehrm` image, wrapped with a custom entrypoint). OrangeHRM's web installer has
no documented way to skip it via environment variables, but the image also ships a Symfony
console command, `php installer/console install:on-new-database`, that takes the exact same
answers over stdin - `orangehrm/entrypoint.sh` drives that command with this project's
answers (organization name, admin credentials, etc.) on every fresh container start.

Deliberately no persisted volumes: every `docker compose up` reinstalls from scratch against
an empty database, rather than committing a database dump or relying on a volume that could
drift from the image over time. That costs ~15-20s per start (verified: consistently well
under a minute), in exchange for a guaranteed-clean instance every time, locally and in CI
alike - no seed data to keep in sync, no risk of a stale dump breaking against a newer image.

CI wires this into the `full-suite` job exactly as it's used locally (`docker compose -f
docker-compose.orangehrm.yml up -d --build`, then a step that polls the same healthcheck the
compose file already defines) - one definition of "how this instance gets set up," not a
second, CI-specific one. The `smoke` job doesn't need it at all: none of its tests touch
OrangeHRM (see the test scenarios table above).

## Accessibility testing

`test_accessibility.py` runs an [axe-core](https://github.com/dequelabs/axe-core) scan
against the authenticated OrangeHRM Dashboard via
[`axe-playwright-python`](https://github.com/pamelafox/axe-playwright-python), which bundles
axe-core itself - no CDN or network call needed to run the scan, consistent with this project
not depending on third parties it doesn't have to.

The scan found real, verified `critical`/`serious` violations in this self-hosted OrangeHRM
image: two icon-only buttons with no accessible name (`button-name`, critical), 8 elements
below the minimum color-contrast ratio, `<html>` missing a `lang` attribute, and a `<ul>`
containing a non-`<li>` child - all confirmed directly against the running instance, not
assumed from axe-core's documentation. These are defects in OrangeHRM's own markup, not in
this project's code, so the test can't "fix itself" by changing test code.

Rather than hard-code a threshold that quietly tolerates future regressions, or skip the test
and lose the signal entirely, it's marked `@pytest.mark.xfail(strict=True, ...)`: the suite
stays green today, but if OrangeHRM's own markup improves, `strict=True` turns that into an
unexpected-pass failure - a forced prompt to come back and remove the marker - rather than a
silent, permanent free pass.

## Third-party demo site still used

One test file still deliberately targets a real external site, because the site itself is
the point of the test, not just a container for some generic markup. Its URL is centralised
in `tests/config.py`. Because it's a real, publicly shared site outside this project's
control, occasional failures unrelated to this codebase can happen (e.g. the site going
down):

- **`practice.expandtesting.com`** (`test_login.py`) - a login form, kept external
  deliberately as this suite's one documented example of handling a real, verified, one-sided
  site bug (see "Cross-browser testing" above) rather than a site every test can be pointed
  away from.

## Troubleshooting

Issue: `ModuleNotFoundError: No module named 'playwright'`
  -> Run: `pip install -r requirements.txt` then `playwright install chromium`

Issue: A UI test fails against a third-party demo site
  -> See "Third-party demo site still used" above - some failures are outside this project's
     control. Re-run the test; if it persists, check whether the demo site itself is down.

Issue: `test_job_titles.py`/`test_session_reuse.py`/`test_find_locators_css_xpath.py` fail
with a connection error
  -> Self-hosted OrangeHRM isn't running (or isn't finished installing yet) - see "Self-hosted
     OrangeHRM" above. Run `docker compose -f docker-compose.orangehrm.yml up -d --build` and
     wait for `docker inspect --format='{{.State.Health.Status}}' <container>` to report
     `healthy` before running these tests.

## Known limitations

- A handful of tests intentionally use raw XPath/CSS locators rather than the Page Object
  Model, specifically because they exist to demonstrate locator strategies
  (`test_find_locators_css_xpath.py`).

## Contact
- Anastasiia Zatorska
- Email: teranastasi9@gmail.com
- LinkedIn: http://www.linkedin.com/in/anastasiia9-zatorska
