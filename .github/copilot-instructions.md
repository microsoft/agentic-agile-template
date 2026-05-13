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
- Do not start implementation without a corresponding GitHub Issue. Every work request must be tracked.
- Do not discard the originating human prompt — capture it in the issue's "Originating Prompt" section or as a comment for retrospective use.
