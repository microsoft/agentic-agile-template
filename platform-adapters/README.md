# Platform Adapters

This directory contains adapter configurations for integrating the Agentic-Agile workflow with specific combinations of agent tools, issue trackers, and CI/CD systems.

## Architecture: The Three-Layer Adapter System

Agentic-Agile is platform-agnostic by design. The adapter system bridges the generic workflow to your specific toolchain through three independent layers that combine into **combo** configurations.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Development Team                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 platform-adapters/combos/                       │
│         (e.g. github-copilot-github-github-actions.md)          │
│   Assembled, tested combination of all three layers             │
└───────────┬─────────────────┬─────────────────────┬────────────┘
            │                 │                     │
            ▼                 ▼                     ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   agent-tools/    │ │  issue-trackers/  │ │     ci-cd/        │
│                   │ │                   │ │  (planned for v2) │
│ Claude Code       │ │ GitHub Issues     │ │                   │
│ GitHub Copilot    │ │                   │ │                   │
│ Cursor            │ │                   │ │                   │
│ Windsurf          │ │                   │ │                   │
│ Cline             │ │                   │ │                   │
│ Aider             │ │                   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

## Layers

| Layer | Directory | Purpose |
|-------|-----------|---------|
| Agent Tools | [agent-tools/](agent-tools/) | AI coding agent configuration (context files, MCP servers, instructions) |
| Issue Trackers | [issue-trackers/](issue-trackers/) | Story templates and backlog management per tracker |
| CI/CD | [ci-cd/](ci-cd/) | Pipeline and workflow configurations (v2, planned) |
| Combos | [combos/](combos/) | Pre-assembled, tested combinations of all three layers |

## How It Works

1. **Pick your combo.** Browse [combos/](combos/) for a pre-assembled configuration matching your stack. Combos are named `<agent-tool>-<issue-tracker>-<ci-cd>.md`.

2. **Or build your own.** If no combo exists, select one adapter from each of the three layers:
   - An **agent-tools** adapter configures your AI coding agent (context files, prompts, MCP server settings).
   - An **issue-trackers** adapter provides story templates in the agentic-story format for your backlog tool.
   - A **ci-cd** adapter wires up the pipeline checks the workflow expects.

3. **Follow the setup steps.** Each adapter and combo document contains prerequisites, installation steps, and verification instructions.

## Adding a New Adapter

### Adding an agent-tools adapter

1. Create `platform-adapters/agent-tools/<tool-name>/` directory.
2. Add the three required files described in [agent-tools/README.md](agent-tools/README.md): `README.md`, a target-named template file (named after the literal filename your agent reads — e.g., `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `CONVENTIONS.md`, or `copilot-instructions.md`), and `quickstart.md`.
3. Update `platform-adapters/agent-tools/README.md` to list the new adapter in the Available Adapters table.
4. Open a PR — include a working example project demonstrating the adapter.

### Adding an issue-trackers adapter

1. Create `platform-adapters/issue-trackers/<tracker-name>/` directory.
2. Add a `README.md` and the tracker-specific story template (e.g., a `quickstart.md` plus any tracker-native template format) following the format in [issue-trackers/README.md](issue-trackers/README.md).
3. Open a PR with screenshots or export examples showing the template in use.

### Adding a ci-cd adapter

The ci-cd layer is planned for v2. See [ci-cd/README.md](ci-cd/README.md) for what's coming and how to contribute early designs.

### Adding a combo

1. Verify all constituent adapters exist (agent-tools and issue-trackers — the ci-cd layer is v2/planned, so use the convention in [combos/README.md](combos/README.md) for the ci-cd segment).
2. Create `platform-adapters/combos/<agent-tool>-<issue-tracker>-<ci-cd>.md`.
3. Follow the combo format and declare a status tier (Maintained, Community, or Stub).
4. See [combos/README.md](combos/README.md) for full format and status tier definitions.

## Status at a Glance

| Combo | Agent Tool | Issue Tracker | CI/CD | Status |
|-------|-----------|---------------|-------|--------|
| [`claude-github-github-actions.md`](combos/claude-github-github-actions.md) | Claude Code | GitHub Issues | GitHub Actions | Stub |
| [`github-copilot-github-github-actions.md`](combos/github-copilot-github-github-actions.md) | GitHub Copilot | GitHub Issues | GitHub Actions | Stub |
| [`cursor-github-github-actions.md`](combos/cursor-github-github-actions.md) | Cursor | GitHub Issues | GitHub Actions | Stub |

> More combos are added as the community contributes. Check [combos/](combos/) for the current list.
