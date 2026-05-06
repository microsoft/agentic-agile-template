# Toward an Agentic-Agile Manifesto

> The full version of this manifesto is published on the [Agentic-Agile Development blog](https://developer.microsoft.com/blog/). This document is a standalone reference for teams adopting the methodology.

*A systems approach to strengthening the human-agent partnership: measurement, governance, and the progression from human-directed to collaborative software development.*

We are discovering better ways of developing software through human-agent partnership and helping others do the same.

The [Agile Manifesto](https://agilemanifesto.org/) taught us to value individuals and interactions, working software, customer collaboration, and responding to change. These values endure. But the team has changed: agents are now development partners, not just tools to configure. And the programming paradigm has shifted: in [Software 3.0](https://www.youtube.com/watch?v=LCEmiRjPEtQ), specifications and context are the new source code.

Agentic-Agile Development is the discipline that bridges Agile process values with Software 3.0 capabilities: the practice of producing production-ready software through structured human-agent collaboration. This manifesto addresses coordination, governance, and context problems the original Agile Manifesto did not need to contemplate. It is not a replacement. It is an evolution.

What distinguishes this framework from other emerging approaches to agent-assisted development is its emphasis on the full development lifecycle: not just session-level workflows, but backlog design, wave-based parallel execution, built-in governance that matures with the partnership, and continuous measurement across eight dimensions. The goal is not merely to use agents faster, but to develop a repeatable, governed model for how human-agent partnerships produce production-grade software.

Through this work we have come to value:

---

## Values

**Specifications and contracts** over open-ended prompts

**Human-agent partnership** over one-directional delegation

**Parallel independence** over sequential handoffs

**Built-in governance** over bolted-on compliance

**Continuous measurement** over post-hoc assessment

*That is, while there is value in the items on the right, we value the items on the left more.*

---

## Principles

We follow these principles:

**1. Specs are the primary control surface.**
Agents operate against well-defined specifications with acceptance criteria, file boundaries, and negative constraints, not open-ended instructions. In Software 3.0, the spec is the program. The quality of agent output is bounded by the quality of the specification that produced it.

**2. Decompose work into independently executable units.**
Each unit has explicit ownership, clear interfaces, and no file-level overlap with other units. When multiple humans and agents work in parallel, decomposition is the primary coordination mechanism. Work is not ready for execution until independence is verified across the full team.

**3. Teams scale through parallel partnerships.**
Multiple humans, each collaborating with their own agentic partners, work simultaneously in the same codebase without collisions. Coordination comes from structural decomposition and shared architectural agreements, not from synchronous communication. As the model matures, agentic teams of orchestrators and sub-agents take on broader coordination, with humans focusing on definition, review, and strategic direction.

**4. Humans design, agents execute, both review.**
The human contributes architectural judgment, domain context, and quality standards. The agent contributes execution speed, parallel capacity, and consistency. Review is shared responsibility. You can outsource execution but not understanding.

**5. Governance is architecture, not afterthought.**
Safety constraints, review gates, and trust boundaries are designed into the process from the start, not added after incidents. Agent capabilities are jagged and unreliable in unpredictable ways. Structural guardrails are non-negotiable.

**6. Independent review is standard practice.**
Every significant unit of work passes through independent review that challenges correctness, assumptions, and blind spots. Findings require explicit disposition: fixed, accepted, or deferred.

**7. Waves, not waterfalls.**
Work executes in small parallel batches with review gates between them. Each batch produces shippable increments. Sequential dependencies are explicit and minimized.

**8. Retrospectives improve the system, not just the output.**
Post-wave retrospectives examine the full partnership. Where did specs fail? Where did agents produce unexpected results? Where did humans fall short, through poor prompting, inconsistent reviews, or introducing concepts without sufficient definition? What should become automated? The team includes agents now. Reflect on every part of the collaboration.

**9. Measure what matters for the partnership.**
Track escaped defects, rework rate, spec quality, and the evolution of agent autonomy, not just velocity or output volume. Measurement reveals where the collaboration is strong and where it breaks down.

**10. Agent autonomy is earned through evidence.**
Early work is more human-directed. Over time, agents take on broader scope, including coordination across parallel work streams, but only within constraints validated by measured outcomes, not assumed capability. In multi-agent teams, orchestrator autonomy follows the same principle: expand scope only where results justify trust.

**11. Shared vocabulary and explicit contracts prevent drift.**
When multiple agents and humans work in parallel, consistency requires defined terms, positioning rules, and coordination artifacts. Ambiguity compounds at scale. What one collaborator assumes, another may contradict.

**12. Every deliverable stands alone.**
Each unit of work, whether a story, module, or component, must be independently shippable and integrable. Cross-cutting concerns are resolved through architectural agreements at planning time, not through runtime coupling or post-hoc coordination.

**13. Budget for the full cycle.**
Plan for review, rework, and integration, not just first-pass implementation. Speed comes from parallelism, not from skipping quality gates.

---

## Lineage

This manifesto builds on two foundations:

**The Agile Manifesto (2001)** established that software development works best through iteration, collaboration, working software, and reflection. Every one of those values carries forward. What changes is the team: it now includes agents as first-class participants, and the collaboration surface is specifications rather than conversations alone.

**Andrej Karpathy's Software 3.0 framework** describes the technological shift that makes agentic development possible. When model weights are the CPU and the context window is RAM, the specification becomes the program. Agentic-Agile Development is the discipline that makes this programming paradigm rigorous: structured, governed, and production-grade.

Multiple teams are independently developing methodologies for agent-assisted software development, each addressing different layers of the problem: session-level workflows, code generation patterns, prompt engineering frameworks, and full-lifecycle partnership models. This manifesto contributes to that emerging landscape by focusing on the governance, measurement, and partnership maturity dimensions that make agent collaboration repeatable and production-safe.

The original Agile Manifesto was written by practitioners reflecting on what worked. This manifesto follows the same tradition.

---

*Daniel Epstein and Minthe (GitHub Copilot), 2025*
