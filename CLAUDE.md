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
