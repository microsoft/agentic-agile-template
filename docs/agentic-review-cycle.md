# Agentic Review Cycle

A tool-neutral pattern for getting a pull request through repeated automated review (GitHub Copilot code review, Claude review, CodeRabbit, or a human) in as few rounds as possible. Tool-specific steps live in the [agent-tools adapters](../platform-adapters/agent-tools/README.md) and [combos](../platform-adapters/combos/README.md).

**Why it matters:** each round costs a full test run and a review wait. Fixing findings one at a time invites a new, adjacent finding every round, and narrow fixes can introduce new defects.

---

## The Rules

1. **Fix whole classes, not instances.** When a finding names one member of a class (one inherited env var), identify the class (all inherited env) and fix it structurally. Add a class-level regression test.
2. **Prefer structural fixes over enumerated ones.** Allowlists over denylists. Pair each with a test that injects several unrelated members and asserts none leak.
3. **Plan holistically after any high-severity finding.** Review all open findings and recent history together, group by root cause, write one fix plan (template below), then implement once.
4. **Triage every finding by origin**, exactly one of: *pre-existing* (the defect existed before this PR's changes and was surfaced by deeper review), *introduced* (created by this PR's changes, including an earlier fix in the same cycle), or *unknown* (origin not yet determined; resolve before closing the round). Introduced gaps signal a missing self-audit.
5. **Audit fixes for introduced gaps.** Check each new mechanism (lock, allowlist, cache, retry) against its own failure modes before requesting review.
6. **Self-audit before the first review.** Run the pre-review checklist below so the first round starts from a class-swept change.
7. **Batch review requests.** Request one exact-head review after a complete, validated batch, never one per finding.
8. **Define the stop condition up front:** stop when the reviewer reports no high or medium findings, or only negligible ones. Record remaining low-severity items instead of chasing them.
9. **Expect depth to grow.** Reviewers dig deeper each round; more rounds do not always mean regressions.
10. **Control validation cost.** Targeted tests per fix; run the full suite once per batch and require it to pass on the exact head **before** requesting review. Run slow suites in the background while preparing the batch (docs, replies, self-audit), and overlap the review wait only with work that does not change the head.
11. **Record the cycle** in the PR (review-cycle log below). The log is **required for every PR**, even when a single round was clean.
12. **Keep the hygiene rules.** Never merge on the agent's behalf; request exact-head reviews; reply to and resolve each addressed thread with the fix commit; verify the commit contains only intended files (no stray temp directories).
13. **Make it durable.** These preferences live in repo guidance (`AGENTS.md` and the adapter files) so every agent session applies them.

---

## Pre-Review Self-Audit Checklist

Run before requesting the first review.

- [ ] For each mechanism touched, name its class and confirm the fix covers the class, not one member.
- [ ] Denylists replaced by allowlists where inputs are open-ended (env, paths, headers, options).
- [ ] Each new lock/cache/allowlist/retry checked against its own failure modes (partial failure, rerun, concurrent run, differing environment).
- [ ] Class-level regression tests exist; malformed input and boundary cases covered.
- [ ] Full suite run once on the exact head being submitted.
- [ ] `git status`/diff shows only intended files.
- [ ] Docs and acceptance criteria updated to match behavior.

## Review-Cycle Checklist (per round)

- [ ] Collect all open findings and unresolved threads for the **exact head**.
- [ ] Triage each by origin (pre-existing / introduced / unknown); severity; class.
- [ ] If any high severity or a repeated class: write a fix plan (below) before editing.
- [ ] Implement as one batch; targeted tests, then full suite once.
- [ ] Commit; reply to and resolve each thread with the fix commit.
- [ ] Request one exact-head review.
- [ ] Check stop condition; if met, log remaining low items and hand to a human to merge.

## Fix-Plan Template

```markdown
### Fix plan — PR #<n>, round <r>
**Open findings:** <ids/links>
**Root-cause groups:**
| Group (class) | Findings | Origin (pre-existing/introduced/unknown) | Severity |
|---|---|---|---|
**Shared design:** <structural fix, e.g. allowlist>
**Blast radius:** <files, behaviors, callers affected>
**Introduced-gap audit:** <failure modes of the new mechanism and how they are handled>
**Validation:** <class-level tests, targeted tests, full suite once>
**Review request:** exact head <sha> after batch complete
```

## Review-Cycle Log (record in the PR)

| Round | Review ID / head SHA | Findings (H/M/L) | Finding → class map | Origin counts (pre-existing / introduced / unknown) | Fix commit(s) | Validation evidence |
|---|---|---|---|---|---|---|

Stop condition: <agreed up front>. Remaining low-severity items: <list>.

A **round** is one distinct reviewed head SHA: several reviewers or repeated submissions on the same head count as one round.

---

## Worked Example (anonymized): forensic-ingest skill PR

Atomic fixes produced many rounds because each finding was one member of a larger class.

| Class | Findings fixed one at a time | Structural fix that would have closed the class |
|---|---|---|
| Git environment isolation | attributes, fsmonitor, `log.showSignature`, repository routing, `GIT_DIFF_OPTS`/`diff.context` | Run git with an inherited-environment allowlist and pinned config; test by injecting several unrelated `GIT_*`/config values and asserting none reach the subprocess |
| Locking | lock root depended on per-process temp settings (introduced by a prior fix) | Derive the lock root from a stable, explicit location; audit the lock for rerun, concurrent run and differing-environment failure modes |
| Hygiene | stray temp directory committed once | Pre-commit diff check for intended files only |

Lessons: group by root cause after the first high-severity finding; audit your own new mechanisms; batch the review request; agree the stop condition early.

---

## Reviewer-Agnostic Notes

The pattern is identical for every reviewer. Only *how to request and read an exact-head review* differs.

| Reviewer | Request exact-head review | Read findings | Notes |
|---|---|---|---|
| GitHub Copilot code review | Request via PR reviewers (UI/`gh`) after pushing the batch | PR review comments/threads on the head SHA | Re-requested review reviews the new head; see [Copilot adapter](../platform-adapters/agent-tools/github-copilot/README.md) |
| Claude (e.g. GitHub Action / `/review`) | Trigger on the pushed head once | Review comments/summary | See [Claude adapter](../platform-adapters/agent-tools/claude/README.md) |
| CodeRabbit or similar bot | Comment command or push triggers; avoid per-commit triggers by pushing once per batch | Walkthrough + inline comments | Pause incremental review while batching if supported |
| Human reviewer | Request review after batch is complete and CI green | Threads | Same stop condition and log |

Other agents (Cursor, Cline, Windsurf, Aider) apply the rules via their conventions files; trackers other than GitHub carry the log fields through the [field mapping](../platform-adapters/issue-trackers/README.md).

## Metrics

Defined in [`evaluation-framework.md`](evaluation-framework.md): rounds to clean, findings per round, recurring-class share, introduced-gap rate.

## Related

[`MANIFESTO.md`](../MANIFESTO.md) · [`AGENTS.md`](../AGENTS.md) · [`STYLE.md`](../STYLE.md) · [`CONTRIBUTING.md`](../CONTRIBUTING.md)
