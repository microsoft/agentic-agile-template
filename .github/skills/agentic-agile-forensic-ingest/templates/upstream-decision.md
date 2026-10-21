${marker}
## Summary

Review the evidence-backed upstream delta for `${profile_id}`.

## Evidence boundary

| Field | Immutable evidence |
|---|---|
| Baseline | `${baseline_sha}` |
| Source tip | `${source_tip}` |
| Fork tip | `${fork_tip}` |
| Run manifest | `${manifest_sha256}` |
| Selected commits | ${commit_count} |
| Unsynced commits | ${unsynced_count} |
| Semantic groups | ${semantic_group_count} |

## Semantic groups and commit inventory

${semantic_group_inventory}

## Decision required

The fork maintainer must decide whether, when, and how to incorporate this
upstream delta. This open record does not claim that the fork delivered,
reviewed, tested, or deployed the upstream work.

## Negative constraints

- Do not merge, rebase, cherry-pick, or push automatically.
- Do not create closed historical delivery records until incorporation is
  proven.
- Do not infer original prompts, approvals, tests, or dependencies.
