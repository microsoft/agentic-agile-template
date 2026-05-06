# Agentic-Agile Template

A starter template for teams adopting [Agentic-Agile Development](https://developer.microsoft.com/blog/): the practice of producing production-ready software through structured human-agent collaboration.

## What is Agentic-Agile Development?

Agentic-Agile Development bridges Agile process values with the capabilities of AI coding agents. It is a methodology for building software through human-agent partnerships, not just using agents as autocomplete tools.

The core insight: agents fail not because of model capability, but because of coordination breakdown. When you give an agent a vague prompt, you get vague output. When you give it a well-specified story with acceptance criteria, file boundaries, and negative constraints, you get production-quality code. The specification is the program.

Agentic-Agile Development provides the process layer that makes agent collaboration repeatable: structured backlogs, spec-first stories, wave-based parallel execution, built-in governance, and continuous measurement across eight dimensions. Teams that adopt these patterns shift from "hoping the agent gets it right" to systematically improving their human-agent partnership over time.

## What's in This Repo

| File | Description |
|------|-------------|
| [`CLAUDE.md`](CLAUDE.md) | Agent context template. Provides AI coding agents with project-specific context so they produce output that fits your conventions from the first interaction. |
| [`MANIFESTO.md`](MANIFESTO.md) | The Agentic-Agile Manifesto: 5 values and 13 principles for human-agent software development. |
| [`STYLE.md`](STYLE.md) | Style guide template covering code conventions, documentation, commit messages, and PR format. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidelines following the Agentic-Agile workflow. |
| [`SECURITY.md`](SECURITY.md) | Standard security policy and vulnerability reporting process. |
| [`LICENSE`](LICENSE) | MIT License. |
| [`mcp.json`](mcp.json) | Example MCP (Model Context Protocol) server configuration for agent tooling. |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot-specific instruction file (shorter subset of CLAUDE.md). |
| [`.github/ISSUE_TEMPLATE/agentic-story.md`](.github/ISSUE_TEMPLATE/agentic-story.md) | Issue template for structured Agentic-Agile stories with scope, file ownership, and acceptance criteria. |
| [`docs/agent-surface-selection.md`](docs/agent-surface-selection.md) | Guide to choosing the right agent surface (CLI, IDE, chat, API, cloud) for different task types. |
| [`docs/evaluation-framework.md`](docs/evaluation-framework.md) | Eight-dimension framework for measuring the effectiveness of human-agent development partnerships. |
| [`docs/epic-decomposition-example.md`](docs/epic-decomposition-example.md) | Worked example showing how to decompose an epic into stories, assign file ownership, and plan wave execution. |

## Getting Started

### 1. Clone or Copy This Template

```bash
# Clone the repository
git clone https://github.com/mcaps-microsoft/agentic-agile-template.git my-project

# Or use it as a GitHub template (click "Use this template" on GitHub)
```

### 2. Customize Your Agent Context

Open `CLAUDE.md` and replace the placeholder content with your project's information:

- **Project Purpose:** What your project does, who it's for, what stack it uses.
- **Repository Structure:** Your actual directory layout.
- **Coding Conventions:** Your language-specific rules (naming, error handling, logging).
- **Testing Strategy:** Your test framework, organization, and coverage expectations.
- **Build and Run Commands:** How to install, build, test, and lint your project.

Also update `.github/copilot-instructions.md` with the same core information in shorter form.

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

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on contributing to this template.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
