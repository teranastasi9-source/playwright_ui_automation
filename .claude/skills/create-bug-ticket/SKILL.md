---
name: create-bug-ticket
description: File a GitHub Issue for a test failure in this project that has been triaged and confirmed as a real bug (not an external-site flake). Use after a test fails and the cause is understood, when it's worth tracking as a ticket.
---

# Create a bug ticket

GitHub Issues on this same repo is the ticket tracker here - free, and already where the code
and CI live, so no separate tool/account is needed.

## 1. Triage first - a ticket is not the default outcome of a red test

Run the `triage-test-failure` skill's process before this one. Only continue here if it
concludes "confirmed real bug":

- A known external flake (dead site, Heroku cold-start, Google bot-check, another visitor's
  edit to shared OrangeHRM demo data) does **not** get a ticket - those are handled by the
  flaky test policy, self-contained data, or mocking (see README.md), not by filing an issue
  every time a public demo site hiccups.
- If triage is inconclusive (still failing but the cause isn't clear yet), that's a reason to
  keep investigating, not to file a vague ticket now and figure it out later.

## 2. Draft the issue - never file blind

Compose, then show the full draft in chat before doing anything else:

- **Title**: `<test_file>::<test_name> - <one-line symptom>`, e.g.
  `test_login.py::test_login_invalid_password - wrong error message asserted`
- **Body**, in this order:
  1. **What failed** - the test's own one-line "Verify ..." docstring.
  2. **Reproduce** - the exact command: `pytest tests/test_x.py::test_y -v --tb=long`.
  3. **Expected vs. actual** - the real values from the assertion failure, not a paraphrase.
  4. **Environment** - Python/Playwright/pytest versions (from the relevant
     `reports/report_<browser>.html`'s Environment table).
  5. **Evidence** - the relevant traceback lines, and a note that a failure screenshot is
     attached to that report for this test (the `pytest_runtest_makereport` hook in
     `conftest.py` attaches one automatically).

## 3. File it - only after I've confirmed the draft

- Check first that this isn't already filed: `gh issue list --search "<test_name>" --state open`
- File with: `gh issue create --title "<title>" --body "<body>" --label bug`
  (if the `bug` label doesn't exist yet: `gh label create bug --color d73a4a`)
- If `gh` isn't installed or authenticated on this machine, don't install/authenticate it
  unattended - instead build a prefilled "new issue" URL and hand it to me to open and submit
  myself:
  `https://github.com/<owner>/<repo>/issues/new?title=<url-encoded-title>&body=<url-encoded-body>`

## 4. Never

- File without independently reproducing the failure first - step 1's triage *is* that
  reproduction step, don't skip straight here from a single red run.
- File without showing the draft in chat first - filing a public issue is a visible, external
  action; I want to see the exact title/wording before it's posted, every time, not just the
  first time this skill is used.
- File a duplicate of an already-open issue for the same test/cause.