# Contributor PR Template

> **How to use:** Copy the sections below into your PR description when opening a pull request.
> This template lives at `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md` and is
> not auto-applied by GitHub — paste it manually into your PR description.

---

## Summary

<!-- One sentence describing what this PR adds or changes. -->

## Related Issue

<!-- Link the issue this PR addresses. -->

Closes #

## Changes Made

<!-- List the specific files changed and what was changed in each. -->

| File | What Changed |
|------|-------------|
|      |             |

## Type of Change

<!-- Check all that apply. -->

- [ ] New adapter
- [ ] New quickstart combo
- [ ] Methodology update
- [ ] Bug fix / correction
- [ ] Documentation improvement
- [ ] Other (describe below)

## Testing Done

<!-- Confirm each item applies to your changes. -->

- [ ] All required adapter files are present (README.md, target-named template file, quickstart.md)
- [ ] No placeholder text remains (no `TODO`, `FIXME`, `YOUR_NAME`, `<fill in>`, etc.)
- [ ] All referenced paths exist in the repository
- [ ] Markdown renders correctly (headings, lists, code blocks)
- [ ] Existing content was not modified unintentionally

## Checklist

<!-- Confirm each item before submitting. -->

- [ ] An issue was created and linked above (`Closes #N`)
- [ ] Branch follows the conventional-commit prefix style used in `CONTRIBUTING-AGENTS.md` (e.g. `feat/add-windsurf-adapter`, `fix/broken-quickstart-link`, `docs/clarify-anatomy`)
- [ ] This PR addresses one concern only (single adapter, combo, or fix)
- [ ] Commits follow Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.)
- [ ] `CONTRIBUTING-AGENTS.md` invariants verified — adapter anatomy compliance confirmed (all required files present, correct structure)
- [ ] Parent `README.md` updated if this PR adds an adapter or quickstart combo

## Pre-Review Self-Audit

<!-- Run before requesting the first review. See docs/agentic-review-cycle.md. -->

- [ ] For each mechanism touched, its class is named and the fix covers the class, not one member
- [ ] Denylists replaced by allowlists where inputs are open-ended (env, paths, headers, options)
- [ ] Each new lock/cache/allowlist/retry checked against its own failure modes (partial failure, rerun, concurrent run, differing environment)
- [ ] Class-level regression tests exist; malformed input and boundary cases covered
- [ ] Full suite run once on the exact head being submitted
- [ ] `git status`/diff shows only intended files
- [ ] Docs and acceptance criteria updated to match behavior

## Review-Cycle Log

<!-- Required for every PR. Add one row per review round, including a single clean round. -->

| Round | Review ID / head SHA | Findings (H/M/L) | Finding → class map | Origin counts (pre-existing / introduced / unknown) | Fix commit(s) | Validation evidence |
|---|---|---|---|---|---|---|
|   |   |   |   |   |   |   |

Stop condition: <!-- agreed up front -->. Remaining low-severity items: <!-- list -->.

## Additional Notes

<!-- Optional. Add context for reviewers, known limitations, follow-up work, or anything else worth noting. -->
