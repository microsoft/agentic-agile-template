# Sample issues — Agentic-Agile worked examples

This directory contains snapshots of two illustrative issue groups, originally filed as live issues in this repository for onboarding purposes:

- **SAMPLE 1 — TaskFlow**: A hypothetical task-management REST API used to demonstrate epic decomposition, wave planning, and parallel agent execution (issues #5–#9).
- **SAMPLE 2 — Onboarding walkthrough**: A worked example of an external contributor's first few stories when adopting this template (issues #10–#14).

## Why these are here (and not in the issue tracker)

These sample issues were originally filed as live issues to give new users readable examples of the Agentic-Agile issue style. After consolidation, they were migrated into version-controlled markdown so that:

1. The public issue tracker is reserved for **real** backlog items from external contributors.
2. The samples remain stable, citable, and edit-tracked alongside the rest of the documentation.
3. New users can reference them via repo-relative links without needing to filter the issue tracker.

The original live issues will be closed with comments pointing back to this directory as part of the consolidation follow-up. If you are reading this directory while the corresponding live issues are still open in the tracker, that closure step has not yet run.

## Index

### SAMPLE 1 — TaskFlow (worked decomposition example)

| File | Original issue | Title |
|------|----------------|-------|
| [`05-taskflow-task-management-with-status-transitions.md`](05-taskflow-task-management-with-status-transitions.md) | [#5](https://github.com/microsoft/agentic-agile-template/issues/5) | [SAMPLE 1] Epic: TaskFlow — Task management with status transitions |
| [`06-task-data-model-and-typescript-types.md`](06-task-data-model-and-typescript-types.md) | [#6](https://github.com/microsoft/agentic-agile-template/issues/6) | [SAMPLE 1] Task data model and TypeScript types |
| [`07-task-repository-layer-with-unit-tests.md`](07-task-repository-layer-with-unit-tests.md) | [#7](https://github.com/microsoft/agentic-agile-template/issues/7) | [SAMPLE 1] Task repository layer with unit tests |
| [`08-task-business-logic-status-transitions-and-validation.md`](08-task-business-logic-status-transitions-and-validation.md) | [#8](https://github.com/microsoft/agentic-agile-template/issues/8) | [SAMPLE 1] Task business logic — status transitions and validation |
| [`09-task-api-endpoints-with-input-validation.md`](09-task-api-endpoints-with-input-validation.md) | [#9](https://github.com/microsoft/agentic-agile-template/issues/9) | [SAMPLE 1] Task API endpoints with input validation |

### SAMPLE 2 — Onboarding walkthrough

| File | Original issue | Title |
|------|----------------|-------|
| [`10-getting-started-with-the-agentic-agile-template.md`](10-getting-started-with-the-agentic-agile-template.md) | [#10](https://github.com/microsoft/agentic-agile-template/issues/10) | [SAMPLE 2] Epic: Getting started with the agentic-agile template |
| [`11-customize-agent-context-file-claude-md.md`](11-customize-agent-context-file-claude-md.md) | [#11](https://github.com/microsoft/agentic-agile-template/issues/11) | [SAMPLE 2] Customize agent context file (CLAUDE.md) |
| [`12-configure-label-taxonomy-and-metadata-scheme.md`](12-configure-label-taxonomy-and-metadata-scheme.md) | [#12](https://github.com/microsoft/agentic-agile-template/issues/12) | [SAMPLE 2] Configure label taxonomy and metadata scheme |
| [`13-create-first-epic-decomposition-with-wave-plan.md`](13-create-first-epic-decomposition-with-wave-plan.md) | [#13](https://github.com/microsoft/agentic-agile-template/issues/13) | [SAMPLE 2] Create first epic decomposition with wave plan |
| [`14-run-first-wave-with-parallel-agent-execution.md`](14-run-first-wave-with-parallel-agent-execution.md) | [#14](https://github.com/microsoft/agentic-agile-template/issues/14) | [SAMPLE 2] Run first wave with parallel agent execution |

## Snapshot provenance

Snapshots were taken on 2026-06-05 as part of a consolidation effort to migrate these onboarding examples out of the live issue tracker. The metadata table at the top of each file records the original author, creation date, labels, and a URL back to the original issue for full provenance. The live issues will be closed with pointer comments back to these files as part of the consolidation follow-up; until then the URLs resolve to the still-open issues.

## Note on SAMPLE 2's framing

SAMPLE 2 (issues `10`–`14`) was authored before this template's multi-platform rewrite, and frames the onboarding flow around customizing `CLAUDE.md` as the canonical agent context file. The current canonical onboarding flow uses [`AGENTS.md`](../../AGENTS.md) as the universal cross-agent entry point and treats `CLAUDE.md` as one of several equal-status platform adapters under [`platform-adapters/agent-tools/`](../../platform-adapters/agent-tools/). The SAMPLE 2 snapshots are preserved verbatim as a worked example of the issue-decomposition pattern; refer to `AGENTS.md` for the current onboarding flow rather than following SAMPLE 2's adapter-selection guidance literally.

## How to write your own sample-style issue

See [`../epic-decomposition-example.md`](../epic-decomposition-example.md) for the structural pattern these samples illustrate, and [`../../.github/ISSUE_TEMPLATE/agentic-story.md`](../../.github/ISSUE_TEMPLATE/agentic-story.md) for the template form to use when filing live issues.
