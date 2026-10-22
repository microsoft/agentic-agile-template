# GitHub Issues Adapter

This adapter documents how [Agentic-Agile](../../../README.md) uses **GitHub Issues** as its default issue tracker.

Unlike other adapters in this directory, this adapter does **not** provide a new template file. The story template is already present in this repository at [`.github/ISSUE_TEMPLATE/agentic-story.md`](../../../.github/ISSUE_TEMPLATE/agentic-story.md) and is automatically discovered by GitHub — no setup required.

## What This Adapter Covers

- How GitHub Issues implements the agentic-story format
- The sections of the template and their purpose
- How to customize the template for your team
- Why this adapter exists alongside others in this directory

## Template Location

The canonical GitHub Issues template lives at:

```
.github/ISSUE_TEMPLATE/agentic-story.md
```

GitHub auto-discovers all files in `.github/ISSUE_TEMPLATE/` and presents them when a user opens a new issue. When you fork or use this template repository, the story template is immediately available — nothing to copy or configure.

## Review-Cycle Fields

The story template includes an optional **Review Cycle** section (stop condition, finding classes expected, exact-head review plan). The per-round log is recorded as a table in the PR description using [`CONTRIBUTOR_PR_TEMPLATE.md`](../../../.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md). See [`docs/agentic-review-cycle.md`](../../../docs/agentic-review-cycle.md) and the [field mapping](../README.md#review-cycle-field-mapping).

## See Also

- [`quickstart.md`](quickstart.md) — step-by-step guide for using GitHub Issues with Agentic-Agile
- [Issue-Trackers Adapters overview](../README.md) — how all issue-tracker adapters relate to the system
