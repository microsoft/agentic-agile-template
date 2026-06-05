# [SAMPLE 2] Run first wave with parallel agent execution

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#14](https://github.com/microsoft/agentic-agile-template/issues/14) |
| Sample group | `SAMPLE 2 (Onboarding worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:49:30Z |
| Labels | `phase:planned`, `priority:3-low`, `effort:Medium`, `category:user-feature`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Execute the first wave of your decomposed epic by assigning stories to parallel agents, reviewing outputs at the wave gate, and merging approved work.

Part of #10

## Context / Motivation

This is where theory meets practice. Running a wave means launching multiple agents in parallel, each working on their own story in their own branch, with no file overlap. The review gate after the wave ensures quality before dependent work begins. This story produces the team's first hands-on experience with the agentic-agile execution model.

## Scope

### Files to Create or Modify

- Feature branches (one per story in the wave)
- Source files as specified in each story's file ownership table
- PR descriptions linking back to story issues

### Interfaces to Implement

- Each story produces a PR targeting `main`
- Each PR references its story issue (`Closes #N`)
- Review gate checklist applied to all PRs in the wave

### Invariants to Preserve

- `main` branch remains stable (all tests pass after each merge)
- No merge conflicts between PRs in the same wave (verified by file ownership)
- Existing functionality is not broken

## Acceptance Criteria

- [ ] Feature branches created for each story in Wave 1 (one branch per story)
- [ ] Each story assigned to an agent (CLI, IDE, or cloud agent)
- [ ] Agents execute in parallel without coordination messages
- [ ] All PRs pass CI checks (tests, linting, type checks)
- [ ] Review gate applied: each PR reviewed for correctness, test coverage, and convention compliance
- [ ] All review findings reach terminal state (fixed, accepted, or deferred)
- [ ] PRs merged to `main` after review approval
- [ ] No merge conflicts encountered (file ownership validated)
- [ ] Phase labels updated: stories move from `phase:planned` → `phase:now` → `phase:done`

## Negative Constraints

- Does NOT execute all waves (just Wave 1 for the first iteration)
- Does NOT require specific agent tooling (any agent surface works)
- Does NOT skip the review gate even if agent output looks correct

## Effort Estimate

- [x] **M** — moderate complexity, up to a day

## Dependencies

- Depends on #13 (Epic decomposition — need stories with file ownership and wave assignments)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| (varies per story) | ✅ | As declared in each story's ownership table |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
