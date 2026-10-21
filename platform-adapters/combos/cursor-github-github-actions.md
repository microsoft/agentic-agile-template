# Combo: Cursor + GitHub Issues + GitHub Actions

**Stack:** [Cursor](../agent-tools/cursor) · [GitHub Issues](../issue-trackers/github) · [GitHub Actions](../ci-cd)
**Status:** Stub

## Adapters Used

- **Agent Tool:** [../agent-tools/cursor](../agent-tools/cursor)
- **Issue Tracker:** [../issue-trackers/github](../issue-trackers/github)
- **CI/CD:** [../ci-cd](../ci-cd)

## Quick Setup

1. Follow the agent tool quickstart: [../agent-tools/cursor/quickstart.md](../agent-tools/cursor/quickstart.md)
2. Follow the issue tracker quickstart: [../issue-trackers/github/quickstart.md](../issue-trackers/github/quickstart.md)
3. Follow the CI/CD setup guide: [../ci-cd/README.md](../ci-cd/README.md)

## Review Cycle

Pattern: [Agentic Review Cycle](../../docs/agentic-review-cycle.md). Cursor does not review PRs on GitHub itself; use the reviewer configured on the repo (for example Copilot code review or a Claude/bot review via GitHub Actions) and request it once on the exact head after pushing a validated batch. Read findings from the PR threads for that head SHA, fix them as one class-level batch in Cursor (paste the fix plan into Composer), reply to and resolve each thread with the fix commit, and record the round in the PR's review-cycle log.

## Notes

Cursor is a popular choice for teams transitioning from VS Code, as it retains a familiar editor experience while adding agentic capabilities. Verify the filename convention when storing stories as issues, as Cursor resolves file references differently from terminal-based agents. The Composer feature works well with structured stories: paste the issue body directly into a Composer prompt to have Cursor implement the full story in one session.
