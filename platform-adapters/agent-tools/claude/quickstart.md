# Quickstart: Claude Agent Tool Adapter

## Target File

**Path:** `CLAUDE.md` at your repository root

```
your-repo/
└── CLAUDE.md    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `CLAUDE.md` from this directory to your repository root:

```bash
cp platform-adapters/agent-tools/claude/CLAUDE.md /path/to/your-repo/CLAUDE.md
```

### 2. Replace placeholder content

Open `CLAUDE.md` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Your Project Name]` → your actual project name
- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Framework, dependencies, structure, conventions, test setup, build commands

### 3. Delete sections you don't need

Not every project requires every section. Remove sections that don't apply rather than leaving placeholders. An accurate short file is more useful than an inaccurate long one.

### 4. Commit the file

```bash
git add CLAUDE.md
git commit -m "docs: add agent context file"
```

---

## Auto-Discovery

Claude reads `CLAUDE.md` automatically at the start of every conversation in a repository context. No additional configuration is required — Claude looks for this file at the repository root by default.

When you open a project in Claude or start a Claude-assisted session, it will:
1. Detect the repository root
2. Load `CLAUDE.md` if present
3. Apply the conventions, structure, and context to all responses in that session

---

## Configuration Notes

- **Must be named exactly `CLAUDE.md`** — Claude does not auto-load files with other names (such as `AGENTS.md`, `CONTEXT.md`, or `agent-context.md`). If you want to support multiple agent tools, maintain separate files for each.

- **Keep the file under ~500 lines** — Longer files consume more context window on every interaction. Prioritize actionable information over completeness. If your conventions are extensive, link to external documents rather than inlining them.

- **Keep it current** — An outdated `CLAUDE.md` is worse than none. Agents will follow stale instructions confidently. Update the file whenever your process, conventions, or structure changes (see the Documentation Maintenance section in the template).

- **No secrets** — Do not include credentials, API keys, or environment-specific configuration. `CLAUDE.md` is a documentation file committed to version control.

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter files:

| Agent Tool | File Path | Notes |
|------------|-----------|-------|
| Claude | `CLAUDE.md` | Auto-loaded at repo root |
| GitHub Copilot | `.github/copilot-instructions.md` | Copilot-specific, typically shorter |
| Cursor | `.cursorrules` (or `.cursor/rules/` directory of `.mdc` files) | Cursor-specific conventions; see [`platform-adapters/agent-tools/cursor/`](../cursor/) |
| _Universal_ | `AGENTS.md` | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth, then create shorter adapter files for other tools that reference or summarize it. Avoid duplicating content — keep one authoritative source and derive the others.

```
your-repo/
├── CLAUDE.md                          # Full context (this adapter)
├── AGENTS.md                          # Universal cross-agent entry point (can reference CLAUDE.md)
└── .github/
    └── copilot-instructions.md        # Copilot adapter (abbreviated subset)
```
