# [Project Name]

> **Universal agent entry point.** Any agent reading this repository cold starts here.
> This file is both orientation reference and onboarding orchestrator.

---

## What This Is

This repository is built on the **Agentic-Agile Template** — a starter framework for teams adopting structured human-agent collaboration. It provides the process layer that makes agent partnerships repeatable: structured backlogs, spec-first stories, platform adapter context files, built-in governance, and continuous measurement.

**This file (`AGENTS.md`) is the single canonical entry point for all AI coding agents.** Read it completely before taking any action in the repository. It detects which state the repository is in and routes you to the right starting point.

---

## Repo Map

| Path | Purpose |
|------|---------|
| `AGENTS.md` | **This file.** Universal agent entry point and onboarding orchestrator. |
| `README.md` | Human-facing project overview and getting-started guide. |
| `MANIFESTO.md` | The Agentic-Agile Manifesto: 5 values and 13 principles for human-agent development. |
| `STYLE.md` | Code conventions, commit message format, PR structure, documentation standards. |
| `CONTRIBUTING.md` | Human contribution workflow and PR guidelines. |
| `SECURITY.md` | Security policy and vulnerability reporting process. |
| `mcp.json` | Example MCP server configuration for agent tooling. |
| `platform-adapters/` | **Layered agent / tracker / CI-CD context.** Three sub-layers: `agent-tools/` (one adapter per AI agent), `issue-trackers/` (one per backlog system), `ci-cd/` (planned v2), plus `combos/` for pre-assembled stacks. |
| `docs/agent-surface-selection.md` | Guide to choosing the right agent surface for different task types. |
| `docs/evaluation-framework.md` | Eight-dimension framework for measuring human-agent partnership effectiveness. |
| `docs/epic-decomposition-example.md` | Worked example: decompose an epic into stories, assign file ownership, plan waves. |
| `docs/history/` | Implementation plan and design history (Phase 1/Phase 2 multi-platform generalization). |
| `.github/copilot-instructions.md` | GitHub Copilot-specific instruction file. |
| `.github/ISSUE_TEMPLATE/agentic-story.md` | Structured story template with scope, file ownership, and acceptance criteria. |

---

## Your Role

You are an AI coding agent working within this repository. Your responsibilities depend on the state detected in the **Onboarding Protocol** below.

In all states, apply these baseline behaviors:

- **Read context first.** Locate and read your platform adapter in `platform-adapters/` before starting any task. Platform adapters contain project-specific context, coding conventions, build commands, and testing strategy.
- **Respect scope.** Implement exactly what the story or task specifies. Do not add features not in scope. Do not modify files outside your assignment without explicit instruction.
- **Ask before assuming.** When requirements are ambiguous, ask. Never guess on incomplete specifications.
- **Keep changes minimal.** Prefer targeted, focused changes over broad refactoring unless the spec requires it.
- **Follow conventions.** Consult `STYLE.md` for code style, commit format, and PR structure.

**This role is additive.** You complement the human's judgment and domain knowledge. You do not replace it. At decision points where business context, stakeholder priorities, or architectural trade-offs are required, surface the question to the human rather than deciding unilaterally.

---

## Onboarding Protocol

Before taking any action, determine which state this repository is in and follow the corresponding path.

### State Detection

Check the title of this file (the first `#` heading):

| Condition | State | Action |
|-----------|-------|--------|
| Title still reads the template sentinel `[Project Name]` | **Template state** | Run the Guided Onboarding Dialogue below. Do not modify any files until the dialogue is complete. |
| Title contains a real project name and you have a specific task | **Configured state** | Skip to Quick Start below. |
| You are contributing to the template itself (not a derived project) | **Contributor state** | Read `CONTRIBUTING-AGENTS.md` before proceeding. |

### Quick Start (Configured State)

1. Find your platform adapter: `platform-adapters/agent-tools/<your-tool>/`.
2. Read the adapter completely — it contains project-specific context, build commands, and conventions.
3. Read your assigned story or task, including acceptance criteria, file scope, and constraints.
4. Confirm you understand the scope before writing any code.
5. Implement. Follow TDD when applicable: write a failing test first, then implement to pass.
6. Self-review against acceptance criteria before signaling completion.

---

## Guided Onboarding Dialogue

**When to run:** Only when the repository is in template state (title still contains the sentinel). If the repository has been initialized, skip this section.

**Purpose:** Collect the information needed to configure this repository for a real project, then apply those settings in two atomic commits.

---

### Step 1: Orient

Say to the human:

> "I'm reading this repository as a fresh agent. It's currently in **template state** — it hasn't been configured for a specific project yet. I'm going to walk you through a short setup that takes about 5 minutes. I'll ask you questions one at a time and apply your answers at the end.
>
> At the end of this dialogue, I'll create two commits: first an exact copy of the template files as a baseline, then a second commit with your project customizations applied.
>
> Ready to start?"

Wait for confirmation before proceeding.

---

### Step 2: Assess Familiarity

Ask:

> "Have you used this Agentic-Agile template before, or is this your first time?"

- If experienced: "Great — I'll keep explanations brief and focus on collecting your inputs."
- If new: "No problem. I'll give you brief context for each question so you understand what each setting controls."

---

### Step 3: Collect Required Inputs

Ask the following questions **one at a time**. Wait for each answer before asking the next.

**Input 1 — Project name:**

> "What is the name of your project? This will replace the title placeholder in `AGENTS.md` and `platform-adapters/` context files."

*(Required. Cannot be deferred.)*

**Input 2 — Agent tools:**

> "Which AI coding agent(s) will your team use? For example: Claude Code, GitHub Copilot, Cursor, Aider, Cline, or others.
>
> I'll use this to configure the relevant platform adapters."

*(Required. Cannot be deferred.)*

**Input 3 — Issue tracker:**

> "Which issue tracker will you use? For example: GitHub Issues, Jira, Linear, or Azure DevOps."

*(Required. Cannot be deferred.)*

**Input 4 — CI/CD system (deferrable):**

> "Do you have a CI/CD system to configure? For example: GitHub Actions, Azure Pipelines, CircleCI. If you're not sure yet, you can skip this and configure it later."

*(Deferrable. Record 'TBD' if skipped.)*

**Input 5 — Contribution Framework (deferrable):**

> "Do you have an existing contribution process, branching strategy, or workflow conventions you want agents to follow? If not, the template defaults in `CONTRIBUTING.md` will apply. You can skip this now."

*(Deferrable. Record 'template defaults' if skipped.)*

---

### Step 4: Confirm and Scaffold

Summarize collected inputs:

> "Here's what I'm going to configure:
>
> - **Project name:** [collected value]
> - **Agent tools:** [collected value]
> - **Issue tracker:** [collected value]
> - **CI/CD:** [collected value or 'TBD']
> - **Contribution Framework:** [collected value or 'template defaults']
>
> I'll apply these in two commits:
>
> **Commit 1 — Baseline:** An exact copy of all template files, committed as-is with a message like `chore: capture template baseline before customization`. This creates a clean diff anchor.
>
> **Commit 2 — Customizations:** Replace the title sentinel, update agent context files with your project details, and configure the relevant platform adapters.
>
> Shall I proceed?"

Wait for explicit confirmation. Do not modify any files until the human confirms.

---

### Step 5: Hand Off

After both commits are complete, say:

> "Setup complete. Here's what to do next:
>
> 1. Open your platform adapter in `platform-adapters/agent-tools/<your-tool>/` and fill in any remaining placeholders (directory structure, build commands, testing strategy).
> 2. Share that adapter file with your agent at the start of each session.
> 3. Use `.github/ISSUE_TEMPLATE/agentic-story.md` when creating your first story — it structures scope and acceptance criteria in the format agents work best with.
> 4. Review `MANIFESTO.md` with your team to align on the human-agent collaboration principles.
>
> From this point forward, agents reading this repository will enter **configured state** and go directly to the Quick Start path."

---

### Step 6: Verification Checklist

Before closing the onboarding session, verify:

- [ ] The title of `AGENTS.md` contains the real project name (not the template sentinel).
- [ ] At least one platform adapter exists under `platform-adapters/` for each confirmed agent tool.
- [ ] The issue tracker is documented in the adapter under `platform-adapters/issue-trackers/<tracker>/`.
- [ ] CI/CD configuration is documented or marked TBD.
- [ ] Both baseline and customization commits are present in git history.
- [ ] No template placeholder text remains in the files that were customized.
- [ ] The human knows which placeholders still need manual completion (directory layout, build commands, test framework).

If any item is unchecked, surface it to the human before closing. Do not silently skip unresolved items.

---

## Fallback: Non-Dialogue Entry Prompt

For teams that prefer to skip the interactive dialogue and supply all setup details in a single prompt, use this template:

```
Configure this Agentic-Agile template repository for my project. Here are the details:

- Project name: <your project name>
- Agent tools: <list of AI coding agents, e.g. Claude Code, Cursor>
- Issue tracker: <e.g. GitHub Issues, Jira, Linear>
- CI/CD system: <e.g. GitHub Actions, Azure Pipelines, or TBD>
- Contribution framework: <existing conventions or "use template defaults">

Apply the two-commit model:
1. Commit 1: exact copy of current template files as baseline
2. Commit 2: apply customizations using the details above

Then run the Step 6 Verification Checklist and report any unchecked items.
```

This produces the same outcome as the guided dialogue. Use whichever entry path fits your workflow.
