# Originating Prompts — Disconnected-Fork Consolidation (Waves 0–6)

> **Companion artifact** to [`2026-06-consolidation.md`](./2026-06-consolidation.md) (Wave 7 retrospective). This file preserves the user prompts (planning phase P1–P8 + execution-phase amendments E1–E6) that drove the consolidation initiative.
>
> **Redaction & retention policy for this public-facing copy:**
>
> - **Redacted:** the internal-staging GitHub organization slug, internal account handles, and any URLs pointing at the internal staging tracker. Placeholders such as `[REDACTED internal org]`, `[REDACTED]`, and `[REDACTED internal-org issue tracker]` mark each removal.
> - **Retained (intentionally):** bare internal-tracking issue numbers (e.g., `#31`, `#42`, `#58`) and commit short-SHAs (e.g., `75661d3`). These are kept verbatim so the maintainer team can cross-reference the originating issues in the internal staging tracker. Public readers without internal access can treat them as opaque change-tracking anchors.
> - **Otherwise verbatim:** the substantive user-authored text of every prompt is preserved as captured.
> - **Session-state references:** a few prompts reference planning artifacts that lived in the agent's session workspace (e.g., `plan.md`, `files/...`) and were not committed to the repo. Where such pointers appeared in the original text, they have been rewritten in place to describe the artifact's role rather than link to it.

---


## P1 — Initial freeform request

**Timestamp (UTC):** 2026-06-05T14:59:01Z
**Prompt type:** freeform (plan-mode initial request)

### Verbatim prompt text

```text
# Disconnected git forked repo consolidation and cleanup

Please evaluate both repos referenced below, including all local and remote branches, and propose the best method to reconnect them for a cleaner, more logical and sustainable maintenance flow. Do not make code changes at this time, only propose a process and write the plan.

## Objectives

- At the conclusion of this plan execution, both repos will be up-to-date and in sync with eachother
- The most current work around onboarding and generalizing the repo in the [REDACTED internal] version will be preserved and consistent (see below)
- Changes to the public repo after the repos diverged will be reviewed and incorporated into the refactored version if it is still relevant
- A final, detailed adversarial code review will be performed with issues
- This merger process will follow Agentic-Agile metholodogy (issues in backlog first, detailed specification and decomposition, execution in waves, retrospective)

## Repositories

- Internal version on private [REDACTED internal org] GitHub:
   - Remote: [REDACTED private repo]
   - Local: '/workspaces/agentic-agile-template'
   - GitHub admin account: [REDACTED]
- Public version on Microsoft open source GitHub:
   - Remote: ['microsoft/agentic-agile-repo'](https://github.com/microsoft/agentic-agile-repo)
   - Local: '/workspaces/agentic-agile-template-pub'
   - GitHub admin account: 'dgepstein', my public GitHub account
   - Branch protections are in place on 'main' requiring JIT admin approval for PR merges.

## Background

- '[REDACTED internal org]/agentic-agile-template' was the original project that was then forked to the public repo.
- 'microsoft/agentic-agile-template' was created as a disconnected fork for publication several weeks ago.
- Since forking, minor development work has been completed in the public version to add some clarifications and cleanup.
- Recently, significant development work has been completed in the '[REDACTED internal org]' repo to:
   - Add an human + agent  onboarding flows
   - Add human + agent contribution guidelines for public contributors
   - Expand and generalize the repo to reflect the Agentic-Agile methodology in multiple agent and issue tracking toolsets
- Work in public was completed with GitHub Copilot CLI working in an Agentic-Agile methodology on one of laptop systems
   - Copilot session history is not available for context but the public repo issues and git commit logs should provide context
   - Issues in public marked 'SAMPLE' are not real working issues but are example github issues to illustrate the issue creation methodology (mostly for human reference)
- Most of the recent work in the '[REDACTED internal org]' repo was accomplished with [Amplifier](https://github.com/microsoft/amplifier) in this GitHub Codespace
   - Agentic-Agile methodology was loosely followed by Amplifier using the 'amplifier-dev' bundle, but many issues were logged retroactively
   - Amplifier session context should be available and consulted, along with git issues and commit logs
- Both repos have had branch merge and PR resolution confusion caused by agents taking different approaches to squash merging and fast forwarding branches
   - This means that you must pay careful attention to the contents of files in different branches and in the larger context of the project
   - Ask for clarification if there is any ambiguity
- Work is being done in this Codespace using a private internal account against a private internal staging repo as the primary target for the following reasons:
   - [REDACTED internal org] budget is available to pay for the Codespace and LLM consumption
   - Branch protections on 'microsoft/agentic-agile-template' 'main' branch may impede cleanup work
   - I want a staging environment for the work-in-flight and final review that is not publicly visible

## Decisions requiring Agent feedback

- Should the next phase of work be completed by Amplifier or GitHub Copilot?
- Should the public repo become canonical and the '[REDACTED internal org]' repo become a downstream fork that pushes back to the parent when changes are made internally?
- Should the 'SAMPLE' github issues be removed from the public repo to avoid clutter and allow for real issues in backlog from external contributors?
```

---

## P2 — Multiple-choice selection on D1 (canonical direction)

**Timestamp (UTC):** ~2026-06-05T15:01Z
**Prompt type:** multiple-choice selection (response to agent's ask_user on D1)
**Agent question:** "For the long-term maintenance model, which direction do you want to be canonical going forward?"

### Verbatim selection

```text
B. Public canonical / [REDACTED internal org] is private downstream — Treat microsoft/agentic-agile-template as the true upstream; the internal mirror becomes a private fork that pushes changes back via PRs to public. Aligns with conventional OSS practice but introduces friction from JIT branch protection on every change.
```

---

## P3 — Multiple-choice selection on D2 (PR strategy into public)

**Timestamp (UTC):** ~2026-06-05T15:02Z
**Prompt type:** multiple-choice selection (response to agent's ask_user on D2)
**Agent question:** "How do you want the [REDACTED internal org] → Public reconciliation to land, given JIT branch-protection on public's main?"

### Verbatim selection

```text
C. Two-stage: a foundation PR + a generalization PR — PR1 lands the small public-style updates and basic onboarding; PR2 lands the entire platform-adapters tree. Balanced compromise.
```

---

## P4 — Multiple-choice selection on D3 (SAMPLE issues)

**Timestamp (UTC):** ~2026-06-05T15:03Z
**Prompt type:** multiple-choice selection (response to agent's ask_user on D3)
**Agent question:** "How should I treat the 10 SAMPLE issues currently open in the public repo, given that real external contributors are now expected?"

### Verbatim selection

```text
A. Convert to docs + close issues (Recommended) — Migrate the 10 SAMPLE issues into a `docs/sample-issues/` markdown reference (rendered examples with the same content), then close the GitHub issues with a comment pointing to the docs location. Backlog becomes clean for real external contributors; educational value is preserved and even more discoverable.
```

---

## P5 — Freeform feedback on first plan (consolidation branch)

**Timestamp (UTC):** ~2026-06-05T15:08Z
**Prompt type:** freeform feedback during exit_plan_mode review

### Verbatim prompt text

```text
Should we introduce a 'dev' or 'consolidation' branch in '[REDACTED internal org]/agentic-agile-template' to land these waves and then promote that to 'main'  when all work has landed in 'dev' and been reviewed?
```

---

## P6 — Freeform feedback on second plan (epic and child issues)

**Timestamp (UTC):** ~2026-06-05T15:11Z
**Prompt type:** freeform feedback during exit_plan_mode review

### Verbatim prompt text

```text
Detailed Epic and child issues should be created in '[REDACTED internal org]/agentic-agile-template' to reflect the plan.
```

---

## P7 — Freeform feedback on third plan (prompt capture)

**Timestamp (UTC):** ~2026-06-05T15:14Z
**Prompt type:** freeform feedback during exit_plan_mode review

### Verbatim prompt text

```text
Are you also capturing my original prompts in the issue to be written? We will need these for retrospective.
```

---

## P8 — Freeform clarifying question on D4 reasoning (Copilot CLI vs Amplifier)

**Timestamp (UTC):** ~2026-06-05T15:17Z
**Prompt type:** freeform clarifying question during exit_plan_mode review
**Stated intent:** information-seeking; user explicitly noted "I'm not asking you to change this — just curious"
**Plan impact:** No structural change to the plan; §3 expanded with detailed rationale because the question itself was evidence that the prior §3 was too terse to be self-evident to the reader.

### Verbatim prompt text

```text
Why are you suggesting Copilot CLI vs Amplifier for execution? I'm not asking you to change this--just curious as to your reasoning.
```

---

## Future prompts (P9+)

Append any further planning-phase prompts here, in order, using the same format,
before Wave 0 issue filing begins. Execution-phase prompts (E1, E2, ...) are
captured per a Prompt Capture Protocol that lived in the agent's session-workspace
planning notes (not committed to the repo) — they go into the
Top Epic body and into a comment on the relevant Story Issue, not into this file.

---

# Execution-Phase Prompts (mirror of Top Epic §"Originating Prompts — Execution Phase")

This section is the canonical mirror of the execution-phase prompt log that lives
inside Top Epic #31's body. It is kept here as a backup against accidental loss
of the GitHub issue body. Entries are append-only and chronological.

## E1 — Multiple-choice selection on public-repo write strategy

**Timestamp (UTC):** 2026-06-05T15:50:39Z
**Prompt type:** multiple-choice selection (response to agent `ask_user` during Wave 0 execution)
**Stated intent:** confirm handoff pattern for public-repo writes after the agent discovered a write block (HTTP 403)
**Plan impact:** clarification + new process artifact for tracking public-side handoff actions; story #42 → `blocked` / `awaiting-manual-handoff`; downstream external-PR stories inherit handoff model.

### Question asked (verbatim, from `ask_user`)

```text
The current `gh` auth (`[REDACTED]` EMU token) can read but cannot write
to `microsoft/agentic-agile-template` (got HTTP 403 trying to create labels). This
blocks `wave0-file-public-issues` (filing 3 tracker issues there) as well as all
external PR / issue-closure work in Waves 2, 3, 4, 6, 7. How would you like to
handle public-repo write access?
```

### User's response (verbatim selection)

```text
Defer all public-side writes — I'll file the 3 trackers and handle external PRs manually as `dgepstein` when each is ready (Recommended for Wave 0; external PRs are weeks away anyway)
```

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E1)
- Story comment: [REDACTED internal-org issue tracker]

---

## E2 — Multiple-choice selection on Wave 1 execution mode

**Timestamp (UTC):** 2026-06-05T15:54:08Z
**Prompt type:** multiple-choice selection (response to agent `ask_user` at Wave 0 → Wave 1 handoff)
**Stated intent:** authorize Wave 1 end-to-end autopilot execution; pause only on blockers
**Plan impact:** no plan change; confirms autopilot mode for Wave 1 stories #43, #44, #45, #46

### Question asked

```text
How should I proceed into Wave 1?
```

### User's response (verbatim selection)

```text
Proceed into Wave 1 in autopilot — you handle the merge + conflict resolution + verification + internal PR end-to-end, pausing only for issues that need my input (Recommended)
```

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E2)
- Story comment: [REDACTED internal-org issue tracker]


---

## E3 — Multiple-choice selection on Wave 2/3/4 branch construction pattern

**Timestamp (UTC):** 2026-06-05T16:05:14Z
**Prompt type:** multiple-choice selection (response to agent `ask_user` on a structural ambiguity discovered at Wave 2 entry)
**Stated intent:** resolve the architectural conflict between plan §5's "internal PR to consolidation" pattern and the reality that consolidation already contains all the files Waves 2/3/4 are meant to surface as external PRs
**Plan impact:** structural — eliminates the per-wave internal-PR step for Waves 2/3/4; affects stories #48, #51, #55 (closed as obsolete) and the acceptance criteria of #47, #49, #52 (verification target changes from `consolidation` to `upstream/main`); branch base for `feat/foundation-pr`, `feat/generalization-pr`, `feat/sample-cleanup` becomes `upstream/main` rather than `consolidation`

### Question asked (verbatim, from `ask_user`)

```text
Plan §5 says: "From `consolidation`, create `feat/foundation-pr` containing only the onboarding scaffolding... Open internal PR to `consolidation`, review, merge. Then open external PR to public `main`."

But there's a structural conflict: `consolidation` already contains all 7 foundation files (they came in via internal-staging Phase 1 before we even started). So an "internal PR to consolidation" is either (a) a no-op if the branch starts FROM consolidation, or (b) a giant rollback PR if the branch is constructed to "only contain" those 7 files (which means branching from upstream/main and cherry-picking).

Reading (b) makes architectural sense for producing the surgical external PR1, but means there's no meaningful internal PR step — the branch sits as a staging branch for the eventual external PR after Wave 6.

Which interpretation do you want me to follow for Waves 2, 3, and 4? (This will be captured as execution-phase prompt E3.)
```

### User's response (verbatim selection)

```text
A. Branch from upstream/main + cherry-pick the wave's files; skip the internal PR (it's a no-op or regression); the branch is purely the staging branch for the eventual external PR after Wave 6. Verification = `git diff upstream/main..feat/<branch>` matches the wave's file list.
```

### Interpretation (executor's summary)

For Waves 2, 3, and 4: each wave's `feat/*` branch is created off `upstream/main` (NOT off `consolidation`). The wave's files are cherry-picked from `consolidation` onto the branch. The branch is then pushed to the internal-staging origin and held there as the staging branch for the eventual external PR to public main (which is deferred until after Wave 6 per plan §5). No internal PR into `consolidation` is opened for these waves. Verification is via `git diff upstream/main..feat/<branch> --name-status`, which must list only the wave's owned files. Internal review of the integrated state happens via Wave 6's adversarial-review pass against `consolidation` (which already has everything these branches produce).

### Resulting changes

- Plan §5 updated: Wave 2/3/4 entries clarified to base branches off `upstream/main`; "internal PR to consolidation, review, merge" step removed for these three waves; new verification criterion specified.
- SQL todos: `wave2-internal-pr-foundation`, `wave3-internal-pr-generalization`, `wave4-internal-pr-sample` marked `done` with description note "removed per E3 — no internal PR needed".
- Story issues #48, #51, #55 closed as `not_planned` with explanation comment linking to E3.
- Story issues #47, #49, #52 amended (via comment) with the corrected verification target.
- Branch construction for `feat/foundation-pr` (Wave 2) now starts in this turn off `upstream/main`.

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E3)
- Story comment: [REDACTED internal-org issue tracker] (E3 mirror comment)

---

## E4 — Multiple-choice selection on collapsing PR1+PR2 into a single PR (amends D2)

**Timestamp (UTC):** 2026-06-05T16:14:00Z
**Prompt type:** multiple-choice selection (response to agent `ask_user` flagging a cross-reference structural problem)
**Stated intent:** resolve the discovered cross-reference issue between PR1 (foundation) and PR2 (generalization) where PR1's `AGENTS.md` and `CONTRIBUTING-AGENTS.md` heavily reference paths (`platform-adapters/**`, `docs/plans/**`) that don't exist until PR2 lands; user opted to collapse the two PRs into one
**Plan impact:** structural — amends D2 (locked decision) from "Two-stage PRs (Foundation + Generalization)" to "Single combined PR (Foundation+Generalization)"; consolidates Waves 2 and 3 into a single execution stream; affects the staging branch construction, story closures, and external-PR flow

### Question asked (verbatim, from `ask_user`)

```text
Wave 2 cross-reference issue: AGENTS.md and CONTRIBUTING-AGENTS.md (planned for PR1) heavily reference platform-adapters/** and docs/plans/**, neither of which exists on upstream/main or PR1's feat/foundation-pr branch. The tree won't exist in public until PR2 (Wave 3) lands. Examples:
- AGENTS.md: "Read context first. Locate and read your platform adapter in `platform-adapters/` before starting any task."
- CONTRIBUTING-AGENTS.md: heavy references to platform-adapters/agent-tools/, platform-adapters/issue-trackers/, etc.
- CONTRIBUTING-AGENTS.md line 14: references docs/plans/2026-06-04-multi-platform-generalization-design.md

Landing PR1 standalone would create a window where public has files pointing at non-existent paths. How would you like to handle this?
```

### User's response (verbatim selection)

```text
C. Collapse PR1 and PR2 into a single PR — effectively reverting D2's two-stage strategy. Simpler review, no cross-reference issues, but a bigger PR to review.
```

### Interpretation (executor's summary)

D2 (the locked decision to use a two-stage PR strategy: PR1 Foundation + PR2 Generalization) is amended in execution. The combined work (all 40 files: 36 adds, 3 modifies, 1 rename) is staged on a single branch — to be named `feat/consolidation-to-public` — branched from `consolidation` (which already contains all 40 files by construction after the Wave 1 sync merge). The branch is pushed to the internal-staging origin and held as the staging branch for a SINGLE external PR to public `main`, opened after Wave 6 adversarial review. Wave 2 is administratively closed and its content absorbed into Wave 3, which is renamed to reflect the unified scope. Wave 4 (SAMPLE cleanup) and Wave 6 (adversarial review) remain unaffected — they keep their own staging branches. Wave 7 retrospective will note that D2's two-stage premise was reversed in execution.

### Resulting changes

- **Plan §5:** D2 amended in §2 (decision table → "Single combined PR — amended per E4"); §5 Wave 2 collapsed; Wave 3 redefined as the unified Foundation+Generalization wave.
- **Story closures (as obsolete per E4):**
  - #34 Wave 2 Epic — closed, content absorbed into #35
  - #47 `wave2-prepare-foundation-branch` — closed
  - #59 `wave2-external-pr-foundation` — closed
- **Story amendments (scope expanded):**
  - #35 Wave 3 Epic — title and body updated to "Wave 3 — Unified Foundation+Generalization PR (formerly PR2; now sole external PR)"
  - #49 `wave3-prepare-generalization-branch` — amended to "prepare unified foundation+generalization branch" (`feat/consolidation-to-public` off `consolidation`); 40-file scope; verification updated
  - #60 `wave3-external-pr-generalization` — amended to "external PR — unified Foundation+Generalization"
- **SQL todos:**
  - `wave2-prepare-foundation-branch`, `wave2-external-pr-foundation` → `done` with E4 note (obsoleted)
  - `wave3-prepare-generalization-branch`, `wave3-external-pr-generalization` → scope expanded
- **Branch construction:** `feat/consolidation-to-public` is created from `consolidation` tip (no cherry-pick needed; the branch IS consolidation by construction). When Wave 6 critical fixes land on consolidation, this branch is fast-forwarded to consolidation's tip.

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E4)
- Story comment (most affected): [REDACTED internal-org issue tracker] (E4 mirror)

---

## E5 — Multiple-choice selection on collapsing Wave 4 into the unified PR

**Timestamp (UTC):** 2026-06-05T16:21:00Z
**Prompt type:** multiple-choice selection (response to agent `ask_user` on a coordination concern between Wave 4 SAMPLE cleanup and the E4 unified PR)
**Stated intent:** consolidate execution further by absorbing Wave 4 into the unified PR rather than running two simultaneous external PRs that both touch README.md
**Plan impact:** structural — extends the E4 collapse pattern; Wave 4 epic #36 closes as content absorbed into Wave 3 epic #35; Wave 4 stories' external-PR step becomes obsolete; Wave 4 content lives on `consolidation` (and propagates to `feat/consolidation-to-public` via fast-forward); D3 (SAMPLE cleanup as separate PR) is implicitly amended to "SAMPLE cleanup ships with the unified PR"

### Question asked (verbatim, from `ask_user`)

```text
Wave 4 (SAMPLE issue cleanup) structural question: I'm about to create feat/sample-cleanup off upstream/main per the E3 pattern, but there's a coordination wrinkle — both the unified PR (E4) and Wave 4 modify README.md (different sections). If both PRs are open simultaneously, whichever merges second will hit a merge conflict on README.md.

The two-PR conflict argument that drove E4 (collapse PR1+PR2) applies here too: keeping Wave 4 separate buys conceptual clarity at the cost of an extra coordination round. How would you like to handle it? (Captured as E5.)
```

### User's response (verbatim selection)

```text
A. Collapse Wave 4 INTO the unified PR (matches E4's collapse rationale). Single external PR carries onboarding + generalization + sample-cleanup. Wave 4 epic #36 closes as content absorbed into Wave 3 epic #35. No separate sample-cleanup PR. (Recommended)
```

### Interpretation (executor's summary)

Wave 4 content (`docs/sample-issues/**` plus README.md "Sample Issues" section update) lands on `consolidation` directly. `feat/consolidation-to-public` fast-forwards to the new tip. The unified external PR (#60) now carries:
- Foundation + Generalization (40 files from E4)
- + 11 new files under `docs/sample-issues/` (10 issue snapshots + 1 index README)
- + Modified README.md Sample Issues section

The closure of the 10 SAMPLE issues themselves (Story #62) is **not** in the PR — that happens via API after the unified PR merges (post-Wave 6). Story #52 (prepare-branch) and Story #61 (external-PR) are closed as obsolete; Stories #53 and #54 remain active but execute against `consolidation`, not against a separate `feat/sample-cleanup` branch. Wave 4 Epic #36 closes as administratively absorbed into Wave 3 Epic #35.

### Resulting changes

- **Plan §2 D3 amendment** (noted in §2 table): SAMPLE cleanup PR is no longer separate — it ships with the unified PR.
- **Plan §5 Wave 4** amended: branch construction removed; content lands directly on `consolidation`; the post-merge issue-closure step (Story #62) remains the only Wave 4 external action.
- **Story closures (per E5):** #36 Wave 4 Epic, #52 `wave4-prepare-sample-branch`, #61 `wave4-external-pr-sample`
- **Story scope retention:** #53 `wave4-migrate-sample-issues` (active — content created on consolidation), #54 `wave4-update-readme-samples-section` (active — README modified on consolidation), #62 `wave4-close-sample-issues` (active — execute after unified PR merges)
- **SQL todos** updated accordingly.

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E5)
- Story comment (most affected): [REDACTED internal-org issue tracker] (E5 mirror)

---

## E6 — Multiple-choice clarification on Wave 6 fix scope

**Timestamp (UTC):** 2026-06-05T17:45:00Z
**Prompt type:** freeform clarification (response to agent `ask_user` after Wave 6 review report surfaced an unusually high-density distribution of High findings)
**Stated intent:** ensure Wave 6 produces a high-quality consolidation; expand the default plan's "critical-only fix" scope to also include all High findings AND triaged Medium findings; file ALL findings as issues regardless of disposition
**Plan impact:** structural — amends the "critical-only fixes against consolidation" policy in plan §5 Wave 6 and the risks-table mitigation ("non-critical findings become follow-up issues, not blockers"); expands Wave 6 scope; defers nothing critical

### Question asked (verbatim, from `ask_user`)

```text
Wave 6 found 1 Critical (internal-org URL leak in `docs/sample-issues/README.md`) and 9 High findings (mostly broken/inaccurate platform-adapters README content and contributor templates). The plan defaults to "fix Critical only; file the rest as follow-up issues." But the High findings are concentrated docs-correctness regressions that would land in public and look bad. How should I scope the fixes?
```

### User's response (verbatim)

```text
Thank you. You were correct to pause and raise this. Looking at the report, I would prefer you a) create issues for ALL findings, b) plan to fix all High and Critical findings and triage the Medium findings either for inclusion before PR merge, or resolution in subsequent waves, and c) backlog other Medium and Low issues to address in subsequent waves.
```

### Interpretation (executor's summary)

**(a) File issues for ALL 17 findings** (C1, H1–H9, M1–M4, L1–L3) under the Wave 6 Epic (#37), with severity labels. **(b) Fix all 10 Critical+High findings now** on consolidation; **triage Medium findings** — for each, decide whether to fix-now (if cheap and on-theme) or fix-later. **(c) Low findings stay in backlog** for subsequent waves.

Executor's Medium triage decision (subject to user override):
- **M1 (combo structure three-way contradiction)** — FIX NOW. Same file/area as H4 (combos/README.md). Coherent single edit pass.
- **M2 (CONTRIBUTOR_PR_TEMPLATE "system prompt" wording)** — FIX NOW. Single-word fix; same file as M4; cheap.
- **M3 (SAMPLE 2 anchored to pre-multi-platform CLAUDE.md model)** — FIX NOW via advisory note in `docs/sample-issues/README.md` (no edit to the verbatim sample files; the advisory is one paragraph in the index). Same file as C1; coherent edit pass.
- **M4 (PR template branch-naming convention conflict)** — FIX NOW. Same file as M2; single bullet edit.

Effectively: **Fix C1 + H1–H9 + M1–M4 = 14 findings**. Backlog L1–L3 = 3 findings.

### Resulting changes

- **Plan §5 Wave 6 amendment:** "critical-only fixes" expanded to "critical + high + triaged medium fixes" before external PR opens.
- **Plan Risks table** mitigation for "Adversarial review surfaces critical issue" amended: non-critical findings are filed as issues and triaged; high-severity findings default to fix-before-external-PR rather than backlog.
- **17 new issues filed in the internal staging tracker** under the Wave 6 Epic with severity labels.
- **Story #58** (`wave6-fix-critical-findings`) renamed in spirit to "fix critical + high + triaged medium findings"; AC expanded.
- **New story** `wave6-fix-medium-low-followups` filed for the L1–L3 backlog work (and any deferred M findings).

### Cross-link

- Top Epic entry: [REDACTED internal-org issue tracker] (§Originating Prompts — Execution Phase, E6)
- Story comment (most affected): [REDACTED internal-org issue tracker] (E6 mirror — triage scope)
- Wave 6 report: see companion file [`2026-06-consolidation-wave6-review-report.md`](./2026-06-consolidation-wave6-review-report.md)
