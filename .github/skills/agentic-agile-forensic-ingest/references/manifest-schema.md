# Manifest Schema

All persisted JSON uses UTF-8, LF line endings, sorted object keys, and a
trailing newline. Hashes use SHA-256 over canonical JSON
(`sort_keys=True`, compact separators, ASCII escaping).
Every `schema_version` is the JSON integer `1`; booleans are invalid even
though Python otherwise compares `true` equal to `1`.

## Configuration (`schema_version: 1`)

| Field | Meaning |
|---|---|
| `profile_id` | Stable, host-neutral identifier used in issue markers. |
| `repository_path` | Local Git worktree path, resolved from the invocation directory. |
| `repository_identity` | Descriptive repository identity; not used for publication. |
| `source_ref` | Upstream/source commit-ish to inspect. |
| `fork_ref` | Fork commit-ish used for incorporation and fork-only analysis. |
| `initial_selection` | `after-baseline` for recurring fork ingest or `all-reachable` for initial reconstruction. |
| `initial_baseline_sha` | Full immutable SHA for `after-baseline`; may be null for `all-reachable`. |
| `github.hostname` | Optional lowercase DNS hostname, defaulting to `github.com`; pinned for every publication API call and checkpoint. |
| `github.repository` | Optional `owner/name` publication target. |
| `github.labels` | Optional array of case-insensitively unique non-empty strings, each at most 50 characters, merged into issue labels only during `publish-github`; local rendered drafts contain the fixed skill labels. |
| `contribution_suppression.path_globs` | Optional array of non-empty, case-sensitive Git path globs; `*` and `?` stay within one path segment, while a complete `**` segment matches recursively. |
| `contribution_suppression.subject_regexes` | Optional array of non-empty valid regular expressions. |

Configuration must not contain credentials. Credential-bearing URI user-info
is rejected for every URI scheme, not only HTTP(S).
Identity, path, ref, repository, and selection fields are type-checked before
regex or membership operations so malformed JSON fails with a deterministic
user-facing error.
The run manifest hashes only the portable extraction contract; local
`repository_path` and GitHub publication settings are excluded.

## State (`schema_version: 1`)

`last_verified_source_sha` records the newest source tip whose publication was
remotely verified. It is checked for ancestry so an observed upstream rewrite
fails closed, but it is not the selection boundary for unresolved work.
`incorporated_baseline_sha` is the recurring analysis baseline and tracks the
latest source tip for which every selected commit was proven exactly or
patch-equivalently incorporated. The two values intentionally differ when the
fork records an upstream delta without integrating it.

A non-empty state must contain the complete schema fields. SHA values must be
null or lowercase strings of the documented length; numeric coercion and
missing checkpoint fields are rejected rather than treated as an empty
selection boundary. The last verified source SHA and its manifest SHA-256 are
both null or both set. A non-null incorporated baseline requires a verified
source SHA and must be its ancestor, so damaged state cannot exclude history
that was never remotely verified. Before the baseline is used, every selected
source commit from the configured initial boundary through that baseline is
also reproven exactly or patch-equivalently incorporated in the current fork.

## Run manifest (`schema_version: 1`)

For initial reconstruction, `all-reachable` inventories every commit reachable
from the frozen source ref. Recurring runs select commits after
`incorporated_baseline_sha`, or after the configured initial baseline until an
incorporated baseline exists. This intentionally keeps previously recorded but
unsynced commits in later runs so incorporation can be proven and backfilled.

The run manifest contains:

- immutable source/fork/baseline/merge-base identities;
- deterministic ordering and diff semantics;
- one record per selected source commit;
- deterministic semantic groups that assign every selected commit exactly once
  by its primary top-level changed-path component;
- integration status (`incorporated_exact`,
  `incorporated_patch_equivalent`, or `unsynced`);
- complete/unique coverage counters;
- `run_id` derived from the evidence payload; and
- `manifest_sha256`, recomputed with that field omitted.

Every selected commit must occur exactly once in both the commit inventory and
the semantic grouping. Validation re-extracts immutable commit metadata,
first-parent changed/rename/test paths, stable patch IDs, integration status,
topology, merge base, semantic groups, all coverage counters, the derived run
ID, and the complete `baseline..source_tip` inventory from Git. When state is
provided, validation also checks the recurring selection boundary. Without
state, validation permits only the configured initial boundary; a manifest
using an incorporated checkpoint requires its matching state file. A manifest
whose evidence or derived identity was edited and rehashed is rejected.

## Rendered drafts (`schema_version: 1`)

Drafts contain the manifest semantic grouping plus `issues`, each with a unique
`logical_id`, stable hidden marker, title, body, state, labels, optional
`parent_id`, optional dependencies, exclusive `commit_shas`, and referenced
semantic group IDs.

An unsynced run renders one open decision issue. A fully incorporated run
renders deterministic closed historical parents and child stories. Each parent
has at most 100 direct children; larger histories are partitioned into stable
100-group chunks before publication.
Before any remote mutation, publication also counts existing children on every
adopted parent and fails if unrelated or prior children leave insufficient
capacity for the planned hierarchy.
Draft validation derives lifecycle state from the manifest, requires complete
and unique commit/group coverage with stable logical IDs, and validates an
acyclic reference graph. Publication independently validates the manifest and
derives state advancement from its Git-verified integration evidence rather
than trusting editable draft metadata.
Publication loads configuration, manifest, drafts, and ingest state once under
the transaction lock, validates those exact in-memory snapshots, and uses the
same objects for every remote decision. Replacing an input file after the
snapshot cannot change the target repository, issue payloads, or checkpoint
derivation for the active run.

Git-derived subjects, paths, and group labels escape both the issue-reference
and forensic-marker control prefixes before templating. Draft validation and
publication resolve only references declared by the issue dependency metadata,
so repository text cannot introduce publication dependencies or logical marker
identities.

Git paths are retained byte-faithfully in manifest evidence through Python's
surrogate-escape representation. Rendering converts non-UTF-8 bytes to stable
`\xNN` display text and escapes control characters in Git-derived subjects,
paths, and group labels before applying body and title limits. Git-derived `@`
characters render as `&#64;` so evidence cannot notify users or teams.

Git-derived text is escaped for its specific Markdown context. Subjects render
as plain text with every Markdown/HTML-active character (backslash, backtick,
brackets, parentheses, angle brackets, emphasis, `#`, `|`, `~`, `&`, `:`, `.`,
and similar) emitted as numeric character references, so crafted commits cannot
hide evidence, add links, or inject HTML. Paths and group labels render in code
spans whose fence is longer than any backtick run in the value. Issue titles are
plain text with backticks removed. Labels must be 1-50 characters with no
commas, control characters, or surrounding whitespace.

## Publication state (`schema_version: 1`)

A missing publication-state file initializes a new publication. Every existing
file must contain a schema-valid checkpoint, including when no issue has been
published yet. An empty JSON object (`{}`), empty file, invalid root, unreadable
file, or malformed checkpoint fails closed before any GitHub access in both
dry-run and execute. Invalid checkpoints are never reset or overwritten
automatically; a human must reconcile them. This differs from the ingest state's
explicit support for an empty object.

Publication state binds a draft hash to one GitHub repository and maps logical
IDs to issue numbers, database IDs, URLs, hierarchy status, and closure status.
Each issue entry also records whether the publisher created it or adopted it by
marker. Only a publisher-created entry may resume a recorded pending close;
marker-only adoption must already match the rendered lifecycle.
Before each issue-creation API call, publication state records a deterministic
creation-intent hash over the logical ID, resolved title, body, and labels. If
the process stops after GitHub creates the issue but before its number and
database ID are checkpointed, the next run may re-adopt that exact marked issue
as publisher-created only when the persisted intent matches the current draft.
An existing intent triggers bounded marker rediscovery before any repeated
create; if no issue becomes visible, publication fails closed and requires
human reconciliation rather than risking a duplicate POST.
It is written atomically after each successful step so interrupted publication
can resume without duplicate creation. A publisher-created issue that is still
open before its recorded historical close can resume that pending transition;
an issue reopened after closure is treated as remote drift and fails closed.
Every existing marked issue is preflighted for title, body, lifecycle, closure
reason, labels, and GitHub database-ID drift before publication creates labels
or performs any other remote mutation. Database IDs are checked again during
final verification before native sub-issue hierarchy is accepted. Final
verification repeats all-marker discovery so a concurrent duplicate logical
marker prevents checkpoint advancement.

The state also binds a hash of the target repository and configured publication
labels. Changing those settings requires a new state file or human
reconciliation.

Changing a draft after partial publication requires a new publication-state
file or explicit human reconciliation.

Publication captures the ingest-state fingerprint used at validation and holds
a host-local transaction lock keyed by GitHub hostname, target repository, and
profile ID (stored under a fixed per-host root: `/var/tmp` on POSIX or the Windows
common application data directory returned by `SHGetKnownFolderPath` for
`FOLDERID_ProgramData`). The Windows location is resolved through the operating
system in an isolated Python child: its entire environment contains only the
Windows directory and drive returned by the kernel's `GetSystemWindowsDirectoryW`.
This prevents the shell API's own first-use environment expansion from observing
spoofed `ProgramData`, `SystemDrive`, home or temp settings. Native lookup,
child-process startup, timeout and invalid-output failures fail closed, without
an inherited-environment or guessed-drive fallback.

On POSIX, an administrator must provision
`/var/tmp/agentic-agile-forensic-ingest-locks` as a real directory, owned by root
(UID 0), with mode `01777`, before `publish-github --execute`. The sticky bit
protects other accounts' active lock files; root ownership is necessary because
a sticky directory's owner can still remove any file inside it. A caller-owned
directory, a symlink, a missing directory, an unreadable directory or different
mode fails explicitly before lock creation or GitHub access. Publication never
creates, chmods, chowns or redirects this shared directory automatically.

After inspecting the exact path and confirming it is not a symlink, an
administrator can provision or reconcile the directory with:

```sh
sudo install -d -o 0 -g 0 -m 1777 /var/tmp/agentic-agile-forensic-ingest-locks
```

Do not delete active locks or recursively change their permissions. Existing
caller-created directories require this explicit administrator reconciliation;
an unprivileged publisher cannot safely change the directory to root ownership.
Dry-run publication does not inspect or require this shared directory and
remains read-only. Ordinary sibling checkpoint directories retain their
existing creation and ownership behavior.

Publication also holds exclusive sibling
checkpoint locks for both the ingest state and publication
state, acquired in deterministic path order, from before the initial marker
scan through every remote mutation, final verification, fingerprint comparison,
and atomic checkpoint replacement. The target key is derived from a preloaded
validated configuration and re-verified against the reloaded configuration
after all locks are held. Publishers sharing the target or either state fail
closed; a later publisher reloads the state and refuses a stale checkpoint
overwrite.
The ingest-state and publication-state paths must resolve to distinct files;
aliases are rejected before the lock or any GitHub access. Their canonical
resolved paths are then used consistently for locking, reads, and atomic
writes, so a symlink cannot leave its target checkpoint stale.
Generated manifests, drafts, recommendation reports, and mutable publication
checkpoints must also resolve to files distinct from every durable input they
could overwrite.
If a process is terminated while holding any lock, a human must verify no
publisher is running before removing the reported lock files.
