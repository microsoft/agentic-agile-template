# [SAMPLE 1] Task API endpoints with input validation

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#9](https://github.com/microsoft/agentic-agile-template/issues/9) |
| Sample group | `SAMPLE 1 (TaskFlow worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:47:40Z |
| Labels | `phase:planned`, `priority:2-normal`, `effort:Large`, `category:user-feature`, `type:story`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Create HTTP handlers for task CRUD operations with input validation middleware.

Part of #5

## Context / Motivation

The API layer exposes task operations over HTTP. It composes the validation middleware and service layer — no business logic lives here. This story runs in Wave 3 alongside the business logic story because the service interface is defined at the Wave 2 review gate, allowing parallel implementation against the contract.

## Scope

### Files to Create or Modify

- `src/api/routes/tasks.ts` — Express route handlers for task endpoints
- `src/middleware/validate-task.ts` — Request validation middleware
- `src/api/routes/index.ts` — Register task routes in the router
- `tests/unit/middleware/validate-task.test.ts` — Validation middleware tests

### Interfaces to Implement

- `POST /api/tasks` — create a task (201 on success)
- `GET /api/tasks` — list tasks with query params for status, assignee, due_date range
- `GET /api/tasks/:id` — get single task (404 if not found)
- `PATCH /api/tasks/:id` — update task including status transitions
- `DELETE /api/tasks/:id` — soft delete (204 on success)

### Invariants to Preserve

- Existing routes and middleware remain unchanged
- Response shape follows project convention: `{ data, error, metadata }`
- Error status codes are consistent: 400 (validation), 404 (not found), 409 (invalid transition), 500 (server error)

## Acceptance Criteria

- [ ] All 5 endpoints implemented and registered
- [ ] Validation middleware rejects invalid create/update requests with field-level 400 errors
- [ ] Title is required on create; status must be valid enum; due_date must be a valid ISO date
- [ ] All endpoints use the service layer (no direct repository access)
- [ ] Consistent `{ data, error, metadata }` response shape
- [ ] Validation middleware unit tests cover valid and invalid inputs

## Negative Constraints

- Does NOT implement authentication or authorization
- Does NOT implement integration tests (separate story)
- Does NOT modify the service layer or repository layer
- Does NOT add WebSocket or real-time notification support

## Effort Estimate

- [x] **L** — significant scope, multi-day

## Dependencies

- Depends on #7 (Task repository — service interface defined at Wave 2 review gate)
- Depends on #8 (Task business logic — parallel in Wave 3, coding against shared contract)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `src/api/routes/tasks.ts` | ✅ | New file |
| `src/middleware/validate-task.ts` | ✅ | New file |
| `src/api/routes/index.ts` | ✅ | Add route registration |
| `tests/unit/middleware/validate-task.test.ts` | ✅ | New file |

## Delivery

<!-- Added post-implementation. Do not fill in when creating the story. -->

## Comments on the original issue

_(no comments at the time of snapshot)_
