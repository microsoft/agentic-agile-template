# Agent Surface Selection Strategy

How to choose the right agent surface for different development tasks.

## 1. Surface Taxonomy

Agent-assisted development tools present themselves through several distinct surfaces, each with different strengths, constraints, and interaction models.

### CLI / Terminal Agents

Agents that operate from the command line, executing autonomously within a terminal session. They work in their own branch, have full access to the file system and development toolchain, and produce commits directly.

**Examples:** GitHub Copilot CLI (coding agent mode), Cline, aider

**Characteristics:**
- High autonomy: can run for extended periods without human interaction
- Full tool access: build, test, lint, git, package managers
- Branch isolation: each agent works in its own branch, preventing collisions
- Scriptable: can be launched programmatically, enabling parallel execution

### IDE Agents

Agents embedded in code editors that provide contextual assistance while the developer works. They see the active file, project structure, and sometimes the full repository context.

**Examples:** GitHub Copilot in VS Code, Cursor, Windsurf

**Characteristics:**
- Contextual: aware of the file you're editing, cursor position, and surrounding code
- Interactive: suggestions appear inline, can be accepted or rejected in real time
- Lower autonomy: typically assist rather than independently execute
- Tight feedback loop: immediate visibility into what the agent produces

### Chat Interfaces

Conversational agents accessed through chat windows, either standalone or embedded in development tools. Used for exploratory work, architecture discussion, and planning.

**Examples:** ChatGPT, Claude, GitHub Copilot Chat

**Characteristics:**
- Exploratory: good for brainstorming, debugging, and design discussion
- No direct tool access (unless extended with MCP or plugins)
- Session-based: context resets between conversations unless explicitly managed
- Flexible: can discuss any topic without being constrained to a specific file or task

### API-Driven Agents

Agents invoked through APIs, typically integrated into CI/CD pipelines, automation scripts, or custom tooling. They process requests programmatically and return structured results.

**Examples:** Custom integrations using LLM APIs, CI pipeline agents

**Characteristics:**
- Fully automated: no human interaction during execution
- Structured input/output: JSON, YAML, or other machine-readable formats
- Pipeline integration: triggered by events (PR opened, build failed, schedule)
- Scalable: can process many requests in parallel

### Cloud Coding Agents

Agents that run in cloud-hosted environments with full development tooling, operating on remote branches and producing PRs autonomously.

**Examples:** GitHub Copilot coding agent, Devin

**Characteristics:**
- Remote execution: run in isolated cloud environments
- Full SDLC capability: can read issues, create branches, write code, run tests, open PRs
- Asynchronous: operate independently; humans review results after completion
- High isolation: each agent instance has its own environment

---

## 2. Task-Surface Matching

Different development tasks have different requirements for autonomy, context, and feedback speed. Match the task to the surface that best fits its characteristics.

| Task Type | Best Surface | Why |
|-----------|-------------|-----|
| **Feature implementation** | CLI / Cloud coding agent | Requires autonomy, tool access, and branch isolation. Agent can run tests, iterate on failures, and produce a complete PR. |
| **Code review** | IDE agent | Needs full codebase context and the ability to navigate across files. Inline suggestions are more actionable than chat-based feedback. |
| **Architecture exploration** | Chat interface | Exploratory, iterative, and conversational. The developer needs to think through options, not execute immediately. |
| **Bug investigation** | IDE agent or CLI agent | IDE for interactive debugging with context. CLI for systematic investigation across many files. |
| **CI/CD automation** | API-driven agent | Triggered by events, produces structured output, integrates with existing pipelines. |
| **Documentation** | CLI or Chat | CLI for bulk generation from code. Chat for drafting and refining narrative content. |
| **Test generation** | CLI agent | Needs to run tests, see failures, and iterate. Benefits from full tool access. |
| **Parallel story execution** | CLI / Cloud coding agent | Multiple agents working simultaneously require branch isolation and independent environments. |

---

## 3. Selection Criteria

When choosing an agent surface for a task, evaluate these dimensions:

### Autonomy Level

How much independent work can the agent do before needing human input?

- **High autonomy tasks** (implement a well-specified story, generate tests, fix a lint error): CLI or cloud coding agents
- **Low autonomy tasks** (explore a design space, discuss trade-offs, review a complex PR): Chat or IDE agents

### Context Window

How much context does the agent need to do the job well?

- **Narrow context** (single file, single function): IDE inline suggestions
- **Broad context** (entire module, cross-cutting change): CLI or cloud agents with full repo access
- **External context** (documentation, API references, design docs): Chat with web access or MCP-enabled tools

### Tool Access

Does the agent need to run commands, build code, or execute tests?

- **Yes:** CLI or cloud coding agents (they have shell access)
- **No:** Chat or IDE agents are sufficient

### Isolation

Does the agent need to work without affecting other developers or agents?

- **Strong isolation needed** (parallel execution, experimental changes): CLI with branch isolation, cloud agents
- **Shared environment acceptable** (pair programming, interactive review): IDE agents

---

## 4. Swarming Considerations

When multiple agents work in parallel (the "swarming" pattern in Agentic-Agile Development), surface selection becomes critical.

### Why CLI and Cloud Agents Are Preferred for Swarming

1. **Branch isolation.** Each agent works in its own feature branch. No shared state means no collisions.
2. **Independent environments.** Each CLI or cloud agent has its own terminal session, file system view, and process space.
3. **Clean dependency management.** Each agent can install dependencies, build, and test without affecting other agents.
4. **Scriptable launch.** Multiple agents can be started programmatically from a wave execution plan.

### Why IDE Agents Are Not Ideal for Swarming

- IDE agents share a single workspace. Two IDE agents editing different files in the same editor will conflict.
- IDE agents are interactive by design. They expect a human in the loop, which limits parallelism.
- Branch management in an IDE context is manual. Switching branches for each agent is impractical.

### Swarming Execution Pattern

```
Wave Plan (3 parallel stories)
│
├── Agent 1 (CLI): branch feat/story-a → implements → tests → PR
├── Agent 2 (CLI): branch feat/story-b → implements → tests → PR
└── Agent 3 (CLI): branch feat/story-c → implements → tests → PR
│
Review Gate: human reviews all 3 PRs
│
Merge + Next Wave
```

---

## 5. Evolution Note

The boundaries between agent surfaces are converging. IDE agents are gaining CLI-like autonomy. Chat agents are gaining tool access through protocols like MCP. Cloud agents are becoming accessible from IDE interfaces.

This means the specific product you use matters less than the capabilities it provides. When selecting an agent surface, focus on:

- **Does it have the autonomy level this task requires?**
- **Does it have access to the tools this task needs?**
- **Does it provide the isolation level parallel execution demands?**

The answers to these questions, not the product name, should drive your selection.

---

## 6. Decision Flowchart

Use this text-based decision tree to select an agent surface for a given task:

```
START: What kind of task?
│
├── Implementation (write code, generate tests, fix bugs)
│   │
│   ├── Is the task well-specified with clear acceptance criteria?
│   │   ├── YES → Is this part of a parallel wave?
│   │   │         ├── YES → CLI or Cloud Coding Agent (isolation required)
│   │   │         └── NO  → CLI Agent or IDE Agent (either works)
│   │   └── NO  → Refine the spec first (Chat interface for exploration)
│   │
│   └── Does the task require running tests or builds?
│       ├── YES → CLI or Cloud Coding Agent (tool access required)
│       └── NO  → IDE Agent (inline assistance sufficient)
│
├── Review (code review, PR review)
│   └── IDE Agent (contextual navigation, inline comments)
│
├── Architecture / Design
│   └── Chat Interface (exploratory, conversational)
│
├── CI/CD / Automation
│   └── API-Driven Agent (event-triggered, structured I/O)
│
└── Documentation
    ├── From code (API docs, type docs) → CLI Agent
    └── Narrative (guides, tutorials) → Chat Interface
```

---

## Summary

Agent surface selection is a tactical decision that directly affects the quality and speed of agent-assisted work. The right surface for a task depends on the autonomy required, the context needed, the tools involved, and the isolation demanded. As surfaces converge, these criteria become more important than any specific product choice.
