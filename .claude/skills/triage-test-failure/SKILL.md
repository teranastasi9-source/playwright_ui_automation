---
name: triage-test-failure
description: Diagnose whether a failing test in this project is a real bug or an external-dependency flake (a shared demo site being slow, down, or having had its data changed by another visitor). Use when a test fails and it's unclear whether the test/code or an external site is at fault.
---

# Triage a test failure

This project intentionally exercises several public, third-party demo sites (see
"Third-party demo sites used" in `README.md`). A failure here can mean a real regression,
or it can mean the outside world changed under the test. Don't assume either way - work
through this before changing any code.

## 1. Re-run it in isolation

```bash
pytest tests/test_<the_failing_file>.py::test_<the_failing_test> -v --tb=long
```

- **Now passes?** That's a strong signal it was transient (a slow response, a momentary
  network blip). Note it and move on - don't "fix" code that isn't actually broken. If it
  keeps happening to the same test, consider whether the test needs more headroom (see
  step 4).
- **Still fails, same error?** Continue to step 2.
- **Still fails, different error?** Treat as a new failure - restart this triage for the new
  error.

## 2. Read the actual error, don't skim it

- A `TimeoutError` waiting on a locator, or a network error (`net::ERR_...`,
  `ERR_NAME_NOT_RESOLVED`) almost always points at the external site, not this codebase.
- An `AssertionError` comparing an *expected* value against what came back is more likely a
  real bug in the test's assumptions, or a real regression - but confirm with step 3 before
  concluding either way.
- A `SyntaxError`/`ImportError`/`ModuleNotFoundError` is always this codebase's fault (or its
  environment) - go fix it, not the site.

## 3. Verify the external state directly, independent of pytest

Don't debug through the full pytest+fixture stack first. Write a minimal, standalone
`sync_playwright()` (or `curl`/`requests` for an API) script that hits the exact same
target the test hits, and look at the real, current result:

- Is the site reachable at all right now?
- Does it return the content/status/timing the test expects?
- If the test targets a shared public demo (OrangeHRM, automationtesting.in, etc.), has the
  data it depends on been changed by another visitor? (This project hit exactly this: a
  shared OrangeHRM job-titles list gets edited by other people using the same public demo.)

This project's own history has concrete examples of each category - worth recognizing the
pattern, not re-diagnosing from scratch every time:
- **Dead site**: `demo.imacros.net` stopped resolving entirely -> replaced with
  `the-internet.herokuapp.com` (see `tests/config.py`).
- **Cold-start slowness**: `the-internet.herokuapp.com` runs on a free Heroku dyno that can
  take longer than expected to respond after being idle -> handled with a longer explicit
  timeout on that one locator, not a blanket retry (see `test_upload_and_download_files.py`).
- **Bot detection**: Google can serve a CAPTCHA/"sorry" page for automated searches -> a
  previous version of `test_job_titles.py::test_job_title_create_and_delete` was a Playwright
  Codegen recording of a live Google search -> otomoto.pl flow; that was replaced with a
  self-contained test against a stable demo app instead of patched (see that test's own
  docstring for the full story).
- **Shared/mutable demo data**: other visitors edit the same public OrangeHRM instance ->
  handled by either creating uniquely-named data and cleaning it up
  (`test_job_titles.py::test_job_title_create_and_delete`), or mocking the network response
  entirely so the assertion never depends on live shared data (the same file's mocked-API
  tests).
- **Browser-specific site behavior**: running cross-browser for real (not just documenting
  `--browser` support) surfaced two genuine per-engine differences on third-party sites -
  `automationtesting.in`'s cookie-consent dialog only renders on Firefox/WebKit (fixed with
  `tests/helpers.py`'s `dismiss_cookie_consent_if_present()`), and `expandtesting.com`'s login
  form fingerprints Firefox/WebKit-driven requests and misreports a wrong error message for
  them specifically - confirmed with a controlled, single-variable repro, not fixable by a
  retry, so those four login tests are excluded on the non-Chromium legs of the CI matrix (see
  "Cross-browser testing" in `README.md`). If a test only fails under a specific
  `--browser` value, re-run the same scenario against a *different* browser as a fresh, fresh
  context, back-to-back, before assuming it's your code - isolate the browser engine as the
  single variable, the same way you'd isolate a flaky site.

## 4. Decide, then act - don't paper over a real bug

- **Confirmed external/environmental**: consider whether the test needs to be hardened
  (longer timeout with a comment explaining why, or switched to creating its own data /
  mocking the response) rather than just re-run until it's green.
- **Confirmed real bug**: fix the actual cause. Never "fix" a failing assertion by loosening
  it to match whatever the code currently does - only change an expected value after you've
  independently verified (step 3's method) that the new value is actually correct.
- Either way, re-run the full suite (`pytest tests`) afterward to confirm the fix didn't
  break anything else.
