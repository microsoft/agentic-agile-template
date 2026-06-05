# Combos

A **combo** is a pre-assembled, tested combination of adapters from all three platform-adapter layers:

- one **agent-tools** adapter (which AI coding agent)
- one **issue-trackers** adapter (which backlog/story tool)
- one **ci-cd** adapter (which pipeline system)

Combos are the recommended starting point. Instead of manually assembling three separate adapters and verifying they work together, you pick the combo that matches your stack and follow a single setup guide.

## Available Combos

| Combo File | Agent Tool | Issue Tracker | CI/CD | Status |
|------------|-----------|---------------|-------|--------|
| [`claude-github-github-actions.md`](claude-github-github-actions.md) | Claude Code | GitHub Issues | GitHub Actions | Stub |
| [`github-copilot-github-github-actions.md`](github-copilot-github-github-actions.md) | GitHub Copilot | GitHub Issues | GitHub Actions | Stub |
| [`cursor-github-github-actions.md`](cursor-github-github-actions.md) | Cursor | GitHub Issues | GitHub Actions | Stub |

> The ci-cd layer is planned for v2. Until then, combos document CI/CD setup as manual steps. See [../ci-cd/README.md](../ci-cd/README.md) for details.

## Status Tiers

Every combo declares one of three status tiers:

### Maintained
The combo is **actively tested** against real projects by the core team or a designated maintainer. It has:
- End-to-end setup tested on a real repository
- At least one maintainer who reviews PRs touching this combo
- A known-working example project linked in the combo document
- Issues filed against it receive timely responses

Maintained combos are safe to use in production teams. When something breaks, someone is accountable for fixing it.

### Community
The combo was **contributed and verified by a community member** but is not actively maintained by the core team. It has:
- Initial setup verified to work at time of contribution
- No guaranteed maintainer for ongoing updates
- May lag behind changes to the underlying adapters
- Issues may receive slower responses

Community combos are usable but require more caution. Verify against the latest adapter versions before adopting.

### Stub
The combo is a **placeholder** — the file exists to document intent but has not been fully implemented or tested. A Stub combo:
- May have incomplete setup steps
- Has not been verified end-to-end
- Exists to signal that this combination is on the roadmap
- Is open for community contributors to promote to Community or Maintained status

Stub combos should not be used in production teams without significant additional work.

## Filename Convention

Combo files follow a strict naming convention:

```
<agent-tool>-<issue-tracker>-<ci-cd>.md
```

Where:
- `<agent-tool>` is the slug of the agent-tools adapter directory (e.g., `claude`, `github-copilot`, `cursor`, `windsurf`, `cline`, `aider`)
- `<issue-tracker>` is the slug of the issue-trackers adapter directory (e.g., `github`)
- `<ci-cd>` is the slug of the ci-cd adapter (e.g., `github-actions` — once the ci-cd layer ships in v2)

**Examples:**
- `github-copilot-github-github-actions.md` — GitHub Copilot + GitHub Issues + GitHub Actions
- `claude-github-github-actions.md` — Claude Code + GitHub Issues + GitHub Actions
- `cursor-github-github-actions.md` — Cursor + GitHub Issues + GitHub Actions

**About the ci-cd segment in v1:** the `platform-adapters/ci-cd/` layer is a planned v2 expansion — only a placeholder `README.md` ships today, and no per-system adapter directories (e.g., `ci-cd/github-actions/`) exist yet. The currently-shipped Stub combos use the eventual slug `github-actions` as a forward-looking placeholder, documenting CI/CD as manual setup steps until the layer adapters ship. Once the ci-cd layer adapters are in place (v2), new combos can either reference a real ci-cd slug or use `none` to mark that the combo is intentionally CI/CD-agnostic:
- `github-copilot-github-none.md` _(future: combo that explicitly skips ci-cd configuration)_

## Combo File Structure

Each combo file follows this structure (aligned with the shipped combo files in this directory and with `.github/contributor-templates/new-combo-story.md`):

```markdown
# Combo: <Agent Tool> + <Issue Tracker> + <CI/CD>

**Stack:** <agent-tool> · <issue-tracker> · <ci-cd>
**Status:** Maintained | Community | Stub

## Adapters Used
- [Agent Tool](../agent-tools/<adapter-name>/)
- [Issue Tracker](../issue-trackers/<adapter-name>/)
- [CI/CD](../ci-cd/<adapter-name>/) _(planned for v2)_

## Quick Setup
Step-by-step instructions for configuring the three layers together.

## Notes
Integration-specific guidance, known limitations, and links to deeper docs.
```

> Optional sections (Prerequisites, Verification, Known Issues, Changelog) can be added by Community or Maintained combos as needed; they are not required for Stub combos.

## Adding a New Combo

1. Verify that adapters exist in all three layers. The ci-cd layer adapters are planned for v2 — until they ship, use the forward-looking slug `github-actions` (matching the currently-shipped Stubs) or `none` for combos that are intentionally CI/CD-agnostic, and document CI/CD setup as manual steps in the combo's Quick Setup section.
2. Name the file using the `<agent-tool>-<issue-tracker>-<ci-cd>.md` convention.
3. Set status to **Stub** initially.
4. Fill in all sections of the combo file structure above.
5. Test the combo end-to-end on a real repository.
6. Update status to **Community** once verified.
7. Open a PR — include a link to the example repository used for testing.

A combo can be promoted from **Stub** to **Community** by any contributor who provides verification evidence. Promotion from **Community** to **Maintained** requires a maintainer to commit to ongoing responsibility.
