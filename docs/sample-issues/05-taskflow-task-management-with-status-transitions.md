# [SAMPLE 1] Epic: TaskFlow — Task management with status transitions

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#5](https://github.com/microsoft/agentic-agile-template/issues/5) |
| Sample group | `SAMPLE 1 (TaskFlow worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:46:20Z |
| Labels | `phase:now`, `priority:1-high`, `effort:X-Large`, `category:user-feature`, `type:epic`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Users can create, assign, and track tasks with due dates and status transitions through a REST API.

## Context / Motivation

TaskFlow is a task management REST API (Node.js, Express, PostgreSQL) used as a worked example of epic decomposition in Agentic-Agile Development. This epic is intentionally too large for a single story — it touches data modeling, repository patterns, business logic, API design, and integration testing. Decomposing it demonstrates wave-based parallel execution.

> **Note:** This is a **sample epic** for onboarding purposes. See `docs/epic-decomposition-example.md` for the full walkthrough of this decomposition.

## Wave Execution Plan

```
Wave 1: [#6 Task Data Model]
         ↓ review gate (schema + types verified)
Wave 2: [#7 Task Repository Layer]
         ↓ review gate (queries verified, service interface defined)
Wave 3: [#8 Task Business Logic] [#9 Task API Endpoints]  ← parallel
         ↓ review gate (transitions + API shapes verified)
```

## Child Issues

| Wave | Issue | Status |
|------|-------|--------|
| 1 | #6 [SAMPLE 1] Task data model and TypeScript types | `phase:done` |
| 2 | #7 [SAMPLE 1] Task repository layer with unit tests | `phase:now` |
| 3 | #8 [SAMPLE 1] Task business logic — status transitions | `phase:next` |
| 3 | #9 [SAMPLE 1] Task API endpoints with input validation | `phase:planned` |

## Acceptance Criteria

- [ ] All 4 child stories are implemented and merged
- [ ] Wave execution order is respected (no story starts before its dependencies are done)
- [ ] Integration between layers works end-to-end (create → assign → transition → complete)
- [ ] Each wave passes a review gate before the next wave begins

## Negative Constraints

- Does NOT include authentication/authorization (separate epic)
- Does NOT include deployment or CI/CD configuration
- Does NOT modify existing user management endpoints

## Comments on the original issue

_(no comments at the time of snapshot)_
