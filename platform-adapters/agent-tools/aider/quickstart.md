# Quickstart: Aider Agent Tool Adapter

> **Research note:** The official aider conventions filename was verified against
> [https://aider.chat/docs/usage/conventions.html](https://aider.chat/docs/usage/conventions.html)
> — `CONVENTIONS.md` is the filename shown in the official aider documentation
> and example transcripts. Confirm the current recommendation in the official
> documentation before deploying, as aider's tooling evolves.

---

## Target File

**Path:** `CONVENTIONS.md` at your repository root

```
your-repo/
└── CONVENTIONS.md    ← place the template here
```

---

## Setup Steps

### 1. Copy the template

Copy `CONVENTIONS.md` from this directory to your repository root:

```bash
cp platform-adapters/agent-tools/aider/CONVENTIONS.md /path/to/your-repo/CONVENTIONS.md
```

### 2. Replace placeholder content

Open `CONVENTIONS.md` and replace every section marked with `[brackets]` or `<!-- comments -->`:

- `[Your Project Name]` → your actual project name
- `[Describe your project here]` → 2–3 sentences about purpose, audience, and constraints
- `[e.g., TypeScript, Python, Go]` → your primary language
- Architecture, dependencies, structure, conventions, test setup, error handling, workflow, anti-patterns
- Commit Message Format → specify your project's commit convention so aider's auto-commits match

### 3. Fill in the Commit Message Format section

Aider generates git commit messages automatically after applying edits. The **Commit Message Format**
section is unique to aider adapters — it tells aider exactly how to format the commits it creates
on your behalf. Be specific:

- State the format (Conventional Commits, gitmoji, ticket-prefixed, etc.)
- Note whether scopes are required or optional
- Specify any footer conventions (breaking changes, issue references)

### 4. Delete sections you don't need

Remove sections that don't apply rather than leaving placeholders. An accurate short file
is more useful than an inaccurate long one.

### 5. Commit the file

```bash
git add CONVENTIONS.md
git commit -m "docs: add aider conventions file"
```

---

## Auto-Discovery

Unlike some agent tools, aider does **not** automatically discover `CONVENTIONS.md` — you must
explicitly load it each session. Aider provides two ways to do this:

### Option 1: `--read` flag (recommended for one-off sessions)

```bash
aider --read CONVENTIONS.md <files-to-edit>
```

The `--read` flag marks the file as read-only context (not editable by aider) and enables
prompt caching if your LLM provider supports it, reducing token costs on repeated sessions.

### Option 2: `.aider.conf.yml` (recommended for persistent setup)

Add the following to `.aider.conf.yml` at your repository root to load `CONVENTIONS.md`
automatically on every aider session:

```yaml
# Load conventions file on every session
read: CONVENTIONS.md

# Load multiple files
# read: [CONVENTIONS.md, another-context-file.md]
```

> **Note:** `.aider.conf.yml` is aider's main configuration file for model selection,
> API keys, editor preferences, and other runtime settings. It is separate from
> `CONVENTIONS.md`, which is purely project context for the AI. Both files can coexist
> at the repository root.

### Using `/read` inside an active session

You can also load the file after starting aider with the in-chat command:

```
/read CONVENTIONS.md
```

---

## Multiple LLM Backends

Aider supports multiple LLM providers — you can use the same `CONVENTIONS.md` regardless
of which backend you run. Switch providers via CLI flags or `.aider.conf.yml`:

```bash
# OpenAI
aider --model gpt-4o --read CONVENTIONS.md

# Anthropic
aider --model claude-opus-4-5 --read CONVENTIONS.md

# Local (Ollama)
aider --model ollama/llama3 --read CONVENTIONS.md
```

The conventions file is model-agnostic — its content is passed as context regardless of
which LLM is in use.

---

## Multiple Agent Tools Compatibility

If your team uses more than one AI coding assistant, you can maintain parallel adapter
files for each:

| Agent Tool     | File Path                             | Notes                                          |
|----------------|---------------------------------------|------------------------------------------------|
| Aider          | `CONVENTIONS.md`                      | This adapter — loaded via `--read` or conf     |
| Cursor         | `.cursorrules`                        | Auto-loaded at repo root by Cursor             |
| Claude         | `CLAUDE.md`                           | Auto-loaded at repo root by Claude Code CLI    |
| Cline          | `.clinerules`                         | Auto-loaded at repo root by Cline              |
| GitHub Copilot | `.github/copilot-instructions.md`     | Copilot-specific, typically shorter            |
| _Universal_    | `AGENTS.md`                           | Cross-agent canonical entry point (`agents.md` convention) |

**Recommended approach:** Maintain a comprehensive `CLAUDE.md` as the source of truth,
then create this `CONVENTIONS.md` adapter as an aider-specific conventions file. Add the
**Commit Message Format** section to `CONVENTIONS.md` to guide aider's auto-commit behavior —
this section is specific to aider and does not need to appear in other adapters.

```
your-repo/
├── CLAUDE.md                          # Full context (Claude adapter)
├── CONVENTIONS.md                     # Aider adapter (this file) — includes Commit Message Format
├── .cursorrules                       # Cursor adapter
├── .clinerules                        # Cline adapter
├── AGENTS.md                          # Universal cross-agent entry point
└── .github/
    └── copilot-instructions.md        # Copilot adapter (abbreviated subset)
```
