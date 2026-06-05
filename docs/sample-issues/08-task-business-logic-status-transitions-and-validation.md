# [SAMPLE 1] Task business logic — status transitions and validation

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#8](https://github.com/microsoft/agentic-agile-template/issues/8) |
| Sample group | `SAMPLE 1 (TaskFlow worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:47:18Z |
| Labels | `phase:next`, `priority:2-normal`, `effort:Medium`, `category:user-feature`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Implement status transition rules, assignment validation, and due date enforcement for tasks.

Part of #5

## Context / Motivation

Business logic is the core of the task management feature. Status transitions follow a defined state machine — not every transition is valid. Assignment must reference existing users. Due dates should warn but not block on past dates. This layer enforces all domain rules before data reaches the repository.

## Scope

### Files to Create or Modify

- `src/services/task-service.ts` — Business logic for task operations
- `tests/unit/services/task-service.test.ts` — Unit tests covering all transition paths

### Interfaces to Implement

- `TaskService.createTask(input): Promise<Task>` — validates and delegates to repository
- `TaskService.updateStatus(id, newStatus): Promise<Task>` — enforces transition rules
- `TaskService.assignTask(id, assigneeId): Promise<Task>` — validates assignee exists
- `TaskService.listTasks(filters): Promise<Task[]>` — delegates to repository with optional enrichment

### Invariants to Preserve

- Status transition rules are the single source of truth (no bypassing from API layer)
- Repository layer is accessed only through service layer
- User existence checks use the existing user repository

## Acceptance Criteria

- [ ] Status transitions follow allowed paths: todo→in_progress, in_progress→in_review, in_review→done, any→todo (reset)
- [ ] Invalid transitions return descriptive `InvalidTransitionError` with current and attempted status
- [ ] Assignment validation: assignee must exist in users table (checked via user-repository)
- [ ] Due date: warn (not block) on past due dates — returns warning in response metadata
- [ ] Unit tests cover all valid transitions, all invalid transitions, and edge cases
- [ ] Tests achieve >90% branch coverage on transition logic

## Negative Constraints

- Does NOT implement HTTP endpoints (that's the API story)
- Does NOT modify the repository layer
- Does NOT implement authentication or authorization checks

## Effort Estimate

- [x] **M** — moderate complexity, up to a day

## Dependencies

- Depends on #7 (Task repository — needs data access functions)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `src/services/task-service.ts` | ✅ | New file |
| `tests/unit/services/task-service.test.ts` | ✅ | New file |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
