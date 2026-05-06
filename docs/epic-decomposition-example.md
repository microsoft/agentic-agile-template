# Epic Decomposition: A Worked Example

This document walks through a complete epic decomposition using Agentic-Agile Development principles. The scenario is fully synthetic, designed to illustrate the process from epic through stories to wave execution.

---

## The Scenario

**Project:** TaskFlow, a task management REST API
**Stack:** Node.js, Express, PostgreSQL
**Team:** One developer working with CLI coding agents in parallel

**Epic:** "Users can create, assign, and track tasks with due dates and status transitions."

This epic is too large for a single story. It touches multiple modules, requires database changes, and has both API and business logic components. It needs decomposition.

---

## Step 1: Identify the Components

Break the epic into its natural components by asking: what are the independent pieces of functionality?

| Component | Description |
|-----------|-------------|
| Data model | Database schema for tasks (tables, migrations) |
| Repository layer | Data access functions for tasks (CRUD operations) |
| Business logic | Status transition rules, assignment validation, due date enforcement |
| API endpoints | HTTP handlers for task operations |
| Input validation | Request validation middleware for task endpoints |
| Tests | Unit tests for business logic, integration tests for API |

---

## Step 2: Map Dependencies

Before creating stories, understand which components depend on which:

```
Data model (migrations, types)
    │
    ├──→ Repository layer (needs schema to query)
    │        │
    │        ├──→ Business logic (needs repository to read/write)
    │        │        │
    │        │        └──→ API endpoints (needs business logic)
    │        │                 │
    │        │                 └──→ Integration tests (needs running API)
    │        │
    │        └──→ Unit tests for repository
    │
    └──→ Input validation (needs types for validation rules)
```

Key insight: the data model and types must exist before anything else can proceed. This is the "foundation" that goes in the first wave.

---

## Step 3: Create Stories with File Ownership

Each story declares exactly which files it owns. No overlap allowed within a wave.

### Story 1: Task Data Model and Types

**Summary:** Create the database migration and TypeScript type definitions for tasks.

**Files owned:**
- `src/models/task.ts` (type definitions)
- `src/migrations/002-create-tasks.sql` (database migration)
- `src/models/index.ts` (export barrel, add task types)

**Acceptance criteria:**
- [ ] Migration creates `tasks` table with columns: id, title, description, status, assignee_id, due_date, created_at, updated_at
- [ ] Status is an enum: `todo`, `in_progress`, `in_review`, `done`
- [ ] TypeScript types match the database schema exactly
- [ ] Migration is reversible

**Negative constraints:**
- Does NOT implement any query logic
- Does NOT create API endpoints

---

### Story 2: Task Repository

**Summary:** Implement data access functions for tasks.

**Files owned:**
- `src/repositories/task-repository.ts`
- `tests/unit/repositories/task-repository.test.ts`

**Acceptance criteria:**
- [ ] Functions: createTask, getTaskById, listTasks (with filters), updateTask, deleteTask
- [ ] All functions use parameterized queries (no SQL injection)
- [ ] Unit tests cover all functions with mocked database

**Dependencies:** Story 1 (needs types and schema)

---

### Story 3: Input Validation

**Summary:** Create request validation middleware for task endpoints.

**Files owned:**
- `src/middleware/validate-task.ts`
- `tests/unit/middleware/validate-task.test.ts`

**Acceptance criteria:**
- [ ] Validates create-task requests (title required, status must be valid enum, due_date must be future)
- [ ] Validates update-task requests (partial updates allowed, same field rules)
- [ ] Returns structured 400 errors with field-level messages

**Dependencies:** Story 1 (needs types for validation rules)

---

### Story 4: Task Business Logic

**Summary:** Implement status transition rules and assignment validation.

**Files owned:**
- `src/services/task-service.ts`
- `tests/unit/services/task-service.test.ts`

**Acceptance criteria:**
- [ ] Status transitions follow allowed paths: todo→in_progress, in_progress→in_review, in_review→done, any→todo (reset)
- [ ] Invalid transitions return descriptive errors
- [ ] Assignment validation: assignee must exist in users table
- [ ] Due date: warn (not block) on past due dates

**Dependencies:** Story 2 (needs repository functions)

---

### Story 5: Task API Endpoints

**Summary:** Create HTTP handlers for task CRUD operations.

**Files owned:**
- `src/api/routes/tasks.ts`
- `src/api/routes/index.ts` (add task routes)

**Acceptance criteria:**
- [ ] POST /api/tasks — create a task
- [ ] GET /api/tasks — list tasks (with query params for status, assignee)
- [ ] GET /api/tasks/:id — get single task
- [ ] PATCH /api/tasks/:id — update task (including status transitions)
- [ ] DELETE /api/tasks/:id — soft delete
- [ ] All endpoints use validation middleware and service layer

**Dependencies:** Story 3 (validation), Story 4 (business logic)

---

### Story 6: Integration Tests

**Summary:** End-to-end tests for the task API.

**Files owned:**
- `tests/integration/tasks.test.ts`
- `tests/fixtures/task-fixtures.ts`

**Acceptance criteria:**
- [ ] Tests cover the full lifecycle: create → assign → transition → complete
- [ ] Tests verify invalid transitions are rejected
- [ ] Tests verify validation errors return proper 400 responses
- [ ] Uses test database with automatic setup/teardown

**Dependencies:** Story 5 (needs complete API)

---

## Step 4: Assign Stories to Waves

Group stories into waves based on dependencies. Stories in the same wave must have no file overlap and no dependencies on each other.

### Wave 1: Foundation

| Story | Agent | Files Owned |
|-------|-------|-------------|
| Story 1: Data Model | Agent 1 | `src/models/task.ts`, `src/migrations/002-create-tasks.sql`, `src/models/index.ts` |

Only one story in Wave 1 because everything else depends on types and schema. This wave is small but critical: get the foundation right.

**Review gate:** Verify schema design, type definitions, and migration reversibility before proceeding.

### Wave 2: Data and Validation Layer

| Story | Agent | Files Owned |
|-------|-------|-------------|
| Story 2: Repository | Agent 1 | `src/repositories/task-repository.ts`, `tests/unit/repositories/task-repository.test.ts` |
| Story 3: Validation | Agent 2 | `src/middleware/validate-task.ts`, `tests/unit/middleware/validate-task.test.ts` |

Stories 2 and 3 both depend on Story 1 but NOT on each other. They touch completely different files. They can run in parallel.

**Review gate:** Verify repository queries are correct and validation rules match the schema.

### Wave 3: Business Logic and API

| Story | Agent | Files Owned |
|-------|-------|-------------|
| Story 4: Business Logic | Agent 1 | `src/services/task-service.ts`, `tests/unit/services/task-service.test.ts` |
| Story 5: API Endpoints | Agent 2 | `src/api/routes/tasks.ts`, `src/api/routes/index.ts` |

Wait: Story 5 depends on Story 4 (it needs the service layer). Can they really be parallel?

This is a judgment call. If the service interface is well-defined (function signatures and return types established in Wave 2's review gate), Agent 2 can implement the API handlers against the interface while Agent 1 implements the logic. The API handlers call service functions; they don't need to know the implementation details.

**To make this work:** During Wave 2's review gate, define and document the service interface (function signatures, parameter types, return types, error types). Both agents in Wave 3 code against this contract.

**Review gate:** Verify status transition logic, API response shapes, and interface contract compliance.

### Wave 4: Integration

| Story | Agent | Files Owned |
|-------|-------|-------------|
| Story 6: Integration Tests | Agent 1 | `tests/integration/tasks.test.ts`, `tests/fixtures/task-fixtures.ts` |

Integration tests run against the complete system. This must wait for all previous waves.

**Review gate:** Verify test coverage, lifecycle scenarios, and edge cases.

---

## Wave Execution Summary

```
Wave 1: [Story 1: Data Model]
         ↓ review gate (schema + types verified)
Wave 2: [Story 2: Repository] [Story 3: Validation]  ← parallel
         ↓ review gate (queries + validation verified, service interface defined)
Wave 3: [Story 4: Business Logic] [Story 5: API Endpoints]  ← parallel
         ↓ review gate (transitions + API shapes verified)
Wave 4: [Story 6: Integration Tests]
```

**Total stories:** 6
**Total waves:** 4
**Maximum parallelism:** 2 agents in Waves 2 and 3
**Sequential bottleneck:** Wave 1 (foundation) and Wave 4 (integration)

---

## Key Takeaways

1. **Dependencies determine wave structure.** You cannot parallelize what has upstream dependencies. Identify the dependency graph first, then group into waves.

2. **File ownership prevents conflicts.** Every story lists its files. If two stories in the same wave need the same file, move one to a later wave.

3. **Review gates are not overhead, they are coordination.** The Wave 2 review gate that defines the service interface is what makes Wave 3 parallelism possible.

4. **Foundation waves may be small.** Wave 1 has only one story. That is fine. Rushing the foundation to "maximize parallelism" creates rework downstream.

5. **Interface contracts enable parallelism.** When two stories depend on each other's interface but not implementation, define the interface first (at a review gate) and let both implement in parallel.

6. **Budget for the full cycle.** This example has 6 stories across 4 waves. A naive estimate might say "6 stories, 2 agents, 3 waves." The dependency graph says otherwise. Plan from the graph, not the story count.
