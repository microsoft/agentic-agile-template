# Multi-Platform Generalization Design

## Goal

Generalize the `agentic-agile-template` repository from a GitHub/Claude-centric template into a multi-platform template that supports any combination of agentic development tools, issue trackers, and CI/CD systems — while keeping the repository maintainable for a small team.

## Background

The current template is tightly coupled to Claude (via `CLAUDE.md`) and GitHub (via `.github/` conventions). Teams using Cursor, Copilot, Windsurf, Cline, aider, Azure DevOps, or JIRA cannot adopt the methodology without manual adaptation. This design introduces a platform adapter layer that decouples the methodology from any specific toolchain while preserving the existing GitHub/Claude path as a first-class supported combination.

## Approach: Hybrid Layered + Quickstart Combos

Three independent component layers inside a `platform-adapters/` directory (agent tools, issue trackers, CI/CD), with a quickstart combo index that helps users navigate their specific stack combination. A new `AGENTS.md` file serves as the universal onboarding orchestrator — the single entry point for any agent reading the repo cold.

---

## Architecture

### Repository Structure

```
agentic-agile-template/
├── AGENTS.md                          ← onboarding orchestrator (replaces CLAUDE.md at root)
├── README.md                          ← rewritten for multi-platform framing
├── MANIFESTO.md                       ← unchanged
├── STYLE.md                           ← unchanged
├── CONTRIBUTING.md                    ← light update: pointer to CONTRIBUTING-AGENTS.md
├── CONTRIBUTING-AGENTS.md             ← agent-specific contribution guide
├── SECURITY.md                        ← unchanged
├── LICENSE                            ← unchanged
├── mcp.json                           ← unchanged
├── docs/                              ← unchanged
│   ├── agent-surface-selection.md
│   ├── evaluation-framework.md
│   └── epic-decomposition-example.md
├── platform-adapters/
│   ├── README.md
│   ├── agent-tools/
│   │   ├── README.md
│   │   ├── claude/
│   │   │   ├── README.md
│   │   │   ├── CLAUDE.md              ← named after target file
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
│   │   ├── github/                    ← links to existing .github/ISSUE_TEMPLATE/
│   │   ├── azure-devops/
│   │   └── jira/
│   ├── ci-cd/
│   │   ├── README.md
│   │   ├── github-actions/            ← links to existing .github/workflows/
│   │   └── azure-pipelines/
│   └── combos/
│       ├── README.md
│       ├── claude-github-github-actions.md
│       ├── cursor-github-github-actions.md
│       └── copilot-github-github-actions.md
├── .github/                           ← unchanged (GitHub-specific files stay here)
│   ├── copilot-instructions.md        ← stub pointing to platform-adapters/
│   ├── ISSUE_TEMPLATE/
│   ├── contributor-templates/         ← templates for contributing to THIS template
│   │   ├── new-adapter-story.md
│   │   ├── new-combo-story.md
│   │   ├── update-methodology-story.md
│   │   └── CONTRIBUTOR_PR_TEMPLATE.md
│   └── workflows/
└── docs/history/
```

README.md files exist at every sub-level of `platform-adapters/` and within each adapter directory.

---

## Components

### AGENTS.md — Onboarding Orchestrator

AGENTS.md is the thin onboarding orchestrator — the single entry point for any agent reading the repo cold. It detects its own state and branches accordingly.

**Internal structure:**

```markdown
# [Project Name] — Agentic-Agile Template

## What This Is
One-paragraph description of the agentic-agile methodology and what this template provides.

## Repo Map
Annotated directory tree — every file and its purpose in one glance.

## Your Role
- One-sentence statement: what the agentic-partner role means
- One-sentence additive clause: "This role is additive — if you've been given a
  specific persona or instructions by your operator or user, retain those while
  also adopting the agentic-partner role described here."
- Branch instruction:
  - Template state → run onboarding
  - Configured state → orient and proceed
  - Contributor state → read CONTRIBUTING-AGENTS.md

## Onboarding Protocol
State detection and routing logic.

## Guided Onboarding Dialogue
Full step-by-step protocol (see Onboarding Dialogue Protocol section below).

## [Project-specific sections — filled in during onboarding]
```

**Key design principles:**

- No greeting — the agent acknowledges understanding and steps into role immediately
- State detection via placeholder project name
- Works with any capable LLM agent — no tool-specific dependency
- Fallback: includes a prompt template for users who prefer non-dialogue entry
- Stays thin — methodology content lives in adapters and docs, not here

---

### Platform Adapter Anatomy

Each adapter directory follows a consistent structure:

```
platform-adapters/agent-tools/<tool>/
├── README.md          ← what this adapter is, when to use it, what it produces (1 paragraph)
├── <target-filename>  ← named after the actual target file (e.g., CLAUDE.md, copilot-instructions.md)
└── quickstart.md      ← where to place the file, what path/filename to use, tool-specific config
```

**Naming rule:** The template file is named after its target filename (not a generic `context.md`). This prevents misplacement — if accidentally copied without onboarding, it lands with the right name. The `quickstart.md` specifies both the target path and the filename.

**Issue tracker and CI/CD adapters** follow the same pattern, with template files appropriate to their artifact type (issue template YAML, pipeline YAML, etc.).

---

### Contributing Guidelines

The `CONTRIBUTING.md` + `CONTRIBUTING-AGENTS.md` pair mirrors the `README.md` + `AGENTS.md` pattern:

- `CONTRIBUTING.md` — human-facing contribution guide (updated with a pointer to CONTRIBUTING-AGENTS.md)
- `CONTRIBUTING-AGENTS.md` — agent-specific contribution guide with structural intent, design rationale, and "what not to break" guidance for agents modifying the template itself

`AGENTS.md` includes a one-liner: *"If you're modifying this template itself, read `CONTRIBUTING-AGENTS.md` first."*

#### Contributor Templates (Template Repo)

`CONTRIBUTING-AGENTS.md` references a set of issue/PR templates specifically for contributors to this template repository, stored at `.github/contributor-templates/`:

```
.github/contributor-templates/
├── new-adapter-story.md          ← adding a new agent-tool/issue-tracker/CI adapter
├── new-combo-story.md            ← adding a new quickstart combo
├── update-methodology-story.md   ← changes to MANIFESTO, docs/, or core process
└── CONTRIBUTOR_PR_TEMPLATE.md    ← PR description template for contributions
```

These are distinct from `.github/ISSUE_TEMPLATE/` (which GitHub auto-discovers for end users of derived projects). The contributor templates are explicitly referenced by `CONTRIBUTING-AGENTS.md`: *"Before starting work on a new adapter, create an issue from `.github/contributor-templates/new-adapter-story.md`."*

---

### Contribution Framework (Derived Repos)

The onboarding dialogue offers a **Contribution Framework** as the fourth configurable component (alongside agent tool, issue tracker, CI/CD). Like CI/CD, it is offered but deferrable — one question covers the full framework.

If the team opts in, the configured repo's second commit includes:

```
CONTRIBUTING.md                   ← human-facing, project-specific (filled from template)
CONTRIBUTING-AGENTS.md            ← agentic-agile workflow for contributors to this project
CONTRIBUTORS.md                   ← empty file, ready for contributors to be listed
.github/contributor-templates/
  ├── feature-story.md            ← new feature contribution (agentic-story format)
  ├── bug-story.md                ← bug fix contribution
  └── refactor-story.md           ← refactoring / technical debt
```

**Key distinction:** The template repo's `.github/contributor-templates/` is for people contributing to *this methodology template* (new adapters, combos, docs). A derived repo's `.github/contributor-templates/` is for people contributing to *that project's software* (features, bugs, refactors). Same pattern, different scope. `CONTRIBUTING-AGENTS.md` in both cases explains the agentic-agile workflow, but the derived repo's version is tailored to the project's stack and team structure.

---

### Quickstart Combo Index

Lives at `platform-adapters/combos/`. One file per combination.

**Filename format:** `<agent-tool>-<issue-tracker>-<ci-cd>.md`
Multi-tool combos use `multi` as the agent-tool segment.

**Each combo file contains:**

```markdown
## <Agent Tool> + <Issue Tracker> + <CI/CD>

**Stack:** <agent tool> · <issue tracker> · <CI/CD>
**Status:** Maintained | Community | Stub

**Adapters used:**
- platform-adapters/agent-tools/<tool>/
- platform-adapters/issue-trackers/<tracker>/
- platform-adapters/ci-cd/<cicd>/

**Notes:** Any combination-specific setup notes.
```

**Status tiers:**

| Tier | Meaning |
|------|---------|
| Maintained | Core team maintains this combination |
| Community | Contributed and tested by the community |
| Stub | Scaffolded, needs contributions |

---

## Data Flow

### Onboarding Dialogue Protocol

The guided onboarding flow is embedded in AGENTS.md and produces a new configured repository with clean two-commit provenance.

**Entry detection:** Agent checks whether `AGENTS.md` still contains a placeholder project name. If yes, run onboarding. If no, orient and proceed.

**6-step sequence:**

1. **Orient** — Agent summarizes: "I've read this repo. I'm operating as your agentic-agile development partner." No greeting — the human already said "go."

2. **Assess familiarity** — One open question: "Are you familiar with Agentic-Agile development, or would you like a brief orientation before we configure your project?"

3. **Collect required inputs** (one at a time):
   - Project name and one-sentence description
   - Agent tool(s) — present available options from `platform-adapters/agent-tools/`; note that multiple tools are supported and the agent has freedom to customize scaffolding for multi-tool setups
   - Issue tracker — present available options
   - CI/CD — present options, explicitly note it's deferrable
   - Contribution Framework — offer to scaffold a full contribution framework for the new project (deferrable; one question covers the full framework)

4. **Confirm and scaffold** — Summarize choices, confirm with human, then:
   - Create new repo locally
   - **Commit 1:** exact copy of template (zero modifications — clean provenance baseline)
   - Apply platform-specific adapter files (renamed to target paths per quickstart.md)
   - Fill in project name and description placeholders throughout
   - **Commit 2:** all customizations applied on top of commit 1

5. **Hand off** — "Your project repo is ready at `[path]`. Your next step is [first wave / backlog creation]."

6. **Verification checklist** — Present checklist and verify together:

   **Agent auto-verifies (structural):**
   - Commit 1 exists and is an unmodified copy of the template
   - Commit 2 exists with only the expected customizations
   - Agent context file is present at the correct target path
   - Issue tracker templates are in place
   - CI/CD config is present or explicitly deferred with a note
   - No placeholder text remains in the configured files

   **Human confirms (readiness):**
   - Agent context file accurately describes the project
   - Issue template matches how the team will write stories
   - Branching strategy and wave structure make sense for team size
   - Human can successfully invoke their agent tool against the new repo

**Fallback:** AGENTS.md includes a prompt template for users who say "go" without a guided flow, triggering the same sequence.

---

## Error Handling

- **Missing adapter:** If a user requests a tool/tracker/CI combination that has no adapter, the onboarding flow acknowledges this and offers to scaffold a minimal adapter or defer that component.
- **Partial onboarding failure:** The two-commit strategy ensures that if onboarding fails mid-way, the user can inspect commit 1 (clean template) and re-run customization.
- **Accidental copy without onboarding:** Target-named template files (e.g., `CLAUDE.md` not `context.md`) land with the correct filename even if manually copied, preventing silent misconfiguration.
- **Stale placeholder detection:** The verification checklist explicitly checks for remaining placeholder text to catch incomplete onboarding runs.

---

## Testing Strategy

- **Structural validation:** A CI check verifies that every adapter directory contains the required files (README.md, target-named template, quickstart.md).
- **Placeholder detection:** A lint rule scans configured repos for remaining placeholder tokens.
- **Combo index consistency:** A check verifies that every combo file references only adapter directories that actually exist.
- **Onboarding dry-run:** The onboarding protocol can be tested by running it against the template itself and verifying the two-commit output structure.

---

## Migration from Current State

| Current | New |
|---|---|
| `CLAUDE.md` | `platform-adapters/agent-tools/claude/CLAUDE.md` |
| `.github/copilot-instructions.md` | `platform-adapters/agent-tools/github-copilot/copilot-instructions.md` (stub remains in `.github/`) |
| `README.md` | Rewritten for multi-platform framing |
| *(nothing)* | + `AGENTS.md` (new) |
| *(nothing)* | + `CONTRIBUTING-AGENTS.md` (new) |
| `CONTRIBUTING.md` | Light update — pointer to `CONTRIBUTING-AGENTS.md` |
| Everything else | Unchanged |

---

## Phased Delivery

| Phase | Scope |
|-------|-------|
| **v1 — Agent Tools Layer** | Fully populate agent tool adapters (Claude, Copilot, Cursor, Windsurf, Cline, aider); GitHub issue tracker linked to existing templates; CI/CD deferred |
| **v1+ — Issue Trackers Layer** | GitHub linked, Azure DevOps scaffolded, JIRA/Bitbucket as "help wanted" stubs with contribution guidelines |
| **v2 — CI/CD Layer** | GitHub Actions linked, Azure Pipelines and others as stubs with extension points |

---

## Implementation Notes

When moving to implementation planning, every task will be filed as a GitHub issue using the existing `agentic-story.md` template before any code is touched. The planning phase generates a ticketed backlog in the repo's GitHub Issues, not just a planning document. Each issue will be scoped to a single implementable unit of work following the agentic-story format already established in `.github/ISSUE_TEMPLATE/`.

---

## Open Questions

None — all design decisions resolved during brainstorming session.
