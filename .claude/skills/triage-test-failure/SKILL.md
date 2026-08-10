---
name: triage-test-failure
description: Diagnose whether a failing test in this project is a real bug or an external-dependency flake (the one remaining external demo site being slow or down). Use when a test fails and it's unclear whether the test/code or the external site is at fault.
---

# Triage a test failure

Most UI-pattern tests run against a self-built local fixture app (see "QA Playground" in
`README.md`), and the OrangeHRM-dependent tests run against a self-hosted instance (see
"Self-hosted OrangeHRM" in `README.md`) - neither can be affected by the outside world at
all. `test_login.py` still deliberately exercises a real, public, third-party site (see
"Third-party demo site still used" in `README.md`) - a failure there can mean a real
regression, or it can mean the outside world changed under the test. Don't assume either way
- work through this before changing any code.

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

- Is the site (or, for OrangeHRM, the local container) reachable at all right now? For
  OrangeHRM specifically, check `docker inspect --format='{{.State.Health.Status}}'
  playwright_ui_automation-orangehrm-1` before suspecting anything else - a connection error
  there almost always just means the compose stack isn't up yet (see "Self-hosted OrangeHRM"
  in `README.md`), not a real regression.
- Does it return the content/status/timing the test expects?

This project's own history has concrete examples of each category - worth recognizing the
pattern, not re-diagnosing from scratch every time:
- **Dead site**: `demo.imacros.net` stopped resolving entirely -> replaced with
  `the-internet.herokuapp.com`, which was itself later replaced by the self-built, always-up
  QA Playground once enough of these sites had proven individually unreliable (see "QA
  Playground" in `README.md`).
- **Bot detection**: a real search engine can serve a CAPTCHA/"sorry" page for automated
  traffic, not because of anything wrong in the test - a Codegen recording of a live search
  flow against one was replaced with a self-contained test against a stable demo app instead
  of patched, for exactly this reason.
- **Shared/mutable demo data**: this suite used to point at the shared public OrangeHRM demo,
  where other visitors edited the same data -> handled at the time by either creating
  uniquely-named data and cleaning it up (`test_job_titles.py::test_job_title_create_and_delete`),
  or mocking the network response entirely (the same file's mocked-API tests). OrangeHRM is
  now self-hosted (see "Self-hosted OrangeHRM" in `README.md`), which removes this risk at the
  root - nobody else can edit this instance's data - but both techniques stayed, since
  self-contained data and API mocking are good practice regardless of whether the risk is
  currently live.
- **Browser-specific site behavior**: running cross-browser for real (not just documenting
  `--browser` support) surfaced a genuine per-engine difference on a third-party site -
  `expandtesting.com`'s login form fingerprints Firefox/WebKit-driven requests to
  `/authenticate` and rejects even genuinely valid credentials for those two engines
  specifically - confirmed with a controlled, single-variable repro, not fixable by a retry.
  This one wasn't fixed by skipping: `test_login.py`'s `mock_login_outcome_for_flaky_engines()`
  intercepts that request for Firefox/WebKit only and serves the same outcome Chromium
  legitimately gets, so those tests still verify our own login-flow code on all three engines
  (see "Cross-browser testing" in `README.md`). If a test only fails under a specific
  `--browser` value, re-run the same scenario against a *different* browser as a fresh context,
  back-to-back, before assuming it's your code - isolate the browser engine as the single
  variable, the same way you'd isolate a flaky site.
- **CI-only, datacenter-IP-specific site behavior**: a failure that only happens on GitHub
  Actions, never locally, isn't necessarily "unreproducible" - it can mean the site treats
  requests differently based on IP range or engine+IP combination. A previously-used
  third-party demo site reliably timed out for Firefox/WebKit on two separate CI runs (14-15
  tests each time) while the identical tests passed 28/28 run locally immediately after -
  confirmed by literally doing both and comparing, not by guessing. That site was later
  replaced by the local QA Playground, removing the problem entirely, but the marker built for
  it (`@pytest.mark.no_browsers_in_ci(...)`, distinct from `no_browsers` since these tests are
  genuinely fine outside of CI) is still registered and ready if a future external target hits
  the same pattern.
- **Unstable site content, not a one-time drift**: don't assume a text/casing mismatch found
  once is now fixed forever - re-check the *same* element again later before hardcoding a new
  exact value. The shared public OrangeHRM demo's "Forgot Your Password?" text was verified as
  "Forgot your password?" (lowercase), then a "Forgot Your Password?" (capitalized) a few
  hours later in the same session, with the "username" label similarly flip-flopping - almost
  certainly inconsistent server instances/edge nodes behind that shared demo, not a one-off.
  An exact-string locator will pass today and silently break again tomorrow for a reason that
  has nothing to do with the test; match case-insensitively (XPath `translate()`, or
  `get_by_text(..., exact=False)`) instead of hardcoding whichever casing happened to be live
  when you checked. This is exactly the kind of instability self-hosting OrangeHRM (see
  "Self-hosted OrangeHRM" in `README.md`) was partly meant to eliminate at the root - but
  `test_find_locators_css_xpath.py::test_css_locators_via_xpath` still matches
  case-insensitively as a general defensive habit, even against the now-stable self-hosted
  instance.

## 4. Decide, then act - don't paper over a real bug

- **Confirmed external/environmental**: consider whether the test needs to be hardened
  (longer timeout with a comment explaining why, or switched to creating its own data /
  mocking the response) rather than just re-run until it's green. State the current reason
  for the change in that comment/docstring, not the diagnostic journey that led to it - see
  `add-test-scenario`'s docstring guidance for the same rule applied there.
- **Confirmed real bug**: fix the actual cause. Never "fix" a failing assertion by loosening
  it to match whatever the code currently does - only change an expected value after you've
  independently verified (step 3's method) that the new value is actually correct.
- Either way, re-run the full suite (`pytest tests`) afterward to confirm the fix didn't
  break anything else.
