---
name: New Quickstart Combo
about: Add a new stack combination quickstart guide
title: 'feat: Add [agent]-[tracker]-[cicd] combo'
labels: 'enhancement, combo'
assignees: ''
---

## Summary

<!-- What stack combination is being added? One sentence describing the agent, tracker, and CI/CD tools being combined. -->

## Context / Motivation

<!-- Why is this combo useful? What developer workflow does it support, and what makes this combination worth documenting? -->

## Scope

### Files to Create or Modify

<!-- Explicit list of files this story will touch. This prevents overlap with parallel stories. -->

- `platform-adapters/combos/<agent>-<tracker>-<cicd>.md` — new combo quickstart file (primary deliverable)
- `platform-adapters/combos/README.md` — update to list the new combo file

### Interfaces to Implement

<!-- The combo file must contain the following required sections (aligned with `platform-adapters/combos/README.md` and the shipped combo files). -->

- **Stack** — lists the agent, tracker, and CI/CD tools in this combination (e.g. `agent · tracker · CI/CD`)
- **Status** — one of `Maintained`, `Community`, or `Stub`, reflecting actual support level
- **Adapters Used** — links to the relevant adapter directories for each component in the stack
- **Quick Setup** — numbered steps that point at each adapter's quickstart
- **Notes** — any integration-specific guidance, known limitations, or setup considerations

### Invariants to Preserve

<!-- Existing behavior, contracts, or constraints that must NOT be broken. -->

- Filename must follow the `<agent>-<tracker>-<cicd>.md` naming convention exactly
- All adapter directories referenced in "Adapters Used" must already exist before this story begins
- Status tier must accurately reflect the actual support level — do not assign `Maintained` to a community-driven or stub entry
- `platform-adapters/combos/README.md` must list every combo file after this story completes

## Acceptance Criteria

<!-- Specific, testable conditions that must be true when this story is complete. -->

- [ ] File `platform-adapters/combos/<agent>-<tracker>-<cicd>.md` exists with the correct filename
- [ ] Combo file contains all five required sections: Stack, Status, Adapters Used, Quick Setup, Notes
- [ ] All adapter directories referenced in "Adapters Used" exist in the repository
- [ ] Status value is one of `Maintained`, `Community`, or `Stub` and matches actual support level
- [ ] `platform-adapters/combos/README.md` is updated to include the new combo file
- [ ] No placeholder text (e.g. `<agent>`, `<tracker>`, `<cicd>`, `TODO`, `...`) remains in any created file

## Negative Constraints

<!-- What this story explicitly does NOT do. Prevents scope creep and clarifies boundaries. -->

- Does NOT create or modify any adapter directories
- Does NOT modify any existing combo files
- Does NOT modify `AGENTS.md` at any level
- Does NOT restructure `platform-adapters/combos/README.md` — append-only update to add the new entry

## Dependencies

<!-- Other issues or stories that must be completed before this one can start. -->

- All adapter directories referenced in the combo's "Adapters Used" section must already exist

## File Ownership

<!-- Explicit list of files this story owns exclusively during its wave. No other story in the same wave should touch these files. -->

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `platform-adapters/combos/<agent>-<tracker>-<cicd>.md` | ✅ | New file — primary combo deliverable |
| `platform-adapters/combos/README.md` | ✅ | Append-only: add new combo entry |
