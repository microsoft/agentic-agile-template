# [SAMPLE 2] Customize agent context file (CLAUDE.md)

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#11](https://github.com/microsoft/agentic-agile-template/issues/11) |
| Sample group | `SAMPLE 2 (Onboarding worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:48:27Z |
| Labels | `phase:planned`, `priority:1-high`, `effort:Medium`, `category:documentation`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Customize the `CLAUDE.md` agent context file with your project's actual information so that coding agents produce output that fits your conventions from the first interaction.

Part of #10

## Context / Motivation

`CLAUDE.md` is the primary control surface for agent behavior. A generic template produces generic output. By filling in your project's purpose, structure, conventions, testing strategy, and build commands, you transform the agent from a general-purpose tool into a project-aware partner. This is the highest-leverage setup step.

## Scope

### Files to Create or Modify

- `CLAUDE.md` — Replace all placeholder sections with project-specific content
- `.github/copilot-instructions.md` — Update the shorter Copilot-specific subset to match

### Interfaces to Implement

- N/A (documentation only)

### Invariants to Preserve

- Section structure of `CLAUDE.md` remains intact (agents expect specific headings)
- `.github/copilot-instructions.md` stays consistent with `CLAUDE.md` content

## Acceptance Criteria

- [ ] Project Purpose section filled with 2-3 sentences, primary language, framework, key dependencies
- [ ] Repository Structure section matches actual directory layout
- [ ] Coding Conventions section has language-specific rules (not placeholders)
- [ ] Testing Strategy section specifies framework, organization, naming, coverage expectations
- [ ] Build and Run section has working commands for install, build, test, lint
- [ ] `.github/copilot-instructions.md` updated to match
- [ ] An agent given the updated context produces code following stated conventions (manual verification)

## Negative Constraints

- Does NOT change the structure or headings of `CLAUDE.md` (template compatibility)
- Does NOT add project-specific code or tests
- Does NOT configure CI/CD or deployment

## Effort Estimate

- [x] **M** — moderate complexity, up to a day

## Dependencies

- None (Wave 1, can start immediately)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `CLAUDE.md` | ✅ | Replace placeholders |
| `.github/copilot-instructions.md` | ✅ | Update to match |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
