# Agentic-Agile Skills

This directory contains optional, portable Agent Skills that add repeatable
workflows without changing the platform-adapter architecture or onboarding
contract.

| Skill | Purpose |
|---|---|
| [`agentic-agile-forensic-ingest`](agentic-agile-forensic-ingest/SKILL.md) | Reconstruct immutable Git evidence, inspect recurring upstream deltas, render evidence-backed issue records, publish idempotently to GitHub, and recommend human-led upstream contributions. |

## Installing a pinned copy

Install a skill into a downstream repository from an immutable template commit
so the copy is byte-identical and auditable:

```text
git -C <template-clone> archive --format=tar <pinned-commit> .github/skills/<skill> | tar -x -C <downstream-repo>
git -C <template-clone> ls-tree -r <pinned-commit> -- .github/skills/<skill>
```

Each skill ships a `.gitattributes` (`* -text`) so line-ending conversion
(`core.autocrlf`) cannot alter bytes on archive, checkout, or commit. Compare
each installed file's SHA-256 with the SHA-256 of the raw bytes emitted by
`git cat-file blob <blob-id>` from the `ls-tree` listing, and record the pinned
commit in the downstream change. The blob command emits bytes, not a digest.
