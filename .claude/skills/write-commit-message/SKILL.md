---
name: write-commit-message
description: House style for git commit messages in this repo - use whenever creating a commit here, whether Claude or the repo owner is the one typing it. Calibrates message depth to the actual size of the change instead of a uniform, verbose template.
---

# Write a commit message

This is a portfolio repo a technical interviewer may actually read commit-by-commit. A commit
history where every single message is a uniformly long, formally-structured explanation reads
as automated, not as one engineer's judgment calls - regardless of whether that's literally
true. The fix isn't hiding that Claude Code is used (`CLAUDE.md` already says so openly) - it's
writing messages the way a person actually would: effort matched to the change, not a template
applied uniformly regardless of size.

## 1. Match depth to the actual change - most commits should be short

- **Trivial** (typo, one-line config value, wording fix, dependency bump): subject line only,
  no body. The diff already shows what changed - don't narrate it.
- **Small/routine** (a new test, a straightforward refactor, a doc section): subject line + at
  most one short sentence of body, only if the *why* genuinely isn't obvious from the subject
  and diff alone.
- **Genuinely non-obvious** (a real bug fix, a design tradeoff, something a reviewer would
  otherwise ask "wait, why?" about): a fuller body is warranted - but write it like a note to a
  colleague, not an incident report (see the before/after below).

Look back at the last 5 commits before writing a new one. If they're all roughly the same
length and shape, that's the smell this skill exists to fix - vary it.

## 2. Subject line

Imperative mood, no trailing period, ideally under ~65 characters. `Fix X` / `Add Y` / `Remove
Z`, not `Fixed`, `Added`, `This commit adds`.

## 3. Avoid these patterns even when the body is warranted

- Don't cite how/when something was verified inside the message itself (`Verified 2026-08-05
  via...`, `Reproduced by...`). Do the verification; don't write it up like a lab report. If it
  genuinely needs to be on record, that's what a PR description or an issue comment is for, not
  every commit.
- Don't use a recurring rigid template (`Problem: ... / Solution: ... / Verified: ...`) across
  commits - even a good template becomes a tell once it's identical every time.
- Don't restate the diff in prose (`Added X. Changed Y. Removed Z.`) - say why, not what.
- Don't hedge with filler transitions - `Note that...`, `It's worth mentioning...`, `This
  ensures that...`. State the reason plainly.
- Never add a `Co-Authored-By` trailer for Claude in this repo's commits.

## 4. Before / after

**Trivial change** - stale wording after an earlier schedule change:

> Bad: *"Fix stale 'Daily' wording in run-name after the weekly schedule change\n\nThe
> run-name field still referenced the old daily cadence even though the schedule was updated to
> weekly in a previous commit. This updates the text to accurately reflect the new weekly
> schedule, ensuring the GitHub Actions UI shows consistent information."*
>
> Good: `Fix stale 'Daily' wording in run-name after the weekly schedule change` - subject
> only. The diff is one word. Nothing above the line adds information.

**Genuinely non-obvious fix** - a real, non-trivial bug (kept short, not restructured into a report):

> Bad: *"Delete stale github-pages artifact before uploading, to survive re-runs\n\nRe-running
> this workflow (rather than triggering a fresh workflow_dispatch) leaves the previous
> attempt's already-uploaded github-pages artifact in place - upload-pages-artifact always uses
> that fixed name, so a second attempt collides with it and deploy-pages fails with 'Multiple
> artifacts named github-pages... Artifact count is 2' (verified 2026-08-05, reproduced by
> re-running a run whose pages job had already succeeded once). Deletes any leftover one via
> the API first, requiring actions: write. No-op on a normal first attempt."*
>
> Good: *"Delete stale github-pages artifact before uploading, to survive re-runs\n\nRe-running
> a workflow whose pages job already succeeded leaves a duplicate github-pages artifact behind,
> which breaks deploy-pages on the second attempt. Clean it up first."*

Same information, a third of the length, reads like a person who understood the bug and moved
on - not a report justifying the change to a skeptical reader.

## 5. When Claude is asked to commit

Apply this skill by default, without being asked each time. If a commit is trivial, propose (or
just make) a subject-only message rather than defaulting to a body "to be thorough."
