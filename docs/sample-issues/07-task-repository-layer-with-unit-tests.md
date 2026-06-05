# [SAMPLE 1] Task repository layer with unit tests

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#7](https://github.com/microsoft/agentic-agile-template/issues/7) |
| Sample group | `SAMPLE 1 (TaskFlow worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:46:59Z |
| Labels | `phase:now`, `priority:1-high`, `effort:Medium`, `category:platform-feature`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Implement data access functions for tasks with full CRUD operations and parameterized queries.

Part of #5

## Context / Motivation

The repository layer sits between the data model (Wave 1) and the business logic (Wave 3). It provides the query interface that the service layer will use. All database access for tasks flows through this layer — no direct SQL in business logic or API handlers.

## Scope

### Files to Create or Modify

- `src/repositories/task-repository.ts` — Data access functions for tasks
- `tests/unit/repositories/task-repository.test.ts` — Unit tests with mocked database

### Interfaces to Implement

- `createTask(input: CreateTaskInput): Promise<Task>`
- `getTaskById(id: string): Promise<Task | null>`
- `listTasks(filters?: TaskFilters): Promise<Task[]>`
- `updateTask(id: string, input: UpdateTaskInput): Promise<Task>`
- `deleteTask(id: string): Promise<void>`

### Invariants to Preserve

- All queries use parameterized statements (no SQL injection)
- Existing repository patterns (from user-repository) are followed consistently
- Database connection pooling is reused, not duplicated

## Acceptance Criteria

- [ ] All 5 CRUD functions implemented with parameterized queries
- [ ] `listTasks` supports filtering by status, assignee_id, and due_date range
- [ ] Unit tests cover all functions with mocked database
- [ ] Tests cover error cases (not found, invalid input)
- [ ] No raw SQL string concatenation anywhere

## Negative Constraints

- Does NOT implement status transition rules (that's business logic)
- Does NOT add HTTP endpoints
- Does NOT implement input validation beyond type safety

## Effort Estimate

- [x] **M** — moderate complexity, up to a day

## Dependencies

- Depends on #6 (Task data model — needs types and schema)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `src/repositories/task-repository.ts` | ✅ | New file |
| `tests/unit/repositories/task-repository.test.ts` | ✅ | New file |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
