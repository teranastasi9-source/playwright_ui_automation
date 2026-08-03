# Instructions for Claude Code — playwright_ui_automation

This file is read automatically by [Claude Code](https://claude.com/claude-code) at the
start of every session in this repo. It encodes the quality bar I (the repo owner, an
Automation QA engineer) hold AI-assisted changes to here — the point is to keep review
consistent regardless of who/what wrote the code, not to hand off judgment to the AI.

## Code review process

Whenever asked to review code in this project (in chat, or via `/code-review`), always:

1. **Run ruff first**: `cd playwright_ui_automation && ruff check .` (add `--fix` only if asked to
   auto-fix, otherwise just report findings). Report every finding, don't silently skip any.
2. **Check the code against the Playwright best-practices checklist below.** Flag violations
   as review findings, don't just fix them silently — explain what's wrong and why.
3. **Scan for stale `# todo` / `# fixme` comments.** For each one, either resolve it
   (implement the cheap ones), or flag it explicitly as still-open, or flag it as obsolete
   and safe to remove if it no longer applies (e.g. describes a feature/state that isn't
   there anymore). Don't just leave them silently unreviewed — this project has had TODOs
   linger for a long time with nobody ever revisiting whether they still made sense.
4. **Don't trust a comment or docstring's claim about external/live behavior at face value.**
   If a comment describes what a real site/API returns or does, and that's easy to check,
   verify it against the real target before relying on it or extending it — comments rot
   quietly, and a wrong one is worse than none (this project had a real bug where an
   assertion matched unrelated page text instead of the real error message, undetected
   until someone finally re-checked the live site's actual behavior).
5. **Watch for duplicated hardcoded values that should be a single shared constant**
   (e.g. a URL or test credential repeated inline in two files instead of imported from
   `tests/config.py`) — flag it and centralize it.
6. **Watch for orphaned artifacts/files that reference something no longer in the codebase**
   (e.g. a `test-results/` subfolder named after a test file that was deleted or renamed).

## Playwright best-practices checklist

### Isolation
- Each test must be independent and get its own fresh context. If using the built-in `page`
  fixture, Playwright already creates a new `BrowserContext` per test — don't undermine that
  by manually reusing a browser/context across tests.
- Avoid shared state between tests (e.g. module-level/global variables holding test data that
  get mutated during test execution).

### Test data
- Generate unique test data rather than hardcoding it (e.g. embed a timestamp/uuid in names
  that must not collide, like `test_job_titles.py::test_job_title_create_and_delete` does).
- Clean up after test execution (e.g. via a fixture's `yield` + teardown, or an explicit
  delete step at the end of the test) — especially important against shared/public demo
  instances.

### Locators and selectors
- Prefer semantic locators — `get_by_role`/`get_by_label`/`get_by_placeholder`/`get_by_text`
  — over raw CSS/XPath, for resilience against markup changes.
- Avoid `.nth()`/positional indexing — it's brittle; prefer a locator that uniquely and
  semantically identifies the element.
- Define locators in one place (a Page Object) rather than inline in every test.
- Prefer `fill()` over `type()` (faster, sets the value directly) — use `type()` only when
  the test specifically needs to exercise per-keystroke behavior (autocomplete, live
  validation, etc.).
- Prefer `expect(locator).to_...()` over a bare `assert` — better failure messages and
  built-in auto-waiting/retrying.
- Prefer `locator.click()` (from a Page Object / named locator) over `page.click("css=...")`.
- Use `expect(locator).to_have_value(...)` after filling data to confirm it actually took.
- For critical business flows, verify state **before** the action (e.g. button is
  disabled/enabled as expected) as well as **after** the action (UI actually changed as
  expected) — don't only check the end state.
- Always rely on Playwright's built-in timeouts/auto-waiting rather than guessing; set an
  explicit timeout only when the default (30s for most actions) genuinely isn't appropriate
  for that step, so failures surface promptly rather than hanging.
- After logging in, consider a `reload()` to verify session persistence where that's part of
  what's being tested.
- Never assert against the literal value of a password field.
- Use fixtures for setup instead of copy-pasting initialization code into every test.

### Stability and CI
- Headless for CI, headed (`--headed`) for local debugging.
- Rely on Playwright's `trace: 'retain-on-failure'` (or equivalent) for failure diagnostics
  rather than reinventing screenshot-on-failure by hand.
- Avoid hardcoded delays like `time.sleep()` / arbitrary `wait_for_timeout()` — wait on a
  condition instead.
- Reruns (`@pytest.mark.flaky(reruns=N, reruns_delay=M)`) are opt-in per test with a specific,
  documented external cause — never a blanket `--reruns` over the whole suite, and never a way
  to avoid diagnosing a real regression. See "Flaky test policy" in `README.md`.

### Readability and reporting
- Name tests after what they verify (business behavior), not how they do it technically.
- Group related tests logically (by module/file, or classes where that fits the domain).

## Running the suite

See `README.md` for setup/run instructions, markers (`smoke`/`api`/`slow`), and the linting
command.
