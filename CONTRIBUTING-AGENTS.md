# Contributing to the Agentic-Agile Template (Agent Guide)

> **Agent-specific contribution guide.** This file is the counterpart to `CONTRIBUTING.md` — just as `AGENTS.md` is the agent-facing version of `README.md`, this file is the agent-facing version of `CONTRIBUTING.md`. Read it completely before modifying anything in this repository.

---

## Before You Start

### 1. Read the design document

All structural decisions for this repository are recorded in:

```
docs/history/2026-06-04-multi-platform-generalization-design.md
```

Read it before making any changes. It explains the three-layer adapter architecture, the adapter anatomy, the onboarding dialogue protocol, and the contributor templates model. Changes that contradict the design document require explicit discussion in a GitHub Issue before proceeding.

### 2. Open an issue using the correct contributor template

This repository stores contributor issue templates separately from the end-user issue templates that downstream projects inherit. The contributor templates live at:

```
.github/contributor-templates/
├── new-adapter-story.md          ← adding a new agent-tool, issue-tracker, or CI/CD adapter
├── new-combo-story.md            ← adding a new quickstart combo
├── update-methodology-story.md   ← changes to MANIFESTO.md, docs/, or core process
└── CONTRIBUTOR_PR_TEMPLATE.md    ← PR description template for all contributions
```

Select the template that matches your contribution type:

| Change type | Template to use |
|-------------|-----------------|
| New agent-tool, issue-tracker, or CI/CD adapter | `.github/contributor-templates/new-adapter-story.md` |
| New quickstart combo | `.github/contributor-templates/new-combo-story.md` |
| Changes to MANIFESTO.md, docs/, or core process | `.github/contributor-templates/update-methodology-story.md` |

Create the issue before writing any code. The issue anchors your branch, scopes the change, and ensures no duplicate work is in progress.

### 3. Use the PR template when submitting

When opening a pull request, use `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md` as your PR description template. It includes the required sections: change summary, affected files, structural invariants verified, and evidence of testing.

---

## Repository Architecture

This repository uses a **three-layer adapter system** inside `platform-adapters/`. Each layer is independent. Combos assemble layers without duplicating their content.

### Directory Structure

> **Target structure (Phase 2):** The tree below shows the intended full structure once all platform adapters are implemented. The `platform-adapters/` layer directories exist but most individual adapter subdirectories and combo files are not yet present. Refer to what actually exists on disk before navigating to a specific path.

```
agentic-agile-template/
├── AGENTS.md                          ← universal agent entry point (onboarding orchestrator)
├── README.md                          ← human-facing project overview
├── MANIFESTO.md                       ← 5 values and 13 principles for human-agent development
├── STYLE.md                           ← code conventions, commit format, PR structure
├── CONTRIBUTING.md                    ← human-facing contribution guide
├── CONTRIBUTING-AGENTS.md             ← this file — agent-facing contribution guide
├── SECURITY.md                        ← security policy
├── LICENSE
├── mcp.json                           ← example MCP server configuration
├── docs/
│   ├── agent-surface-selection.md
│   ├── evaluation-framework.md
│   ├── epic-decomposition-example.md
│   └── history/                       ← design and implementation history
├── platform-adapters/
│   ├── README.md                      ← adapter system overview and architecture diagram
│   ├── agent-tools/
│   │   ├── README.md                  ← layer overview and three-file anatomy
│   │   ├── claude/
│   │   │   ├── README.md
│   │   │   ├── CLAUDE.md              ← named after the target file
│   │   │   └── quickstart.md
│   │   ├── github-copilot/
│   │   │   ├── README.md
│   │   │   ├── copilot-instructions.md
│   │   │   └── quickstart.md
│   │   ├── cursor/
│   │   ├── windsurf/
│   │   ├── cline/
│   │   └── aider/
│   ├── issue-trackers/
│   │   ├── README.md
│   │   ├── github/
│   │   ├── azure-devops/
│   │   └── jira/
│   ├── ci-cd/
│   │   ├── README.md
│   │   └── github-actions/
│   └── combos/
│       ├── README.md                  ← combo format, status tiers, naming convention
│       ├── github-copilot-github-github-actions.md
│       ├── claude-github-github-actions.md
│       └── cursor-github-github-actions.md
└── .github/
    ├── ISSUE_TEMPLATE/                ← end-user issue templates (auto-discovered by GitHub)
    │   └── agentic-story.md
    └── contributor-templates/         ← templates for contributing to THIS template repo
        ├── new-adapter-story.md
        ├── new-combo-story.md
        ├── update-methodology-story.md
        └── CONTRIBUTOR_PR_TEMPLATE.md
```

### The Three Layers

| Layer | Directory | Purpose |
|-------|-----------|---------|
| Agent Tools | `platform-adapters/agent-tools/` | AI coding agent configuration (context files, MCP servers, instructions) |
| Issue Trackers | `platform-adapters/issue-trackers/` | Story templates and backlog management per tracker |
| CI/CD | `platform-adapters/ci-cd/` | Pipeline and workflow configurations |
| Combos | `platform-adapters/combos/` | Pre-assembled, tested combinations of all three layers |

Each layer is **independent**. An agent-tools adapter must not reference a specific issue tracker or CI/CD system — that coupling belongs in combo files. Layers compose at the combo level, not within individual adapters.

---

## Adapter Anatomy

Every adapter directory — regardless of layer — follows a consistent three-file structure:

```
platform-adapters/<layer>/<adapter-name>/
├── README.md            ← what this adapter is, when to use it, prerequisites
├── <target-filename>    ← named after the actual target file in the project
└── quickstart.md        ← where to place the file, tool-specific configuration steps
```

### README.md

Overview of the adapter: which tool it configures, what it produces, prerequisites, and any tool-specific conventions that affect how agentic-agile stories should be written for that tool.

### Target-named file

The template file is **named after its target filename**, not a generic name like `context.md`. Examples:

- `platform-adapters/agent-tools/claude/CLAUDE.md` — target is `CLAUDE.md` at the project root
- `platform-adapters/agent-tools/github-copilot/copilot-instructions.md` — target is `.github/copilot-instructions.md`

This naming prevents misplacement: if a file is accidentally copied without the full onboarding flow, it lands with the correct name.

### quickstart.md

Step-by-step placement instructions: the exact path where the file should be copied, any filename requirements, and tool-specific setup steps (IDE settings, MCP server configuration, etc.).

---

## What Not to Break

These five invariants are structural requirements of this repository. Verify each one holds before submitting a PR.

### 1. AGENTS.md state detection

`AGENTS.md` detects its own state by inspecting the first `#` heading for the sentinel `[Project Name]`. The three states — template, configured, contributor — must remain navigable from this single detection point. Do not modify the state detection logic, the sentinel string, or the section headings that state detection routes to without also updating the routing table.

### 2. Two-commit provenance model

The onboarding dialogue creates exactly two commits: first an exact copy of unmodified template files as a baseline, then a second commit applying project customizations. This model gives downstream projects a clean diff anchor. Do not introduce changes that collapse these into one commit, add a third commit, or require the baseline and customization commits to touch overlapping files.

### 3. Adapter independence

Each adapter layer must function independently of the other two layers. An agent-tools adapter must not reference a specific issue tracker or CI/CD system. An issue-tracker adapter must not reference a specific agent tool. Cross-layer integration belongs exclusively in combo files. Breaking this invariant forces combo files to hard-code adapter internals, making future adapter updates break existing combos.

### 4. README.md at every level

Every directory under `platform-adapters/` — including each individual adapter directory — must contain a `README.md`. This invariant ensures that any agent or human can navigate to any level of the tree and immediately understand what they are looking at. A new adapter without a `README.md` is incomplete, regardless of how complete its template file and quickstart are.

### 5. Agentic-story format

The `.github/ISSUE_TEMPLATE/agentic-story.md` template is the story format that downstream projects adopt for their own backlogs. Its three core sections — Scope, File Ownership, and Acceptance Criteria — must remain stable. Downstream teams write their own stories against this format, and breaking it forces all derived projects to update their issue workflows. Changes to the agentic-story format require an issue using `.github/contributor-templates/update-methodology-story.md` and explicit justification.

---

## Contribution Workflow

### Overview

1. **Issue first.** Open a GitHub Issue using the appropriate contributor template before writing any code.
2. **Branch from main.** Create a feature branch from `main` with a descriptive name (e.g., `feat/add-windsurf-adapter`).
3. **One adapter or combo per PR.** Keep pull requests tightly scoped. One new adapter or one new combo per PR. Do not bundle unrelated changes.
4. **Validate structure.** Before opening a PR, verify the five structural invariants in the **What Not to Break** section above.
5. **Reference the issue.** Every PR must reference its originating issue number in the description.
6. **Use the PR template.** Complete all sections of `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md` in your PR description.

### Checking Your Work Before Submitting

Walk through this checklist before marking a PR ready for review:

- [ ] Issue opened using the correct contributor template
- [ ] Branch branched from current `main`
- [ ] PR touches only files in scope for the issue
- [ ] All five structural invariants verified
- [ ] `README.md` present at every new directory level
- [ ] No cross-layer dependencies introduced in adapter files
- [ ] PR description completed using `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md`
- [ ] Issue number referenced in PR description

---

## Adding a New Agent Tool Adapter

1. **Open an issue** using `.github/contributor-templates/new-adapter-story.md`. Define the agent tool, the target filename it reads, and the file's expected location in a project.

2. **Create the adapter directory:**
   ```
   platform-adapters/agent-tools/<tool-name>/
   ```

3. **Add `README.md`.** Include: which agent this adapter configures, prerequisites, what the adapter produces, and any agent-specific conventions that affect how agentic-agile stories should be structured for this tool.

4. **Add the target-named file.** Name it after the filename the agent reads in a real project (e.g., if the agent reads `.windsurfrules`, name the file `windsurfrules` or `.windsurfrules` as appropriate). The file should contain the agent context template — instructions that tell the agent about the agentic-agile workflow, story anatomy, and project conventions.

5. **Add `quickstart.md`.** Document: the exact path where the file should be placed in a target project, whether the filename changes (e.g., the file is stored without a leading dot in the adapter but placed with one in the project), and any tool-specific setup steps.

6. **Verify adapter independence.** The three files must not reference any specific issue tracker, CI/CD system, or combo configuration. Cross-layer integration belongs in combo files.

7. **Update `platform-adapters/agent-tools/README.md`** to add the new adapter to the Available Adapters table.

8. **Open a PR** using `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md`. Reference the issue from step 1. Include the new adapter directory, the updated `agent-tools/README.md`, and nothing else.

---

## Adding a New Quickstart Combo

1. **Open an issue** using `.github/contributor-templates/new-combo-story.md`. Identify the three constituent adapters (agent-tool, issue-tracker, CI/CD) and verify they all exist before proceeding.

2. **Confirm all three layer adapters exist:**
   - `platform-adapters/agent-tools/<tool>/`
   - `platform-adapters/issue-trackers/<tracker>/`
   - `platform-adapters/ci-cd/<system>/` (or document a known gap)

3. **Name the combo file** using the strict convention:
   ```
   platform-adapters/combos/<agent-tool>-<issue-tracker>-<ci-cd>.md
   ```
   Use the layer slugs from each adapter directory name (e.g., `github-copilot`, `claude`, `cursor` for `<agent-tool>`; `github` for `<issue-tracker>`). The ci-cd layer is planned for v2 — until those adapters ship, use the forward-looking slug `github-actions` (matching the currently-shipped Stubs) or `none` for combos that are intentionally CI/CD-agnostic; see `platform-adapters/combos/README.md` for the authoritative naming guidance.

4. **Create the combo file** following the structure defined in `platform-adapters/combos/README.md`. Set status to **Stub** initially.

5. **Fill in the required sections defined in `platform-adapters/combos/README.md`:** Stack, Status, Adapters Used, Quick Setup, and Notes. Additional sections (Prerequisites, Verification, Known Issues, Changelog, etc.) are optional but encouraged once the combo has been tested end-to-end.

6. **Test the combo end-to-end** on a real repository. Verify the full setup path, not just that the files exist.

7. **Update status to Community** once verified. Include a link to the example repository used for testing.

8. **Update `platform-adapters/combos/README.md`** to add the new combo to the Available Combos table.

9. **Open a PR** using `.github/contributor-templates/CONTRIBUTOR_PR_TEMPLATE.md`. Reference the issue from step 1. Include the new combo file and the updated `combos/README.md`.

---

## Commit Message Format

Use conventional commits with types appropriate to this repository:

```
<type>: <short summary>

<optional body — explain why, not just what>
```

**Types:**

| Type | Use for |
|------|---------|
| `feat` | New adapters, combos, or features |
| `docs` | Documentation additions or corrections |
| `template` | Changes to issue templates, PR templates, or contributor templates |
| `fix` | Corrections to existing adapters, combos, or docs |
| `chore` | Maintenance, renaming, restructuring without functional change |

**Examples:**

```
feat: add windsurf agent-tool adapter

Adds three-file adapter for Windsurf (Codeium) under platform-adapters/agent-tools/windsurf/.
Target file is .windsurfrules. Verified against Windsurf v1.2 on macOS.
Closes #42.
```

```
template: update new-adapter-story.md to include quickstart verification step

The previous template did not prompt contributors to verify the quickstart.md
end-to-end. Added a verification step as required acceptance criterion.
```

When a commit is generated with the assistance of an AI agent, include a `Co-Authored-By` trailer that identifies the specific agent used. Examples:

```
Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

```
Co-Authored-By: Copilot <223556219+Copilot@users.noreply.github.com>
```

Use the trailer that matches the tool used to produce the commit. If multiple agents materially contributed, include one trailer per agent. Do not use a trailer for any agent that did not contribute to the commit.
