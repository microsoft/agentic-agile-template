# Retrospective Template — Agentic-Agile Composite Evaluation

> **Wave:** [Wave ID]
> **Date:** [YYYY-MM-DD]
> **Session:** [Duration, participants]
> **Operator:** [Human + agent details]

---

## 1. What Was Delivered

| Issue | Scope | PR | New Tests | Status |
|-------|-------|-----|-----------|--------|
| #___ | | #___ | | ✅ / ❌ |

**Totals:** ___→___ tests (+___), ___ issues closed, ___ PRs merged.

---

## 2. Prompt Retention Review

> For detailed dimension definitions and scoring methodology, see [`docs/evaluation-framework.md`](../evaluation-framework.md).

### 2.1 Prompt Coverage

| Wave | Issues | Issues with prompt captured | Coverage % |
|------|--------|-----------------------------|------------|
| Wave ___ | | | |
| Wave ___ | | | |
| **Total** | | | |

**Assessment:** [Summarize prompt capture practices — were prompts captured per-issue, session-level, or not at all? Note any gaps.]

### 2.2 Prompt Quality Assessment

Score a representative sample of prompts on 4 criteria (1–5 each):

**Prompt: [description]** (source: [issue/PR/comment link])

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Context completeness | /5 | |
| Constraint explicitness | /5 | |
| Success criteria clarity | /5 | |
| Artifact linkage | /5 | |
| **Average** | **/5** | |

**Prompt: [description]** (source: [issue/PR/comment link])

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Context completeness | /5 | |
| Constraint explicitness | /5 | |
| Success criteria clarity | /5 | |
| Artifact linkage | /5 | |
| **Average** | **/5** | |

> Copy the table above for additional prompts as needed.

**Scoring guide:**
- **Context completeness** — Does the prompt reference prior work, existing issues, and relevant constraints?
- **Constraint explicitness** — Are rules, boundaries, and non-obvious requirements stated rather than implied?
- **Success criteria clarity** — Are outcomes testable and unambiguous, or qualitative and open to interpretation?
- **Artifact linkage** — Does the prompt link to specs, issues, PRs, files, or other artifacts the agent needs?

**Overall range:** [min] – [max]/5. [Note any trends across the wave/milestone.]

### 2.3 Prompt-to-Outcome Correlation

| Prompt (quality score) | Outcome Quality | Correlation |
|------------------------|----------------|-------------|
| [description] ([score]) | | Weak / Moderate / Strong / Direct |

**Pattern:** [Summarize which prompt quality criteria most strongly predicted outcome quality.]

### 2.4 Improvement Recommendations

1. [Recommendation based on prompt coverage gaps]
2. [Recommendation based on prompt quality patterns]
3. [Recommendation based on prompt-to-outcome correlations]

---

## 3. Dimension Scores

Rate each dimension 1–5 using the rubric below. "N/A" is acceptable when data is not yet tracked.

| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | Spec Quality | /5 | |
| D2 | Decomposition Effectiveness | /5 | |
| D3 | Agent Reliability | /5 | |
| D4 | Partnership Efficiency | /5 | |
| D5 | Delivery Performance | /5 | |
| D6 | Governance Health | /5 | |
| D7 | Cost Efficiency | /5 | |
| D8 | Process Maturity | /5 | |
| | **Composite** | **/5** | Average of scored dimensions |

### Scoring Rubric

**D1 — Spec Quality:** Did issue acceptance criteria match delivered scope?
- 5: All ACs precise and testable, zero rework from spec ambiguity
- 4: Minor clarifications needed, no scope change
- 3: Some ACs needed reinterpretation during implementation
- 2: Significant rework due to spec gaps
- 1: Specs unusable, majority rewritten during implementation

**D2 — Decomposition Effectiveness:** Were tasks independent? File overlap?
- 5: Zero file overlap, all tasks parallelizable, no dependency waits
- 4: Minimal overlap resolved with simple rebasing
- 3: Some dependency-driven serialization required
- 2: Significant overlap caused merge conflicts or rework
- 1: Monolithic tasks, could not parallelize

**D3 — Agent Reliability:** Test pass rate, first-pass success, fix iterations?
- 5: All tests pass first attempt, no fix cycles needed
- 4: Minor fixes (1 iteration), all tests green after
- 3: Multiple fix cycles but all resolved in-session
- 2: Significant debugging required, some issues deferred
- 1: Agent output required major manual rework

**D4 — Partnership Efficiency:** Human vs agent time allocation, decision quality?
- 5: Human time <20% of total, all decisions sound
- 4: Human time 20-35%, minor course corrections
- 3: Human time 35-50%, some significant redirections needed
- 2: Human time >50%, frequent intervention required
- 1: Agent work mostly discarded, human did most work

**D5 — Delivery Performance:** Cycle time, throughput, change-failure rate?
- 5: All items delivered under estimate, zero rollbacks
- 4: Delivered on estimate, no rollbacks
- 3: Minor delays, all items completed
- 2: Significant delays, some items deferred
- 1: Major delays, wave objectives not met

**D6 — Governance Health:** Review findings count/severity, disposition tracking?
- 5: <3 findings, all Low/Info, all dispositioned
- 4: Some Medium findings, all dispositioned, none escaped
- 3: Critical/High findings caught and fixed pre-merge
- 2: Critical findings required significant rework
- 1: Escaped defects found post-merge

**D7 — Cost Efficiency:** API tokens, human time, cost per feature?
- 5: Well under budget, high value per token/hour
- 4: On budget, reasonable efficiency
- 3: Moderate overrun, acceptable ROI
- 2: Significant overrun, questionable ROI
- 1: Major overrun, poor value delivered
- N/A: Not tracked (add tracking in Phase 3)

**D8 — Process Maturity:** Convention adherence, improvement adoption?
- 5: All conventions followed, improvements from prior retros adopted
- 4: Minor deviations, most improvements adopted
- 3: Some conventions skipped, partial improvement adoption
- 2: Significant convention violations
- 1: Process not followed

**D8 supplemental — One-off script count:** How many times did agents need manual workarounds (one-off scripts, data fixes) to correct agent output? Consider tagging relevant issues with a dedicated label (e.g., `retro-workaround`) for automatic collection. A decreasing trend indicates improving agent reliability and workflow completeness.

---

## 4. Governance Health — Findings Table

| # | Finding | Severity | Source | Disposition | Notes |
|---|---------|----------|--------|-------------|-------|
| 1 | | Crit/High/Med/Low/Info | Agent/Model | fixed/accepted/deferred | |

**Summary:** ___ findings total, ___ Critical/High, ___ fixed, ___ accepted, ___ deferred.

---

## 5. Delivery Timeline

| Phase | Items | Duration |
|-------|-------|----------|
| Planning | | |
| Implementation | | |
| Review | | |
| Fix + Merge | | |
| Documentation | | |
| **Total** | | |

---

## 6. Recommendations

### What Worked Well
1.

### What to Improve
1.

### Action Items for Next Wave
1.

---

## 7. Trend Analysis

| Metric | Prior Wave | This Wave | Δ |
|--------|-----------|-----------|---|
| Test count | → | → | + |
| Issues closed | | | |
| PRs merged | | | |
| Critical/High findings | | | |
| Composite score | /5 | /5 | |
