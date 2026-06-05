# CI/CD Adapters

> **Status: Planned for v2**
>
> The ci-cd adapter layer is not yet implemented. This directory is a placeholder that documents what's coming and how to contribute early designs.

## What Are CI/CD Adapters?

A **ci-cd adapter** wires up the pipeline checks that the Agentic-Agile workflow expects: automated test runs, lint gates, and story-verification steps that give agents and reviewers fast, deterministic feedback on whether a story's acceptance criteria have been met.

In v1, CI/CD configuration is left to teams to wire up manually using their existing pipeline knowledge. In v2, ci-cd adapters will provide ready-made pipeline templates that integrate with the agent-tools and issue-trackers layers.

## What's Coming in v2

### Planned Adapters

| Adapter | CI/CD System | Planned Features |
|---------|-------------|-----------------|
| `github-actions/` | GitHub Actions | Workflow templates for test, lint, story-verify |
| `azure-pipelines/` | Azure Pipelines | YAML pipeline templates with stage gates |
| `gitlab-ci/` | GitLab CI/CD | `.gitlab-ci.yml` templates |
| `jenkins/` | Jenkins | Jenkinsfile templates with parallel stages |
| `circleci/` | CircleCI | `config.yml` templates |

### Planned Capabilities

Each ci-cd adapter will provide:

1. **Test gate** — Run the project's test suite and block merge on failure. Configured to align with the test strategy declared in the agent-tools adapter.

2. **Lint gate** — Run language-appropriate linters and formatters. Blocks merge on rule violations.

3. **Story-verify step** — A pipeline step that reads acceptance criteria from the linked story and runs the specified verification commands. Enables agents to declare "this story is done" with machine-verifiable evidence.

4. **Wave-execution support** — Pipeline configuration that reflects the wave-based parallel execution model, allowing concurrent story branches to run their checks in parallel.

5. **Agent-authored PR check** — Validates that PRs from agents include the required metadata (story link, acceptance criteria evidence, file scope compliance).

### Integration with the Three-Layer System

When the ci-cd layer ships, the three-layer adapter system will be complete:

- **agent-tools** — configures the AI agent → see [../agent-tools/](../agent-tools/)
- **issue-trackers** — provides story templates → see [../issue-trackers/](../issue-trackers/)
- **ci-cd** (this layer) — wires up pipeline checks
- **combos** — pre-assembled combinations → see [../combos/](../combos/)

## Contributing Early Designs

If you want to contribute a ci-cd adapter ahead of v2:

1. Create a `platform-adapters/ci-cd/<system-name>/` directory.
2. Add a `README.md` describing the pipeline template and what it provides.
3. Add the pipeline configuration file(s) as templates.
4. Open a PR with the label `ci-cd-adapter` and note that it's an early/experimental contribution.
5. The adapter will be listed in [../combos/README.md](../combos/README.md) with status **Stub** until it passes end-to-end testing.

## Timeline

The ci-cd adapter layer is tracked as part of the v2 roadmap. Follow the project's GitHub Issues for updates.
