# Quickstart: Windsurf Agent Tool Adapter

> **Research note:** The official Windsurf rules filename was verified against
> community documentation and the [Codeium blog](https://codeium.com/blog).
> `.windsurfrules` is the established convention for the repository root and
> continues to be supported by the Codeium AI engine (Cascade). Newer Windsurf
> versions also introduced a directory-based system at `.windsurf/rules/`
> where rules are defined as named markdown files with activation modes (always
> on, manual, glob, model decision). Verify the current recommendation in the
> [official Windsurf documentation](https://docs.windsurf.com/) before deploying,
> as Windsurf's tooling evolves frequently.

---

## Target File

**Path:** `.windsurfrules` at your repository root

```
your-repo/
└── .windsurfrules    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `.windsurfrules` from this directory to your repository root:

```bash
cp platform-adapters/agent-tools/windsurf/.windsurfrules /path/to/your-repo/.windsurfrules
```

### 2. Replace placeholder content

Open `.windsurfrules` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Your Project Name]` → your actual project name
- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Architecture, dependencies, structure, conventions, test setup, error handling, workflow, anti-patterns

### 3. Delete sections you don't need

Remove sections that don't apply rather than leaving placeholders. An accurate short file
is more useful than an inaccurate long one.

### 4. Commit the file

```bash
git add .windsurfrules
git commit -m "docs: add Windsurf agent context file"
```

---

## Auto-Discovery

Windsurf reads `.windsurfrules` automatically when you open a repository — no additional
configuration is required. When you start a Windsurf session in a repository, Cascade will:

1. Detect the repository root
2. Load `.windsurfrules` if present
3. Apply the rules to all AI suggestions and agent interactions in that session

The file must be named exactly `.windsurfrules` and placed at the repository root for
auto-discovery to work. No path configuration or explicit reference is needed.

---

## Codeium AI Engine Compatibility

Windsurf is built on the Codeium AI engine, which powers the Cascade autonomous agent.
The `.windsurfrules` file provides persistent context to Cascade across all sessions in
your repository. Rules defined here are applied globally to:

- Inline code completions
- Cascade chat interactions
- Autonomous agent tasks (file edits, refactors, multi-step workflows)

For more granular control, newer Windsurf versions support the `.windsurf/rules/` directory system,
where individual rule files can be scoped by activation mode (always on, manual, glob
pattern, or model decision). This allows you to define rules that apply only to specific
file types, directories, or task contexts.

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter
files for each:

| Agent Tool     | File Path                             | Notes                                        |
|----------------|---------------------------------------|----------------------------------------------|
| Windsurf       | `.windsurfrules`                      | This adapter — auto-loaded at repo root      |
| Cursor         | `.cursorrules`                        | Auto-loaded at repo root by Cursor           |
| Claude         | `CLAUDE.md`                           | Auto-loaded at repo root by Claude Code CLI  |
| GitHub Copilot | `.github/copilot-instructions.md`     | Copilot-specific, typically shorter          |
| _Universal_    | `AGENTS.md`                           | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth,
then create this `.windsurfrules` adapter as a project-specific conventions file for
Windsurf. Avoid duplicating content — keep one authoritative source and derive the others.

```
your-repo/
├── CLAUDE.md                          # Full context (Claude adapter)
├── .windsurfrules                     # Windsurf adapter (this file)
├── .cursorrules                       # Cursor adapter
├── AGENTS.md                          # Universal cross-agent entry point
└── .github/
    └── copilot-instructions.md        # Copilot adapter (abbreviated subset)
```
