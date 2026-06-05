# Multi-Platform Generalization — Phase 1: Foundation

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Create the foundational files that exist regardless of which platform adapter is selected — the onboarding orchestrator, contribution guides, and contributor templates.

**Architecture:** Root-level markdown files establish the universal entry points (`AGENTS.md`, `CONTRIBUTING-AGENTS.md`), while `.github/contributor-templates/` provides structured templates for agents contributing to this methodology template. Existing files (`README.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`) are updated to reflect the multi-platform framing.

**Tech Stack:** Markdown, GitHub CLI (`gh`), Git

---

## Task 0: Create GitHub Issues for All Phase 1 Tasks

**Purpose:** Establish the ticketed backlog before any file work begins. Issues are malleable — specs can be amended during planning, sub-issues created during decomposition, and execution modifications documented as comments.

**Step 1: Verify `gh` CLI is authenticated**

Run:
```bash
gh auth status
```
Expected: Shows authenticated user and repo access.

**Step 2: Create issues for Tasks 1–8**

Run each command below. Each issue references the design document and is labeled as part of the multi-platform generalization project.

```bash
gh issue create \
  --title "feat: Create AGENTS.md onboarding orchestrator" \
  --label "enhancement" \
  --body "## Summary

Create the root-level \`AGENTS.md\` file — the universal onboarding orchestrator and single entry point for any agent reading the repo cold.

## Context / Motivation

Currently the repo has \`CLAUDE.md\` as the primary agent context file, which couples the template to a single tool. \`AGENTS.md\` replaces this as the tool-agnostic entry point that detects its own state and routes agents appropriately.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: AGENTS.md — Onboarding Orchestrator

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`AGENTS.md\` — new file, root-level onboarding orchestrator

### Interfaces to Implement

- State detection via placeholder project name (\`[Project Name]\`)
- Three-state routing: template → onboarding, configured → orient, contributor → CONTRIBUTING-AGENTS.md
- 6-step guided onboarding dialogue protocol
- Additive persona clause in Your Role section

### Invariants to Preserve

- \`CLAUDE.md\` remains unchanged (migration happens in Phase 2)
- No other existing files are modified

## Acceptance Criteria

- [ ] \`AGENTS.md\` exists at repo root
- [ ] Contains \`## What This Is\`, \`## Repo Map\`, \`## Your Role\`, \`## Onboarding Protocol\`, \`## Guided Onboarding Dialogue\` sections
- [ ] State detection logic uses \`[Project Name]\` as sentinel
- [ ] Additive persona clause is present in Your Role
- [ ] 6-step onboarding dialogue is fully specified
- [ ] Fallback prompt template included for non-dialogue entry
- [ ] No tool-specific dependencies — works with any LLM agent

## Negative Constraints

- Does NOT modify \`CLAUDE.md\`
- Does NOT implement platform adapters (Phase 2)
- Does NOT contain project-specific content (only template scaffolding)

## Dependencies

- None (first task after issue creation)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`AGENTS.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Create CONTRIBUTING-AGENTS.md for template contributors" \
  --label "enhancement" \
  --body "## Summary

Create \`CONTRIBUTING-AGENTS.md\` — the agent-specific contribution guide for agents modifying this template repository.

## Context / Motivation

Mirrors the README/AGENTS pattern for contributions: \`CONTRIBUTING.md\` is human-facing, \`CONTRIBUTING-AGENTS.md\` is agent-facing. Provides structural intent, design rationale, and references to contributor templates.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Contributing Guidelines

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`CONTRIBUTING-AGENTS.md\` — new file at repo root

### Interfaces to Implement

- References \`.github/contributor-templates/\` for issue/PR templates
- Explains the three adapter layers and how to add new ones
- Provides \"what not to break\" guidance

### Invariants to Preserve

- \`CONTRIBUTING.md\` not modified in this task (separate task)
- Existing \`.github/\` structure unchanged

## Acceptance Criteria

- [ ] \`CONTRIBUTING-AGENTS.md\` exists at repo root
- [ ] References all four \`.github/contributor-templates/\` files by path
- [ ] Explains the three-layer adapter architecture
- [ ] Contains \"what not to break\" section
- [ ] Explains contribution workflow specific to agents
- [ ] References the design document for architectural decisions

## Negative Constraints

- Does NOT modify \`CONTRIBUTING.md\` (separate task)
- Does NOT create the contributor templates themselves (separate task)

## Dependencies

- None (can run in parallel with Task 1)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`CONTRIBUTING-AGENTS.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Create .github/contributor-templates/new-adapter-story.md" \
  --label "enhancement" \
  --body "## Summary

Create the contributor issue template for adding a new platform adapter (agent tool, issue tracker, or CI/CD).

## Context / Motivation

Contributors (human or agent) adding a new adapter need a structured template that ensures they include all required files and follow the adapter anatomy defined in the design.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Contributor Templates

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`.github/contributor-templates/new-adapter-story.md\` — new file

### Interfaces to Implement

- Follows the agentic-story format from \`.github/ISSUE_TEMPLATE/agentic-story.md\`
- Scoped to adapter contribution type (requires README.md, target file, quickstart.md)

### Invariants to Preserve

- \`.github/ISSUE_TEMPLATE/\` directory unchanged
- Existing GitHub auto-discovery not affected

## Acceptance Criteria

- [ ] File exists at \`.github/contributor-templates/new-adapter-story.md\`
- [ ] Uses agentic-story format (Summary, Context, Scope, Acceptance Criteria, Negative Constraints, Dependencies, File Ownership)
- [ ] Specifies the three required adapter files (README.md, target-named template, quickstart.md)
- [ ] References the adapter anatomy section of the design document

## Negative Constraints

- Does NOT modify existing issue templates
- Does NOT create the actual adapters

## Dependencies

- None (can run in parallel)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`.github/contributor-templates/new-adapter-story.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Create .github/contributor-templates/new-combo-story.md" \
  --label "enhancement" \
  --body "## Summary

Create the contributor issue template for adding a new quickstart combo file.

## Context / Motivation

Quickstart combos document a specific stack combination (agent tool + issue tracker + CI/CD). Contributors adding new combos need a template ensuring consistency with the combo index format.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Quickstart Combo Index

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`.github/contributor-templates/new-combo-story.md\` — new file

### Interfaces to Implement

- Follows agentic-story format
- References combo filename format and required sections

### Invariants to Preserve

- Existing \`.github/\` structure unchanged

## Acceptance Criteria

- [ ] File exists at \`.github/contributor-templates/new-combo-story.md\`
- [ ] Uses agentic-story format
- [ ] Specifies combo filename convention (\`<agent>-<tracker>-<cicd>.md\`)
- [ ] Lists required combo file sections (Stack, Status, Adapters used, Notes)
- [ ] References combo README for status tier definitions

## Negative Constraints

- Does NOT create the combos directory or files (Phase 2)

## Dependencies

- None (can run in parallel)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`.github/contributor-templates/new-combo-story.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Create .github/contributor-templates/update-methodology-story.md" \
  --label "enhancement" \
  --body "## Summary

Create the contributor issue template for changes to the methodology documentation (MANIFESTO.md, docs/, or core process files).

## Context / Motivation

Methodology changes affect all derived repos and all adapters. They require higher scrutiny and explicit scope definition. This template ensures contributors articulate the impact of their proposed changes.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Contributor Templates

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`.github/contributor-templates/update-methodology-story.md\` — new file

### Interfaces to Implement

- Follows agentic-story format
- Includes impact assessment section specific to methodology changes

### Invariants to Preserve

- Existing methodology files unchanged

## Acceptance Criteria

- [ ] File exists at \`.github/contributor-templates/update-methodology-story.md\`
- [ ] Uses agentic-story format
- [ ] Includes section for impact assessment (which adapters affected, downstream effects)
- [ ] Lists common methodology files (MANIFESTO.md, STYLE.md, docs/*.md)

## Negative Constraints

- Does NOT modify any methodology files

## Dependencies

- None (can run in parallel)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`.github/contributor-templates/update-methodology-story.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Create .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md" \
  --label "enhancement" \
  --body "## Summary

Create a PR description template for contributors to this template repository.

## Context / Motivation

A structured PR template ensures contributors provide the necessary context for review: what changed, why, which adapter/docs are affected, and what testing was done.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Contributor Templates

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md\` — new file

### Interfaces to Implement

- Sections: Summary, Related Issue, Changes Made, Testing Done, Checklist

### Invariants to Preserve

- Does not interfere with any existing PR template at \`.github/PULL_REQUEST_TEMPLATE.md\` (if one exists)

## Acceptance Criteria

- [ ] File exists at \`.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md\`
- [ ] Contains Summary, Related Issue, Changes Made, Testing Done, and Checklist sections
- [ ] Checklist includes items for: adapter anatomy compliance, README updated, no placeholder text remaining

## Negative Constraints

- Does NOT replace or modify any existing GitHub PR template

## Dependencies

- None (can run in parallel)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md\` | ✅ | New file |"
```

```bash
gh issue create \
  --title "feat: Rewrite README.md for multi-platform framing" \
  --label "enhancement" \
  --body "## Summary

Rewrite \`README.md\` to remove GitHub/Claude-centric language and present the template as a multi-platform methodology scaffold.

## Context / Motivation

The current README references \`CLAUDE.md\` as the primary agent context and assumes GitHub as the only platform. The rewrite introduces the three-layer adapter architecture, points to \`AGENTS.md\` as the universal entry point, and presents all supported platforms equally.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Migration from Current State

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`README.md\` — full rewrite

### Interfaces to Implement

- Multi-platform framing (no single-tool bias)
- References \`AGENTS.md\` as the primary entry point
- Explains three-layer adapter architecture
- Updated Getting Started section for onboarding flow

### Invariants to Preserve

- Blog series links preserved
- MCP configuration section preserved
- Contributing and License sections preserved (updated links)
- Manifesto values summary preserved

## Acceptance Criteria

- [ ] No references to \`CLAUDE.md\` as the primary agent context file
- [ ] \`AGENTS.md\` presented as universal entry point
- [ ] Three-layer architecture (agent-tools, issue-trackers, ci-cd) explained
- [ ] Getting Started updated to reference onboarding dialogue
- [ ] File table updated with new files (\`AGENTS.md\`, \`CONTRIBUTING-AGENTS.md\`)
- [ ] All external links still functional

## Negative Constraints

- Does NOT delete or modify \`CLAUDE.md\` itself
- Does NOT create platform-adapters directory (Phase 2)

## Dependencies

- Depends on Task 1 (\`AGENTS.md\` must exist to reference it accurately)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`README.md\` | ✅ | Full rewrite |"
```

```bash
gh issue create \
  --title "feat: Update CONTRIBUTING.md with pointer to CONTRIBUTING-AGENTS.md" \
  --label "enhancement" \
  --body "## Summary

Add a pointer to \`CONTRIBUTING-AGENTS.md\` in the existing \`CONTRIBUTING.md\` file.

## Context / Motivation

Light update — adds one section directing agent contributors to the agent-specific guide. Keeps \`CONTRIBUTING.md\` focused on human contributors while acknowledging the agent contribution path.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Contributing Guidelines

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`CONTRIBUTING.md\` — add one section (\"Agent Contributors\")

### Interfaces to Implement

- New section with pointer to \`CONTRIBUTING-AGENTS.md\`

### Invariants to Preserve

- All existing content preserved verbatim
- Section ordering unchanged (new section added at a logical position)

## Acceptance Criteria

- [ ] \`CONTRIBUTING.md\` contains a section referencing \`CONTRIBUTING-AGENTS.md\`
- [ ] All original content preserved
- [ ] New section is concise (2-3 sentences maximum)

## Negative Constraints

- Does NOT restructure existing sections
- Does NOT remove or rewrite existing content

## Dependencies

- Depends on Task 2 (\`CONTRIBUTING-AGENTS.md\` must exist)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`CONTRIBUTING.md\` | ✅ | Minor addition |"
```

```bash
gh issue create \
  --title "feat: Convert .github/copilot-instructions.md to stub" \
  --label "enhancement" \
  --body "## Summary

Replace the current \`.github/copilot-instructions.md\` template content with a short stub that points to \`platform-adapters/agent-tools/github-copilot/\`.

## Context / Motivation

The full Copilot instructions content will live in the platform-adapters directory (Phase 2). The \`.github/\` file remains as a stub because GitHub auto-discovers it, but its content directs users to the canonical location.

Design: \`docs/history/2026-06-04-multi-platform-generalization-design.md\` — Section: Migration from Current State

Part of: Multi-Platform Generalization (Phase 1: Foundation)

## Scope

### Files to Create or Modify

- \`.github/copilot-instructions.md\` — replace content with stub

### Interfaces to Implement

- Short explanation of why content moved
- Path to canonical location
- Note that this stub exists for GitHub auto-discovery

### Invariants to Preserve

- File remains at \`.github/copilot-instructions.md\` (GitHub requires this path)
- File is valid markdown

## Acceptance Criteria

- [ ] \`.github/copilot-instructions.md\` is a short stub (< 15 lines)
- [ ] Contains path to \`platform-adapters/agent-tools/github-copilot/\`
- [ ] Explains why content moved
- [ ] Notes that full content will be available at the adapter path after Phase 2

## Negative Constraints

- Does NOT create the \`platform-adapters/\` directory (Phase 2)
- Does NOT preserve the old template content in this file

## Dependencies

- None (can run independently)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| \`.github/copilot-instructions.md\` | ✅ | Content replacement |"
```

**Step 3: Record issue numbers**

Run:
```bash
gh issue list --limit 10 --state open --json number,title
```

Save the output — you'll reference these issue numbers in commit messages for Tasks 1–8.

**Step 4: Commit**

No file changes to commit for Task 0 — issues live in GitHub, not the repo.

---

## Task 1: Create AGENTS.md — Onboarding Orchestrator

**Files:**
- Create: `AGENTS.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f AGENTS.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the file (GREEN)**

Create `AGENTS.md` at the repository root with this exact content:

```markdown
# [Project Name] — Agentic-Agile Development

## What This Is

This is the Agentic-Agile methodology template — a scaffold for teams adopting structured human-agent software development. It provides the process layer, templates, and tooling configuration that make agent collaboration repeatable across any combination of AI coding tools, issue trackers, and CI/CD systems.

## Repo Map

```
agentic-agile-template/
├── AGENTS.md                      ← you are here (onboarding orchestrator)
├── README.md                      ← project overview and getting started
├── MANIFESTO.md                   ← Agentic-Agile values and principles
├── STYLE.md                       ← code and documentation style guide
├── CONTRIBUTING.md                ← human contribution guide
├── CONTRIBUTING-AGENTS.md         ← agent contribution guide (for modifying this template)
├── SECURITY.md                    ← security policy
├── LICENSE                        ← MIT License
├── mcp.json                       ← MCP server configuration example
├── platform-adapters/             ← tool/tracker/CI configuration templates
│   ├── agent-tools/               ← per-tool agent context files
│   ├── issue-trackers/            ← per-tracker issue templates
│   ├── ci-cd/                     ← per-CI pipeline configurations
│   └── combos/                    ← quickstart guides for specific stacks
├── .github/
│   ├── ISSUE_TEMPLATE/            ← GitHub issue templates (agentic-story format)
│   ├── contributor-templates/     ← templates for contributing to this template
│   ├── copilot-instructions.md   ← GitHub Copilot stub (points to adapter)
│   └── workflows/                 ← CI/CD workflow definitions
└── docs/                          ← methodology documentation and examples
    ├── agent-surface-selection.md
    ├── evaluation-framework.md
    └── epic-decomposition-example.md
```

## Your Role

You are an agentic-agile development partner. You collaborate with humans to produce production-ready software through structured specification, parallel execution, and continuous measurement — following the methodology defined in this repository.

This role is additive — if you've been given a specific persona or instructions by your operator or user, retain those while also adopting the agentic-partner role described here.

**How to proceed depends on the state of this file:**

- **Template state** (this file contains `[Project Name]` in its title) → You are reading the raw template. Run the Guided Onboarding Dialogue below to configure a new project.
- **Configured state** (the title contains an actual project name) → This is a configured project repo. Orient yourself by reading the project-specific sections below, then proceed with the user's request.
- **Contributor state** (you are here to modify *this template itself*) → Read `CONTRIBUTING-AGENTS.md` for structural guidance before making changes.

## Onboarding Protocol

### State Detection

Check the title of this file (the `# ...` heading on line 1):
- If it contains `[Project Name]` → **template state** → proceed to Guided Onboarding Dialogue
- If it contains a real project name → **configured state** → orient and proceed
- If the user explicitly states they want to contribute to the template → **contributor state** → read `CONTRIBUTING-AGENTS.md`

### On Entry (Template State)

Do not greet the user. Acknowledge understanding and step into role immediately by running the Guided Onboarding Dialogue.

### On Entry (Configured State)

Do not greet the user. Acknowledge the project context ("I've read the project context for [Name]. Ready to proceed.") and address the user's request directly.

## Guided Onboarding Dialogue

When this file is in template state, execute the following 6-step protocol:

### Step 1: Orient

Summarize what you've read:

> "I've read this repository. It provides the Agentic-Agile methodology scaffold — structured templates for human-agent software development. I'm operating as your agentic-agile development partner. Let's configure this for your project."

### Step 2: Assess Familiarity

Ask one open question:

> "Are you familiar with Agentic-Agile development, or would you like a brief orientation before we configure your project?"

If orientation requested, provide a 3-4 sentence summary of the methodology from `MANIFESTO.md`, then proceed.

### Step 3: Collect Required Inputs

Collect each input one at a time. Do not batch questions.

1. **Project name and one-sentence description**
   > "What's the name of your project, and can you give me a one-sentence description of what it does?"

2. **Agent tool(s)**
   > "Which AI coding tool(s) will your team use? Available adapters: [list from `platform-adapters/agent-tools/`]. You can choose multiple — I'll configure each one. If your tool isn't listed, I can scaffold a minimal adapter."

3. **Issue tracker**
   > "Which issue tracker will you use? Available: [list from `platform-adapters/issue-trackers/`]. If yours isn't listed, I can defer this or scaffold a stub."

4. **CI/CD** (deferrable)
   > "Which CI/CD system? Available: [list from `platform-adapters/ci-cd/`]. This is deferrable — we can add it later if you're not ready."

5. **Contribution Framework** (deferrable)
   > "Would you like me to scaffold a Contribution Framework for your project? This includes CONTRIBUTING.md, CONTRIBUTING-AGENTS.md, CONTRIBUTORS.md, and contributor issue templates tailored to your project. You can defer this and add it later."

### Step 4: Confirm and Scaffold

Summarize all choices and ask for confirmation:

> "Here's what I'll set up:
> - **Project:** [name] — [description]
> - **Agent tool(s):** [tools]
> - **Issue tracker:** [tracker]
> - **CI/CD:** [choice or "deferred"]
> - **Contribution Framework:** [yes or "deferred"]
>
> I'll create the repo with two commits:
> 1. Exact copy of the template (clean provenance baseline)
> 2. All customizations applied
>
> Ready to proceed?"

On confirmation:
1. Create new repo directory
2. **Commit 1:** Copy template contents verbatim (no modifications)
3. Apply platform-specific adapter files to their target paths (per each adapter's `quickstart.md`)
4. Replace `[Project Name]` with actual project name throughout
5. Fill in project description where indicated
6. If Contribution Framework opted in: create `CONTRIBUTING.md`, `CONTRIBUTING-AGENTS.md`, `CONTRIBUTORS.md`, and `.github/contributor-templates/` with project-specific templates
7. **Commit 2:** All customizations in a single commit

### Step 5: Hand Off

> "Your project repo is ready at `[path]`. Your next step is to create your first backlog — define an epic, decompose it into stories using the issue template, and plan your first wave. See `docs/epic-decomposition-example.md` for a worked example."

### Step 6: Verification Checklist

Present this checklist and verify together:

**I'll verify (structural):**
- [ ] Commit 1 exists and is an unmodified copy of the template
- [ ] Commit 2 exists with only the expected customizations
- [ ] Agent context file is present at the correct target path
- [ ] Issue tracker templates are in place
- [ ] CI/CD config is present or explicitly deferred with a note
- [ ] No placeholder text remains in the configured files

**Please confirm (readiness):**
- [ ] Agent context file accurately describes the project
- [ ] Issue template matches how the team will write stories
- [ ] Branching strategy and wave structure make sense for team size
- [ ] You can successfully invoke your agent tool against the new repo

## Fallback: Non-Dialogue Entry

If you prefer to skip the guided dialogue, paste this prompt to your agent:

> "Configure this agentic-agile template for my project:
> - Project: [name] — [description]
> - Agent tool: [tool name]
> - Issue tracker: [tracker name]
> - CI/CD: [system name or 'defer']
> - Contribution Framework: [yes or 'defer']
>
> Create the repo with two commits: template copy first, then customizations."

---

<!-- PROJECT-SPECIFIC SECTIONS BELOW — filled in during onboarding -->
<!-- After onboarding, this area will contain: -->
<!-- ## Project Context -->
<!-- ## Architecture -->
<!-- ## Development Workflow -->
<!-- ## Current Status -->
```

**Step 3: Verify the file (VERIFY)**

Run:
```bash
test -f AGENTS.md && echo "PASS - file exists" || echo "FAIL"
```
Expected: `PASS - file exists`

Run:
```bash
grep -c '## What This Is\|## Repo Map\|## Your Role\|## Onboarding Protocol\|## Guided Onboarding Dialogue' AGENTS.md
```
Expected: `5` (all five required sections present)

Run:
```bash
grep -c '\[Project Name\]' AGENTS.md
```
Expected: `2` (title heading + one reference in state detection — confirms template state sentinel is present)

Run:
```bash
grep 'This role is additive' AGENTS.md | wc -l
```
Expected: `1` (additive persona clause present)

**Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "feat: create AGENTS.md onboarding orchestrator

Universal entry point for any agent reading the repo cold.
Implements state detection, three-state routing, 6-step guided
onboarding dialogue, and additive persona clause.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 2: Create CONTRIBUTING-AGENTS.md

**Files:**
- Create: `CONTRIBUTING-AGENTS.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f CONTRIBUTING-AGENTS.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the file (GREEN)**

Create `CONTRIBUTING-AGENTS.md` at the repository root with this exact content:

```markdown
# Contributing to Agentic-Agile Template — Agent Guide

This file is for AI coding agents contributing to **this methodology template**. If you're working in a derived project (one created via the onboarding dialogue), this file does not apply — look for that project's own `CONTRIBUTING-AGENTS.md`.

## Before You Start

1. **Read the design document** at `docs/history/2026-06-04-multi-platform-generalization-design.md` for architectural decisions and rationale.
2. **Create an issue** from the appropriate template in `.github/contributor-templates/`:
   - Adding a new adapter (agent tool, issue tracker, or CI/CD): use `.github/contributor-templates/new-adapter-story.md`
   - Adding a new quickstart combo: use `.github/contributor-templates/new-combo-story.md`
   - Changing methodology docs (MANIFESTO.md, STYLE.md, docs/): use `.github/contributor-templates/update-methodology-story.md`
3. **Use the PR template** at `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md` when submitting your pull request.

## Repository Architecture

This template uses a three-layer adapter system:

```
platform-adapters/
├── agent-tools/          ← agent context files (CLAUDE.md, copilot-instructions.md, etc.)
├── issue-trackers/       ← issue template configurations per platform
├── ci-cd/                ← CI/CD pipeline templates per platform
└── combos/               ← quickstart guides for specific stack combinations
```

Each layer is independent — adding a new agent tool does not affect issue trackers or CI/CD.

### Adapter Anatomy

Every adapter directory follows this structure:

```
platform-adapters/<layer>/<adapter-name>/
├── README.md              ← what this adapter is, when to use it (1 paragraph)
├── <target-filename>      ← named after the actual target file in derived repos
└── quickstart.md          ← where to place the file, tool-specific setup notes
```

**Naming rule:** The template file is named after its target filename (e.g., `CLAUDE.md`, not `context.md`). This prevents misplacement if accidentally copied without running onboarding.

## What Not to Break

These are the structural invariants you must preserve:

1. **AGENTS.md state detection** — The `[Project Name]` sentinel in the title must remain exactly as-is. It's how agents detect template vs. configured state.
2. **Two-commit provenance model** — The onboarding protocol creates repos with commit 1 (pristine template) and commit 2 (customizations). Don't add steps that modify the template before copy.
3. **Adapter independence** — Adapters in different layers must not reference each other. A CI/CD adapter cannot assume a specific agent tool is in use.
4. **README.md at every level** — Every directory in `platform-adapters/` must have a README.md explaining what it contains.
5. **Agentic-story format** — All issue templates (both `.github/ISSUE_TEMPLATE/` and `.github/contributor-templates/`) must follow the agentic-story format with: Summary, Context, Scope, Acceptance Criteria, Negative Constraints, Dependencies, File Ownership.

## Contribution Workflow

1. **Issue first** — Create an issue from the appropriate contributor template. Define scope, file ownership, and acceptance criteria before writing any content.
2. **Branch from main** — Use the naming convention: `feat/<short-description>` for new content, `fix/<short-description>` for corrections, `docs/<short-description>` for documentation.
3. **One adapter per PR** — Each pull request should add or modify exactly one adapter, one combo, or one methodology change. Never bundle unrelated changes.
4. **Validate structure** — Before submitting, verify:
   - All files in the adapter directory are present (README.md, target file, quickstart.md)
   - No placeholder text remains (search for `[`, `TODO`, `TBD`)
   - The README.md explains what the adapter does in one paragraph
   - The quickstart.md specifies the exact target path for the template file
5. **Reference the issue** — Your PR must reference the issue number it addresses.

## Adding a New Agent Tool Adapter

1. Create the issue from `.github/contributor-templates/new-adapter-story.md`
2. Create the directory: `platform-adapters/agent-tools/<tool-name>/`
3. Add `README.md` — one paragraph explaining the tool and when to use this adapter
4. Add the target-named template file (e.g., `CLAUDE.md`, `.cursorrules`, `.windsurfrules`)
5. Add `quickstart.md` — specify target path, filename, and any tool-specific configuration
6. Update `platform-adapters/agent-tools/README.md` to list the new adapter
7. Submit PR using `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md`

## Adding a New Quickstart Combo

1. Create the issue from `.github/contributor-templates/new-combo-story.md`
2. Create the file: `platform-adapters/combos/<agent>-<tracker>-<cicd>.md`
3. Follow the combo format: Stack, Status, Adapters used, Notes
4. Verify all referenced adapter directories exist
5. Update `platform-adapters/combos/README.md` to list the new combo
6. Submit PR

## Commit Message Format

Use conventional commits:

```
<type>: <short summary>

<optional body>

Closes #<issue-number>
```

Types: `feat` (new adapter/content), `fix` (corrections), `docs` (documentation), `chore` (maintenance)
```

**Step 3: Verify the file (VERIFY)**

Run:
```bash
test -f CONTRIBUTING-AGENTS.md && echo "PASS - file exists" || echo "FAIL"
```
Expected: `PASS - file exists`

Run:
```bash
grep -c 'contributor-templates' CONTRIBUTING-AGENTS.md
```
Expected: `7` or more (confirms references to all four contributor template files)

Run:
```bash
grep -c '## What Not to Break' CONTRIBUTING-AGENTS.md
```
Expected: `1`

**Step 4: Commit**

```bash
git add CONTRIBUTING-AGENTS.md
git commit -m "feat: create CONTRIBUTING-AGENTS.md for template contributors

Agent-specific contribution guide with structural invariants,
adapter anatomy, and explicit references to contributor templates.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 3: Create .github/contributor-templates/new-adapter-story.md

**Files:**
- Create: `.github/contributor-templates/new-adapter-story.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f .github/contributor-templates/new-adapter-story.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the directory and file (GREEN)**

```bash
mkdir -p .github/contributor-templates
```

Create `.github/contributor-templates/new-adapter-story.md` with this exact content:

```markdown
---
name: New Platform Adapter
about: Add a new agent tool, issue tracker, or CI/CD adapter to the template
title: 'feat: Add [tool-name] adapter to [layer]'
labels: 'enhancement, adapter'
assignees: ''
---

## Summary

<!-- What adapter are you adding? One sentence: "Add [tool] adapter to platform-adapters/[layer]/[name]/" -->

## Context / Motivation

<!-- Why should this adapter exist? Who uses this tool? What gap does it fill? -->

## Scope

### Files to Create or Modify

- `platform-adapters/<layer>/<adapter-name>/README.md` — adapter description
- `platform-adapters/<layer>/<adapter-name>/<target-filename>` — the template file (named after target)
- `platform-adapters/<layer>/<adapter-name>/quickstart.md` — placement and setup instructions
- `platform-adapters/<layer>/README.md` — update to list new adapter

### Interfaces to Implement

- README.md: one paragraph explaining the tool and when to use this adapter
- Target file: complete, ready-to-use template that works when placed at the target path
- quickstart.md: exact target path, filename, and any tool-specific configuration steps

### Invariants to Preserve

- Adapter directory follows the standard anatomy (README.md + target file + quickstart.md)
- Target file is named after its actual filename in derived repos
- No cross-layer dependencies (this adapter must not reference other layers)
- Parent layer README.md updated to include this adapter

## Acceptance Criteria

- [ ] Directory exists at `platform-adapters/<layer>/<adapter-name>/`
- [ ] `README.md` explains the adapter in one paragraph
- [ ] Target-named template file is complete and functional
- [ ] `quickstart.md` specifies exact target path and setup steps
- [ ] Parent layer `README.md` lists this adapter
- [ ] No placeholder text remains (`[`, `TODO`, `TBD`)
- [ ] Template file works correctly when placed at the target path

## Negative Constraints

- Does NOT modify adapters in other layers
- Does NOT modify `AGENTS.md` or the onboarding dialogue
- Does NOT add dependencies on other adapters

## Dependencies

- The parent layer directory must exist (`platform-adapters/<layer>/`)
- Parent layer `README.md` must exist (to update it)

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `platform-adapters/<layer>/<adapter-name>/README.md` | ✅ | New |
| `platform-adapters/<layer>/<adapter-name>/<target-filename>` | ✅ | New |
| `platform-adapters/<layer>/<adapter-name>/quickstart.md` | ✅ | New |
| `platform-adapters/<layer>/README.md` | ✅ | Update only |
```

**Step 3: Verify (VERIFY)**

Run:
```bash
test -f .github/contributor-templates/new-adapter-story.md && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

Run:
```bash
grep -c '## Summary\|## Context\|## Scope\|## Acceptance Criteria\|## Negative Constraints\|## Dependencies\|## File Ownership' .github/contributor-templates/new-adapter-story.md
```
Expected: `7` (all agentic-story sections present)

**Step 4: Commit**

```bash
git add .github/contributor-templates/new-adapter-story.md
git commit -m "feat: add new-adapter-story contributor template

Structured issue template for contributors adding new platform
adapters. Follows agentic-story format with adapter-specific
acceptance criteria.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 4: Create .github/contributor-templates/new-combo-story.md

**Files:**
- Create: `.github/contributor-templates/new-combo-story.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f .github/contributor-templates/new-combo-story.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the file (GREEN)**

Create `.github/contributor-templates/new-combo-story.md` with this exact content:

```markdown
---
name: New Quickstart Combo
about: Add a new stack combination quickstart guide
title: 'feat: Add [agent]-[tracker]-[cicd] combo'
labels: 'enhancement, combo'
assignees: ''
---

## Summary

<!-- What combination are you documenting? One sentence: "Add quickstart combo for [agent tool] + [issue tracker] + [CI/CD]" -->

## Context / Motivation

<!-- Why document this combination? Is it commonly used? Has it been tested? -->

## Scope

### Files to Create or Modify

- `platform-adapters/combos/<agent>-<tracker>-<cicd>.md` — the combo quickstart file
- `platform-adapters/combos/README.md` — update to list new combo

### Interfaces to Implement

Combo file must contain these sections:
- **Stack:** `<agent tool> · <issue tracker> · <CI/CD>`
- **Status:** `Maintained` | `Community` | `Stub`
- **Adapters used:** links to each adapter directory
- **Notes:** any combination-specific setup notes

### Invariants to Preserve

- Filename follows convention: `<agent>-<tracker>-<cicd>.md`
- All referenced adapter directories must actually exist
- Status tier matches actual level of support (see `platform-adapters/combos/README.md` for tier definitions)
- Combos `README.md` lists all combo files

## Acceptance Criteria

- [ ] File exists at `platform-adapters/combos/<agent>-<tracker>-<cicd>.md`
- [ ] Filename follows the `<agent>-<tracker>-<cicd>.md` convention
- [ ] Contains all required sections (Stack, Status, Adapters used, Notes)
- [ ] All referenced adapter directories exist in the repo
- [ ] Status tier is appropriate (Maintained = core team, Community = tested by community, Stub = scaffolded)
- [ ] `platform-adapters/combos/README.md` updated to include this combo
- [ ] No placeholder text remains

## Negative Constraints

- Does NOT create or modify adapter directories
- Does NOT change existing combo files
- Does NOT modify the combo README format

## Dependencies

- All adapter directories referenced in the combo must exist

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `platform-adapters/combos/<agent>-<tracker>-<cicd>.md` | ✅ | New |
| `platform-adapters/combos/README.md` | ✅ | Update only |
```

**Step 3: Verify (VERIFY)**

Run:
```bash
test -f .github/contributor-templates/new-combo-story.md && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

Run:
```bash
grep -c '## Summary\|## Context\|## Scope\|## Acceptance Criteria\|## Negative Constraints\|## Dependencies\|## File Ownership' .github/contributor-templates/new-combo-story.md
```
Expected: `7`

**Step 4: Commit**

```bash
git add .github/contributor-templates/new-combo-story.md
git commit -m "feat: add new-combo-story contributor template

Structured issue template for contributors adding quickstart
combo files. Enforces filename convention and section requirements.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 5: Create .github/contributor-templates/update-methodology-story.md

**Files:**
- Create: `.github/contributor-templates/update-methodology-story.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f .github/contributor-templates/update-methodology-story.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the file (GREEN)**

Create `.github/contributor-templates/update-methodology-story.md` with this exact content:

```markdown
---
name: Methodology Update
about: Propose changes to the Agentic-Agile methodology, core process, or documentation
title: 'docs: [brief description of methodology change]'
labels: 'documentation, methodology'
assignees: ''
---

## Summary

<!-- What methodology change are you proposing? One sentence. -->

## Context / Motivation

<!-- Why is this change needed? What problem does it solve or what improvement does it make? -->

## Impact Assessment

<!-- Methodology changes can have broad effects. Describe the impact: -->

### Files Affected

- [ ] `MANIFESTO.md` — values or principles
- [ ] `STYLE.md` — code/documentation conventions
- [ ] `AGENTS.md` — onboarding protocol or repo map
- [ ] `docs/agent-surface-selection.md` — agent surface guidance
- [ ] `docs/evaluation-framework.md` — measurement dimensions
- [ ] `docs/epic-decomposition-example.md` — decomposition patterns
- [ ] Other: `___`

### Downstream Effects

<!-- How does this affect: -->
- **Existing adapters:** <!-- do any adapters need updating? -->
- **Derived projects:** <!-- will projects already using the template need to update? -->
- **Onboarding dialogue:** <!-- does the onboarding flow need to change? -->

## Scope

### Files to Create or Modify

- `path/to/file.md` — description of changes

### Interfaces to Implement

- 

### Invariants to Preserve

- AGENTS.md `[Project Name]` sentinel must remain intact
- Agentic-story format in issue templates must not change
- Two-commit provenance model must not be altered
- Adapter independence principle must be maintained

## Acceptance Criteria

- [ ] Change is internally consistent with existing methodology
- [ ] Impact Assessment is complete (no unacknowledged downstream effects)
- [ ] All affected files are updated consistently
- [ ] No placeholder text introduced
- [ ] Change is documented in a way that agents can follow without ambiguity

## Negative Constraints

- Does NOT change adapter structure or anatomy
- Does NOT modify issue template format (agentic-story)
- Does NOT affect the two-commit provenance model

## Dependencies

- 

## File Ownership

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `path/to/file.md` | ✅ | |
```

**Step 3: Verify (VERIFY)**

Run:
```bash
test -f .github/contributor-templates/update-methodology-story.md && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

Run:
```bash
grep -c '## Impact Assessment' .github/contributor-templates/update-methodology-story.md
```
Expected: `1` (methodology-specific section present)

**Step 4: Commit**

```bash
git add .github/contributor-templates/update-methodology-story.md
git commit -m "feat: add update-methodology-story contributor template

Structured issue template for methodology changes with
impact assessment section for downstream effects analysis.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 6: Create .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md

**Files:**
- Create: `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md`

**Step 1: Verify file does not exist (RED)**

Run:
```bash
test -f .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md && echo "ALREADY EXISTS" || echo "PASS - file does not exist"
```
Expected: `PASS - file does not exist`

**Step 2: Create the file (GREEN)**

Create `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md` with this exact content:

```markdown
# Pull Request — Agentic-Agile Template Contribution

## Summary

<!-- One sentence: what does this PR add or change? -->

## Related Issue

<!-- Link to the GitHub Issue this PR addresses. Format: Closes #123 -->

Closes #

## Changes Made

<!-- Describe what you changed and why. Be specific about which files and what the change accomplishes. -->

- 

## Type of Change

- [ ] New adapter (`platform-adapters/<layer>/<name>/`)
- [ ] New quickstart combo (`platform-adapters/combos/`)
- [ ] Methodology update (MANIFESTO.md, STYLE.md, docs/)
- [ ] Bug fix / correction
- [ ] Documentation improvement
- [ ] Other: ___

## Testing Done

<!-- How did you verify your changes work correctly? -->

- [ ] All files in adapter directory present (README.md, target file, quickstart.md)
- [ ] No placeholder text remains (searched for `[`, `TODO`, `TBD`)
- [ ] Referenced paths/directories exist in the repo
- [ ] Markdown renders correctly (no broken formatting)
- [ ] Existing content not inadvertently modified

## Checklist

- [ ] Issue created and linked above
- [ ] Branch follows naming convention (`feat/`, `fix/`, `docs/`)
- [ ] One concern per PR (not bundling unrelated changes)
- [ ] Commit messages follow conventional format
- [ ] `CONTRIBUTING-AGENTS.md` invariants preserved (verified "What Not to Break" section)
- [ ] Parent README.md updated (if adding adapter or combo)

## Additional Notes

<!-- Anything else reviewers should know? -->
```

**Step 3: Verify (VERIFY)**

Run:
```bash
test -f .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

Run:
```bash
grep -c '## Summary\|## Related Issue\|## Changes Made\|## Testing Done\|## Checklist' .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md
```
Expected: `5` (all major PR template sections present)

**Step 4: Commit**

```bash
git add .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md
git commit -m "feat: add CONTRIBUTOR_PR_TEMPLATE for template contributions

PR description template with adapter compliance checklist,
testing verification, and structural invariant checks.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 7: Rewrite README.md for Multi-Platform Framing

**Files:**
- Modify: `README.md`

**Step 1: Verify current state (RED)**

Run:
```bash
grep -c 'CLAUDE.md' README.md
```
Expected: `3` or more (confirms Claude-centric references still present — this is what we're fixing)

**Step 2: Rewrite the file (GREEN)**

Replace the entire contents of `README.md` with:

```markdown
# Agentic-Agile Template

A starter template for teams adopting [Agentic-Agile Development](https://developer.microsoft.com/blog/): the practice of producing production-ready software through structured human-agent collaboration.

## What is Agentic-Agile Development?

Agentic-Agile Development bridges Agile process values with the capabilities of AI coding agents. It is a methodology for building software through human-agent partnerships, not just using agents as autocomplete tools.

The core insight: agents fail not because of model capability, but because of coordination breakdown. When you give an agent a vague prompt, you get vague output. When you give it a well-specified story with acceptance criteria, file boundaries, and negative constraints, you get production-quality code. The specification is the program.

Agentic-Agile Development provides the process layer that makes agent collaboration repeatable: structured backlogs, spec-first stories, wave-based parallel execution, built-in governance, and continuous measurement across eight dimensions. Teams that adopt these patterns shift from "hoping the agent gets it right" to systematically improving their human-agent partnership over time.

## What's in This Repo

| File | Description |
|------|-------------|
| [`AGENTS.md`](AGENTS.md) | Universal onboarding orchestrator. The single entry point for any AI coding agent — detects repo state and guides project configuration. |
| [`MANIFESTO.md`](MANIFESTO.md) | The Agentic-Agile Manifesto: 5 values and 13 principles for human-agent software development. |
| [`STYLE.md`](STYLE.md) | Style guide template covering code conventions, documentation, commit messages, and PR format. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Human-facing contribution guidelines following the Agentic-Agile workflow. |
| [`CONTRIBUTING-AGENTS.md`](CONTRIBUTING-AGENTS.md) | Agent-specific contribution guide for modifying this template. |
| [`SECURITY.md`](SECURITY.md) | Standard security policy and vulnerability reporting process. |
| [`LICENSE`](LICENSE) | MIT License. |
| [`mcp.json`](mcp.json) | Example MCP (Model Context Protocol) server configuration for agent tooling. |
| [`platform-adapters/`](platform-adapters/) | Three-layer adapter system for agent tools, issue trackers, and CI/CD. |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) | Issue template for structured Agentic-Agile stories. |
| [`.github/contributor-templates/`](.github/contributor-templates/) | Issue and PR templates for contributing to this template. |
| [`docs/`](docs/) | Methodology documentation: agent surface selection, evaluation framework, epic decomposition example. |

## Platform Adapter Architecture

This template supports **any combination** of AI coding tools, issue trackers, and CI/CD systems through a three-layer adapter architecture:

```
platform-adapters/
├── agent-tools/        ← Claude, GitHub Copilot, Cursor, Windsurf, Cline, aider
├── issue-trackers/     ← GitHub Issues, Azure DevOps, JIRA
├── ci-cd/              ← GitHub Actions, Azure Pipelines
└── combos/             ← Quickstart guides for specific stack combinations
```

Each layer is independent. You choose one (or more) from each layer during onboarding. If your tool isn't listed, you can scaffold a minimal adapter or contribute one.

## Getting Started

### 1. Point Your Agent at This Repo

Open this repository with your preferred AI coding agent (Claude, GitHub Copilot, Cursor, Windsurf, Cline, aider, or any LLM-based tool). The agent will read `AGENTS.md` and detect that this is an unconfigured template.

### 2. Follow the Guided Onboarding

Your agent will walk you through a 6-step configuration dialogue:

1. **Orient** — The agent acknowledges the template and its role
2. **Assess** — Quick check on your familiarity with the methodology
3. **Collect inputs** — Project name, agent tool(s), issue tracker, CI/CD, contribution framework
4. **Scaffold** — Two-commit repo creation (template copy + customizations)
5. **Hand off** — Your configured repo is ready
6. **Verify** — Structural and readiness checklist

The result is a new repository configured for your specific stack with clean two-commit provenance.

### 3. Create Your First Backlog

Use the issue template at `.github/ISSUE_TEMPLATE/agentic-story.md` to create your first stories:

1. **Define an epic** — a feature too large for a single story.
2. **Decompose it** — break it into stories with explicit file ownership. See [`docs/epic-decomposition-example.md`](docs/epic-decomposition-example.md) for a worked example.
3. **Map dependencies** — determine which stories depend on which.
4. **Assign to waves** — group independent stories into parallel execution batches.

### 4. Run Your First Wave

1. Create a feature branch for each story in the wave.
2. Assign each story to an agent (CLI agent, cloud coding agent, or IDE agent).
3. Let agents execute in parallel. Each agent works in its own branch on its own files.
4. Review all PRs at the wave's review gate.
5. Merge, then launch the next wave.

See [`docs/agent-surface-selection.md`](docs/agent-surface-selection.md) for guidance on choosing the right agent surface for each task type.

### 5. Measure and Improve

After your first wave, start measuring:

- **Merge conflicts** — should be zero (if not, improve your decomposition)
- **First-pass acceptance rate** — how often agent output matches the spec without rework
- **Escaped defects** — bugs found after merge that review should have caught

See [`docs/evaluation-framework.md`](docs/evaluation-framework.md) for the full eight-dimension measurement framework.

## The Agentic-Agile Manifesto

This template is grounded in the [Agentic-Agile Manifesto](MANIFESTO.md), which defines five values:

1. **Specifications and contracts** over open-ended prompts
2. **Human-agent partnership** over one-directional delegation
3. **Parallel independence** over sequential handoffs
4. **Built-in governance** over bolted-on compliance
5. **Continuous measurement** over post-hoc assessment

And 13 principles for human-agent software development. Read the full manifesto: [`MANIFESTO.md`](MANIFESTO.md)

## Blog Series

This template accompanies the Agentic-Agile Development blog series:

- [Why Agent Development Needs Agile (Not Just Prompts)](https://developer.microsoft.com/blog/)
- [Backlog Grooming and Retrospectives for Human-Agent Teams](https://developer.microsoft.com/blog/)
- [Spec-First Decomposition: The Foundation of Agent Parallelism](https://developer.microsoft.com/blog/)
- [Agent Swarming in Practice: From Days to Hours](https://developer.microsoft.com/blog/)
- [Risks, Governance, and Mitigations](https://developer.microsoft.com/blog/)
- [Toward a Repeatable Model for Human-Agent Development](https://developer.microsoft.com/blog/)

## MCP Configuration

The `mcp.json` file configures [Model Context Protocol](https://modelcontextprotocol.io/) servers that extend your agent's capabilities. MCP servers give agents access to external tools and data sources.

### Server Entries

| Server | Purpose | Configuration |
|--------|---------|---------------|
| `github` | Gives the agent access to GitHub APIs: reading issues, creating PRs, searching code across repositories. | Set `GITHUB_PERSONAL_ACCESS_TOKEN` to a GitHub PAT with appropriate scopes (`repo`, `read:org`). |
| `filesystem` | Gives the agent read/write access to a specific directory on your file system. | Replace `/path/to/allowed/directory` with the actual directory path you want the agent to access. |
| `memory` | Gives the agent a persistent memory store across sessions for storing and retrieving facts. | No additional configuration required. |

### How to Use

1. Copy `mcp.json` to your project root.
2. Replace placeholder values (PAT tokens, directory paths) with your actual configuration.
3. Add or remove server entries based on the tools your agents need.
4. Never commit real credentials. Use environment variable references or a `.env` file excluded from version control.

### Adding More Servers

Browse available MCP servers at [modelcontextprotocol.io](https://modelcontextprotocol.io/) or the [MCP Servers repository](https://github.com/modelcontextprotocol/servers). Common additions include database servers, web search, and documentation fetching.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for human contribution guidelines, or [`CONTRIBUTING-AGENTS.md`](CONTRIBUTING-AGENTS.md) if you're an AI agent modifying this template.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
```

**Step 3: Verify (VERIFY)**

Run:
```bash
grep -c 'CLAUDE.md' README.md
```
Expected: `0` (no Claude-centric references as primary context file)

Run:
```bash
grep -c 'AGENTS.md' README.md
```
Expected: `3` or more (AGENTS.md is now the primary entry point)

Run:
```bash
grep -c 'platform-adapters' README.md
```
Expected: `3` or more (three-layer architecture explained)

Run:
```bash
grep 'CONTRIBUTING-AGENTS.md' README.md | wc -l
```
Expected: `2` or more (referenced in table and Contributing section)

**Step 4: Commit**

```bash
git add README.md
git commit -m "feat: rewrite README.md for multi-platform framing

Remove Claude-centric language. Present AGENTS.md as universal
entry point. Explain three-layer adapter architecture. Update
Getting Started to reference onboarding dialogue.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 8: Update CONTRIBUTING.md with Pointer to CONTRIBUTING-AGENTS.md

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: Verify pointer does not exist (RED)**

Run:
```bash
grep -c 'CONTRIBUTING-AGENTS.md' CONTRIBUTING.md
```
Expected: `0` (no existing reference — this is what we're adding)

**Step 2: Add the section (GREEN)**

Insert the following section immediately after the `## How to Contribute` heading's content (after line 28, before `### What Makes a Good Contribution`):

Add this block between the "Contribution Workflow" numbered list and "### What Makes a Good Contribution":

```markdown

### Agent Contributors

If you're an AI coding agent contributing to this template, read [`CONTRIBUTING-AGENTS.md`](CONTRIBUTING-AGENTS.md) for agent-specific guidance including structural invariants, adapter anatomy, and contributor templates.

```

The exact edit: insert the three lines above (with surrounding blank lines) between line 28 (end of the numbered workflow list) and line 30 (`### What Makes a Good Contribution`).

**Step 3: Verify (VERIFY)**

Run:
```bash
grep -c 'CONTRIBUTING-AGENTS.md' CONTRIBUTING.md
```
Expected: `1`

Run:
```bash
grep '### Agent Contributors' CONTRIBUTING.md | wc -l
```
Expected: `1`

Run:
```bash
wc -l CONTRIBUTING.md
```
Expected: approximately `76` (original 72 + 4 new lines)

**Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "feat: add agent contributors pointer to CONTRIBUTING.md

Light update — one section directing agent contributors to
CONTRIBUTING-AGENTS.md for agent-specific guidance.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Task 9: Convert .github/copilot-instructions.md to Stub

**Files:**
- Modify: `.github/copilot-instructions.md`

**Step 1: Verify current state (RED)**

Run:
```bash
wc -l .github/copilot-instructions.md
```
Expected: `58` (confirms full template content still present — this is what we're replacing)

**Step 2: Replace with stub (GREEN)**

Replace the entire contents of `.github/copilot-instructions.md` with:

```markdown
# Copilot Instructions

> **This file is a stub.** The full GitHub Copilot agent context template has moved to the platform adapters directory.

## Where to Find the Full Content

The complete Copilot instructions template lives at:

```
platform-adapters/agent-tools/github-copilot/copilot-instructions.md
```

This stub file remains at `.github/copilot-instructions.md` because GitHub automatically discovers and applies files at this path. Once `platform-adapters/` is fully populated (Phase 2), the adapter's `quickstart.md` will explain how to copy the template content here for your project.

## Why This Moved

The Agentic-Agile template now supports multiple AI coding tools through a platform adapter architecture. Each tool's configuration lives in its own adapter directory under `platform-adapters/agent-tools/`. This keeps the repository root clean and makes it clear which files belong to which tool.

See `AGENTS.md` for the universal entry point that works with any agent.
```

**Step 3: Verify (VERIFY)**

Run:
```bash
wc -l .github/copilot-instructions.md
```
Expected: approximately `19` (confirms stub is short)

Run:
```bash
grep -c 'platform-adapters/agent-tools/github-copilot' .github/copilot-instructions.md
```
Expected: `1` (path to canonical location present)

Run:
```bash
grep -c 'AGENTS.md' .github/copilot-instructions.md
```
Expected: `1` (reference to universal entry point)

**Step 4: Commit**

```bash
git add .github/copilot-instructions.md
git commit -m "feat: convert copilot-instructions.md to stub

Replace full template content with stub pointing to
platform-adapters/agent-tools/github-copilot/. File remains
at .github/ path for GitHub auto-discovery.

Closes #<ISSUE_NUMBER_FROM_TASK_0>

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Final Validation

After all tasks are complete, run this comprehensive check:

```bash
echo "=== Phase 1 Structural Validation ==="

echo ""
echo "--- File Existence ---"
for f in AGENTS.md CONTRIBUTING-AGENTS.md .github/contributor-templates/new-adapter-story.md .github/contributor-templates/new-combo-story.md .github/contributor-templates/update-methodology-story.md .github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md; do
  test -f "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "--- Modified Files ---"
test -f README.md && echo "PASS: README.md exists" || echo "FAIL: README.md"
test -f CONTRIBUTING.md && echo "PASS: CONTRIBUTING.md exists" || echo "FAIL: CONTRIBUTING.md"
test -f .github/copilot-instructions.md && echo "PASS: .github/copilot-instructions.md exists" || echo "FAIL"

echo ""
echo "--- AGENTS.md Sections ---"
grep -c '## What This Is\|## Repo Map\|## Your Role\|## Onboarding Protocol\|## Guided Onboarding Dialogue' AGENTS.md

echo ""
echo "--- Placeholder Check (excluding AGENTS.md sentinel) ---"
grep -rn '\[FILL\|TODO\|TBD' AGENTS.md CONTRIBUTING-AGENTS.md README.md .github/contributor-templates/ | grep -v '\[Project Name\]' | wc -l

echo ""
echo "--- Cross-references ---"
grep -l 'CONTRIBUTING-AGENTS.md' CONTRIBUTING.md AGENTS.md README.md | wc -l

echo ""
echo "--- Claude-centric removal ---"
grep -c 'CLAUDE.md' README.md

echo ""
echo "--- Copilot stub ---"
wc -l .github/copilot-instructions.md

echo ""
echo "=== Validation Complete ==="
```

Expected output:
- All files PASS
- AGENTS.md sections: `5`
- Placeholder check: `0`
- Cross-references: `3` (all three files reference CONTRIBUTING-AGENTS.md)
- Claude-centric: `0`
- Copilot stub: approximately `19` lines
