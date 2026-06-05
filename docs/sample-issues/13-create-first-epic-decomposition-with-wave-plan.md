# [SAMPLE 2] Create first epic decomposition with wave plan

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#13](https://github.com/microsoft/agentic-agile-template/issues/13) |
| Sample group | `SAMPLE 2 (Onboarding worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:49:05Z |
| Labels | `phase:planned`, `priority:2-normal`, `effort:Large`, `category:architecture`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Decompose your first epic into stories with explicit file ownership, acceptance criteria, and wave assignments following the pattern in `docs/epic-decomposition-example.md`.

Part of #10

## Context / Motivation

Epic decomposition is the core skill of agentic-agile development. A well-decomposed epic enables parallel execution without merge conflicts. This story walks through the full decomposition process: identifying components, mapping dependencies, creating stories with file ownership, and assigning them to waves. The output is a set of issues ready for agent execution.

## Scope

### Files to Create or Modify

- GitHub Issues (new epic + child story issues)
- No source files modified

### Interfaces to Implement

- Each story issue follows the agentic-story template (`.github/ISSUE_TEMPLATE/agentic-story.md`)
- Each story declares file ownership with no overlap within a wave

### Invariants to Preserve

- Existing issues and labels remain unchanged
- Issue template structure is followed exactly

## Acceptance Criteria

- [ ] One epic issue created with summary, wave execution plan, and child issue list
- [ ] 3-6 child story issues created, each using the agentic-story template
- [ ] Every child story has explicit file ownership (no two stories in the same wave own the same file)
- [ ] Dependency graph is documented (which stories depend on which)
- [ ] Stories are assigned to waves based on dependency analysis
- [ ] Each story has labels for phase, priority, effort, and category
- [ ] Wave plan shows maximum safe parallelism

## Negative Constraints

- Does NOT implement any code from the stories (that's Wave 3)
- Does NOT require a specific project or tech stack
- Does NOT modify the issue template itself

## Effort Estimate

- [x] **L** — significant scope, multi-day

## Dependencies

- Depends on #11 (CLAUDE.md — agent context needed for decomposition quality)
- Depends on #12 (Labels — needed to tag the new issues)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| (GitHub Issues) | ✅ | New issues only |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
