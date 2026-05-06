# Style Guide

> Customize this guide for your project's conventions. Each section includes placeholder content and examples to adapt.

---

## 1. Code Style

### Language-Specific Conventions

<!-- Replace with your project's language and conventions. -->

**Primary language:** [e.g., TypeScript, Python, Go, Rust]

| Convention | Rule |
|-----------|------|
| Indentation | [e.g., 2 spaces for JS/TS, 4 spaces for Python, tabs for Go] |
| Line length | [e.g., 100 characters] |
| Semicolons | [e.g., required / omitted] |
| Quotes | [e.g., single quotes for strings] |
| Trailing commas | [e.g., always in multiline] |

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variables | [e.g., camelCase] | `userName` |
| Functions | [e.g., camelCase] | `getUserById` |
| Classes/Types | [e.g., PascalCase] | `UserService` |
| Constants | [e.g., UPPER_SNAKE] | `MAX_RETRY_COUNT` |
| Files | [e.g., kebab-case] | `user-service.ts` |
| Test files | [e.g., same name + .test] | `user-service.test.ts` |

### Formatting Tools

<!-- List the formatters and linters your project uses. -->

- **Formatter:** [e.g., Prettier, Black, gofmt]
- **Linter:** [e.g., ESLint, pylint, golangci-lint]
- **Config files:** [e.g., `.prettierrc`, `pyproject.toml`]
- **Run before commit:** [e.g., `npm run lint`, `make fmt`]

---

## 2. Documentation Style

### Code Comments

- Comment **why**, not **what**. The code shows what; comments explain reasoning.
- Use doc comments for all public APIs (functions, classes, modules).
- Remove commented-out code. Use version control, not comments, for history.

### Doc Comment Format

<!-- Adapt to your language's conventions. -->

```
/**
 * Brief description of what this function does.
 *
 * @param paramName - Description of the parameter
 * @returns Description of the return value
 * @throws ErrorType - When this error occurs
 */
```

### README and Docs

- Every module or package should have a README explaining its purpose.
- Use short paragraphs (2-5 sentences).
- Lead with the most important information.
- Include runnable examples where possible.

---

## 3. Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) or a similar structured format:

```
<type>(<scope>): <short summary>

<optional body: explain what and why, not how>

<optional footer: breaking changes, issue references>
```

### Types

| Type | When to Use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build, CI, tooling changes |

### Examples

```
feat(auth): add JWT token refresh endpoint

Implements automatic token refresh when the access token expires.
Refresh tokens are stored in HTTP-only cookies.

Closes #42
```

```
fix(api): handle null response from external service

The payment gateway occasionally returns null instead of an error
object. Added null check with appropriate error mapping.
```

---

## 4. Pull Request Format

### PR Title

Follow the same format as commit messages: `<type>(<scope>): <summary>`

### PR Description Template

```markdown
## What

Brief description of what this PR changes.

## Why

Context and motivation for the change.

## How

Key implementation decisions (not a line-by-line walkthrough).

## Testing

How the changes were tested. Include commands to reproduce.

## Checklist

- [ ] Tests pass locally
- [ ] Documentation updated (if applicable)
- [ ] No unrelated changes included
```

---

## 5. Agent Communication Preferences

When working with AI coding agents, these conventions improve output quality:

### Spec Structure for Agent Stories

- Start with a clear summary of the deliverable.
- List specific files to create or modify.
- Define acceptance criteria as testable conditions.
- Include negative constraints (what the story does NOT do).
- Specify file ownership to prevent overlap with parallel work.

### Review Expectations

- Agent-generated code should pass the same review standards as human-written code.
- Review for correctness, not style (let formatters handle style).
- Every review finding reaches a terminal state: fixed, accepted, or deferred.

### Context Files

- Maintain a `CLAUDE.md` (or equivalent agent context file) at the repo root.
- Keep it current. Outdated context files cause agent drift.
- Include: project purpose, structure, conventions, process, and validation gates.

---

## 6. Hard Bans

<!-- List things that should never appear in your codebase. -->

- No credentials or secrets in source code.
- No `TODO` comments without a linked issue.
- No suppressed linter warnings without a justifying comment.
- No wildcard imports (import only what you use).
- [Add your project-specific bans here]
