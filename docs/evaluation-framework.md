# Evaluation Framework for Agentic-Agile Development

A composite framework for measuring the effectiveness of human-agent software development partnerships. Eight dimensions cover spec quality, decomposition, agent reliability, partnership efficiency, delivery, governance, cost, and process maturity.

---

## Why Existing Frameworks Fall Short

Developer productivity frameworks like DORA, SPACE, and DevEx were designed for human-only teams. They measure the pipeline: how fast, how often, how satisfying. They do not measure the partnership: how well humans and agents collaborate, how reliable agent output is, or how effective the specifications that drive agent behavior are.

When an agent handles implementation and the human shifts to specification, review, and correction, the measurement model breaks in specific ways:

| Framework | What Transfers | Key Gap |
|-----------|---------------|---------|
| **DORA** (Forsgren et al., 2018) | Pipeline metrics: lead time, deployment frequency, change failure rate | No decomposition quality dimension; fast delivery of poorly decomposed work is not progress |
| **SPACE** (Forsgren et al., 2021) | Satisfaction, Efficiency dimensions | Activity metrics are inflated by agent parallelism; commit counts become misleading |
| **DevEx** (Noda et al., 2023) | Flow state concept, cognitive load awareness | No model for the role transition from implementer to reviewer |
| **Flow Framework** (Kersten, 2018) | Flow Time, Flow Distribution | Flow Efficiency approaches 100% artificially because agent execution has near-zero queue time |
| **Team Topologies** (Skelton & Pais, 2019) | Cognitive load concept (intrinsic, extraneous, germane) | No agent-introduced cognitive load: reviewing agent output and diagnosing agent failures are unmeasured |

The pattern: existing frameworks measure pipeline throughput. They do not measure collaboration quality, which is what makes agent-assisted development qualitatively different.

---

## The Eight Dimensions

### Dimension 1: Spec Quality

**Definition:** Measures how well human-authored specifications predict agent output quality.

**Metrics:**
- Acceptance criteria completeness score (percentage of stories with testable, unambiguous criteria)
- Spec-to-implementation fidelity rate (percentage of agent outputs matching spec on first attempt)
- Rework rate post-spec (percentage of stories requiring spec revision after agent execution begins)

**How to collect:** Track how often agent output matches the spec on first implementation versus how often it requires revision. Log whether revisions stem from spec ambiguity, missing context, or agent error. The distinction matters: spec-caused rework is a process problem; agent-caused rework is a tool problem.

**What good looks like:** Greater than 80% first-implementation acceptance. Rework rate trending toward zero over milestones.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Most specs are ambiguous; first-pass acceptance below 40% |
| 2 | Some specs have clear criteria; first-pass acceptance 40-60% |
| 3 | Most specs have testable criteria; first-pass acceptance 60-80% |
| 4 | Specs consistently predict output; first-pass acceptance 80-90% |
| 5 | Specs are precise contracts; first-pass acceptance above 90% |

---

### Dimension 2: Decomposition Effectiveness

**Definition:** Measures how well work is broken into independent, parallelizable units.

**Metrics:**
- Merge conflict count (should be zero in a well-decomposed wave)
- File overlap rate across parallel stories (percentage of files touched by more than one story in the same wave)
- Story independence score (percentage of stories with no runtime or compile-time dependencies on concurrent stories)

**How to collect:** Automated from Git. Merge conflicts are directly observable. File overlap analysis compares the file lists in concurrent PRs.

**What good looks like:** Zero merge conflicts. Every story in a wave targets exclusive files.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Frequent merge conflicts; no explicit file ownership |
| 2 | Some file ownership; occasional conflicts |
| 3 | File ownership declared; rare conflicts (1-2 per wave) |
| 4 | Strict file ownership; zero conflicts in most waves |
| 5 | Zero conflicts sustained; decomposition is a reliable discipline |

---

### Dimension 3: Agent Reliability

**Definition:** Measures consistency of agent output across repeated executions and fault conditions.

**Metrics:**
- pass^k score: probability that a spec produces acceptable output across k independent trials
- Behavioral consistency rate: percentage of repeated runs producing substantially similar implementations
- Fault tolerance: agent recovery rate when encountering ambiguous specs, missing dependencies, or failing tests

**How to collect:** Run the same spec through agent sessions multiple times. Compare outputs for structural similarity. This is most practical as a periodic audit rather than continuous measurement.

**What good looks like:** pass^3 greater than 90%. Fault tolerance trending upward as specs improve.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Agent output varies wildly across runs; frequent failures on valid specs |
| 2 | Some consistency on simple tasks; unreliable on complex ones |
| 3 | Consistent on well-specified tasks; struggles with ambiguity |
| 4 | Reliable across most task types; graceful degradation on edge cases |
| 5 | Highly consistent; recovers from faults and flags ambiguity proactively |

---

### Dimension 4: Partnership Efficiency

**Definition:** Measures the quality of human-agent collaboration, not just speed.

**Metrics:**
- Architecture-to-correction ratio: percentage of human time spent on design versus correcting agent output (target: favor architecture)
- Agent output acceptance rate: percentage of agent-generated PRs accepted without substantive rework
- Review gate throughput: average time from PR opened to review decision
- Cognitive load assessment: adapted from Team Topologies' three-type model, measured via periodic survey

**How to collect:** Time tracking per activity type. Acceptance and rejection counts at review gates. Periodic cognitive load surveys.

**What good looks like:** Greater than 70% of human time on design and architecture rather than correction. Cognitive load stable or decreasing.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Human spends most time correcting agent output; high frustration |
| 2 | Significant correction needed; some design time preserved |
| 3 | Balanced between correction and design; cognitive load manageable |
| 4 | Mostly design work; agent output rarely needs substantive rework |
| 5 | Human focuses on architecture and strategy; agent executes reliably |

---

### Dimension 5: Delivery Performance

**Definition:** Measures throughput and stability of the delivery pipeline.

**Metrics:**
- Compressed lead time: elapsed time from spec authored to PR merged
- Wave cycle time: elapsed time from wave launch to all wave PRs merged
- Change failure rate: percentage of merged PRs that introduce defects requiring rollback or hotfix

**How to collect:** Automated from Git and CI. Timestamps on spec commits, PR opens, and merge commits.

**What good looks like:** Lead time compressing over milestones. Change failure rate below 5%.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Lead times unpredictable; high change failure rate (>15%) |
| 2 | Some predictability; change failure rate 10-15% |
| 3 | Consistent delivery cadence; change failure rate 5-10% |
| 4 | Fast, predictable delivery; change failure rate below 5% |
| 5 | Delivery is routine; near-zero change failures; continuous improvement visible |

---

### Dimension 6: Governance Health

**Definition:** Measures whether safety and quality controls are functioning at the speed of agent execution.

**Metrics:**
- Escaped defect rate: percentage of defects found in production that review gates should have caught
- Review gate catch rate: percentage of total defects found during review versus production
- Retrospective action item close rate: percentage of retro findings that reach a terminal state (fixed, accepted, or deferred)

**How to collect:** Defect tracking with root cause analysis. Review gate logs with accept/reject/rework counts.

**What good looks like:** Escaped defects trending toward zero. Greater than 90% of defects found at review gates.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | No structured review; defects found primarily in production |
| 2 | Some review process; many defects still escape |
| 3 | Consistent review gates; escaped defect rate declining |
| 4 | Strong governance; >90% of defects caught at review |
| 5 | Governance is reliable and fast; review gates do not bottleneck delivery |

---

### Dimension 7: Cost Efficiency

**Definition:** Measures the economic efficiency of agent-assisted development.

**Metrics:**
- Cost-per-resolved-issue: total agent compute cost plus human review time per completed story
- Human-hours-per-delivered-feature: human time investment normalized by feature output
- Total cost of ownership: agent costs plus human time versus equivalent sequential development baseline

**How to collect:** Track agent API costs per story. Track human time investment per milestone. Compare against a sequential baseline.

**What good looks like:** Cost-per-issue decreasing over milestones as spec quality improves and rework decreases.

**Scoring rubric:**

| Score | Description |
|-------|-------------|
| 1 | Agent costs exceed time savings; net negative ROI |
| 2 | Break-even on some task types; overall ROI unclear |
| 3 | Positive ROI on well-specified tasks; cost tracking in place |
| 4 | Consistent positive ROI; cost-per-issue declining over time |
| 5 | Clear cost advantage; savings reinvested into quality and scope |

---

### Dimension 8: Process Maturity

**Definition:** Measures the team's progression through adoption stages of agent-assisted development.

**Metrics:**
- Maturity level: self-assessed on a 1-5 scale
- Dimension scores by level: composite scores across the other seven dimensions at each maturity stage
- Level progression velocity: time spent at each maturity level before advancing

**How to collect:** Self-assessment at regular intervals (quarterly recommended). Dimension scores aggregated from the other seven dimensions.

**What good looks like:** Steady progression without regression. Dimension scores improving at each level.

**Scoring rubric:**

| Level | Description |
|-------|-------------|
| 1 | **Exploring:** Single agent, prompt-driven, no structured process |
| 2 | **Structured:** Specs exist, some review process, single-agent workflows |
| 3 | **Parallel:** Multiple agents, wave-based execution, file ownership, structured review |
| 4 | **Optimized:** Measurement-driven improvement, governance automated, cost-efficient |
| 5 | **Adaptive:** Multi-agent coordination, agents propose decompositions, continuous learning |

---

## How the Dimensions Connect

The eight dimensions form a dependency structure:

```
Spec Quality → Decomposition Effectiveness → Delivery Performance
     |                                              |
     v                                              v
Agent Reliability → Partnership Efficiency    Governance Health
                                                     |
                          Cost Efficiency ←───────────
                                |
                         Process Maturity (tracks all dimensions over time)
```

- **Spec Quality** drives **Decomposition Effectiveness.** You cannot decompose work cleanly if the specifications are ambiguous.
- **Decomposition Effectiveness** drives **Delivery Performance.** Independent stories enable parallelism, which compresses lead time.
- **Agent Reliability** determines **Partnership Efficiency.** Reliable agents let humans focus on design; unreliable agents force humans into correction loops.
- **Governance Health** catches what the other dimensions miss. Fast delivery with poor governance is technical debt at machine speed.
- **Cost Efficiency** bounds the whole operation. Speed without cost control is not sustainable.
- **Process Maturity** tracks the learning trajectory across all dimensions.

---

## How to Use This Framework

### Start with Three Dimensions

Do not try to measure all eight dimensions on day one. Start with:

1. **Spec Quality** — track first-pass acceptance rate for agent-generated PRs
2. **Decomposition Effectiveness** — count merge conflicts per wave (target: zero)
3. **Governance Health** — track where defects are found (review vs. production)

These three are measurable from Git data you already have and provide the highest signal with the lowest effort.

### Add Dimensions as You Mature

| Maturity Level | Focus Dimensions |
|---------------|-----------------|
| Level 1 (Exploring) | Spec Quality |
| Level 2 (Structured) | + Decomposition Effectiveness, Governance Health |
| Level 3 (Parallel) | + Delivery Performance, Agent Reliability |
| Level 4 (Optimized) | + Partnership Efficiency, Cost Efficiency |
| Level 5 (Adaptive) | + Process Maturity (all dimensions tracked) |

### Baseline First

Your first measurement is a starting point, not a judgment. Measure one milestone, then set targets for the next. Improvement compounds.

### Measure Outcomes, Not Activity

Agent parallelism inflates traditional activity metrics. Commit counts, PR volume, and lines of code all increase mechanically when multiple agents execute in parallel. These are not productivity gains. Measure:
- Stories accepted (not PRs opened)
- Defects escaped (not tests written)
- Cost per feature (not tokens consumed)

### Measurement Cadence

| Cadence | What to Measure | Why |
|---------|----------------|-----|
| Per wave | Merge conflicts, spec fidelity, review findings | Immediate feedback; catching problems early prevents compounding |
| Per milestone | Delivery performance, agent reliability, cost | Requires enough data for meaningful aggregation |
| Per quarter | Partnership efficiency, cognitive load, maturity level | Slow-moving indicators; more frequent measurement creates false urgency |

### Cross-Project Portability

The framework is designed for any project using agent-assisted development. Dimension definitions are universal. Targets are project-specific. A team building a payments system will have different acceptable change failure rates than a team building a content site. The dimensions apply equally; the thresholds do not.

---

## Operator Takeaway

This week: pick three metrics and measure them on your next agent-assisted milestone.

1. **Merge conflict count** — should be zero; if not, your decomposition needs work.
2. **Spec-to-implementation fidelity** — track the first-pass acceptance rate for agent-generated PRs.
3. **Escaped defect rate** — bugs found after merge that review gates should have caught.

Track trends, not absolutes. The first measurement is a baseline. A team that reduces its rework rate by 10% per milestone is building a practice. A team that measures once and sets arbitrary targets is building a dashboard.
