# Quickstart: Cline Agent Tool Adapter

> **Research note:** The official Cline rules filename was verified against
> [https://github.com/cline/cline](https://github.com/cline/cline) and community
> documentation. `.clinerules` is the established convention Cline uses at the
> repository root to load project-specific rules for autonomous coding sessions.
> Confirm the current recommendation in the official documentation before deploying,
> as Cline's tooling evolves frequently.

---

## Target File

**Path:** `.clinerules` at your repository root

```
your-repo/
└── .clinerules    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `.clinerules` from this directory to your repository root:

```bash
cp platform-adapters/agent-tools/cline/.clinerules /path/to/your-repo/.clinerules
```

### 2. Replace placeholder content

Open `.clinerules` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Your Project Name]` → your actual project name
- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Architecture, dependencies, structure, conventions, test setup, error handling, workflow, anti-patterns
- Autonomy Guidelines → define what Cline may do freely, what requires confirmation, and what is off-limits

### 3. Fill in the Autonomy Guidelines section

Cline operates autonomously — it can execute commands, write files, and chain multi-step actions
without asking for approval at each step. The **Autonomy Guidelines** section is therefore
especially important: it defines the boundaries of autonomous behavior to prevent unintended
actions. Be explicit about:

- What Cline may do freely (e.g., run tests, create files on feature branches)
- What requires human confirmation (e.g., installing production dependencies)
- What is never permitted (e.g., pushing to main, exposing secrets)

### 4. Delete sections you don't need

Remove sections that don't apply rather than leaving placeholders. An accurate short file
is more useful than an inaccurate long one.

### 5. Commit the file

```bash
git add .clinerules
git commit -m "docs: add Cline agent context file"
```

---

## Auto-Discovery

Cline reads `.clinerules` automatically when you open a repository in VS Code — no additional
configuration is required. When you start a Cline session in a repository, Cline will:

1. Detect the repository root
2. Load `.clinerules` if present
3. Apply the rules to all autonomous operations and agent interactions in that session

The file must be named exactly `.clinerules` and placed at the repository root for
auto-discovery to work. No path configuration or explicit reference is needed.

---

## Autonomy Guidelines Are Critical for Cline

Unlike interactive AI assistants that ask for confirmation at each step, Cline is designed
to operate autonomously — executing commands, writing and editing files, and chaining
multi-step tasks with minimal interruption. This makes the **Autonomy Guidelines** section
uniquely important in `.clinerules`:

- **Without autonomy bounds**, Cline may take actions outside your intended scope
- **With clear bounds**, Cline can work efficiently within defined limits and escalate when needed
- Define the "free action" zone broadly enough to avoid interruptions on routine work
- Define hard limits explicitly — Cline treats these as non-negotiable constraints

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter
files for each:

| Agent Tool     | File Path                             | Notes                                        |
|----------------|---------------------------------------|----------------------------------------------|
| Cline          | `.clinerules`                         | This adapter — auto-loaded at repo root      |
| Cursor         | `.cursorrules`                        | Auto-loaded at repo root by Cursor           |
| Claude         | `CLAUDE.md`                           | Auto-loaded at repo root by Claude Code CLI  |
| GitHub Copilot | `.github/copilot-instructions.md`     | Copilot-specific, typically shorter          |
| _Universal_    | `AGENTS.md`                           | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth,
then create this `.clinerules` adapter as a Cline-specific conventions file. Add the
Autonomy Guidelines section to `.clinerules` to bound Cline's autonomous behavior —
this section is specific to Cline and does not need to appear in other adapters.

```
your-repo/
├── CLAUDE.md                          # Full context (Claude adapter)
├── .clinerules                        # Cline adapter (this file) — includes Autonomy Guidelines
├── .cursorrules                       # Cursor adapter
├── AGENTS.md                          # Universal cross-agent entry point
└── .github/
    └── copilot-instructions.md        # Copilot adapter (abbreviated subset)
```
