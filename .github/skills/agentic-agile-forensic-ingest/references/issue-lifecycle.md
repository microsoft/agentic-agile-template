# Issue Lifecycle

## Unsynced upstream delta

If any selected source commit is absent from the fork by exact reachability and
stable patch equivalence, render one **open decision record**. The record:

- identifies the immutable source/fork/baseline SHAs;
- lists every selected commit exactly once;
- distinguishes incorporated and unsynced commits;
- asks the fork maintainer to decide whether and how to incorporate the delta;
- makes no claim that the fork delivered the upstream work.

Publishing this record may advance `last_verified_source_sha` as an observation
checkpoint. It must not advance `incorporated_baseline_sha`. Later runs continue
selecting from the incorporated baseline, retaining unresolved commits alongside
any newer upstream commits until incorporation is proven.

Decision records are immutable per-run snapshots: their identity includes the
run ID, so a later run never edits or closes an earlier run's decision issue.
Publication reports earlier runs' still-open decision issues for the same
profile in `open_decision_issues_from_other_runs`; the fork maintainer closes
them once the decision is recorded.

## Incorporated source work

If every selected commit is incorporated exactly or patch-equivalently, render
closed historical parents with closed child stories grouped deterministically
by primary changed-path area. Each parent contains at most 100 direct children;
larger histories are partitioned into stable 100-group chunks before any remote
write. These are retrospective evidence records. Their timestamps are
publication timestamps, not original implementation timestamps.

After verified publication, both the verified-source and incorporated
baselines may advance to the source tip.

## Stable markers and reruns

Every issue begins with:

```text
<!-- forensic-ingest-id:<logical-id> -->
```

Before writing, publication discovers all markers in the target repository and
rejects duplicates. Existing exact records are adopted for resume/idempotency.
An existing marked issue that differs from the draft fails closed rather than
being overwritten. Publication state records whether an issue was created by
the publisher or adopted only by marker; only a publisher-created issue may
resume a recorded pending historical close. A deterministic creation intent is
written before each GitHub issue-creation call, allowing safe publisher-created
re-adoption if the process stops after the remote create but before the local
issue number and database ID are checkpointed.

## Hierarchy and dependencies

Historical child stories are linked with GitHub's native sub-issue API.
Dependencies and `{{issue:<logical-id>}}` references are resolved only after a
complete unknown-reference and cycle check. No label, issue, or hierarchy write
occurs before that validation.

## Remote verification

Publication is not complete until the publisher re-reads the target repository
and verifies titles, bodies, states, closure reasons, labels, markers, and
native parent-child links. Ingest state advances only after that verification.

## Contribution-back recommendations

Fork-only analysis is separate from upstream-delta publication. Commits whose
changed paths and subjects are entirely covered by configured
process/governance suppression rules are omitted from recommendations.
Rename suppression evaluates both source and destination paths, so moving a
product path into an overlay path remains a contribution candidate.
Fork-only commits whose stable patch is already present in source are reported
separately as `already_in_source`, not as contribution candidates.
Merge commits are also suppressed because they are not standalone contribution
candidates. A subject match alone does not suppress a commit that changes
non-overlay product paths.
Remaining commits are local evidence for a human decision. The skill never
contacts upstream or creates upstream Git/GitHub objects.
