# Quickstart: GitHub Copilot Agent Tool Adapter

## Target File

**Path:** `.github/copilot-instructions.md` in your repository root

```
your-repo/
└── .github/
    └── copilot-instructions.md    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `copilot-instructions.md` from this directory to `.github/` in your repository:

```bash
mkdir -p /path/to/your-repo/.github
cp platform-adapters/agent-tools/github-copilot/copilot-instructions.md /path/to/your-repo/.github/copilot-instructions.md
```

### 2. Replace placeholder content

Open `.github/copilot-instructions.md` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Framework, file structure, conventions, testing setup, anti-patterns

### 3. Keep it concise

Delete sections you don't need rather than leaving placeholders. Copilot instructions are most effective when short and focused — aim for the conventions that most directly affect code generation. An accurate focused file outperforms a comprehensive one.

### 4. Commit the file

```bash
git add .github/copilot-instructions.md
git commit -m "docs: add Copilot agent context file"
```

---

## Auto-Discovery

GitHub Copilot reads `.github/copilot-instructions.md` automatically — no additional configuration required. Auto-discovery works across:

- **VS Code** — Copilot Chat and inline suggestions pick up the file automatically when you open a repository
- **GitHub.com** — Copilot on GitHub reads the file for context when you use Copilot Chat on the repository
- **JetBrains IDEs** — Copilot plugin reads the file automatically in supported JetBrains environments

The file must be at exactly `.github/copilot-instructions.md` — Copilot does not search for alternate names or locations.

---

## Configuration Notes

- **Keep it concise** — Copilot instructions work best when short and focused. Unlike `CLAUDE.md`, which supports comprehensive documentation, Copilot instructions are most effective as a tight summary of conventions that directly affect code generation. Prioritize actionable rules over background context.

- **No secrets** — Do not include credentials, API keys, or environment-specific configuration. This file is committed to version control.

- **Keep it current** — Stale instructions are worse than none. Update the file when your conventions or structure change.

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter files for each:

| Agent Tool | File Path | Notes |
|------------|-----------|-------|
| Claude | `CLAUDE.md` | Auto-loaded at repo root |
| GitHub Copilot | `.github/copilot-instructions.md` | This adapter — shorter/more focused |
| Cursor | `.cursorrules` (or `.cursor/rules/` directory of `.mdc` files) | Cursor-specific conventions; see [`platform-adapters/agent-tools/cursor/`](../cursor/) |
| _Universal_ | `AGENTS.md` | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth, then create this shorter Copilot adapter as an abbreviated subset. Avoid duplicating content — keep one authoritative source and derive the others.

```
your-repo/
├── CLAUDE.md                          # Full context (Claude adapter)
├── AGENTS.md                          # Universal cross-agent entry point
└── .github/
    └── copilot-instructions.md        # Copilot adapter (this file — abbreviated)
```
