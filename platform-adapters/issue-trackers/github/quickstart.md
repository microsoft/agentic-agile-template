# GitHub Issues Quickstart

## Nothing to Copy

GitHub Issues is the **default tracker** for Agentic-Agile. The story template is already configured at:

```
.github/ISSUE_TEMPLATE/agentic-story.md
```

GitHub automatically discovers all files under `.github/ISSUE_TEMPLATE/` and presents them in the "New Issue" dialog. There is nothing to copy, install, or configure.

## Using the Template

1. Open your repository on GitHub.
2. Click **Issues** → **New issue**.
3. Select **Agentic Story** from the template picker.
4. Fill in the sections (see format reference below).

## Agentic-Story Format Reference

The template at [`.github/ISSUE_TEMPLATE/agentic-story.md`](../../../.github/ISSUE_TEMPLATE/agentic-story.md) implements the following sections:

| Section | Purpose |
|---------|---------|
| **Summary** | One sentence describing the outcome this story delivers. |
| **Context / Motivation** | Why this work is needed; the problem it solves or capability it enables. |
| **Scope** | Exact files to create or modify, interfaces to implement, and invariants to preserve. |
| **Acceptance Criteria** | Specific, testable conditions that must be true when the story is complete. |
| **Negative Constraints** | What this story explicitly does NOT do. Prevents scope creep. |
| **Dependencies** | Other issues or stories that must be completed before this one can start. |
| **File Ownership** | Explicit list of files this story owns exclusively during its execution wave. |

Each section is designed for agent consumption: the agent reads the story, understands exactly what to build, self-verifies against the acceptance criteria, and avoids touching files not listed in scope.

## Customizing the Template

To adapt the template for your team:

1. Edit `.github/ISSUE_TEMPLATE/agentic-story.md` directly in your repository.
2. Keep all seven core sections — agents depend on them for reliable parsing.
3. Add team-specific fields (e.g., **Wave**, **Points**, **Component**) at the end rather than replacing existing sections.
4. Update the `labels:` and `assignees:` front-matter fields to match your GitHub project configuration.

Changes take effect immediately — GitHub reads the file from the repository on every page load.

## Why This Adapter Exists

Other issue-tracker adapters (Jira, Azure DevOps, Linear) require copying a template file and configuring custom fields. GitHub Issues requires neither. This adapter entry exists for consistency with the rest of the `platform-adapters/issue-trackers/` directory so teams evaluating multiple trackers find the same documentation structure everywhere.

The canonical template lives at `.github/ISSUE_TEMPLATE/agentic-story.md` — that file is the single source of truth for the agentic-story format on GitHub.
