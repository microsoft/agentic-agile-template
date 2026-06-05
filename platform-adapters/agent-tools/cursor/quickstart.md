# Quickstart: Cursor Agent Tool Adapter

> **Research note:** The official Cursor rules filename was verified against
> [https://docs.cursor.com/context/rules](https://docs.cursor.com/context/rules).
> `.cursorrules` is the established legacy convention Cursor continues to support
> at the repository root. Cursor's modern system also supports rule files under
> `.cursor/rules/` for per-directory and multi-file configurations. Verify the
> current recommendation in the official documentation before deploying, as
> Cursor's tooling evolves frequently.

---

## Target File

**Path:** `.cursorrules` at your repository root

```
your-repo/
└── .cursorrules    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `.cursorrules` from this directory to your repository root:

```bash
cp platform-adapters/agent-tools/cursor/.cursorrules /path/to/your-repo/.cursorrules
```

### 2. Replace placeholder content

Open `.cursorrules` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Your Project Name]` → your actual project name
- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Architecture, dependencies, structure, conventions, test setup, error handling, workflow, anti-patterns

### 3. Delete sections you don't need

Remove sections that don't apply rather than leaving placeholders. An accurate short file
is more useful than an inaccurate long one.

### 4. Commit the file

```bash
git add .cursorrules
git commit -m "docs: add Cursor agent context file"
```

---

## Auto-Discovery

Cursor reads `.cursorrules` automatically when you open a repository — no additional
configuration is required. When you start a Cursor session in a repository, Cursor will:

1. Detect the repository root
2. Load `.cursorrules` if present
3. Apply the rules to all AI suggestions and agent interactions in that session

The file must be named exactly `.cursorrules` and placed at the repository root for
auto-discovery to work with the legacy convention. No path configuration or explicit
reference is needed.

---

## Per-Directory Rules

Cursor also supports per-directory rule files through its modern `.cursor/rules/` system.
You can place rule files in subdirectories to provide context that applies only to a
specific area of the codebase:

```
your-repo/
├── .cursorrules              # Root-level rules (applies everywhere)
└── .cursor/
    └── rules/
        ├── backend.mdc       # Rules for backend code only
        ├── frontend.mdc      # Rules for frontend code only
        └── migrations.mdc    # Rules scoped to database migrations
```

Per-directory rules allow you to tailor AI behavior for different parts of a monorepo
or a project with distinct subsystems. The `.cursor/rules/` system supports YAML
frontmatter for activation conditions, glob patterns for file matching, and richer
rule metadata. Refer to the official Cursor documentation for the current file format
and activation semantics.

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter
files for each:

| Agent Tool     | File Path                           | Notes                                        |
|----------------|-------------------------------------|----------------------------------------------|
| Cursor         | `.cursorrules`                      | This adapter — auto-loaded at repo root      |
| Claude         | `CLAUDE.md`                         | Auto-loaded at repo root by Claude Code CLI  |
| GitHub Copilot | `.github/copilot-instructions.md`   | Copilot-specific, typically shorter          |
| _Universal_    | `AGENTS.md`                         | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth,
then create this `.cursorrules` adapter as a project-specific conventions file for
Cursor. Avoid duplicating content — keep one authoritative source and derive the others.

```
your-repo/
├── CLAUDE.md                          # Full context (Claude adapter)
├── .cursorrules                       # Cursor adapter (this file)
├── AGENTS.md                          # Universal cross-agent entry point
└── .github/
    └── copilot-instructions.md        # Copilot adapter (abbreviated subset)
```
