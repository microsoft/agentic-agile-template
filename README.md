# Agentic-Agile Template

> [!CAUTION]
> Agentic-Agile methodology is an **active area of investigation** with the potential for unanticipated results. While models and workflows are improving rapidly, agentic development is inherently non-deterministic. Use good judgement and appropriate safeguards before putting AI-generated work-product into production.

A starter template for teams adopting [Agentic-Agile Development](MANIFESTO.md): the practice of producing production-ready software through structured human-agent collaboration.

## What is Agentic-Agile Development?

Agentic-Agile Development bridges Agile process values with the capabilities of AI coding agents. It is a methodology for building software through human-agent partnerships, not just using agents as autocomplete tools.

The core insight: agents fail not because of model capability, but because of coordination breakdown. When you give an agent a vague prompt, you get vague output. When you give it a well-specified story with acceptance criteria, file boundaries, and negative constraints, you get production-quality code. **The specification is the program.**

Agentic-Agile Development provides the process layer that makes agent collaboration repeatable: structured backlogs, spec-first stories, wave-based parallel execution, built-in governance, and continuous measurement across eight dimensions. Teams that adopt these patterns shift from "hoping the agent gets it right" to systematically improving their human-agent partnership over time.

## What's in This Repo

| File / Directory | Description |
|------|-------------|
| [`AGENTS.md`](AGENTS.md) | Universal onboarding orchestrator. Any AI coding agent reads this first. It guides a structured 6-step onboarding dialogue and activates the platform adapters appropriate for your toolchain. |
| [`CONTRIBUTING-AGENTS.md`](CONTRIBUTING-AGENTS.md) | Guide for agents contributing to this template repository. Covers adapter anatomy, structural invariants, and how to add new adapters or quickstart combos. |
| [`platform-adapters/`](platform-adapters/) | Three-layer adapter library: agent-tool instructions, issue-tracker integrations, and CI/CD configurations. Mix and match for your stack. |
| [`.github/contributor-templates/`](.github/contributor-templates/) | PR and issue templates for both human and agent contributors following Agentic-Agile story structure. |
| [`MANIFESTO.md`](MANIFESTO.md) | The Agentic-Agile Manifesto: 5 values and 13 principles for human-agent software development. |
| [`STYLE.md`](STYLE.md) | Style guide template covering code conventions, documentation, commit messages, and PR format. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Human contribution guidelines following the Agentic-Agile workflow. |
| [`SECURITY.md`](SECURITY.md) | Standard security policy and vulnerability reporting process. |
| [`LICENSE`](LICENSE) | MIT License. |
| [`mcp.json`](mcp.json) | Example MCP (Model Context Protocol) server configuration for agent tooling. |
| [`.github/ISSUE_TEMPLATE/agentic-story.md`](.github/ISSUE_TEMPLATE/agentic-story.md) | Issue template for structured Agentic-Agile stories with scope, file ownership, and acceptance criteria. |
| [`docs/agent-surface-selection.md`](docs/agent-surface-selection.md) | Guide to choosing the right agent surface (CLI, IDE, chat, API, cloud) for different task types. |
| [`docs/evaluation-framework.md`](docs/evaluation-framework.md) | Eight-dimension framework for measuring the effectiveness of human-agent development partnerships. |
| [`docs/epic-decomposition-example.md`](docs/epic-decomposition-example.md) | Worked example showing how to decompose an epic into stories, assign file ownership, and plan wave execution. |

## Platform Adapter Architecture

The `platform-adapters/` directory provides a three-layer architecture that separates agent-tool conventions, issue-tracker workflows, and CI/CD integrations. Each layer is independently swappable — change your issue tracker without touching your agent instructions, or adopt a new CI system without rewriting your agent conventions.

```
platform-adapters/
├── agent-tools/           # Agent-specific instruction sets and context files
│   ├── claude/            # Claude Code conventions and context patterns
│   ├── github-copilot/    # GitHub Copilot instruction files
│   ├── cursor/            # Cursor rules and context
│   ├── windsurf/          # Windsurf configuration
│   ├── cline/             # Cline conventions
│   └── aider/             # Aider conventions
├── issue-trackers/        # Workflow templates per issue tracker
│   └── github/            # GitHub Issues adapter (more trackers planned)
├── ci-cd/                 # CI/CD pipeline templates (placeholder — full layer planned for v2)
└── combos/                # Tested stack combinations (e.g., github-copilot + github + github-actions)
```

During onboarding, [`AGENTS.md`](AGENTS.md) asks which adapters your project needs and activates only those layers. This keeps agent context lean and targeted rather than flooding the agent with instructions for tools you don't use.

### Sample Issues

This repository ships with two sets of **worked-example issues** under [`docs/sample-issues/`](docs/sample-issues/) that illustrate the Agentic-Agile workflow — label taxonomy, epic decomposition, wave structure, and the agentic-story template in action.

- **SAMPLE 1 — TaskFlow** ([`docs/sample-issues/`](docs/sample-issues/), files prefixed `05`–`09`): a hypothetical task-management REST API used to demonstrate epic decomposition, dependency mapping, and wave-based parallel execution.
- **SAMPLE 2 — Onboarding walkthrough** ([`docs/sample-issues/`](docs/sample-issues/), files prefixed `10`–`14`): a worked example of an external contributor's first few stories when adopting this template.

These are **read-only onboarding references** — kept in version-controlled markdown rather than in the live issue tracker so the issue tracker stays clean for real backlog items. See [`docs/sample-issues/README.md`](docs/sample-issues/README.md) for the full index and provenance.

## Getting Started

### 1. Copy This Template

Click **"Use this template"** on the [GitHub repository page](https://github.com/microsoft/agentic-agile-template) to create a new repository with all the template files.

Then open the project in your AI coding agent of choice (Claude Code, Cursor, Copilot, Windsurf, Cline, or Aider).

### 2. Follow the Guided Onboarding Dialogue

Direct your agent to [`AGENTS.md`](AGENTS.md). It will run a structured 6-step onboarding dialogue:

1. **Orient** — the agent announces that the repository is in template state and asks you to confirm you're ready to start.
2. **Assess Familiarity** — the agent asks whether you've used this template before, and calibrates its explanations accordingly.
3. **Collect Inputs** — the agent asks five questions, one at a time: project name, agent tools your team will use, issue tracker, CI/CD system (deferrable), and any existing contribution conventions (deferrable).
4. **Confirm and Scaffold** — the agent summarizes what it collected and creates two commits: one exact copy of the unmodified template as a baseline, then a second commit with your customizations applied.
5. **Hand Off** — the agent explains which placeholders still need manual completion and what to do next.
6. **Verify** — the agent runs a checklist to confirm the repository is fully configured before closing the session.

After this dialogue, agents reading the repository enter configured state and go directly to task execution on subsequent sessions.

### 3. Create Your First Backlog

> **Issues first:** Every work request must be captured as a GitHub Issue before implementation begins. Include the originating human prompt in the issue (use the "Originating Prompt" section in the issue template) so it's available for retrospectives.

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

This template accompanies the Agentic-Agile Development blog series. The first post is published; additional posts are forthcoming.

- [Why Agent Development Needs Agile (Not Just Prompts)](https://devblogs.microsoft.com/blog/agentic-agile-why-agent-development-needs-agile-not-just-prompts)

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

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for human contribution guidelines and [`CONTRIBUTING-AGENTS.md`](CONTRIBUTING-AGENTS.md) for agent-specific contribution patterns, story format requirements, and wave governance rules.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
