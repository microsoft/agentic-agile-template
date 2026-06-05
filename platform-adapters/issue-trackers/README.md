# Issue-Trackers Adapters

An **issue-trackers adapter** provides story templates and backlog conventions for a specific issue tracking system. Agentic-Agile stories have a precise anatomy — scope, file ownership, acceptance criteria, negative constraints — and each issue tracker represents these fields differently. Adapters bridge the gap.

## Available Adapters

| Adapter | Tracker | Status | Template Format |
|---------|---------|--------|-----------------|
| [`github/`](github/) | GitHub Issues | Maintained | `.github/ISSUE_TEMPLATE/agentic-story.md` |

> Additional trackers (Azure DevOps Boards, Jira, Linear, Shortcut) are on the roadmap. To propose or contribute one, see [`../../CONTRIBUTING-AGENTS.md`](../../CONTRIBUTING-AGENTS.md) §"Contributing a New Adapter".

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

### Why Precise Story Format Matters

Agents fail not because of model capability, but because of specification quality. A vague story produces vague output. The agentic-story format enforces precision at the point of story creation — before an agent ever reads it. Acceptance criteria that are executable (run this command, check this output) let the agent self-verify without human intervention. Scope constraints that list exact files prevent agents from refactoring code they were never asked to touch.

## Relationship to Other Layers

Issue-trackers adapters are one of three layers in the platform-adapters system:

- **agent-tools** — configures the AI agent → see [../agent-tools/](../agent-tools/)
- **issue-trackers** (this layer) — provides story templates for your backlog tool
- **ci-cd** — wires up pipeline checks → see [../ci-cd/](../ci-cd/)

For a pre-assembled combination of all three layers, see [../combos/](../combos/).
