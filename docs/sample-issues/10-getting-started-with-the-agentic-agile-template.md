# [SAMPLE 2] Epic: Getting started with the agentic-agile template

> **Sample issue** — preserved here as a worked example of the Agentic-Agile issue style.
> This file is a verbatim snapshot of the original GitHub issue. If the live tracker issue is
> still open at the time you are reading this, it will be closed with a pointer back to this
> file as part of the consolidation follow-up, so the public issue tracker stays clear for real
> backlog items.

## Metadata

| Field | Value |
|-------|-------|
| Original issue | [microsoft/agentic-agile-template#10](https://github.com/microsoft/agentic-agile-template/issues/10) |
| Sample group | `SAMPLE 2 (Onboarding worked example)` |
| Author | @dgepstein |
| Created | 2026-05-13T01:47:59Z |
| Labels | `phase:planned`, `priority:2-normal`, `effort:Large`, `category:documentation`, `type:epic`, `sample` |
| Comment count on snapshot | 0 |

## Original body (verbatim)

## Summary

Set up the agentic-agile-template for a new project by customizing agent context, configuring the label taxonomy, performing first epic decomposition, and running a first wave with parallel agents.

## Context / Motivation

The agentic-agile-template ships with documentation and templates, but new teams need a guided path from "I cloned the repo" to "I'm running my first parallel wave." This epic walks through the essential setup steps in order, demonstrating how each template artifact becomes a working part of the development process.

> **Note:** This is a **sample epic** for onboarding purposes. It models the "Getting Started" workflow described in the README.

## Wave Execution Plan

```
Wave 1: [#11 Customize CLAUDE.md] [#12 Configure Labels]  ← parallel
         ↓ review gate (agent context + labels verified)
Wave 2: [#13 First Epic Decomposition]
         ↓ review gate (decomposition + wave plan verified)
Wave 3: [#14 Run First Wave]
```

## Child Issues

| Wave | Issue | Status |
|------|-------|--------|
| 1 | #11 [SAMPLE 2] Customize agent context file (CLAUDE.md) | `phase:planned` |
| 1 | #12 [SAMPLE 2] Configure label taxonomy and metadata scheme | `phase:planned` |
| 2 | #13 [SAMPLE 2] Create first epic decomposition with wave plan | `phase:planned` |
| 3 | #14 [SAMPLE 2] Run first wave with parallel agent execution | `phase:planned` |

## Acceptance Criteria

- [ ] All 4 child stories are completed in wave order
- [ ] Agent context file is customized with real project information
- [ ] Label taxonomy is configured in the repository
- [ ] At least one epic is decomposed into stories with file ownership
- [ ] At least one wave is executed with parallel agent assignments

## Negative Constraints

- Does NOT modify the template files themselves (those are upstream)
- Does NOT require a specific tech stack (works with any language/framework)
- Does NOT cover advanced topics (evaluation framework, retrospectives)

## Comments on the original issue

_(no comments at the time of snapshot)_
