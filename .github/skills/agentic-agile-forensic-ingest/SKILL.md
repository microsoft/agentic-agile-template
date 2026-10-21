---
name: agentic-agile-forensic-ingest
description: 'Reconstruct evidence-backed Git history and recurring upstream deltas into deterministic Agentic-Agile manifests and GitHub issue records. Use for repository adoption, forensic backlog reconstruction, fork/upstream traceability, resumable issue publication, or contribution-back recommendations.'
license: MIT
---

# Agentic-Agile Forensic Ingest

Analyze immutable Git evidence without changing history, render evidence-backed
Agentic-Agile issue drafts, and optionally publish verified records to GitHub.

## When to Use This Skill

- Reconstruct delivered work from a repository that did not retain its backlog.
- Inspect commits added upstream since a fork's last verified ingest.
- Record unsynced upstream work as an open fork decision record.
- Record incorporated upstream work as closed historical evidence.
- Identify fork-only product changes that may merit a human-led upstream
  contribution while suppressing process/governance overlays.

## Prerequisites

- Python 3.9 or later, using only the standard library.
- Git 2.45 or later available on `PATH`.
- GitHub CLI (`gh`) authenticated only when running `publish-github`.
- A clean understanding of the source ref, fork ref, and initial immutable
  baseline.

## Safe Workflow

1. Copy and customize
   [`templates/config.example.json`](./templates/config.example.json) and
   [`templates/state.example.json`](./templates/state.example.json).
2. Run `analyze`, then `validate` the deterministic run manifest before
   rendering or publication.
3. Run `render` and inspect every draft. Rendering does not contact GitHub.
4. Run `publish-github` without flags to review the local dry-run plan, then
   add `--execute` only after human approval. It is the only operation allowed
   to contact GitHub or advance state.
5. Run `recommend-upstream-contribution` separately. Treat its output as a
   recommendation for humans, never permission to create an upstream branch,
   pull request, or message.

```text
python scripts/forensic_ingest.py analyze --config <config> --state <state> --output <manifest>
python scripts/forensic_ingest.py validate --config <config> --manifest <manifest> --state <state>
python scripts/forensic_ingest.py render --manifest <manifest> --output <drafts>
python scripts/forensic_ingest.py publish-github --config <config> --manifest <manifest> --drafts <drafts> --state <state> --publication-state <publication-state> [--execute]
python scripts/forensic_ingest.py recommend-upstream-contribution --config <config> --output <report>
```

Read the detailed contracts before adapting the workflow:

- [Evidence model](./references/evidence-model.md)
- [Manifest schema](./references/manifest-schema.md)
- [Issue lifecycle](./references/issue-lifecycle.md)

## Safety Boundaries

- Treat `analyze`, `validate`, `render`, and
  `recommend-upstream-contribution` as local dry-run operations.
- Permit GitHub access only through `publish-github --execute`, and only in
  the configured fork repository. Without `--execute` it validates inputs and
  any existing publication checkpoint locally, prints the planned issue order,
  and neither contacts GitHub nor writes state.
- Exit codes: `0` success, `1` deterministic failure (diagnostics on stderr,
  credential-redacted), `2` usage error.
- Advance ingest state only after publication and remote verification succeed.
- Keep extraction and manifests host-neutral. GitHub behavior belongs only in
  the publisher.
- Preserve full commit SHAs and immutable object metadata. Never replace them
  with issue timestamps or inferred chronology.

## Gotchas

- **Never use a rewritten or disconnected baseline.** The baseline must still
  be an ancestor of the configured source tip. A failure requires human
  reconciliation, not silently selecting a new merge base.
- **Do not equate changed test paths with passing tests.** A path touch is
  evidence of a change, not evidence of execution or acceptance.
- **Do not publish closed delivery records for unsynced work.** Unsynced
  upstream changes remain an open decision record until exact or
  patch-equivalent incorporation is proven.
- **Treat semantic groups as deterministic navigation, not recovered intent.**
  Each commit is assigned once by its primary top-level changed-path component;
  the grouping does not reconstruct original epics, prompts, or approvals.
- **Do not infer dependencies from timestamps.** Only explicit draft
  dependencies are published, and the complete graph is validated before any
  write.
- **Do not edit an existing marked issue automatically.** Marker collisions or
  remote drift fail closed so a human can decide how to reconcile them.
- **Replace the template baseline.** `initial_baseline_sha` in the example
  configuration is an all-zero sentinel and must be set to a real immutable
  commit before running `analyze`.
- **Do not place tokens in configuration.** The publisher relies on the
  authenticated `gh` credential helper and redacts credential-like diagnostics.
- **Do not treat a contribution recommendation as authorization.** The command
  never creates upstream branches, pull requests, comments, or messages.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Baseline is rejected | Restore/fetch the expected immutable commit or reconcile a documented upstream rewrite with a new human-approved state file. |
| Validation reports coverage drift | Re-run `analyze` against unchanged refs and do not hand-edit commit assignments. |
| Duplicate marker is reported | Remove or reconcile the duplicate GitHub records manually; publication intentionally stops before writing. |
| Publication is throttled | Leave the command running; bounded exponential recovery handles GitHub secondary-rate-limit responses. |
| Existing issue differs from the draft | Review the remote change and choose a new run or manual reconciliation. The publisher will not overwrite it. |

## Validation

Run:

```text
python -m unittest discover -s .github/skills/agentic-agile-forensic-ingest/tests -v
python .github/skills/agentic-agile-forensic-ingest/scripts/forensic_ingest.py --help
```
