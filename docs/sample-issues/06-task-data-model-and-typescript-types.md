# [SAMPLE 1] Task data model and TypeScript types

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#6](https://github.com/microsoft/agentic-agile-template/issues/6) |
| Sample group | `SAMPLE 1 (TaskFlow worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:46:41Z |
| Labels | `phase:done`, `priority:1-high`, `effort:Small`, `category:architecture`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Create the database migration and TypeScript type definitions for the tasks table, establishing the data foundation for all downstream TaskFlow stories.

Part of #5

## Context / Motivation

Every other TaskFlow story depends on the task schema and types. This is the Wave 1 foundation — getting it right prevents rework in later waves. The schema must support status transitions, assignment, and due date tracking.

## Scope

### Files to Create or Modify

- `src/models/task.ts` — TypeScript type definitions (Task, TaskStatus enum, CreateTaskInput, UpdateTaskInput)
- `src/migrations/002-create-tasks.sql` — Database migration creating the tasks table
- `src/models/index.ts` — Export barrel, add task type exports

### Interfaces to Implement

- `TaskStatus` enum: `todo`, `in_progress`, `in_review`, `done`
- `Task` type matching the database schema exactly

### Invariants to Preserve

- Existing user model and migrations remain unchanged
- Migration numbering follows sequential order (001 already exists for users)

## Acceptance Criteria

- [ ] Migration creates `tasks` table with columns: id, title, description, status, assignee_id, due_date, created_at, updated_at
- [ ] Status is an enum type: `todo`, `in_progress`, `in_review`, `done`
- [ ] TypeScript types match the database schema exactly
- [ ] Migration is reversible (includes DOWN migration)
- [ ] Types are exported from `src/models/index.ts`

## Negative Constraints

- Does NOT implement any query logic (that's the repository story)
- Does NOT create API endpoints
- Does NOT add business rules or validation

## Effort Estimate

- [x] **S** — small, well-understood, a few hours

## Dependencies

- None (this is the Wave 1 foundation)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `src/models/task.ts` | ✅ | New file |
| `src/migrations/002-create-tasks.sql` | ✅ | New file |
| `src/models/index.ts` | ✅ | Add exports only |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
