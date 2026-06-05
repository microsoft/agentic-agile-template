# Multi-Platform Generalization — Phase 2: Agent Tools Layer

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Populate the `platform-adapters/` directory with all agent tool adapters, the GitHub issue tracker adapter, initial combo quickstart files, and remove the root `CLAUDE.md` now that its content has migrated.

**Architecture:** Each agent tool adapter follows the three-file anatomy (README.md, target-named template file, quickstart.md). The issue tracker adapter links to existing `.github/ISSUE_TEMPLATE/` rather than duplicating content. Combo files document tested stack combinations with status tiers.

**Tech Stack:** Markdown, GitHub CLI (`gh`), Git

**Git Continuity:** `git push` steps are embedded after Tasks 1, 3, 7, and 10 to ensure progress is preserved against browser/session interruptions. Executors must not skip these push steps.

---

## Task 0: Create GitHub Issues for All Phase 2 Tasks

**Purpose:** Establish the ticketed backlog before any file work begins. Issues are malleable — specs can be amended during planning, sub-issues created during decomposition, and execution modifications documented as comments.

**Step 1: Verify `gh` CLI is authenticated**

Run:
```bash
gh auth status
```
Expected: Shows authenticated user and repo access.

**Step 2: Create issues for Tasks 1–10**

Run each command below. Each issue references the design document and is labeled as part of the multi-platform generalization project.

```bash
gh issue create \
  --title "feat: Create platform-adapters/ directory skeleton with READMEs" \
  --label "enhancement" \
  --body "## Summary

Create the \`platform-adapters/\` directory structure with meaningful README.md files at every level explaining the three-layer adapter system.

## Context / Motivation

Phase 2 populates the adapter layer designed in \`docs/history/2026-06-04-multi-platform-generalization-design.md\`. The directory skeleton provides the navigational structure before individual adapters are added.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/README.md\` — overview of the three-layer adapter system
- \`platform-adapters/agent-tools/README.md\` — lists all adapters, explains selection
- \`platform-adapters/issue-trackers/README.md\` — lists trackers, explains adapter contents
- \`platform-adapters/ci-cd/README.md\` — explains CI/CD layer is planned for v2
- \`platform-adapters/combos/README.md\` — explains combo format, status tiers, filename convention

### Invariants to Preserve

- No existing files modified
- README.md exists at every directory level per design

## Acceptance Criteria

- [ ] All five README.md files exist
- [ ] Each README has meaningful content (not empty stubs)
- [ ] \`platform-adapters/README.md\` links to all three layers + combos
- [ ] \`platform-adapters/combos/README.md\` defines status tiers (Maintained/Community/Stub)
- [ ] \`platform-adapters/combos/README.md\` documents filename convention

## Negative Constraints

- Does NOT create adapter subdirectories (Tasks 2–7)
- Does NOT create combo files (Task 10)

## Dependencies

- Phase 1 must be complete (AGENTS.md references platform-adapters/)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/README.md\` | ✅ | New |
| \`platform-adapters/issue-trackers/README.md\` | ✅ | New |
| \`platform-adapters/ci-cd/README.md\` | ✅ | New |
| \`platform-adapters/combos/README.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create Claude agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the Claude adapter at \`platform-adapters/agent-tools/claude/\` with README.md, CLAUDE.md template, and quickstart.md.

## Context / Motivation

Claude (Anthropic) uses \`CLAUDE.md\` as its project context file. This adapter migrates the existing root \`CLAUDE.md\` template content into the platform-adapters structure.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Platform Adapter Anatomy

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/claude/README.md\` — adapter description
- \`platform-adapters/agent-tools/claude/CLAUDE.md\` — full template (verbatim from current root CLAUDE.md)
- \`platform-adapters/agent-tools/claude/quickstart.md\` — placement instructions

### Invariants to Preserve

- Root \`CLAUDE.md\` remains unchanged (removed in Task 9)
- Adapter follows standard anatomy

## Acceptance Criteria

- [ ] All three files exist in \`platform-adapters/agent-tools/claude/\`
- [ ] \`CLAUDE.md\` contains the full template content
- [ ] \`quickstart.md\` specifies target path as repo root \`CLAUDE.md\`
- [ ] \`README.md\` explains Claude and when to use this adapter

## Negative Constraints

- Does NOT remove root \`CLAUDE.md\` (Task 9)
- Does NOT modify other adapters

## Dependencies

- Task 1 (directory skeleton must exist)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/claude/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/claude/CLAUDE.md\` | ✅ | New |
| \`platform-adapters/agent-tools/claude/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create GitHub Copilot agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the GitHub Copilot adapter at \`platform-adapters/agent-tools/github-copilot/\` with README.md, copilot-instructions.md template, and quickstart.md.

## Context / Motivation

GitHub Copilot reads \`.github/copilot-instructions.md\` for project context. This adapter stores the full template content while the \`.github/\` file is a stub (converted in Phase 1).

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\`

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/github-copilot/README.md\`
- \`platform-adapters/agent-tools/github-copilot/copilot-instructions.md\`
- \`platform-adapters/agent-tools/github-copilot/quickstart.md\`

## Acceptance Criteria

- [ ] All three files exist
- [ ] \`copilot-instructions.md\` contains full template content
- [ ] \`quickstart.md\` specifies target path as \`.github/copilot-instructions.md\`

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/github-copilot/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/github-copilot/copilot-instructions.md\` | ✅ | New |
| \`platform-adapters/agent-tools/github-copilot/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create Cursor agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the Cursor adapter at \`platform-adapters/agent-tools/cursor/\`. Research and verify the correct target filename from Cursor documentation before creating.

## Context / Motivation

Cursor uses a rules file for project context. The current best-known filename is \`.cursorrules\` but this must be confirmed from official documentation.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/cursor/README.md\`
- \`platform-adapters/agent-tools/cursor/.cursorrules\` (verify filename)
- \`platform-adapters/agent-tools/cursor/quickstart.md\`

## Acceptance Criteria

- [ ] All three files exist
- [ ] Target filename verified from official Cursor documentation
- [ ] Template content adapts the methodology for Cursor's format

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/cursor/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/cursor/.cursorrules\` | ✅ | New (verify name) |
| \`platform-adapters/agent-tools/cursor/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create Windsurf agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the Windsurf adapter at \`platform-adapters/agent-tools/windsurf/\`. Research and verify the correct target filename from Windsurf documentation before creating.

## Context / Motivation

Windsurf uses a rules file for project context. The current best-known filename is \`.windsurfrules\` but this must be confirmed from official documentation.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/windsurf/README.md\`
- \`platform-adapters/agent-tools/windsurf/.windsurfrules\` (verify filename)
- \`platform-adapters/agent-tools/windsurf/quickstart.md\`

## Acceptance Criteria

- [ ] All three files exist
- [ ] Target filename verified from official Windsurf documentation
- [ ] Template content adapts the methodology for Windsurf's format

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/windsurf/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/windsurf/.windsurfrules\` | ✅ | New (verify name) |
| \`platform-adapters/agent-tools/windsurf/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create Cline agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the Cline adapter at \`platform-adapters/agent-tools/cline/\`. Research and verify the correct target filename from Cline documentation before creating.

## Context / Motivation

Cline uses a rules file for project context. The current best-known filename is \`.clinerules\` but this must be confirmed from official documentation.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/cline/README.md\`
- \`platform-adapters/agent-tools/cline/.clinerules\` (verify filename)
- \`platform-adapters/agent-tools/cline/quickstart.md\`

## Acceptance Criteria

- [ ] All three files exist
- [ ] Target filename verified from official Cline documentation
- [ ] Template content adapts the methodology for Cline's format

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/cline/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/cline/.clinerules\` | ✅ | New (verify name) |
| \`platform-adapters/agent-tools/cline/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create aider agent tool adapter" \
  --label "enhancement" \
  --body "## Summary

Create the aider adapter at \`platform-adapters/agent-tools/aider/\`. Research and verify the correct target filename from aider documentation before creating.

## Context / Motivation

aider uses a conventions file for project context. The current best-known filename is \`CONVENTIONS.md\` but this must be confirmed from official documentation.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/agent-tools/aider/README.md\`
- \`platform-adapters/agent-tools/aider/CONVENTIONS.md\` (verify filename)
- \`platform-adapters/agent-tools/aider/quickstart.md\`

## Acceptance Criteria

- [ ] All three files exist
- [ ] Target filename verified from official aider documentation
- [ ] Template content adapts the methodology for aider's format

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/agent-tools/aider/README.md\` | ✅ | New |
| \`platform-adapters/agent-tools/aider/CONVENTIONS.md\` | ✅ | New (verify name) |
| \`platform-adapters/agent-tools/aider/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Create GitHub issue tracker adapter" \
  --label "enhancement" \
  --body "## Summary

Create the GitHub issue tracker adapter at \`platform-adapters/issue-trackers/github/\` that links to the existing \`.github/ISSUE_TEMPLATE/\` directory.

## Context / Motivation

The GitHub issue tracker adapter does not duplicate templates — it explains how to use the existing \`.github/ISSUE_TEMPLATE/agentic-story.md\` that GitHub auto-discovers.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/issue-trackers/github/README.md\`
- \`platform-adapters/issue-trackers/github/quickstart.md\`

## Acceptance Criteria

- [ ] Both files exist
- [ ] \`quickstart.md\` points to \`.github/ISSUE_TEMPLATE/agentic-story.md\`
- [ ] No files are duplicated — adapter only links/references

## Dependencies

- Task 1 (directory skeleton)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/issue-trackers/github/README.md\` | ✅ | New |
| \`platform-adapters/issue-trackers/github/quickstart.md\` | ✅ | New |"
```

```bash
gh issue create \
  --title "feat: Remove root CLAUDE.md — content migrated to platform adapter" \
  --label "enhancement" \
  --body "## Summary

Remove the root \`CLAUDE.md\` file. Its content has been migrated to \`platform-adapters/agent-tools/claude/CLAUDE.md\`. \`AGENTS.md\` is now the universal entry point.

## Context / Motivation

With Phase 2 complete, the root CLAUDE.md is redundant. The design specifies that AGENTS.md replaces it as the entry point, and the full template content lives in the adapter directory.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`CLAUDE.md\` — remove (git rm)

## Acceptance Criteria

- [ ] \`CLAUDE.md\` does not exist at repo root
- [ ] \`platform-adapters/agent-tools/claude/CLAUDE.md\` contains the migrated content
- [ ] \`AGENTS.md\` is the sole root-level agent entry point

## Negative Constraints

- Does NOT modify \`AGENTS.md\`
- Does NOT modify any adapter files

## Dependencies

- Task 2 (Claude adapter must exist with migrated content)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`CLAUDE.md\` | ✅ | Removed |"
```

```bash
gh issue create \
  --title "feat: Add initial combo quickstart files (claude, copilot, cursor)" \
  --label "enhancement" \
  --body "## Summary

Create three initial quickstart combo files documenting tested stack combinations.

## Context / Motivation

Combo files help users who know their stack find a quickstart guide quickly. Initial combos cover the most common GitHub-based stacks.

Part of: Multi-Platform Generalization (Phase 2: Agent Tools Layer)

## Scope

### Files to Create or Modify

- \`platform-adapters/combos/claude-github-github-actions.md\`
- \`platform-adapters/combos/copilot-github-github-actions.md\`
- \`platform-adapters/combos/cursor-github-github-actions.md\`

## Acceptance Criteria

- [ ] All three combo files exist
- [ ] Each follows the combo format (Stack, Status, Adapters used, Notes)
- [ ] Filenames follow convention \`<agent>-<tracker>-<cicd>.md\`
- [ ] All referenced adapter directories exist

## Dependencies

- Tasks 2, 3, 4, 8 (referenced adapters must exist)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`platform-adapters/combos/claude-github-github-actions.md\` | ✅ | New |
| \`platform-adapters/combos/copilot-github-github-actions.md\` | ✅ | New |
| \`platform-adapters/combos/cursor-github-github-actions.md\` | ✅ | New |"
```

**Step 3: Record issue numbers**

Run:
```bash
gh issue list --limit 20 --state open --json number,title
```

Save the output — you'll reference these issue numbers in commit messages for Tasks 1–10.

**Step 4: Commit**

No file changes to commit for Task 0 — issues live in GitHub, not the repo.

---

## Task 1: Create platform-adapters/ Directory Skeleton with READMEs

**Files:**
- Create: `platform-adapters/README.md`
- Create: `platform-adapters/agent-tools/README.md`
- Create: `platform-adapters/issue-trackers/README.md`
- Create: `platform-adapters/ci-cd/README.md`
- Create: `platform-adapters/combos/README.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Create the directories and files (GREEN)**

```bash
mkdir -p platform-adapters/agent-tools platform-adapters/issue-trackers platform-adapters/ci-cd platform-adapters/combos
```

Create `platform-adapters/README.md` with this exact content:

```markdown
# Platform Adapters

This directory contains the three-layer adapter system that makes the Agentic-Agile template work with any combination of development tools.

## Architecture

```
platform-adapters/
├── agent-tools/        ← AI coding tool context files (one per tool)
├── issue-trackers/     ← Issue tracker configurations (one per platform)
├── ci-cd/              ← CI/CD pipeline templates (one per system)
└── combos/             ← Quickstart guides for specific stack combinations
```

Each layer is **independent** — choosing a specific agent tool does not constrain your issue tracker or CI/CD choice.

## How It Works

1. **During onboarding**, the guided dialogue in `AGENTS.md` asks which tools your team uses.
2. **The onboarding agent** copies adapter template files to their target paths in your new project.
3. **Each adapter's `quickstart.md`** specifies exactly where files go and any tool-specific setup.

## Layers

### [Agent Tools](agent-tools/)

Context files that tell AI coding agents about your project — conventions, architecture, workflow. Each tool has its own filename convention (e.g., `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`).

### [Issue Trackers](issue-trackers/)

Issue template configurations for different platforms. Some adapters link to existing configurations (like GitHub's `.github/ISSUE_TEMPLATE/`) rather than duplicating them.

### [CI/CD](ci-cd/)

Pipeline and workflow configurations for continuous integration and deployment systems. Planned for v2.

### [Combos](combos/)

Quickstart guides for specific stack combinations (e.g., "Claude + GitHub Issues + GitHub Actions"). These help users who know their stack find the right setup path quickly.

## Adding a New Adapter

See [`CONTRIBUTING-AGENTS.md`](../CONTRIBUTING-AGENTS.md) for the contribution workflow, or use the issue template at [`.github/contributor-templates/new-adapter-story.md`](../.github/contributor-templates/new-adapter-story.md).

Every adapter directory follows this anatomy:

```
platform-adapters/<layer>/<adapter-name>/
├── README.md              ← what this adapter is (1 paragraph)
├── <target-filename>      ← named after the actual target file in derived repos
└── quickstart.md          ← where to place it, tool-specific setup notes
```
```

Create `platform-adapters/agent-tools/README.md` with this exact content:

```markdown
# Agent Tools Adapters

Context files that provide AI coding agents with project-specific information — architecture, conventions, workflow, and constraints.

## Available Adapters

| Adapter | Target File | Tool |
|---------|-------------|------|
| [claude/](claude/) | `CLAUDE.md` (repo root) | Claude (Anthropic) |
| [github-copilot/](github-copilot/) | `.github/copilot-instructions.md` | GitHub Copilot |
| [cursor/](cursor/) | `.cursorrules` (repo root) | Cursor |
| [windsurf/](windsurf/) | `.windsurfrules` (repo root) | Windsurf |
| [cline/](cline/) | `.clinerules` (repo root) | Cline |
| [aider/](aider/) | `CONVENTIONS.md` (repo root) | aider |

> **Note:** Target filenames listed above are best-known conventions as of this writing. Each adapter's `quickstart.md` contains a research note to verify the current filename from official documentation, as tool authors may change conventions between versions.

## How to Choose

- **You know which tool your team uses** → go directly to that adapter directory.
- **You use multiple tools** → apply multiple adapters. They don't conflict — each produces a different file at a different path.
- **Your tool isn't listed** → scaffold a new adapter using the template at [`.github/contributor-templates/new-adapter-story.md`](../../.github/contributor-templates/new-adapter-story.md).

## What Each Adapter Contains

Every adapter directory has three files:

1. **`README.md`** — One paragraph explaining the tool and when to use this adapter.
2. **`<target-filename>`** — The complete template file, named after where it will live in derived repos. Ready to customize with your project details.
3. **`quickstart.md`** — Exact target path, placement instructions, and tool-specific configuration notes.
```

Create `platform-adapters/issue-trackers/README.md` with this exact content:

```markdown
# Issue Tracker Adapters

Configurations for structuring work items (issues, stories, tickets) across different project management platforms.

## Available Adapters

| Adapter | Platform | Type |
|---------|----------|------|
| [github/](github/) | GitHub Issues | Links to existing `.github/ISSUE_TEMPLATE/` |

## Planned (v1+)

| Adapter | Platform | Status |
|---------|----------|--------|
| azure-devops/ | Azure DevOps | Scaffolded — contributions welcome |
| jira/ | JIRA / Atlassian | Stub — contributions welcome |

## What Each Adapter Contains

Issue tracker adapters explain how to configure the Agentic-Agile story format for a specific platform:

- **`README.md`** — What this tracker adapter provides and how it maps to the methodology.
- **`quickstart.md`** — How to apply the configuration. For some platforms (like GitHub), this means pointing to existing auto-discovered files rather than creating new ones.

## The Agentic-Story Format

All issue tracker adapters implement the same story structure:

- **Summary** — one sentence describing the work
- **Context / Motivation** — why this work matters
- **Scope** — files to create/modify, interfaces to implement, invariants to preserve
- **Acceptance Criteria** — checkboxes defining "done"
- **Negative Constraints** — what is explicitly out of scope
- **Dependencies** — what must be complete before this starts
- **File Ownership** — which files this story owns exclusively

The format ensures agents receive unambiguous specifications regardless of which platform hosts the issue.
```

Create `platform-adapters/ci-cd/README.md` with this exact content:

```markdown
# CI/CD Adapters

Pipeline and workflow configurations for continuous integration and deployment systems.

## Status: Planned for v2

The CI/CD adapter layer is planned for the v2 release. The architecture is defined, but adapter content has not yet been created.

## What's Coming

| Adapter | Platform | Status |
|---------|----------|--------|
| github-actions/ | GitHub Actions | Planned — will link to existing `.github/workflows/` |
| azure-pipelines/ | Azure Pipelines | Planned |

## What CI/CD Adapters Will Contain

Each CI/CD adapter will follow the standard anatomy:

- **`README.md`** — What this CI/CD system provides and how it integrates with the methodology.
- **Pipeline/workflow template files** — Ready-to-use configurations for common Agentic-Agile workflows (story validation, PR checks, wave gating).
- **`quickstart.md`** — Where to place pipeline files, required secrets/variables, and platform-specific setup.

## Contributing

If you'd like to contribute a CI/CD adapter ahead of the v2 timeline, use the issue template at [`.github/contributor-templates/new-adapter-story.md`](../../.github/contributor-templates/new-adapter-story.md). Community contributions are welcome for any platform.
```

Create `platform-adapters/combos/README.md` with this exact content:

```markdown
# Quickstart Combos

Pre-documented stack combinations that help users get started quickly when they already know which tools they're using.

## Available Combos

| Combo | Agent Tool | Issue Tracker | CI/CD | Status |
|-------|-----------|---------------|-------|--------|
| [claude-github-github-actions.md](claude-github-github-actions.md) | Claude | GitHub Issues | GitHub Actions | Maintained |
| [copilot-github-github-actions.md](copilot-github-github-actions.md) | GitHub Copilot | GitHub Issues | GitHub Actions | Maintained |
| [cursor-github-github-actions.md](cursor-github-github-actions.md) | Cursor | GitHub Issues | GitHub Actions | Community |

## Filename Convention

Combo files follow the naming pattern:

```
<agent-tool>-<issue-tracker>-<ci-cd>.md
```

Examples:
- `claude-github-github-actions.md`
- `cursor-jira-azure-pipelines.md`
- `multi-github-github-actions.md` (for multi-tool setups)

## Status Tiers

| Tier | Meaning | Who Maintains |
|------|---------|---------------|
| **Maintained** | Actively tested and updated by the core team | Core team |
| **Community** | Contributed and tested by community members | Community contributors |
| **Stub** | Scaffolded with basic structure, needs contributions | Anyone welcome |

## Combo File Format

Every combo file contains these sections:

- **Stack** — `<agent tool> · <issue tracker> · <CI/CD>`
- **Status** — one of: Maintained, Community, Stub
- **Adapters used** — links to each adapter directory
- **Quick Setup** — abbreviated setup steps referencing each adapter's quickstart.md
- **Notes** — any combination-specific considerations

## Adding a New Combo

Use the issue template at [`.github/contributor-templates/new-combo-story.md`](../../.github/contributor-templates/new-combo-story.md) to propose a new combo. All referenced adapter directories must exist before a combo can be created.
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/README.md platform-adapters/agent-tools/README.md platform-adapters/issue-trackers/README.md platform-adapters/ci-cd/README.md platform-adapters/combos/README.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All five files show `PASS`

Run:
```bash
grep -c 'agent-tools\|issue-trackers\|ci-cd\|combos' platform-adapters/README.md
```
Expected: `8` or more (confirms all layers referenced)

Run:
```bash
grep -c 'Maintained\|Community\|Stub' platform-adapters/combos/README.md
```
Expected: `6` or more (status tiers defined)

**Step 4: Commit**

```bash
git add platform-adapters/
git commit -m "feat: create platform-adapters directory skeleton with layer READMEs

Five README.md files establishing the three-layer adapter architecture:
agent-tools, issue-trackers, ci-cd, and combos index.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

**Step 5: Push to remote (git continuity safeguard)**

```bash
git push origin feat/multi-platform-phase2
```

---

## Task 2: Create Claude Adapter

**Files:**
- Create: `platform-adapters/agent-tools/claude/README.md`
- Create: `platform-adapters/agent-tools/claude/CLAUDE.md`
- Create: `platform-adapters/agent-tools/claude/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/claude && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Create the directory and files (GREEN)**

```bash
mkdir -p platform-adapters/agent-tools/claude
```

Create `platform-adapters/agent-tools/claude/README.md` with this exact content:

```markdown
# Claude Adapter

[Claude](https://claude.ai) is Anthropic's AI coding assistant. It reads a `CLAUDE.md` file at the repository root for project context — architecture, conventions, workflow, and constraints. This adapter provides the Agentic-Agile methodology template formatted for Claude's context file convention.
```

Create `platform-adapters/agent-tools/claude/CLAUDE.md` with the **exact** content from the current root `CLAUDE.md` file (315 lines). The executing agent must read `/workspaces/agentic-agile-template/CLAUDE.md` and copy it verbatim:

```markdown
# Agent Context — [Your Project Name]

<!--
  WHAT IS THIS FILE?

  This is an agent context file. It provides AI coding agents (GitHub Copilot,
  Claude, Cursor, or any LLM-based development tool) with the information they
  need to work effectively in your repository.

  Think of it as onboarding documentation, but optimized for agents: structured,
  explicit, and maintained alongside your code.

  WHY DOES IT MATTER?

  Without an agent context file, every agent session starts from zero. The agent
  must infer your conventions, guess your architecture, and hope its assumptions
  match yours. With a well-maintained context file, agents produce output that
  fits your project from the first interaction.

  HOW TO USE IT:

  1. Replace all placeholder content (marked with [brackets] or <!-- comments -->)
     with your project's actual information.
  2. Delete sections you don't need. Not every project requires every section.
  3. Keep it updated. An outdated context file is worse than none because agents
     will follow stale instructions confidently.
  4. Start small. You can always add sections as your project grows.

  NAMING:

  - CLAUDE.md (convention used by Claude/Anthropic-based agents)
  - .github/copilot-instructions.md (GitHub Copilot-specific, shorter subset)
  - AGENTS.md, CONTEXT.md (alternatives used by some teams)

  You can maintain multiple files: a comprehensive CLAUDE.md and a shorter
  copilot-instructions.md that references it.
-->

---

## Project Purpose

<!--
  2-3 sentences describing what this project does, who it's for, and what
  problem it solves. This helps agents understand the domain and make
  appropriate design decisions.

  Example:
  "A REST API for inventory management used by warehouse operations teams.
  Built with Go and PostgreSQL. Handles ~10K requests/minute in production.
  Reliability and data consistency are more important than feature velocity."
-->

[Describe your project here]

**Primary language:** [e.g., TypeScript, Python, Go]
**Framework:** [e.g., Express, FastAPI, Gin]
**Key dependencies:** [e.g., PostgreSQL, Redis, RabbitMQ]

---

## Repository Structure

<!--
  Map out your project layout. Agents use this to understand where to find
  things and where to put new code. Be explicit about conventions.
-->

```
project-root/
├── src/                    # Application source code
│   ├── api/                # HTTP handlers / route definitions
│   ├── services/           # Business logic layer
│   ├── models/             # Data models / types
│   ├── repositories/       # Data access layer
│   └── utils/              # Shared utilities
├── tests/                  # Test files (mirrors src/ structure)
├── docs/                   # Project documentation
├── scripts/                # Build, deploy, and utility scripts
├── .github/                # GitHub configuration (workflows, templates)
├── CLAUDE.md               # This file
├── STYLE.md                # Code and documentation style guide
└── README.md               # Project overview
```

<!--
  Customize the tree above to match your project. Key things to include:
  - Where source code lives
  - Where tests live (and how they map to source)
  - Where configuration files are
  - Any generated directories to avoid modifying
-->

---

## Development Process

<!--
  Describe how work flows from idea to merged code. Agents use this to
  understand your workflow expectations: how to structure PRs, when to
  run tests, what review looks like.

  The process below is an Agentic-Agile template. Adapt it to your team.
-->

### Workflow

```
Plan → Issue → Implement → Review → Merge → Docs
```

| Phase | Description |
|-------|-------------|
| **Plan** | Define what to build. Identify scope, dependencies, and file ownership. |
| **Issue** | Create a GitHub Issue with structured scope, acceptance criteria, and negative constraints. |
| **Implement** | Build the feature in a feature branch. Follow coding conventions. Write tests. |
| **Review** | Submit a PR. Every PR receives review that checks correctness, test coverage, and convention compliance. |
| **Merge** | Merge to the integration branch after review approval. |
| **Docs** | Update documentation affected by the change. Close the issue. |

### Branch Strategy

- **`main`** — stable, production-ready code
- **Feature branches** — one per issue, branched from `main`
  - Naming: `[type]/[short-description]` (e.g., `feat/user-auth`, `fix/null-response`)
- **Merge flow:** feature → `main` (via reviewed PR)

### Review Standards

- Every PR receives at least one review.
- Review findings must reach a terminal state: `fixed`, `accepted` (with justification), or `deferred` (tracked as follow-up issue).
- Agents can be used for implementation, but review remains a human responsibility until trust is established through measured outcomes.

---

## Coding Conventions

<!--
  Explicit conventions help agents write code that fits your project without
  guessing. Be specific. "Follow best practices" is not actionable.
-->

### General Rules

- [e.g., "All functions must have type annotations"]
- [e.g., "Use dependency injection for service classes"]
- [e.g., "No magic numbers. Define constants with descriptive names."]
- [e.g., "Prefer composition over inheritance"]
- [e.g., "All API endpoints return consistent response shapes: { data, error, metadata }"]

### Error Handling

- [e.g., "Use typed error classes, not generic Error"]
- [e.g., "Never swallow exceptions silently"]
- [e.g., "Log errors at the boundary, not at every level"]
- [e.g., "Return meaningful HTTP status codes with error details"]

### Logging

- [e.g., "Use structured logging (JSON format)"]
- [e.g., "Include request ID in all log entries"]
- [e.g., "Log levels: debug for development, info for operations, error for failures"]

### Security

- Never commit secrets or credentials.
- Use environment variables for configuration.
- Validate and sanitize all external input.
- [Add project-specific security requirements]

---

## Testing Strategy

<!--
  Tell agents how to write tests for your project: what framework, what
  conventions, what level of coverage you expect.
-->

### Framework and Tools

- **Test framework:** [e.g., Jest, pytest, Go testing]
- **Assertion library:** [e.g., built-in, Chai, testify]
- **Mocking:** [e.g., jest.mock, unittest.mock, gomock]
- **Coverage tool:** [e.g., Istanbul/nyc, coverage.py, go cover]

### Test Organization

- [e.g., "Test files live alongside source files: `user-service.test.ts` next to `user-service.ts`"]
- [e.g., "Integration tests in `tests/integration/`, unit tests alongside source"]
- [e.g., "Test fixtures in `tests/fixtures/`"]

### Test Naming

- [e.g., "Describe blocks match the class/module name"]
- [e.g., "Test names describe behavior: `should return 404 when user not found`"]

### Coverage Expectations

- [e.g., "All public functions must have at least one test"]
- [e.g., "Target 80% line coverage"]
- [e.g., "Critical paths (auth, payments) require 95%+ coverage"]

### Running Tests

```bash
# Run all tests
[e.g., npm test, pytest, go test ./...]

# Run with coverage
[e.g., npm run test:coverage, pytest --cov, go test -cover ./...]

# Run a specific test file
[e.g., npm test -- path/to/test, pytest path/to/test.py]
```

---

## Documentation Maintenance

<!--
  Define which documents exist, and when each should be updated.
  This prevents documentation from drifting out of sync with code.
-->

| Document | Update When |
|----------|-------------|
| `README.md` | Project scope, setup, or usage changes |
| `CLAUDE.md` | Process, conventions, or structure changes |
| `STYLE.md` | Style conventions change |
| `CONTRIBUTING.md` | Contribution process changes |
| API docs | Endpoints added, modified, or removed |
| [Your doc] | [Your trigger] |

---

## Parallelization Rules

<!--
  If your team uses multiple agents or humans working in parallel, these rules
  prevent merge conflicts and coordination failures. Adapt to your workflow.
-->

### File Ownership

Every story (work unit) explicitly declares which files it owns. No two stories in the same wave (parallel execution batch) should touch the same file.

### Wave Structure

Work executes in waves. Each wave is a set of stories that can proceed in parallel because they have no file overlap and no runtime dependencies on each other.

```
Wave 1: [Story A: owns src/auth/] [Story B: owns src/api/users/]
         ↓ review gate ↓
Wave 2: [Story C: owns src/api/orders/] [Story D: owns tests/integration/]
         ↓ review gate ↓
Wave 3: [Story E: owns docs/]
```

### Dependency Gates

- A story cannot start until all stories it depends on are complete and merged.
- Review gates between waves ensure quality before dependent work begins.
- Cross-cutting concerns (e.g., shared types, configuration) are resolved in earlier waves.

### Conflict Prevention

- If two stories must touch the same file, they go in sequential waves, not parallel.
- Shared interfaces are defined in a dedicated story that completes before stories that implement those interfaces.

---

## Validation Gates

<!--
  Define the checklist that every piece of work must satisfy before it's
  considered complete. Agents and humans both use this as a quality gate.
-->

Before a PR is considered ready for merge:

- [ ] **Tests pass** — all existing and new tests pass
- [ ] **Linter clean** — no linter warnings or errors
- [ ] **Types check** — no type errors (for typed languages)
- [ ] **Documentation updated** — affected docs are current
- [ ] **No unrelated changes** — PR is scoped to the issue
- [ ] **Acceptance criteria met** — all criteria from the issue are satisfied
- [ ] **Negative constraints respected** — nothing out-of-scope was modified
- [ ] **Review complete** — at least one review with all findings resolved

---

## Build and Run

<!--
  Include commands for building, running, and testing the project.
  Agents use these to verify their changes work.
-->

```bash
# Install dependencies
[e.g., npm install, pip install -r requirements.txt, go mod download]

# Build
[e.g., npm run build, make build, go build ./...]

# Run locally
[e.g., npm run dev, python main.py, go run .]

# Run tests
[e.g., npm test, pytest, go test ./...]

# Lint
[e.g., npm run lint, flake8, golangci-lint run]
```
```

Create `platform-adapters/agent-tools/claude/quickstart.md` with this exact content:

```markdown
# Claude Adapter — Quickstart

## Target Path

Place the template file at your **repository root**:

```
your-project/
└── CLAUDE.md
```

## Setup Steps

1. Copy `CLAUDE.md` from this adapter directory to your project root.
2. Replace all placeholder content (marked with `[brackets]` or `<!-- comments -->`) with your project's actual information.
3. Update the project name in the heading.
4. Delete sections you don't need — not every project requires every section.
5. Commit the customized file.

## How Claude Discovers This File

Claude automatically reads `CLAUDE.md` at the repository root when starting a session. No additional configuration is needed — the file's presence at the root is sufficient.

## Configuration Notes

- **File must be named exactly `CLAUDE.md`** at the repo root for automatic discovery.
- Keep the file under ~500 lines for optimal context utilization.
- The file supports standard Markdown formatting.
- Update it whenever project conventions, architecture, or workflow change — an outdated context file is worse than none.

## Multiple Agent Tools

If your team uses Claude alongside other tools (e.g., GitHub Copilot), you can apply both adapters. They produce different files at different paths and don't conflict:
- Claude: `CLAUDE.md` (repo root)
- Copilot: `.github/copilot-instructions.md`
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/claude/README.md platform-adapters/agent-tools/claude/CLAUDE.md platform-adapters/agent-tools/claude/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c '## Project Purpose\|## Repository Structure\|## Development Process\|## Coding Conventions\|## Testing Strategy' platform-adapters/agent-tools/claude/CLAUDE.md
```
Expected: `5` (all major sections from original CLAUDE.md present)

Run:
```bash
grep 'CLAUDE.md' platform-adapters/agent-tools/claude/quickstart.md | head -1
```
Expected: Line containing `CLAUDE.md` (target path specified)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/claude/
git commit -m "feat: create Claude agent tool adapter

Migrates CLAUDE.md template content to platform-adapters/agent-tools/claude/
with README, full template file, and quickstart placement guide.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 3: Create GitHub Copilot Adapter

**Files:**
- Create: `platform-adapters/agent-tools/github-copilot/README.md`
- Create: `platform-adapters/agent-tools/github-copilot/copilot-instructions.md`
- Create: `platform-adapters/agent-tools/github-copilot/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/github-copilot && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Create the directory and files (GREEN)**

```bash
mkdir -p platform-adapters/agent-tools/github-copilot
```

Create `platform-adapters/agent-tools/github-copilot/README.md` with this exact content:

```markdown
# GitHub Copilot Adapter

[GitHub Copilot](https://github.com/features/copilot) is GitHub's AI coding assistant. It reads a `copilot-instructions.md` file at `.github/copilot-instructions.md` for project-specific context — coding style, testing approach, file structure, and key conventions. This adapter provides the Agentic-Agile methodology template formatted for Copilot's shorter, more focused context format.
```

Create `platform-adapters/agent-tools/github-copilot/copilot-instructions.md` with the **exact** content from the current `.github/copilot-instructions.md` file (58 lines). The executing agent must read `/workspaces/agentic-agile-template/.github/copilot-instructions.md` and copy the original pre-stub content verbatim:

```markdown
# Copilot Instructions

> This file provides GitHub Copilot with project-specific context. For the full development process, see `CLAUDE.md` in the repository root.

## Project Description

<!-- Replace this with a 2-3 sentence description of your project. -->
<!-- Example: "A REST API for task management built with Node.js and Express. Uses PostgreSQL for storage and JWT for authentication." -->

[Describe your project here]

## Coding Style

<!-- Define the conventions Copilot should follow when generating code. -->

- **Language:** [e.g., TypeScript, Python, Go]
- **Formatting:** [e.g., Prettier with default config, Black for Python]
- **Naming:** [e.g., camelCase for variables, PascalCase for classes]
- **Imports:** [e.g., absolute imports only, group by stdlib/third-party/local]
- **Error handling:** [e.g., always use typed errors, never swallow exceptions]

## Testing Approach

<!-- Describe how tests should be written and organized. -->

- **Framework:** [e.g., Jest, pytest, Go testing]
- **Location:** [e.g., `__tests__/` directories alongside source, `tests/` at root]
- **Naming:** [e.g., `test_<function_name>`, `describe/it` blocks]
- **Coverage expectations:** [e.g., all public functions must have tests]

## File Structure

<!-- Describe the project layout so Copilot understands where things belong. -->

```
project-root/
├── src/              # Application source code
├── tests/            # Test files
├── docs/             # Documentation
├── .github/          # GitHub configuration
└── ...
```

## Key Conventions

<!-- List project-specific conventions that affect code generation. -->

- [e.g., "Use dependency injection for all service classes"]
- [e.g., "All API endpoints return JSON with {data, error, metadata} shape"]
- [e.g., "Database queries go through the repository layer, never called directly"]

## What Not to Do

<!-- Explicit anti-patterns to avoid. -->

- [e.g., "Do not use `any` type in TypeScript"]
- [e.g., "Do not commit secrets or credentials"]
- [e.g., "Do not add dependencies without documenting the reason"]
```

Create `platform-adapters/agent-tools/github-copilot/quickstart.md` with this exact content:

```markdown
# GitHub Copilot Adapter — Quickstart

## Target Path

Place the template file at:

```
your-project/
└── .github/
    └── copilot-instructions.md
```

## Setup Steps

1. Ensure your project has a `.github/` directory (create it if needed: `mkdir -p .github`).
2. Copy `copilot-instructions.md` from this adapter directory to `.github/copilot-instructions.md` in your project.
3. Replace all placeholder content (marked with `[brackets]` or `<!-- comments -->`) with your project's actual information.
4. Commit the customized file.

## How Copilot Discovers This File

GitHub Copilot automatically discovers and applies instructions from `.github/copilot-instructions.md`. The file must be at this exact path — no configuration needed beyond placing it there.

## Configuration Notes

- **Path must be exactly `.github/copilot-instructions.md`** for automatic discovery.
- Keep this file concise — Copilot works best with focused, actionable instructions rather than lengthy documentation.
- For comprehensive project context, consider also applying the Claude adapter (`CLAUDE.md`) and referencing it from this file.
- The `> This file provides GitHub Copilot with project-specific context` note at the top can be updated to reference your project's full context file if you maintain one.

## Multiple Agent Tools

If your team uses Copilot alongside other tools (e.g., Claude), you can apply both adapters. They produce different files at different paths and don't conflict:
- Copilot: `.github/copilot-instructions.md`
- Claude: `CLAUDE.md` (repo root)
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/github-copilot/README.md platform-adapters/agent-tools/github-copilot/copilot-instructions.md platform-adapters/agent-tools/github-copilot/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c '## Project Description\|## Coding Style\|## Testing Approach\|## File Structure\|## Key Conventions\|## What Not to Do' platform-adapters/agent-tools/github-copilot/copilot-instructions.md
```
Expected: `6` (all sections from original copilot-instructions.md present)

Run:
```bash
grep '.github/copilot-instructions.md' platform-adapters/agent-tools/github-copilot/quickstart.md | head -1
```
Expected: Line containing `.github/copilot-instructions.md` (target path specified)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/github-copilot/
git commit -m "feat: create GitHub Copilot agent tool adapter

Stores copilot-instructions.md template in platform-adapters with
README and quickstart guide. Target path: .github/copilot-instructions.md

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

**Step 5: Push to remote (git continuity safeguard)**

```bash
git push origin feat/multi-platform-phase2
```

---

## Task 4: Create Cursor Adapter

**Files:**
- Create: `platform-adapters/agent-tools/cursor/README.md`
- Create: `platform-adapters/agent-tools/cursor/.cursorrules`
- Create: `platform-adapters/agent-tools/cursor/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/cursor && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Research and create the directory and files (GREEN)**

> **IMPORTANT — Research step:** Before creating the template file, verify the correct filename at: https://docs.cursor.com/context/rules — the current best-known filename is `.cursorrules` but this must be confirmed. If the documentation shows a different filename, use that instead and update the README and quickstart accordingly.

```bash
mkdir -p platform-adapters/agent-tools/cursor
```

Create `platform-adapters/agent-tools/cursor/README.md` with this exact content:

```markdown
# Cursor Adapter

[Cursor](https://cursor.com) is an AI-first code editor built on VS Code. It reads a `.cursorrules` file at the repository root for project-specific context — coding conventions, architecture patterns, and workflow instructions. This adapter provides the Agentic-Agile methodology template formatted for Cursor's rules file convention.

> **Research note:** Verify the current target filename at https://docs.cursor.com/context/rules — Cursor may update their filename convention between versions.
```

Create `platform-adapters/agent-tools/cursor/.cursorrules` with this exact content:

```markdown
<!-- Research note: verify target filename is .cursorrules at https://docs.cursor.com/context/rules before placing this file -->

# Project Context — [Your Project Name]

## Project Purpose

[Describe your project in 2-3 sentences: what it does, who it's for, what problem it solves.]

**Primary language:** [e.g., TypeScript, Python, Go]
**Framework:** [e.g., Next.js, FastAPI, Gin]
**Key dependencies:** [e.g., PostgreSQL, Redis, RabbitMQ]

## Architecture

```
project-root/
├── src/                    # Application source code
│   ├── api/                # HTTP handlers / route definitions
│   ├── services/           # Business logic layer
│   ├── models/             # Data models / types
│   ├── repositories/       # Data access layer
│   └── utils/              # Shared utilities
├── tests/                  # Test files (mirrors src/ structure)
├── docs/                   # Project documentation
└── .github/                # GitHub configuration
```

## Coding Conventions

- [e.g., "All functions must have type annotations"]
- [e.g., "Use dependency injection for service classes"]
- [e.g., "No magic numbers — define constants with descriptive names"]
- [e.g., "Prefer composition over inheritance"]
- [e.g., "All API endpoints return consistent response shapes: { data, error, metadata }"]

## Error Handling

- [e.g., "Use typed error classes, not generic Error"]
- [e.g., "Never swallow exceptions silently"]
- [e.g., "Log errors at the boundary, not at every level"]

## Testing

- **Framework:** [e.g., Jest, pytest, Go testing]
- **Location:** [e.g., tests alongside source, or in tests/ directory]
- **Naming:** [e.g., describe behavior: `should return 404 when user not found`]
- **Coverage:** [e.g., all public functions must have at least one test]

## Development Workflow

```
Plan → Issue → Implement → Review → Merge → Docs
```

- Create a GitHub Issue with structured scope and acceptance criteria before implementing.
- Use feature branches: `[type]/[short-description]` (e.g., `feat/user-auth`).
- Every PR receives review. All findings reach terminal state: fixed, accepted, or deferred.

## Parallelization Rules

- Every story declares which files it owns exclusively.
- No two stories in the same wave touch the same file.
- Review gates between waves ensure quality before dependent work begins.

## What Not to Do

- Do not commit secrets or credentials.
- Do not modify files owned by another story in the current wave.
- Do not skip tests for "simple" changes.
- [Add project-specific anti-patterns]
```

Create `platform-adapters/agent-tools/cursor/quickstart.md` with this exact content:

```markdown
# Cursor Adapter — Quickstart

> **Research note:** Verify the correct filename/path in Cursor documentation before applying — filenames may change between tool versions. Check: https://docs.cursor.com/context/rules

## Target Path

Place the template file at your **repository root**:

```
your-project/
└── .cursorrules
```

## Setup Steps

1. Copy `.cursorrules` from this adapter directory to your project root.
2. Replace all placeholder content (marked with `[brackets]`) with your project's actual information.
3. Update the project name in the heading.
4. Delete sections you don't need.
5. Commit the customized file.

## How Cursor Discovers This File

Cursor automatically reads `.cursorrules` at the repository root when opening a project. No additional configuration is needed.

## Configuration Notes

- **File must be named exactly `.cursorrules`** at the repo root (verify current convention in Cursor docs).
- Cursor also supports per-directory rules in some configurations — see Cursor documentation for details.
- Keep instructions actionable and specific — "follow best practices" is not useful; "all functions must have type annotations" is.

## Multiple Agent Tools

If your team uses Cursor alongside other tools (e.g., Claude, Copilot), you can apply multiple adapters. They produce different files at different paths and don't conflict:
- Cursor: `.cursorrules` (repo root)
- Claude: `CLAUDE.md` (repo root)
- Copilot: `.github/copilot-instructions.md`
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/cursor/README.md platform-adapters/agent-tools/cursor/.cursorrules platform-adapters/agent-tools/cursor/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c 'Research note' platform-adapters/agent-tools/cursor/.cursorrules
```
Expected: `1` (research verification note present)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/cursor/
git commit -m "feat: create Cursor agent tool adapter

Adds .cursorrules template with Agentic-Agile methodology content.
Includes research note to verify filename from official docs.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 5: Create Windsurf Adapter

**Files:**
- Create: `platform-adapters/agent-tools/windsurf/README.md`
- Create: `platform-adapters/agent-tools/windsurf/.windsurfrules`
- Create: `platform-adapters/agent-tools/windsurf/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/windsurf && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Research and create the directory and files (GREEN)**

> **IMPORTANT — Research step:** Before creating the template file, verify the correct filename at Windsurf documentation. The current best-known filename is `.windsurfrules` but this must be confirmed. If the documentation shows a different filename, use that instead and update the README and quickstart accordingly.

```bash
mkdir -p platform-adapters/agent-tools/windsurf
```

Create `platform-adapters/agent-tools/windsurf/README.md` with this exact content:

```markdown
# Windsurf Adapter

[Windsurf](https://codeium.com/windsurf) is Codeium's AI-powered code editor. It reads a `.windsurfrules` file at the repository root for project-specific context — coding conventions, architecture patterns, and workflow instructions. This adapter provides the Agentic-Agile methodology template formatted for Windsurf's rules file convention.

> **Research note:** Verify the current target filename in Windsurf documentation — Windsurf may update their filename convention between versions.
```

Create `platform-adapters/agent-tools/windsurf/.windsurfrules` with this exact content:

```markdown
<!-- Research note: verify target filename is .windsurfrules at Windsurf documentation before placing this file -->

# Project Context — [Your Project Name]

## Project Purpose

[Describe your project in 2-3 sentences: what it does, who it's for, what problem it solves.]

**Primary language:** [e.g., TypeScript, Python, Go]
**Framework:** [e.g., Next.js, FastAPI, Gin]
**Key dependencies:** [e.g., PostgreSQL, Redis, RabbitMQ]

## Architecture

```
project-root/
├── src/                    # Application source code
│   ├── api/                # HTTP handlers / route definitions
│   ├── services/           # Business logic layer
│   ├── models/             # Data models / types
│   ├── repositories/       # Data access layer
│   └── utils/              # Shared utilities
├── tests/                  # Test files (mirrors src/ structure)
├── docs/                   # Project documentation
└── .github/                # GitHub configuration
```

## Coding Conventions

- [e.g., "All functions must have type annotations"]
- [e.g., "Use dependency injection for service classes"]
- [e.g., "No magic numbers — define constants with descriptive names"]
- [e.g., "Prefer composition over inheritance"]
- [e.g., "All API endpoints return consistent response shapes: { data, error, metadata }"]

## Error Handling

- [e.g., "Use typed error classes, not generic Error"]
- [e.g., "Never swallow exceptions silently"]
- [e.g., "Log errors at the boundary, not at every level"]

## Testing

- **Framework:** [e.g., Jest, pytest, Go testing]
- **Location:** [e.g., tests alongside source, or in tests/ directory]
- **Naming:** [e.g., describe behavior: `should return 404 when user not found`]
- **Coverage:** [e.g., all public functions must have at least one test]

## Development Workflow

```
Plan → Issue → Implement → Review → Merge → Docs
```

- Create a GitHub Issue with structured scope and acceptance criteria before implementing.
- Use feature branches: `[type]/[short-description]` (e.g., `feat/user-auth`).
- Every PR receives review. All findings reach terminal state: fixed, accepted, or deferred.

## Parallelization Rules

- Every story declares which files it owns exclusively.
- No two stories in the same wave touch the same file.
- Review gates between waves ensure quality before dependent work begins.

## What Not to Do

- Do not commit secrets or credentials.
- Do not modify files owned by another story in the current wave.
- Do not skip tests for "simple" changes.
- [Add project-specific anti-patterns]
```

Create `platform-adapters/agent-tools/windsurf/quickstart.md` with this exact content:

```markdown
# Windsurf Adapter — Quickstart

> **Research note:** Verify the correct filename/path in Windsurf documentation before applying — filenames may change between tool versions.

## Target Path

Place the template file at your **repository root**:

```
your-project/
└── .windsurfrules
```

## Setup Steps

1. Copy `.windsurfrules` from this adapter directory to your project root.
2. Replace all placeholder content (marked with `[brackets]`) with your project's actual information.
3. Update the project name in the heading.
4. Delete sections you don't need.
5. Commit the customized file.

## How Windsurf Discovers This File

Windsurf automatically reads `.windsurfrules` at the repository root when opening a project. No additional configuration is needed.

## Configuration Notes

- **File must be named exactly `.windsurfrules`** at the repo root (verify current convention in Windsurf docs).
- Keep instructions actionable and specific.
- Windsurf shares Codeium's AI engine — conventions that work well for code completion also work here.

## Multiple Agent Tools

If your team uses Windsurf alongside other tools, you can apply multiple adapters. They produce different files at different paths and don't conflict:
- Windsurf: `.windsurfrules` (repo root)
- Claude: `CLAUDE.md` (repo root)
- Copilot: `.github/copilot-instructions.md`
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/windsurf/README.md platform-adapters/agent-tools/windsurf/.windsurfrules platform-adapters/agent-tools/windsurf/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c 'Research note' platform-adapters/agent-tools/windsurf/.windsurfrules
```
Expected: `1` (research verification note present)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/windsurf/
git commit -m "feat: create Windsurf agent tool adapter

Adds .windsurfrules template with Agentic-Agile methodology content.
Includes research note to verify filename from official docs.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 6: Create Cline Adapter

**Files:**
- Create: `platform-adapters/agent-tools/cline/README.md`
- Create: `platform-adapters/agent-tools/cline/.clinerules`
- Create: `platform-adapters/agent-tools/cline/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/cline && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Research and create the directory and files (GREEN)**

> **IMPORTANT — Research step:** Before creating the template file, verify the correct filename in Cline documentation. The current best-known filename is `.clinerules` but this must be confirmed. If the documentation shows a different filename, use that instead and update the README and quickstart accordingly.

```bash
mkdir -p platform-adapters/agent-tools/cline
```

Create `platform-adapters/agent-tools/cline/README.md` with this exact content:

```markdown
# Cline Adapter

[Cline](https://github.com/cline/cline) is an autonomous AI coding agent that runs in VS Code. It reads a `.clinerules` file at the repository root for project-specific context — coding conventions, architecture patterns, and workflow instructions. This adapter provides the Agentic-Agile methodology template formatted for Cline's rules file convention.

> **Research note:** Verify the current target filename in Cline documentation — Cline may update their filename convention between versions.
```

Create `platform-adapters/agent-tools/cline/.clinerules` with this exact content:

```markdown
<!-- Research note: verify target filename is .clinerules at Cline documentation before placing this file -->

# Project Context — [Your Project Name]

## Project Purpose

[Describe your project in 2-3 sentences: what it does, who it's for, what problem it solves.]

**Primary language:** [e.g., TypeScript, Python, Go]
**Framework:** [e.g., Next.js, FastAPI, Gin]
**Key dependencies:** [e.g., PostgreSQL, Redis, RabbitMQ]

## Architecture

```
project-root/
├── src/                    # Application source code
│   ├── api/                # HTTP handlers / route definitions
│   ├── services/           # Business logic layer
│   ├── models/             # Data models / types
│   ├── repositories/       # Data access layer
│   └── utils/              # Shared utilities
├── tests/                  # Test files (mirrors src/ structure)
├── docs/                   # Project documentation
└── .github/                # GitHub configuration
```

## Coding Conventions

- [e.g., "All functions must have type annotations"]
- [e.g., "Use dependency injection for service classes"]
- [e.g., "No magic numbers — define constants with descriptive names"]
- [e.g., "Prefer composition over inheritance"]
- [e.g., "All API endpoints return consistent response shapes: { data, error, metadata }"]

## Error Handling

- [e.g., "Use typed error classes, not generic Error"]
- [e.g., "Never swallow exceptions silently"]
- [e.g., "Log errors at the boundary, not at every level"]

## Testing

- **Framework:** [e.g., Jest, pytest, Go testing]
- **Location:** [e.g., tests alongside source, or in tests/ directory]
- **Naming:** [e.g., describe behavior: `should return 404 when user not found`]
- **Coverage:** [e.g., all public functions must have at least one test]

## Development Workflow

```
Plan → Issue → Implement → Review → Merge → Docs
```

- Create a GitHub Issue with structured scope and acceptance criteria before implementing.
- Use feature branches: `[type]/[short-description]` (e.g., `feat/user-auth`).
- Every PR receives review. All findings reach terminal state: fixed, accepted, or deferred.

## Parallelization Rules

- Every story declares which files it owns exclusively.
- No two stories in the same wave touch the same file.
- Review gates between waves ensure quality before dependent work begins.

## Autonomy Guidelines

- Ask for confirmation before making large-scale changes (>5 files).
- Do not modify files outside the scope of the current task.
- If uncertain about a design decision, present options rather than choosing arbitrarily.

## What Not to Do

- Do not commit secrets or credentials.
- Do not modify files owned by another story in the current wave.
- Do not skip tests for "simple" changes.
- [Add project-specific anti-patterns]
```

Create `platform-adapters/agent-tools/cline/quickstart.md` with this exact content:

```markdown
# Cline Adapter — Quickstart

> **Research note:** Verify the correct filename/path in Cline documentation before applying — filenames may change between tool versions.

## Target Path

Place the template file at your **repository root**:

```
your-project/
└── .clinerules
```

## Setup Steps

1. Copy `.clinerules` from this adapter directory to your project root.
2. Replace all placeholder content (marked with `[brackets]`) with your project's actual information.
3. Update the project name in the heading.
4. Delete sections you don't need.
5. Commit the customized file.

## How Cline Discovers This File

Cline automatically reads `.clinerules` at the repository root when starting a task. No additional configuration is needed.

## Configuration Notes

- **File must be named exactly `.clinerules`** at the repo root (verify current convention in Cline docs).
- Cline operates autonomously — the "Autonomy Guidelines" section helps bound its behavior appropriately.
- Keep instructions clear and actionable since Cline may execute multi-step plans without intermediate confirmation.

## Multiple Agent Tools

If your team uses Cline alongside other tools, you can apply multiple adapters. They produce different files at different paths and don't conflict:
- Cline: `.clinerules` (repo root)
- Claude: `CLAUDE.md` (repo root)
- Copilot: `.github/copilot-instructions.md`
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/cline/README.md platform-adapters/agent-tools/cline/.clinerules platform-adapters/agent-tools/cline/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c 'Research note' platform-adapters/agent-tools/cline/.clinerules
```
Expected: `1` (research verification note present)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/cline/
git commit -m "feat: create Cline agent tool adapter

Adds .clinerules template with Agentic-Agile methodology content.
Includes autonomy guidelines and research note to verify filename.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 7: Create Aider Adapter

**Files:**
- Create: `platform-adapters/agent-tools/aider/README.md`
- Create: `platform-adapters/agent-tools/aider/CONVENTIONS.md`
- Create: `platform-adapters/agent-tools/aider/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/agent-tools/aider && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Research and create the directory and files (GREEN)**

> **IMPORTANT — Research step:** Before creating the template file, verify the correct filename in aider documentation. The current best-known filename is `CONVENTIONS.md` but this must be confirmed. Check https://aider.chat/docs/usage/conventions.html or the aider GitHub repository. If the documentation shows a different filename, use that instead and update the README and quickstart accordingly.

```bash
mkdir -p platform-adapters/agent-tools/aider
```

Create `platform-adapters/agent-tools/aider/README.md` with this exact content:

```markdown
# aider Adapter

[aider](https://aider.chat) is a command-line AI pair programming tool that works with any LLM. It reads a `CONVENTIONS.md` file at the repository root for project-specific context — coding conventions, architecture patterns, and workflow instructions. This adapter provides the Agentic-Agile methodology template formatted for aider's conventions file.

> **Research note:** Verify the current target filename at https://aider.chat/docs/usage/conventions.html — aider may update their filename convention between versions.
```

Create `platform-adapters/agent-tools/aider/CONVENTIONS.md` with this exact content:

```markdown
<!-- Research note: verify target filename is CONVENTIONS.md at https://aider.chat/docs/usage/conventions.html before placing this file -->

# Conventions — [Your Project Name]

## Project Purpose

[Describe your project in 2-3 sentences: what it does, who it's for, what problem it solves.]

**Primary language:** [e.g., TypeScript, Python, Go]
**Framework:** [e.g., Next.js, FastAPI, Gin]
**Key dependencies:** [e.g., PostgreSQL, Redis, RabbitMQ]

## Architecture

```
project-root/
├── src/                    # Application source code
│   ├── api/                # HTTP handlers / route definitions
│   ├── services/           # Business logic layer
│   ├── models/             # Data models / types
│   ├── repositories/       # Data access layer
│   └── utils/              # Shared utilities
├── tests/                  # Test files (mirrors src/ structure)
├── docs/                   # Project documentation
└── .github/                # GitHub configuration
```

## Coding Conventions

- [e.g., "All functions must have type annotations"]
- [e.g., "Use dependency injection for service classes"]
- [e.g., "No magic numbers — define constants with descriptive names"]
- [e.g., "Prefer composition over inheritance"]
- [e.g., "All API endpoints return consistent response shapes: { data, error, metadata }"]

## Error Handling

- [e.g., "Use typed error classes, not generic Error"]
- [e.g., "Never swallow exceptions silently"]
- [e.g., "Log errors at the boundary, not at every level"]

## Testing

- **Framework:** [e.g., Jest, pytest, Go testing]
- **Location:** [e.g., tests alongside source, or in tests/ directory]
- **Naming:** [e.g., describe behavior: `should return 404 when user not found`]
- **Coverage:** [e.g., all public functions must have at least one test]

## Development Workflow

```
Plan → Issue → Implement → Review → Merge → Docs
```

- Create a GitHub Issue with structured scope and acceptance criteria before implementing.
- Use feature branches: `[type]/[short-description]` (e.g., `feat/user-auth`).
- Every PR receives review. All findings reach terminal state: fixed, accepted, or deferred.

## Parallelization Rules

- Every story declares which files it owns exclusively.
- No two stories in the same wave touch the same file.
- Review gates between waves ensure quality before dependent work begins.

## Commit Message Format

Use conventional commits:

```
<type>: <short summary>

<optional body>

Closes #<issue-number>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

## What Not to Do

- Do not commit secrets or credentials.
- Do not modify files owned by another story in the current wave.
- Do not skip tests for "simple" changes.
- [Add project-specific anti-patterns]
```

Create `platform-adapters/agent-tools/aider/quickstart.md` with this exact content:

```markdown
# aider Adapter — Quickstart

> **Research note:** Verify the correct filename/path in aider documentation before applying — filenames may change between tool versions. Check: https://aider.chat/docs/usage/conventions.html

## Target Path

Place the template file at your **repository root**:

```
your-project/
└── CONVENTIONS.md
```

## Setup Steps

1. Copy `CONVENTIONS.md` from this adapter directory to your project root.
2. Replace all placeholder content (marked with `[brackets]`) with your project's actual information.
3. Update the project name in the heading.
4. Delete sections you don't need.
5. Commit the customized file.

## How aider Discovers This File

aider automatically reads `CONVENTIONS.md` at the repository root when starting a session. You can also explicitly pass it with `--read CONVENTIONS.md` if using a different filename.

## Configuration Notes

- **File should be named `CONVENTIONS.md`** at the repo root for automatic discovery (verify in aider docs).
- aider also supports `.aider.conf.yml` for tool configuration — that's separate from project conventions.
- Keep the file focused on coding conventions and workflow — aider works best with clear, actionable instructions.
- aider supports multiple LLM backends (GPT-4, Claude, etc.) — conventions apply regardless of which model is used.

## Multiple Agent Tools

If your team uses aider alongside other tools, you can apply multiple adapters. They produce different files at different paths and don't conflict:
- aider: `CONVENTIONS.md` (repo root)
- Claude: `CLAUDE.md` (repo root)
- Copilot: `.github/copilot-instructions.md`
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/agent-tools/aider/README.md platform-adapters/agent-tools/aider/CONVENTIONS.md platform-adapters/agent-tools/aider/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c 'Research note' platform-adapters/agent-tools/aider/CONVENTIONS.md
```
Expected: `1` (research verification note present)

**Step 4: Commit**

```bash
git add platform-adapters/agent-tools/aider/
git commit -m "feat: create aider agent tool adapter

Adds CONVENTIONS.md template with Agentic-Agile methodology content.
Includes research note to verify filename from official docs.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

**Step 5: Push to remote (git continuity safeguard)**

```bash
git push origin feat/multi-platform-phase2
```

---

## Task 8: Create GitHub Issue Tracker Adapter

**Files:**
- Create: `platform-adapters/issue-trackers/github/README.md`
- Create: `platform-adapters/issue-trackers/github/quickstart.md`

**Step 1: Verify directory does not exist (RED)**

Run:
```bash
test -d platform-adapters/issue-trackers/github && echo "ALREADY EXISTS" || echo "PASS - directory does not exist"
```
Expected: `PASS - directory does not exist`

**Step 2: Create the directory and files (GREEN)**

```bash
mkdir -p platform-adapters/issue-trackers/github
```

Create `platform-adapters/issue-trackers/github/README.md` with this exact content:

```markdown
# GitHub Issue Tracker Adapter

This adapter documents how the Agentic-Agile methodology uses GitHub Issues for structured work management. Unlike agent tool adapters, this adapter does not provide a new template file — it links to the existing `.github/ISSUE_TEMPLATE/agentic-story.md` that GitHub automatically discovers and presents to issue creators.
```

Create `platform-adapters/issue-trackers/github/quickstart.md` with this exact content:

```markdown
# GitHub Issue Tracker — Quickstart

## How It Works

GitHub Issues is the default issue tracker for this template. The Agentic-Agile story format is already configured at:

```
.github/ISSUE_TEMPLATE/agentic-story.md
```

GitHub automatically discovers issue templates at this path and presents them when users click "New Issue" in the repository.

## No Files to Copy

Unlike agent tool adapters, there is nothing to copy or configure for GitHub Issues. The template already includes the issue template at the correct path. When you create a new project via the onboarding dialogue, the `.github/ISSUE_TEMPLATE/` directory is included in the template copy (Commit 1).

## What the Issue Template Provides

The `agentic-story.md` template enforces the Agentic-Agile story format:

- **Summary** — one sentence describing the work
- **Context / Motivation** — why this work matters
- **Scope** — files to create/modify, interfaces to implement, invariants to preserve
- **Acceptance Criteria** — checkboxes defining "done"
- **Negative Constraints** — what is explicitly out of scope
- **Dependencies** — what must be complete before this starts
- **File Ownership** — which files this story owns exclusively

## Customization

After onboarding, you can customize the issue template:

1. Edit `.github/ISSUE_TEMPLATE/agentic-story.md` to add project-specific fields.
2. Add additional templates for different work types (bugs, spikes, etc.).
3. The format is flexible — the key structural sections should remain, but you can add or rename fields.

## Why This Adapter Exists

Even though there's nothing to "install," this adapter exists for completeness in the three-layer architecture. It documents:
- Where the issue template lives
- What format it expects
- How GitHub auto-discovers it
- How to customize it for your project

This allows the onboarding dialogue to list "GitHub Issues" as a supported tracker and point users to the right documentation.
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/issue-trackers/github/README.md platform-adapters/issue-trackers/github/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: Both files show `PASS`

Run:
```bash
grep -c 'agentic-story.md' platform-adapters/issue-trackers/github/quickstart.md
```
Expected: `3` or more (references to the existing issue template)

**Step 4: Commit**

```bash
git add platform-adapters/issue-trackers/github/
git commit -m "feat: create GitHub issue tracker adapter

Links to existing .github/ISSUE_TEMPLATE/agentic-story.md rather
than duplicating content. Documents how GitHub auto-discovers templates.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 9: Remove Root CLAUDE.md

**Files:**
- Remove: `CLAUDE.md`

**Step 1: Verify file exists (RED)**

Run:
```bash
test -f CLAUDE.md && echo "PASS - file exists (ready to remove)" || echo "FAIL - file already gone"
```
Expected: `PASS - file exists (ready to remove)`

**Step 2: Remove the file (GREEN)**

```bash
git rm CLAUDE.md
```

**Step 3: Verify (VERIFY)**

Run:
```bash
test ! -f CLAUDE.md && echo "PASS - file removed" || echo "FAIL - file still exists"
```
Expected: `PASS - file removed`

Run:
```bash
test -f platform-adapters/agent-tools/claude/CLAUDE.md && echo "PASS - migrated content exists in adapter" || echo "FAIL - adapter content missing"
```
Expected: `PASS - migrated content exists in adapter`

Run:
```bash
test -f AGENTS.md && echo "PASS - AGENTS.md is the entry point" || echo "FAIL - AGENTS.md missing"
```
Expected: `PASS - AGENTS.md is the entry point`

**Step 4: Commit**

```bash
git commit -m "feat: remove root CLAUDE.md — content migrated to platform adapter

CLAUDE.md template content now lives at
platform-adapters/agent-tools/claude/CLAUDE.md.
AGENTS.md is the universal entry point for all agents.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 10: Create Combo Files

**Files:**
- Create: `platform-adapters/combos/claude-github-github-actions.md`
- Create: `platform-adapters/combos/copilot-github-github-actions.md`
- Create: `platform-adapters/combos/cursor-github-github-actions.md`

**Step 1: Verify files do not exist (RED)**

Run:
```bash
for f in platform-adapters/combos/claude-github-github-actions.md platform-adapters/combos/copilot-github-github-actions.md platform-adapters/combos/cursor-github-github-actions.md; do
  test -f "$f" && echo "ALREADY EXISTS: $f" || echo "PASS - does not exist: $f"
done
```
Expected: All three show `PASS - does not exist`

**Step 2: Create the files (GREEN)**

Create `platform-adapters/combos/claude-github-github-actions.md` with this exact content:

```markdown
# Claude + GitHub Issues + GitHub Actions

**Stack:** Claude · GitHub Issues · GitHub Actions
**Status:** Maintained

## Adapters Used

- [`platform-adapters/agent-tools/claude/`](../agent-tools/claude/) — Claude agent context file (`CLAUDE.md`)
- [`platform-adapters/issue-trackers/github/`](../issue-trackers/github/) — GitHub Issues with agentic-story template
- CI/CD: GitHub Actions (planned for v2 — uses existing `.github/workflows/`)

## Quick Setup

1. **Agent context:** Copy `platform-adapters/agent-tools/claude/CLAUDE.md` to your project root. Customize with your project details. See [`quickstart.md`](../agent-tools/claude/quickstart.md).
2. **Issue tracker:** Already configured — GitHub auto-discovers `.github/ISSUE_TEMPLATE/agentic-story.md`. See [`quickstart.md`](../issue-trackers/github/quickstart.md).
3. **CI/CD:** Use existing `.github/workflows/` directory. CI/CD adapter with Agentic-Agile-specific workflows coming in v2.

## Notes

This is the original stack combination that the Agentic-Agile template was built with. It is the most thoroughly tested and documented combination.

- Claude reads `CLAUDE.md` automatically — no IDE extension configuration needed.
- GitHub Issues with the agentic-story template provides structured specs that Claude executes well.
- GitHub Actions provides CI validation; Agentic-Agile-specific workflow templates are planned for v2.
```

Create `platform-adapters/combos/copilot-github-github-actions.md` with this exact content:

```markdown
# GitHub Copilot + GitHub Issues + GitHub Actions

**Stack:** GitHub Copilot · GitHub Issues · GitHub Actions
**Status:** Maintained

## Adapters Used

- [`platform-adapters/agent-tools/github-copilot/`](../agent-tools/github-copilot/) — Copilot instructions file (`.github/copilot-instructions.md`)
- [`platform-adapters/issue-trackers/github/`](../issue-trackers/github/) — GitHub Issues with agentic-story template
- CI/CD: GitHub Actions (planned for v2 — uses existing `.github/workflows/`)

## Quick Setup

1. **Agent context:** Copy `platform-adapters/agent-tools/github-copilot/copilot-instructions.md` to `.github/copilot-instructions.md`. Customize with your project details. See [`quickstart.md`](../agent-tools/github-copilot/quickstart.md).
2. **Issue tracker:** Already configured — GitHub auto-discovers `.github/ISSUE_TEMPLATE/agentic-story.md`. See [`quickstart.md`](../issue-trackers/github/quickstart.md).
3. **CI/CD:** Use existing `.github/workflows/` directory. CI/CD adapter with Agentic-Agile-specific workflows coming in v2.

## Notes

This is the all-GitHub stack — everything stays within the GitHub ecosystem.

- Copilot reads `.github/copilot-instructions.md` automatically in VS Code, GitHub.com, and JetBrains IDEs.
- For more comprehensive project context, consider also applying the Claude adapter alongside Copilot — they use different files and don't conflict.
- GitHub Copilot Workspace and Copilot Chat both benefit from the instructions file.
```

Create `platform-adapters/combos/cursor-github-github-actions.md` with this exact content:

```markdown
# Cursor + GitHub Issues + GitHub Actions

**Stack:** Cursor · GitHub Issues · GitHub Actions
**Status:** Community

## Adapters Used

- [`platform-adapters/agent-tools/cursor/`](../agent-tools/cursor/) — Cursor rules file (`.cursorrules`)
- [`platform-adapters/issue-trackers/github/`](../issue-trackers/github/) — GitHub Issues with agentic-story template
- CI/CD: GitHub Actions (planned for v2 — uses existing `.github/workflows/`)

## Quick Setup

1. **Agent context:** Copy `platform-adapters/agent-tools/cursor/.cursorrules` to your project root. Customize with your project details. See [`quickstart.md`](../agent-tools/cursor/quickstart.md).
2. **Issue tracker:** Already configured — GitHub auto-discovers `.github/ISSUE_TEMPLATE/agentic-story.md`. See [`quickstart.md`](../issue-trackers/github/quickstart.md).
3. **CI/CD:** Use existing `.github/workflows/` directory. CI/CD adapter with Agentic-Agile-specific workflows coming in v2.

## Notes

Cursor is popular among teams transitioning from VS Code who want deeper AI integration.

- Cursor reads `.cursorrules` automatically — verify the current filename convention in Cursor documentation as it may change between versions.
- Cursor's Composer feature works well with the structured story format from the agentic-story issue template.
- For teams using both Cursor and Claude (e.g., Cursor for IDE work, Claude CLI for complex tasks), apply both adapters.
```

**Step 3: Verify (VERIFY)**

Run:
```bash
for f in platform-adapters/combos/claude-github-github-actions.md platform-adapters/combos/copilot-github-github-actions.md platform-adapters/combos/cursor-github-github-actions.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: All three files show `PASS`

Run:
```bash
grep -c '**Stack:**\|**Status:**' platform-adapters/combos/claude-github-github-actions.md
```
Expected: `2` (both required fields present)

Run:
```bash
grep '**Status:**' platform-adapters/combos/cursor-github-github-actions.md
```
Expected: `**Status:** Community`

**Step 4: Commit**

```bash
git add platform-adapters/combos/claude-github-github-actions.md platform-adapters/combos/copilot-github-github-actions.md platform-adapters/combos/cursor-github-github-actions.md
git commit -m "feat: add initial combo quickstart files (claude, copilot, cursor)

Three stack combination guides for GitHub-based workflows:
- claude-github-github-actions (Maintained)
- copilot-github-github-actions (Maintained)
- cursor-github-github-actions (Community)

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

**Step 5: Push to remote (git continuity safeguard)**

```bash
git push origin feat/multi-platform-phase2
```

---

## Final Validation

After all tasks are complete, run this comprehensive check:

```bash
echo "=== Phase 2 Structural Validation ==="

echo ""
echo "--- Directory READMEs ---"
for f in platform-adapters/README.md platform-adapters/agent-tools/README.md platform-adapters/issue-trackers/README.md platform-adapters/ci-cd/README.md platform-adapters/combos/README.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "--- Agent Tool Adapters (3 files each) ---"
for tool in claude github-copilot cursor windsurf cline aider; do
  dir="platform-adapters/agent-tools/$tool"
  test -d "$dir" && echo "PASS: $dir/ exists" || echo "FAIL: $dir/ missing"
  test -f "$dir/README.md" && echo "  PASS: README.md" || echo "  FAIL: README.md"
  test -f "$dir/quickstart.md" && echo "  PASS: quickstart.md" || echo "  FAIL: quickstart.md"
  # Check for target file (varies by tool)
  count=$(find "$dir" -maxdepth 1 -type f ! -name README.md ! -name quickstart.md | wc -l)
  test "$count" -ge 1 && echo "  PASS: target file present ($count)" || echo "  FAIL: no target file"
done

echo ""
echo "--- Issue Tracker Adapter ---"
for f in platform-adapters/issue-trackers/github/README.md platform-adapters/issue-trackers/github/quickstart.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "--- Combo Files ---"
for f in platform-adapters/combos/claude-github-github-actions.md platform-adapters/combos/copilot-github-github-actions.md platform-adapters/combos/cursor-github-github-actions.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "--- Root CLAUDE.md Removed ---"
test ! -f CLAUDE.md && echo "PASS: CLAUDE.md removed from root" || echo "FAIL: CLAUDE.md still at root"

echo ""
echo "--- AGENTS.md is Entry Point ---"
test -f AGENTS.md && echo "PASS: AGENTS.md exists as entry point" || echo "FAIL: AGENTS.md missing"

echo ""
echo "--- .github/copilot-instructions.md is Stub (from Phase 1) ---"
lines=$(wc -l < .github/copilot-instructions.md 2>/dev/null || echo "0")
test "$lines" -lt 25 && echo "PASS: stub ($lines lines)" || echo "FAIL: not a stub ($lines lines)"

echo ""
echo "--- Research Notes Present (Cursor, Windsurf, Cline, Aider) ---"
for tool in cursor windsurf cline aider; do
  dir="platform-adapters/agent-tools/$tool"
  count=$(grep -rl 'Research note' "$dir" 2>/dev/null | wc -l)
  test "$count" -ge 1 && echo "PASS: $tool has research notes" || echo "FAIL: $tool missing research notes"
done

echo ""
echo "=== Validation Complete ==="
```

Expected output:
- All directory READMEs: PASS
- All 6 agent tool adapter directories: PASS with README.md, quickstart.md, and target file
- Issue tracker adapter: PASS
- All 3 combo files: PASS
- Root CLAUDE.md: PASS (removed)
- AGENTS.md: PASS (exists)
- Copilot stub: PASS (< 25 lines)
- Research notes: PASS for cursor, windsurf, cline, aider
