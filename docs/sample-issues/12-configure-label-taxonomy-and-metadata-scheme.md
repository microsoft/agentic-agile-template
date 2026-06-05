# [SAMPLE 2] Configure label taxonomy and metadata scheme

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#12](https://github.com/microsoft/agentic-agile-template/issues/12) |
| Sample group | `SAMPLE 2 (Onboarding worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:48:46Z |
| Labels | `phase:planned`, `priority:2-normal`, `effort:Small`, `category:devops`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Create the label taxonomy in the GitHub repository so issues can be tagged with development phase, priority, effort, and category metadata.

Part of #10

## Context / Motivation

Labels are the primary metadata system for agentic-agile backlogs. They encode the information that agents and humans need to prioritize, filter, and track work. A consistent prefix convention (`dimension:value`) makes labels filterable and unambiguous. This story creates the full taxonomy so that all subsequent issues can be properly tagged from creation.

## Scope

### Files to Create or Modify

- No source files modified. All work is in GitHub repository label settings.

### Interfaces to Implement

- N/A (GitHub label configuration)

### Invariants to Preserve

- Existing default labels (bug, enhancement, documentation, etc.) remain untouched
- No existing issues lose their labels

## Acceptance Criteria

- [ ] Phase labels created (5): `phase:planned`, `phase:next`, `phase:now`, `phase:blocked`, `phase:done`
- [ ] Priority labels created (5): `priority:0-crit` through `priority:4-trivial`
- [ ] Effort labels created (5): `effort:X-Small` through `effort:X-Large`
- [ ] Category labels created (7): `category:architecture`, `category:documentation`, `category:bug`, `category:security`, `category:user-feature`, `category:platform-feature`, `category:devops`
- [ ] Meta labels created (3): `type:epic`, `type:story`, `sample`
- [ ] Each label has a distinct color and description
- [ ] All labels use consistent prefix convention

## Negative Constraints

- Does NOT remove or rename existing default GitHub labels
- Does NOT create a GitHub Project board
- Does NOT modify issue templates

## Effort Estimate

- [x] **S** — small, well-understood, a few hours

## Dependencies

- None (Wave 1, can run parallel with B1)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| (GitHub labels) | ✅ | Repository settings |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
