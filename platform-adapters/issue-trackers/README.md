# Issue-Trackers Adapters

An **issue-trackers adapter** provides story templates and backlog conventions for a specific issue tracking system. Agentic-Agile stories have a precise anatomy — scope, file ownership, acceptance criteria, negative constraints — and each issue tracker represents these fields differently. Adapters bridge the gap.

## Available Adapters

| Adapter | Tracker | Status | Template Format |
|---------|---------|--------|-----------------|
| [`github/`](github/) | GitHub Issues | Maintained | `.github/ISSUE_TEMPLATE/agentic-story.md` |

> Additional trackers (Azure DevOps Boards, Jira, Linear, Shortcut) are on the roadmap. To propose or contribute one, see [`../../CONTRIBUTING-AGENTS.md`](../../CONTRIBUTING-AGENTS.md) §"Adapter Anatomy" and the `new-adapter-story.md` contributor template.

## Adapter Contents

Each issue-trackers adapter contains:

### `README.md`
Overview of the adapter: which tracker it configures, field mapping from agentic-agile story anatomy to tracker fields, and setup instructions. Explains any tracker-specific limitations (e.g., field length limits, required fields, permission requirements).

### `agentic-story.md` (or tracker-specific template format)
The **story template** in the format natively supported by the tracker. This is the primary artifact of an issue-trackers adapter. The template implements the full agentic-story anatomy described below.

### `field-mapping.md` (optional)
For trackers with rigid schemas (Jira, Azure DevOps), a mapping table showing which tracker field corresponds to each agentic-story section. Useful when customizing the template for teams with existing field conventions.

## The Agentic-Story Format

Every issue-trackers adapter implements the agentic-story anatomy. The core sections are:

| Section | Purpose | Why It Matters to Agents |
|---------|---------|--------------------------|
| **Objective** | One-sentence goal | Agent understands intent without reading context |
| **Scope** | Exact files to create/modify/delete | Agent knows file ownership; no sprawl |
| **Acceptance Criteria** | Verifiable, executable checks | Agent can self-verify completion |
| **Negative Constraints** | What NOT to do | Prevents agent overreach into adjacent files |
| **Implementation Notes** | Hints, patterns, references | Reduces round-trips for common questions |
| **Wave** | Parallel execution group | Orchestrator knows which stories can run concurrently |

The GitHub Issues implementation of this format lives in [`.github/ISSUE_TEMPLATE/agentic-story.md`](../../.github/ISSUE_TEMPLATE/agentic-story.md) and serves as the reference implementation.

### Review-Cycle Field Mapping

Stories may carry optional review-cycle data (see [`docs/agentic-review-cycle.md`](../../docs/agentic-review-cycle.md)). Trackers represent it differently; map the fields as follows.

| Field | GitHub Issues / PRs | Jira | Azure DevOps | Linear |
|-------|---------------------|------|--------------|--------|
| **Stop condition** | "Review Cycle" section of the story body | Custom text field or description section | Custom text field or Description section | Description section |
| **Round count** | Rows in the PR review-cycle log (or `review-round-N` label) | Custom number field | Custom integer field or tag | Number property or label (`review-round-N`) |
| **Finding classes** | Story section; recurring classes as labels | Custom multi-select or labels | Tags or custom picklist | Labels |
| **Review log** | Review-Cycle Log table in the PR description | Comment or custom text field linking the PR log | Work-item Discussion or linked PR log | Comment linking the PR log |

Whatever the tracker, the log itself lives in the PR; the tracker holds a summary and a link.

### Why Precise Story Format Matters

Agents fail not because of model capability, but because of specification quality. A vague story produces vague output. The agentic-story format enforces precision at the point of story creation — before an agent ever reads it. Acceptance criteria that are executable (run this command, check this output) let the agent self-verify without human intervention. Scope constraints that list exact files prevent agents from refactoring code they were never asked to touch.

## Relationship to Other Layers

Issue-trackers adapters are one of three layers in the platform-adapters system:

- **agent-tools** — configures the AI agent → see [../agent-tools/](../agent-tools/)
- **issue-trackers** (this layer) — provides story templates for your backlog tool
- **ci-cd** — wires up pipeline checks → see [../ci-cd/](../ci-cd/)

For a pre-assembled combination of all three layers, see [../combos/](../combos/).
