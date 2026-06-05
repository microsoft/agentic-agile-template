---
name: Methodology Update
about: Propose changes to the Agentic-Agile methodology, core process, or documentation
title: 'docs: [brief description]'
labels: 'documentation, methodology'
assignees: ''
---

## Summary

<!-- What methodology change is being proposed? One sentence describing the outcome. -->

## Context / Motivation

<!-- Why is this change needed? What gap, inconsistency, or improvement does it address in the Agentic-Agile methodology? -->

## Scope

### Files to Create or Modify

<!-- Explicit list of files this story will touch. This prevents overlap with parallel stories. -->

- `MANIFESTO.md` — core methodology principles (if applicable)
- `STYLE.md` — style and tone guidelines (if applicable)
- `AGENTS.md` — agent onboarding entry point (if applicable)
- `docs/agent-surface-selection.md` — surface selection guidance (if applicable)
- `docs/evaluation-framework.md` — evaluation criteria (if applicable)
- `docs/epic-decomposition-example.md` — decomposition example (if applicable)

### Interfaces to Implement

<!-- Contracts or structural requirements this change must satisfy. -->

- Follow the existing section structure and heading hierarchy in each affected file
- Maintain consistency with sibling documentation and cross-references

### Invariants to Preserve

<!-- Existing behavior, contracts, or constraints that must NOT be broken. -->

- `AGENTS.md` `[Project Name]` sentinel must remain intact and unmodified
- Agentic-story format in issue templates must not change
- Two-commit provenance model must not be altered
- Adapter independence must be maintained — no cross-adapter dependencies introduced

## Acceptance Criteria

<!-- Specific, testable conditions that must be true when this story is complete. -->

- [ ] Change is internally consistent across all affected files
- [ ] Impact Assessment section is complete with all relevant items checked
- [ ] All affected files updated consistently with no contradictions
- [ ] No placeholder text (e.g. `[brief description]`, `TODO`, `...`) remains in any modified file
- [ ] Change is documented in a way that agents can understand and act on

## Negative Constraints

<!-- What this story explicitly does NOT do. Prevents scope creep and clarifies boundaries. -->

- Does NOT change adapter structure or anatomy in `platform-adapters/`
- Does NOT change the format of issue templates in `.github/contributor-templates/`
- Does NOT alter the two-commit provenance model
- Does NOT introduce dependencies between adapters

## Dependencies

<!-- Other issues or stories that must be completed before this one can start. -->

- None unless this change depends on a prior structural change (document here if so)

## File Ownership

<!-- Explicit list of files this story owns exclusively during its wave. No other story in the same wave should touch these files. -->

| File | Owner (this story) | Notes |
|------|-------------------|-------|
| `MANIFESTO.md` | (check if applicable) | Core methodology document |
| `STYLE.md` | (check if applicable) | Style and tone guidelines |
| `AGENTS.md` | (check if applicable) | Agent onboarding entry point |
| `docs/agent-surface-selection.md` | (check if applicable) | Surface selection guidance |
| `docs/evaluation-framework.md` | (check if applicable) | Evaluation framework |
| `docs/epic-decomposition-example.md` | (check if applicable) | Decomposition example |

## Impact Assessment

### Files Affected

<!-- Check all files that this methodology change touches or whose readers need to be aware of the change. -->

- [ ] `MANIFESTO.md`
- [ ] `STYLE.md`
- [ ] `AGENTS.md`
- [ ] `docs/agent-surface-selection.md`
- [ ] `docs/evaluation-framework.md`
- [ ] `docs/epic-decomposition-example.md`
- [ ] Other: <!-- list any additional files -->

### Downstream Effects

<!-- Describe the impact on each downstream concern. -->

**Existing adapters:** <!-- How does this change affect existing platform adapters? Are any adapter files inconsistent with the updated methodology? -->

**Derived projects:** <!-- How does this change affect projects that have forked or adopted this template? What migration steps (if any) would they need to take? -->

**Onboarding dialogue:** <!-- How does this change affect the first-run experience for new agents or contributors reading AGENTS.md? Does the onboarding narrative need updating? -->
