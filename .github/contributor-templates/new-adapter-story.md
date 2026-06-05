---
name: New Adapter Story
about: Add a new platform adapter (agent tool, issue tracker, or CI/CD)
title: 'feat: Add [tool-name] adapter to [layer]'
labels: 'enhancement, adapter'
assignees: ''
---

## Summary

<!-- What adapter is being added and to which layer? One sentence describing the outcome. -->

## Context / Motivation

<!-- Why is this adapter needed? What platform or tool does it integrate with, and what capability does it enable? -->

## Scope

### Files to Create or Modify

<!-- Explicit list of files this story will touch. This prevents overlap with parallel stories.
     Replace [layer] with one of: agent-tools, issue-trackers, ci-cd.
     Replace [tool-name] with the actual adapter directory slug.
     Replace [target-filename] with the literal filename the agent reads in a downstream project
     (e.g., CLAUDE.md, .cursorrules, .windsurfrules, .clinerules, CONVENTIONS.md, copilot-instructions.md). -->

- `platform-adapters/[layer]/[tool-name]/README.md` — adapter overview (new file)
- `platform-adapters/[layer]/[tool-name]/[target-filename]` — primary deliverable, named after the literal file the agent loads in downstream projects (new file)
- `platform-adapters/[layer]/[tool-name]/quickstart.md` — quickstart guide for adopting the adapter (new file)
- `platform-adapters/[layer]/README.md` — update parent layer README to list the new adapter (modified file)

### Interfaces to Implement

<!-- APIs, contracts, or integration points this adapter must satisfy. -->

- Follow the existing adapter file structure in the target layer
- Include all required sections matching sibling adapters in the same layer

### Invariants to Preserve

<!-- Existing behavior, contracts, or constraints that must NOT be broken. -->

- No cross-layer dependencies: adapter must not import from or reference other layers
- Adapter file must be self-contained within its layer directory
- Parent layer README update must only add the new adapter entry, not restructure existing content

## Acceptance Criteria

<!-- Specific, testable conditions that must be true when this story is complete. -->

- [ ] Directory `platform-adapters/[layer]/[tool-name]/` exists
- [ ] `platform-adapters/[layer]/[tool-name]/README.md` contains an overview describing when to choose this adapter and any agent-specific conventions
- [ ] `platform-adapters/[layer]/[tool-name]/[target-filename]` exists, is named after the literal filename the agent reads in a downstream project, and contains no placeholder text
- [ ] `platform-adapters/[layer]/[tool-name]/quickstart.md` exists and references the exact path `platform-adapters/[layer]/[tool-name]/[target-filename]`
- [ ] Parent layer `platform-adapters/[layer]/README.md` is updated to list the new adapter in its Available Adapters table
- [ ] No placeholder text (e.g. `[tool-name]`, `[target-filename]`, `TODO`, `...`) remains in any created file

## Negative Constraints

<!-- What this story explicitly does NOT do. Prevents scope creep and clarifies boundaries. -->

- Does NOT modify files in any other layer
- Does NOT modify `AGENTS.md` at any level
- Does NOT add dependencies between this adapter and other adapters

## Dependencies

<!-- Other issues or stories that must be completed before this one can start. -->

- Parent layer directory `[layer]/` must already exist before this story begins

## File Ownership

<!-- Explicit list of files this story owns exclusively during its wave. No other story in the same wave should touch these files. -->

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `platform-adapters/[layer]/[tool-name]/README.md` | ✅ | New file |
| `platform-adapters/[layer]/[tool-name]/[target-filename]` | ✅ | New file — primary adapter deliverable, named after the literal filename the agent reads |
| `platform-adapters/[layer]/[tool-name]/quickstart.md` | ✅ | New file |
| `platform-adapters/[layer]/README.md` | ✅ | Append-only: add new adapter entry |
