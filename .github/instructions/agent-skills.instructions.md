---
description: 'Guidelines for creating portable, discoverable, and testable GitHub Copilot Agent Skills'
applyTo: '**/skills/**'
---

# Agent Skill Guidelines

Create each skill in `.github/skills/<lowercase-hyphenated-name>/` with a
`SKILL.md` entry point.

## Discovery metadata

- Include YAML frontmatter with `name` and `description`.
- Keep `name` lowercase and hyphenated, with at most 64 characters.
- Make `description` state what the skill does, when to use it, and the terms a
  user is likely to mention.

## Progressive disclosure

- Keep `SKILL.md` focused on activation, prerequisites, the safe workflow, and
  gotchas.
- Put detailed contracts in `references/`.
- Put deterministic automation in `scripts/`.
- Put starter configuration and output bodies in `templates/`.
- Reference bundled resources with relative links.

## Script requirements

- Prefer cross-platform standard-library Python for complex automation.
- Provide `--help`, deterministic errors, and explicit exit codes.
- Default to read-only or dry-run behavior. Make writes explicit.
- Never store credentials. Reuse existing credential helpers.
- Redact credentials and authorization headers from diagnostics.
- Use atomic writes for persistent state and generated artifacts.
- Add tests for safety boundaries, reruns, partial failures, and malformed input.

## Content quality

- Document non-obvious constraints in a `Gotchas` section.
- Distinguish observed evidence from inferred intent.
- Avoid repository-specific paths, identities, snapshots, and counts.
- Keep `SKILL.md` below 500 lines; move workflows longer than five steps to a
  reference file.

## Validation

- Verify frontmatter and relative links.
- Run bundled tests and every public command's help output.
- Search for placeholders, credentials, personal identifiers, and
  repository-specific literals before publication.
