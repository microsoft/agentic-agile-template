# Evidence Model

## Observed evidence

The skill records only evidence that can be reproduced from immutable Git
objects and configured refs:

- full commit, tree, and parent SHAs;
- author and committer timestamps embedded in each commit object;
- first-line commit subject and a SHA-256 digest of the complete commit-message
  bytes;
- first-parent changed paths with rename source/destination evidence;
- test-path classification using documented path rules;
- exact reachability or stable patch equivalence in the configured fork;
- source tip, fork tip, deterministic merge base, baseline, and selected commit
  range.

Rename detection always uses a 50 percent similarity threshold with an
explicit unlimited candidate count, so user or repository `diff.renameLimit`
configuration cannot change recorded path evidence.

All Git extraction and validation commands pin the Myers diff algorithm,
disable the indent heuristic, pin default `a/` and `b/` diff prefixes, ignore
committed/global/system attributes, disable fsmonitor, signature display,
external diff, and text-conversion helpers, set
`GIT_NO_REPLACE_OBJECTS=1`, and set `GIT_NO_LAZY_FETCH=1`. Non-empty
repository-local `info/attributes` files fail extraction.
Git 2.45 or later is required before any repository extraction so lazy-fetch
suppression and the other isolation controls cannot be silently ignored by an
older client. The canonical empty Git tree is used as the verified attribute
source. Local diff or attribute configuration therefore cannot change patch
identity or execute conversion or signature-verification helpers, replacement
refs cannot substitute commit metadata, and a partial clone cannot silently
fetch missing objects from a remote during extraction.

The extraction order is parent-before-child. When more than one commit is ready,
committer timestamp and then full SHA provide deterministic tie-breaking.

## Inferences and limits

Issue titles, summaries, grouping, lifecycle state, and contribution
recommendations are derived records. They are not original prompts, planned
acceptance criteria, proof of review, proof of test execution, or evidence of
deployment.

Semantic groups are deterministic navigation aids. A commit belongs to the
lexicographically first top-level component among its changed paths, or to
`repository-root` when it has no changed path. This rule provides complete,
exclusive, reproducible grouping without claiming recovered product intent.
Group IDs preserve the short readable form when unique and add a deterministic
full-digest collision suffix plus ordinal only when two roots would otherwise
produce the same identifier.

First-parent changed paths prevent a merge from double-counting both parent
histories. A rename records both the prior and destination path; the destination
is the changed-path identity, while either side may trigger test-path
classification or prevent process-overlay suppression. When Git reports
multiple best merge bases, extraction and validation use the lexicographically
smallest full SHA from `git merge-base --all`.

Stable patch equivalence proves that Git computed the same patch identity for a
selected non-merge source commit and a non-merge commit reachable anywhere in
the configured fork. It does not prove identical metadata, intent, review, or
surrounding history.

Contribution recommendations use `git cherry` evidence to exclude fork-only
commits whose stable patch is already present in the source history.

## Mutation guard

Analysis, validation, and contribution recommendation capture `HEAD`, every
ref/object pair, and the complete porcelain worktree state before reading Git
objects. Each repeats the capture after its Git-backed work. Any difference
fails the run; publication therefore stops before remote access when validation
observes concurrent repository mutation. Local output is written only after the
applicable comparison, using atomic replacement.

The Git wrapper passes only an allowlist of inherited environment variables
(path, temp, home, and locale values); every other inherited `GIT_*` variable
and unrelated credential variable is dropped, so repository routing, diff,
pager, exec-path, and config-injection overrides cannot reach Git. The
configured repository path therefore remains authoritative even when the
calling shell is configured for another repository.

Extraction also fails closed on history-altering repository state: non-empty
`info/grafts` or `shallow` files and shallow repositories are rejected before
and during extraction, so ancestry and `all-reachable` coverage always reflect
the complete immutable object graph. Commit subjects and paths are retained
byte-faithfully through surrogate-escape decoding.

The guard detects concurrent or accidental Git/ref/worktree mutation; it does
not lock the repository. Run against a stable checkout.

## Diagnostic safety

Errors redact PEM private-key blocks, common GitHub token prefixes,
bearer/basic authorization values, credential-bearing URIs across schemes, and
token/password query fields. Configuration rejects the same credential forms
before manifest generation. Manifests never contain credentials. Commit
subjects and changed paths remain repository evidence and therefore require
normal repository access controls.

When Git evidence is rendered into issue titles or bodies, non-printable
control characters use stable escaped display text. Issue-reference and
forensic-marker control literals are HTML-escaped so their displayed text is
preserved without being interpreted as publication instructions.
