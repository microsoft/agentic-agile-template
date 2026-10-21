"""Host-neutral forensic Git extraction plus isolated GitHub publication."""

from __future__ import annotations

from contextlib import contextmanager
import fnmatch
import hashlib
import heapq
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time
import unicodedata
from string import Template
from typing import Any, Callable, Iterable, Iterator, Mapping, Optional


SCHEMA_VERSION = 1
EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
MIN_GIT_VERSION = (2, 45, 0)
GIT_ENVIRONMENT_ALLOWLIST = frozenset(
    {
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "SYSTEMDRIVE",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
        "HOME",
        "USERPROFILE",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
    }
)
MAX_BODY_BYTES = 60_000
MAX_GITHUB_PAGES = 10_000
MAX_LABELS_PER_ISSUE = 100
MAX_SUB_ISSUES_PER_PARENT = 100
MARKER_PATTERN = re.compile(r"<!-- forensic-ingest-id:([^ >]+) -->")
ISSUE_REFERENCE_PATTERN = re.compile(r"\{\{issue:([^}]+)\}\}")
TOKEN_PATTERNS = (
    (
        re.compile(
            r"-----BEGIN ([A-Z0-9 ]*PRIVATE KEY)-----"
            r"[\s\S]*?"
            r"-----END \1-----",
            re.IGNORECASE,
        ),
        "[REDACTED PRIVATE KEY]",
    ),
    (
        re.compile(r"(?i)((?:proxy-)?authorization\s*:\s*)[^\r\n]+"),
        r"\1[REDACTED]",
    ),
    (re.compile(r"(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]+"), "[REDACTED]"),
    (re.compile(r"(?i)(bearer\s+)\S+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(basic\s+)\S+"), r"\1[REDACTED]"),
    (
        re.compile(r"([A-Za-z][A-Za-z0-9+.-]*://)[^/\s@]+@"),
        r"\1[REDACTED]@",
    ),
    (
        re.compile(
            r"(?i)([?&;](?:password|passwd|token|"
            r"access(?:[_-]|%5f|%2d)?token|"
            r"github(?:[_-]|%5f|%2d)?token|"
            r"api(?:[_-]|%5f|%2d)?key|authorization|"
            r"client(?:[_-]|%5f|%2d)?secret|"
            r"private(?:[_-]|%5f|%2d)?key|secret)=)[^&;\s]+"
        ),
        r"\1[REDACTED]",
    ),
)
TEST_PATH_RULES = (
    "Directory named test, tests, __tests__, e2e, or integration-tests.",
    "Directory/project component ending in .Test or .Tests.",
    "Filename beginning test_ or ending _test before the extension.",
    "Filename containing .test. or .spec., or stem ending Test, Tests, Spec, or Specs.",
)


class ForensicIngestError(RuntimeError):
    """Raised for deterministic user-facing failures."""


class DuplicateMarkerError(ForensicIngestError):
    """Raised when a logical issue marker is not globally unique."""


def _supported_schema_version(value: Any) -> bool:
    return type(value) is int and value == SCHEMA_VERSION


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def redact(value: Any) -> str:
    text = str(value)
    for pattern, replacement in TOKEN_PATTERNS:
        text = pattern.sub(replacement, text)
    return text.strip()[:4000]


def atomic_write_text(path: Path, text: str) -> None:
    path = path.absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor: Optional[int] = None
    temporary: Optional[Path] = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
            text=True,
        )
        temporary = Path(temporary_name)
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as stream:
            descriptor = None
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
    )


def _canonical_path(path: Path) -> Path:
    try:
        return path.absolute().resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ForensicIngestError(
            f"Cannot resolve state path {path}: {redact(exc)}"
        ) from exc


def _paths_alias(first: Path, second: Path) -> bool:
    first_absolute = first.absolute()
    second_absolute = second.absolute()
    first_canonical = _canonical_path(first_absolute)
    second_canonical = _canonical_path(second_absolute)
    if first_canonical == second_canonical:
        return True
    # Conservatively treat names differing only by case in one directory as the
    # same file: case-insensitive filesystems cannot be detected for paths that
    # do not exist yet.
    if (
        os.path.normcase(str(first_canonical)).casefold()
        == os.path.normcase(str(second_canonical)).casefold()
    ):
        return True
    if (
        first_canonical.name.casefold() == second_canonical.name.casefold()
        and first_canonical.parent.exists()
        and second_canonical.parent.exists()
    ):
        try:
            if os.path.samefile(first_canonical.parent, second_canonical.parent):
                return True
        except OSError:
            pass
    if not first_absolute.exists() or not second_absolute.exists():
        return False
    try:
        return os.path.samefile(first_absolute, second_absolute)
    except OSError:
        return False


def _reject_write_aliases(
    write_name: str,
    write_path: Path,
    read_paths: Iterable[tuple[str, Path]],
) -> None:
    for read_name, read_path in read_paths:
        if _paths_alias(write_path, read_path):
            raise ForensicIngestError(
                f"{write_name} path must be distinct from {read_name} path"
            )


def checkpoint_lock_path(state_path: Path) -> Path:
    state_path = Path(os.path.normcase(str(_canonical_path(state_path))))
    return state_path.with_name(f".{state_path.name}.lock")


def publication_target_key(config: Mapping[str, Any]) -> str:
    validate_config(config)
    github = config.get("github")
    if not isinstance(github, dict) or not github.get("repository"):
        raise ForensicIngestError(
            "Configuration github.repository is required for publication"
        )
    return sha256_value(
        {
            "hostname": str(github.get("hostname", "github.com")).casefold(),
            "repository": str(github["repository"]).casefold(),
            "profile_id": config["profile_id"],
        }
    )


def publication_target_lock_path(target_key: str) -> Path:
    # Fixed per-host root so differing TMPDIR/TEMP settings cannot split the lock.
    if os.name == "nt":
        root = Path(os.environ.get("ProgramData") or r"C:\ProgramData")
    else:
        root = Path("/var/tmp")
    return (
        root
        / "agentic-agile-forensic-ingest-locks"
        / f"publication-{target_key}.lock"
    )


@contextmanager
def exclusive_checkpoint_lock(
    state_path: Path, *, lock_path: Optional[Path] = None
) -> Iterator[None]:
    lock_path = lock_path or checkpoint_lock_path(state_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor: Optional[int] = None
    try:
        descriptor = os.open(
            lock_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError as exc:
        raise ForensicIngestError(
            f"State checkpoint lock already exists: {lock_path}"
        ) from exc
    except OSError as exc:
        raise ForensicIngestError(
            f"Cannot create state checkpoint lock {lock_path}: {redact(exc)}"
        ) from exc
    try:
        os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
        yield
    finally:
        os.close(descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def load_json(path: Path, *, required: bool = True) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise ForensicIngestError(f"JSON file does not exist: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ForensicIngestError(f"Invalid JSON file {path}: {redact(exc)}") from exc
    if not isinstance(value, dict):
        raise ForensicIngestError(f"JSON root must be an object: {path}")
    return value


def _reject_credential_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            separated = re.sub(
                r"([a-z0-9])([A-Z])",
                r"\1_\2",
                str(key),
            )
            normalized = re.sub(
                r"[^a-z0-9]+",
                "_",
                separated.lower(),
            ).strip("_")
            if re.search(
                r"(?:^|_)(?:password|passwd|token|access_token|github_token|"
                r"api_key|authorization|client_secret|private_key|secret)"
                r"(?:_|$)",
                normalized,
            ):
                raise ForensicIngestError(
                    f"Credential-like configuration key is forbidden: {path}.{key}"
                )
            _reject_credential_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_credential_keys(child, f"{path}[{index}]")
    elif isinstance(value, str) and any(
        pattern.search(value) for pattern, _ in TOKEN_PATTERNS
    ):
        raise ForensicIngestError(
            f"Credential-like configuration value is forbidden: {path}"
        )


def validate_config(config: Mapping[str, Any]) -> None:
    if not _supported_schema_version(config.get("schema_version")):
        raise ForensicIngestError("Unsupported configuration schema_version")
    required = (
        "profile_id",
        "repository_path",
        "repository_identity",
        "source_ref",
        "fork_ref",
    )
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise ForensicIngestError(f"Configuration fields are required: {missing}")
    for field in required:
        if not isinstance(config.get(field), str) or not config[field].strip():
            raise ForensicIngestError(
                f"Configuration {field} must be a non-empty string"
            )
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", config["profile_id"]):
        raise ForensicIngestError(
            "profile_id must be lowercase, stable, and contain only letters, digits, ., _, or -"
        )
    initial_selection = config.get("initial_selection", "after-baseline")
    if not isinstance(initial_selection, str) or initial_selection not in (
        "after-baseline",
        "all-reachable",
    ):
        raise ForensicIngestError(
            "initial_selection must be after-baseline or all-reachable"
        )
    baseline = config.get("initial_baseline_sha")
    if baseline is not None and not isinstance(baseline, str):
        raise ForensicIngestError("initial_baseline_sha must be null or a full SHA")
    if initial_selection == "after-baseline" and not re.fullmatch(
        r"[0-9a-f]{40}", baseline or ""
    ):
        raise ForensicIngestError(
            "initial_baseline_sha must be a full lowercase SHA for after-baseline"
        )
    if baseline is not None and not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise ForensicIngestError("initial_baseline_sha must be null or a full SHA")
    github = config.get("github")
    if github is not None:
        if not isinstance(github, dict):
            raise ForensicIngestError("github configuration must be an object")
        repository = github.get("repository")
        if repository is not None and (
            not isinstance(repository, str) or not repository.strip()
        ):
            raise ForensicIngestError(
                "github.repository must be a non-empty string"
            )
        hostname = github.get("hostname", "github.com")
        if (
            not isinstance(hostname, str)
            or not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?",
                hostname,
            )
            or ".." in hostname
        ):
            raise ForensicIngestError(
                "github.hostname must be a lowercase DNS hostname"
            )
        labels = github.get("labels", [])
        if not isinstance(labels, list) or not all(
            _is_valid_label(label) for label in labels
        ):
            raise ForensicIngestError(
                "github.labels must be an array of non-empty strings "
                "no longer than 50 characters, without commas, control "
                "characters, or surrounding whitespace"
            )
        if len({label.casefold() for label in labels}) != len(labels):
            raise ForensicIngestError(
                "github.labels must not contain case-insensitive duplicates"
            )
    suppression = config.get("contribution_suppression")
    if suppression is not None:
        if not isinstance(suppression, dict):
            raise ForensicIngestError(
                "contribution_suppression configuration must be an object"
            )
        for key in ("path_globs", "subject_regexes"):
            values = suppression.get(key, [])
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip()
                for value in values
            ):
                raise ForensicIngestError(
                    f"contribution_suppression.{key} must be an array "
                    "of non-empty strings"
                )
        for pattern in suppression.get("subject_regexes", []):
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ForensicIngestError(
                    "contribution_suppression.subject_regexes contains "
                    f"an invalid regular expression: {redact(exc)}"
                ) from exc
    _reject_credential_keys(config)


def validate_state(state: Mapping[str, Any], profile_id: str) -> None:
    if not state:
        return
    required_fields = {
        "schema_version",
        "profile_id",
        "last_verified_source_sha",
        "last_verified_run_manifest_sha256",
        "incorporated_baseline_sha",
    }
    missing = required_fields - set(state)
    unknown = set(state) - required_fields
    if missing:
        raise ForensicIngestError(
            f"State fields are required: {sorted(missing)}"
        )
    if unknown:
        raise ForensicIngestError(
            f"State contains unknown fields: {sorted(unknown)}"
        )
    if not _supported_schema_version(state.get("schema_version")):
        raise ForensicIngestError("Unsupported state schema_version")
    if not isinstance(state.get("profile_id"), str):
        raise ForensicIngestError("State profile_id must be a string")
    if state.get("profile_id") != profile_id:
        raise ForensicIngestError("State profile_id does not match configuration")
    for key in ("last_verified_source_sha", "incorporated_baseline_sha"):
        value = state.get(key)
        if value is not None and (
            not isinstance(value, str)
            or not re.fullmatch(r"[0-9a-f]{40}", value)
        ):
            raise ForensicIngestError(f"State field {key} must be null or a full SHA")
    manifest_hash = state.get("last_verified_run_manifest_sha256")
    if manifest_hash is not None and (
        not isinstance(manifest_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", manifest_hash)
    ):
        raise ForensicIngestError(
            "State field last_verified_run_manifest_sha256 must be null or a SHA-256"
        )
    verified_sha = state.get("last_verified_source_sha")
    if (verified_sha is None) != (manifest_hash is None):
        raise ForensicIngestError(
            "State last verified source SHA and manifest SHA-256 must both be null "
            "or both be set"
        )
    if state.get("incorporated_baseline_sha") is not None and verified_sha is None:
        raise ForensicIngestError(
            "State incorporated baseline requires a last verified source SHA"
        )


def analysis_config_contract(config: Mapping[str, Any]) -> dict[str, Any]:
    """Return only portable fields that influence host-neutral extraction."""
    return {
        "schema_version": config["schema_version"],
        "profile_id": config["profile_id"],
        "repository_identity": config["repository_identity"],
        "source_ref": config["source_ref"],
        "fork_ref": config["fork_ref"],
        "initial_selection": config.get("initial_selection", "after-baseline"),
        "initial_baseline_sha": config.get("initial_baseline_sha"),
    }


def is_test_path(path: Optional[str]) -> bool:
    if not path:
        return False
    parts = PurePosixPath(path).parts
    directories = [part.lower() for part in parts[:-1]]
    if any(
        part in {"test", "tests", "__tests__", "e2e", "integration-tests"}
        or part.endswith((".test", ".tests"))
        for part in directories
    ):
        return True
    name = parts[-1].lower()
    stem = PurePosixPath(name).stem
    original_stem = PurePosixPath(parts[-1]).stem
    return (
        name.startswith("test_")
        or stem.endswith("_test")
        or ".test." in name
        or ".spec." in name
        or stem.endswith(
            ("_tests", "-test", "-tests", "_spec", "_specs", "-spec", "-specs")
        )
        or stem in {"test", "tests", "spec", "specs"}
        or original_stem.endswith(("Test", "Tests", "Spec", "Specs"))
    )


class GitRepository:
    """Read-only Git command wrapper with credential-safe diagnostics."""

    def __init__(self, path: Path):
        self.path = path.resolve()
        # Allowlist rather than denylist: every inherited GIT_* control
        # (diff, pager, exec-path, routing, config injection) is dropped.
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in GIT_ENVIRONMENT_ALLOWLIST
        }
        self.environment.update(
            GIT_ATTR_NOSYSTEM="1",
            GIT_ATTR_SOURCE=EMPTY_TREE_SHA,
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_SYSTEM=os.devnull,
            GIT_NO_LAZY_FETCH="1",
            GIT_NO_REPLACE_OBJECTS="1",
            GIT_OPTIONAL_LOCKS="0",
            GIT_TERMINAL_PROMPT="0",
            GIT_PAGER="cat",
        )
        git_version = self._installed_git_version()
        if git_version < MIN_GIT_VERSION:
            required = ".".join(str(part) for part in MIN_GIT_VERSION)
            installed = ".".join(str(part) for part in git_version)
            raise ForensicIngestError(
                f"Git {required} or later is required; found {installed}"
            )
        self.local_attributes_path: Optional[Path] = None
        self.local_history_paths: dict[str, Path] = {}
        if not (self.path / ".git").exists() and not self._is_worktree():
            raise ForensicIngestError(f"Not a Git worktree: {self.path}")
        attributes_path = self._git_path("info/attributes")
        self.local_attributes_path = attributes_path
        # Repository-local files that rewrite or truncate reachable history.
        self.local_history_paths = {
            "info/grafts": self._git_path("info/grafts"),
            "shallow": self._git_path("shallow"),
        }
        if (
            self.run("rev-parse", "--is-shallow-repository").strip() != "false"
        ):
            raise ForensicIngestError(
                "Shallow repositories are not supported; fetch complete history "
                "before forensic extraction"
            )
        self._assert_no_local_attributes()
        # Git resolves the empty tree as a built-in object, so it need not
        # exist in the inspected repository's object database.
        if self.run("cat-file", "-t", EMPTY_TREE_SHA).strip() != "tree":
            raise ForensicIngestError(
                "Canonical empty Git attribute tree is unavailable"
            )

    def _git_command(self, *arguments: str) -> list[str]:
        return [
            "git",
            "-c",
            f"core.attributesFile={os.devnull}",
            "-c",
            f"attr.tree={EMPTY_TREE_SHA}",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "color.ui=false",
            "-c",
            "color.diff=false",
            "-c",
            "diff.renames=true",
            "-c",
            "diff.renameLimit=0",
            "-c",
            "diff.algorithm=myers",
            "-c",
            "diff.indentHeuristic=false",
            "-c",
            "diff.noprefix=false",
            "-c",
            "diff.mnemonicPrefix=false",
            "-c",
            "diff.srcPrefix=a/",
            "-c",
            "diff.dstPrefix=b/",
            "-c",
            "diff.context=3",
            "-c",
            "diff.interHunkContext=0",
            "-c",
            "log.showSignature=false",
            "--no-pager",
            *arguments,
        ]

    def _installed_git_version(self) -> tuple[int, int, int]:
        try:
            result = subprocess.run(
                ["git", "--version"],
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ForensicIngestError(
                f"Cannot determine Git version: {redact(exc)}"
            ) from exc
        output = result.stdout.decode("ascii", errors="replace").strip()
        match = re.fullmatch(
            r"git version (\d+)\.(\d+)(?:\.(\d+))?(?:[\s.-].*)?",
            output,
        )
        if result.returncode or not match:
            diagnostic = result.stderr.decode("utf-8", errors="replace")
            raise ForensicIngestError(
                f"Cannot determine Git version: {redact(diagnostic or output)}"
            )
        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3) or "0"),
        )

    def _git_path(self, name: str) -> Path:
        value = Path(self.run("rev-parse", "--git-path", name).strip())
        if not value.is_absolute():
            value = self.path / value
        return value.resolve()

    def _assert_no_local_attributes(self) -> None:
        if self.local_attributes_path is None:
            return
        try:
            if (
                self.local_attributes_path.exists()
                and self.local_attributes_path.stat().st_size
            ):
                raise ForensicIngestError(
                    "Repository-local info/attributes is not allowed during "
                    "forensic extraction"
                )
            for name, path in self.local_history_paths.items():
                if path.exists() and path.stat().st_size:
                    raise ForensicIngestError(
                        f"Repository-local {name} rewrites history and is not "
                        "allowed during forensic extraction"
                    )
        except OSError as exc:
            raise ForensicIngestError(
                f"Cannot inspect repository-local history state: {redact(exc)}"
            ) from exc

    def _is_worktree(self) -> bool:
        result = subprocess.run(
            self._git_command("rev-parse", "--is-inside-work-tree"),
            cwd=self.path,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == b"true"

    def run_bytes(
        self,
        *arguments: str,
        input_bytes: Optional[bytes] = None,
        check: bool = True,
        timeout: int = 120,
    ) -> bytes:
        self._assert_no_local_attributes()
        try:
            result = subprocess.run(
                self._git_command(*arguments),
                cwd=self.path,
                env=self.environment,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ForensicIngestError(f"Git execution failed: {redact(exc)}") from exc
        if check and result.returncode:
            raise ForensicIngestError(
                f"git {arguments[0]} exited {result.returncode}: "
                f"{redact(result.stderr.decode('utf-8', errors='replace'))}"
            )
        if not check:
            return result.returncode.to_bytes(4, "big", signed=True) + result.stdout
        return result.stdout

    def run(self, *arguments: str, **kwargs: Any) -> str:
        return self.run_bytes(*arguments, **kwargs).decode(
            "utf-8", errors="surrogateescape"
        )

    def resolve_commit(self, value: str) -> str:
        resolved = self.run("rev-parse", "--verify", f"{value}^{{commit}}").strip()
        if not re.fullmatch(r"[0-9a-f]{40}", resolved):
            raise ForensicIngestError(f"Commit-ish did not resolve to a full SHA: {value}")
        return resolved

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        self._assert_no_local_attributes()
        result = subprocess.run(
            self._git_command(
                "merge-base",
                "--is-ancestor",
                ancestor,
                descendant,
            ),
            cwd=self.path,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise ForensicIngestError(
                f"git merge-base failed: "
                f"{redact(result.stderr.decode('utf-8', errors='replace'))}"
            )
        return result.returncode == 0

    def guard(self) -> dict[str, str]:
        return {
            "head": self.run("rev-parse", "HEAD").strip(),
            "refs_sha256": hashlib.sha256(
                self.run_bytes("for-each-ref", "--format=%(refname) %(objectname)")
            ).hexdigest(),
            "worktree_sha256": hashlib.sha256(
                self.run_bytes(
                    "status", "--porcelain=v1", "-z", "--untracked-files=all"
                )
            ).hexdigest(),
        }

    def selected_shas(self, baseline: Optional[str], tip: str) -> list[str]:
        arguments = ["rev-list", tip]
        if baseline:
            arguments.append(f"^{baseline}")
        arguments.append("--")
        output = self.run(*arguments).splitlines()
        if len(output) != len(set(output)):
            raise ForensicIngestError("Git returned duplicate commits for the selected range")
        return output

    def fork_only_shas(self, fork_tip: str, source_tip: str) -> list[str]:
        output = self.run("rev-list", fork_tip, f"^{source_tip}", "--").splitlines()
        return output

    def deterministic_merge_base(self, left: str, right: str) -> str:
        merge_bases = sorted(
            set(self.run("merge-base", "--all", left, right).splitlines())
        )
        if not merge_bases or any(
            not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in merge_bases
        ):
            raise ForensicIngestError("Git returned invalid merge-base evidence")
        return merge_bases[0]

    def source_patch_equivalent_fork_shas(
        self,
        source_tip: str,
        fork_tip: str,
    ) -> set[str]:
        equivalent: set[str] = set()
        for line in self.run("cherry", source_tip, fork_tip).splitlines():
            match = re.fullmatch(r"([+-]) ([0-9a-f]{40})", line)
            if not match:
                raise ForensicIngestError("Git returned malformed cherry evidence")
            if match.group(1) == "-":
                equivalent.add(match.group(2))
        return equivalent

    def reachable_patch_id_shas(self, tip: str) -> dict[str, list[str]]:
        self._assert_no_local_attributes()
        by_patch_id: dict[str, list[str]] = {}
        log_process: Optional[subprocess.Popen[bytes]] = None
        patch_process: Optional[subprocess.Popen[bytes]] = None
        deadline = time.monotonic() + 600
        with tempfile.TemporaryFile() as log_error:
            with tempfile.TemporaryFile() as patch_output:
                with tempfile.TemporaryFile() as patch_error:
                    try:
                        log_process = subprocess.Popen(
                            self._git_command(
                                "log",
                                "--no-merges",
                                "--pretty=format:commit %H",
                                "-p",
                                "--binary",
                                "--full-index",
                                "--default-prefix",
                                "--no-ext-diff",
                                "--no-textconv",
                                tip,
                                "--",
                            ),
                            cwd=self.path,
                            env=self.environment,
                            stdout=subprocess.PIPE,
                            stderr=log_error,
                        )
                        if log_process.stdout is None:
                            raise ForensicIngestError(
                                "Git patch pipeline did not expose log output"
                            )
                        patch_process = subprocess.Popen(
                            self._git_command("patch-id", "--stable"),
                            cwd=self.path,
                            env=self.environment,
                            stdin=log_process.stdout,
                            stdout=patch_output,
                            stderr=patch_error,
                        )
                        log_process.stdout.close()
                        patch_process.wait(
                            timeout=max(0.1, deadline - time.monotonic())
                        )
                        log_process.wait(
                            timeout=max(0.1, deadline - time.monotonic())
                        )
                    except subprocess.TimeoutExpired as exc:
                        raise ForensicIngestError(
                            "Git patch-id pipeline timed out"
                        ) from exc
                    except OSError as exc:
                        raise ForensicIngestError(
                            f"Git patch-id pipeline failed: {redact(exc)}"
                        ) from exc
                    finally:
                        for process in (patch_process, log_process):
                            if process is not None and process.poll() is None:
                                process.kill()
                                process.wait()

                    log_error.seek(0)
                    patch_error.seek(0)
                    log_diagnostic = log_error.read().decode(
                        "utf-8", errors="replace"
                    )
                    patch_diagnostic = patch_error.read().decode(
                        "utf-8", errors="replace"
                    )
                    if log_process.returncode:
                        raise ForensicIngestError(
                            f"git log exited {log_process.returncode}: "
                            f"{redact(log_diagnostic)}"
                        )
                    if patch_process.returncode:
                        raise ForensicIngestError(
                            f"git patch-id exited {patch_process.returncode}: "
                            f"{redact(patch_diagnostic)}"
                        )

                    patch_output.seek(0)
                    for raw_line in patch_output:
                        line = raw_line.decode(
                            "ascii", errors="replace"
                        ).rstrip("\r\n")
                        match = re.fullmatch(
                            r"([0-9a-f]{40}) ([0-9a-f]{40})",
                            line,
                        )
                        if not match:
                            raise ForensicIngestError(
                                "Git returned malformed reachable patch-id evidence"
                            )
                        by_patch_id.setdefault(match.group(1), []).append(
                            match.group(2)
                        )
        return {
            patch_id: sorted(shas)
            for patch_id, shas in sorted(by_patch_id.items())
        }

    def read_commit(self, sha: str) -> dict[str, Any]:
        content = self.run_bytes("cat-file", "commit", sha)
        if b"\n\n" in content:
            header, message = content.split(b"\n\n", 1)
        else:
            header, message = content, b""
        fields: dict[bytes, list[bytes]] = {}
        for line in header.splitlines():
            if line.startswith(b" "):
                continue
            key, separator, value = line.partition(b" ")
            if separator:
                fields.setdefault(key, []).append(value)
        try:
            tree_sha = fields[b"tree"][0].decode("ascii")
            parents = [value.decode("ascii") for value in fields.get(b"parent", [])]
            author_timestamp = self._identity_timestamp(fields[b"author"][0])
            committer_timestamp = self._identity_timestamp(fields[b"committer"][0])
        except (KeyError, IndexError, UnicodeError) as exc:
            raise ForensicIngestError(f"Malformed commit object: {sha}") from exc
        subject_bytes = re.split(br"\r?\n", message, maxsplit=1)[0]
        subject = subject_bytes.decode("utf-8", errors="surrogateescape")
        return {
            "sha": sha,
            "tree_sha": tree_sha,
            "parent_shas": parents,
            "author_timestamp": author_timestamp,
            "committer_timestamp": committer_timestamp,
            "subject": subject,
            "message_bytes_sha256": hashlib.sha256(message).hexdigest(),
        }

    @staticmethod
    def _identity_timestamp(identity: bytes) -> dict[str, Any]:
        match = re.search(rb" (-?\d+) ([+-]\d{4})$", identity)
        if not match:
            raise ForensicIngestError("Commit identity lacks an immutable timestamp")
        return {
            "unix_seconds": int(match.group(1)),
            "timezone_offset": match.group(2).decode("ascii"),
        }

    def changed_files(self, sha: str, parents: list[str]) -> list[dict[str, Any]]:
        if parents:
            raw = self.run_bytes(
                "diff",
                "--name-status",
                "-z",
                "--find-renames=50%",
                "-l0",
                "--no-ext-diff",
                "--no-textconv",
                parents[0],
                sha,
                "--",
            )
        else:
            raw = self.run_bytes(
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-status",
                "-z",
                "-r",
                "--find-renames=50%",
                "-l0",
                "--no-ext-diff",
                "--no-textconv",
                sha,
                "--",
            )
        fields = raw.split(b"\0")
        if fields and fields[-1] == b"":
            fields.pop()
        index = 0
        changed: list[dict[str, Any]] = []
        while index < len(fields):
            status = fields[index].decode("ascii")
            index += 1
            if index >= len(fields):
                raise ForensicIngestError(f"Malformed name-status output for {sha}")
            old_path: Optional[str] = None
            if status.startswith(("R", "C")):
                old_path = fields[index].decode("utf-8", errors="surrogateescape")
                index += 1
                if index >= len(fields):
                    raise ForensicIngestError(f"Malformed rename output for {sha}")
            path = fields[index].decode("utf-8", errors="surrogateescape")
            index += 1
            changed.append(
                {
                    "path": path,
                    "old_path": old_path,
                    "status": status,
                    "is_test": is_test_path(path) or is_test_path(old_path),
                }
            )
        return sorted(
            changed,
            key=lambda item: (item["path"], item["old_path"] or "", item["status"]),
        )

    def stable_patch_id(self, sha: str, parents: list[str]) -> Optional[str]:
        if len(parents) > 1:
            return None
        self._assert_no_local_attributes()
        show_command = self._git_command(
            "show",
            "--pretty=format:",
            "--binary",
            "--full-index",
            "--default-prefix",
            "--no-ext-diff",
            "--no-textconv",
            sha,
            "--",
        )
        patch_id_command = self._git_command("patch-id", "--stable")
        show: Optional[subprocess.Popen[bytes]] = None
        patch_id_process: Optional[subprocess.Popen[bytes]] = None
        try:
            show = subprocess.Popen(
                show_command,
                cwd=self.path,
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            patch_id_process = subprocess.Popen(
                patch_id_command,
                cwd=self.path,
                env=self.environment,
                stdin=show.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert show.stdout is not None
            show.stdout.close()
            deadline = time.monotonic() + 120
            patch_id_output, patch_id_error = patch_id_process.communicate(
                timeout=max(deadline - time.monotonic(), 0.001)
            )
            show_error = show.stderr.read() if show.stderr else b""
            show.wait(timeout=max(deadline - time.monotonic(), 0.001))
        except (OSError, subprocess.SubprocessError) as exc:
            raise ForensicIngestError(f"Git execution failed: {redact(exc)}") from exc
        finally:
            for process in (patch_id_process, show):
                if process is None:
                    continue
                if process.poll() is None:
                    process.kill()
                    process.wait()
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
        if show.returncode:
            raise ForensicIngestError(
                f"git show exited {show.returncode}: "
                f"{redact(show_error.decode('utf-8', errors='replace'))}"
            )
        if patch_id_process.returncode:
            raise ForensicIngestError(
                f"git patch-id exited {patch_id_process.returncode}: "
                f"{redact(patch_id_error.decode('utf-8', errors='replace'))}"
            )
        output = patch_id_output.decode("utf-8", errors="surrogateescape").strip()
        if not output:
            return None
        patch_id = output.split()[0]
        if not re.fullmatch(r"[0-9a-f]{40}", patch_id):
            raise ForensicIngestError(f"Malformed stable patch-id for {sha}")
        return patch_id


def topological_order(records: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    children: dict[str, list[str]] = {sha: [] for sha in records}
    pending: dict[str, int] = {}
    for sha, record in records.items():
        internal_parents = [
            parent for parent in record["parent_shas"] if parent in records
        ]
        pending[sha] = len(internal_parents)
        for parent in internal_parents:
            children[parent].append(sha)
    ready = [
        (record["committer_timestamp"]["unix_seconds"], sha)
        for sha, record in records.items()
        if pending[sha] == 0
    ]
    heapq.heapify(ready)
    ordered: list[dict[str, Any]] = []
    while ready:
        _, sha = heapq.heappop(ready)
        ordered.append(records[sha])
        for child in sorted(children[sha]):
            pending[child] -= 1
            if pending[child] == 0:
                heapq.heappush(
                    ready,
                    (
                        records[child]["committer_timestamp"]["unix_seconds"],
                        child,
                    ),
                )
    if len(ordered) != len(records):
        raise ForensicIngestError("Selected commits do not form an acyclic Git graph")
    return ordered


def _repository_from_config(config: Mapping[str, Any]) -> GitRepository:
    return GitRepository(Path(str(config["repository_path"])))


def _selection_baseline(
    config: Mapping[str, Any],
    state: Mapping[str, Any],
    repository: GitRepository,
    source_tip: str,
    fork_tip: str,
) -> tuple[Optional[str], str]:
    last_verified = state.get("last_verified_source_sha")
    verified_sha: Optional[str] = None
    if last_verified is not None:
        verified_sha = str(last_verified)
        if repository.resolve_commit(verified_sha) != verified_sha:
            raise ForensicIngestError("Last verified source SHA did not resolve exactly")
        if not repository.is_ancestor(verified_sha, source_tip):
            raise ForensicIngestError(
                "Last verified source SHA is rewritten, disconnected, or not an "
                "ancestor of the source tip"
            )

    incorporated = state.get("incorporated_baseline_sha")
    if incorporated is not None:
        baseline = str(incorporated)
        selection_mode = "after-incorporated-baseline"
    elif config.get("initial_selection", "after-baseline") == "all-reachable":
        baseline = None
        selection_mode = "all-reachable"
    else:
        baseline = str(config["initial_baseline_sha"])
        selection_mode = "after-initial-baseline"

    if baseline is not None:
        if repository.resolve_commit(baseline) != baseline:
            raise ForensicIngestError("Baseline SHA did not resolve exactly")
        if not repository.is_ancestor(baseline, source_tip):
            raise ForensicIngestError(
                "Baseline is rewritten, disconnected, or not an ancestor of the source tip"
            )
        if incorporated is not None and (
            verified_sha is None
            or not repository.is_ancestor(baseline, verified_sha)
        ):
            raise ForensicIngestError(
                "Incorporated baseline is not an ancestor of the last verified "
                "source SHA"
            )
        if incorporated is not None:
            if config.get("initial_selection", "after-baseline") == "all-reachable":
                initial_baseline = None
            else:
                initial_baseline = str(config["initial_baseline_sha"])
                if not repository.is_ancestor(initial_baseline, baseline):
                    raise ForensicIngestError(
                        "Incorporated baseline is disconnected from the configured "
                        "initial baseline"
                    )
            selected = repository.selected_shas(initial_baseline, baseline)
            fork_patch_ids = set(
                repository.reachable_patch_id_shas(fork_tip)
            )
            unresolved = []
            for source_sha in selected:
                if repository.is_ancestor(source_sha, fork_tip):
                    continue
                source_record = repository.read_commit(source_sha)
                patch_id = repository.stable_patch_id(
                    source_sha,
                    source_record["parent_shas"],
                )
                if patch_id is None or patch_id not in fork_patch_ids:
                    unresolved.append(source_sha)
            if unresolved:
                raise ForensicIngestError(
                    "Incorporated baseline includes source commits not proven "
                    "incorporated in the configured fork"
                )
    return baseline, selection_mode


def _extract_commit_records(
    repository: GitRepository,
    selected: Iterable[str],
    source_tip: str,
    fork_tip: str,
) -> list[dict[str, Any]]:
    fork_patch_ids = repository.reachable_patch_id_shas(fork_tip)

    raw_records = {sha: repository.read_commit(sha) for sha in selected}
    for sha, record in raw_records.items():
        changed = repository.changed_files(sha, record["parent_shas"])
        record["changed_files"] = changed
        record["changed_paths"] = sorted({item["path"] for item in changed})
        record["test_paths"] = sorted(
            {
                path
                for item in changed
                if item["is_test"]
                for path in (item["old_path"], item["path"])
                if path and is_test_path(path)
            }
        )
        patch_id = repository.stable_patch_id(sha, record["parent_shas"])
        record["stable_patch_id"] = patch_id
        if repository.is_ancestor(sha, fork_tip):
            record["integration"] = {
                "status": "incorporated_exact",
                "fork_commit_shas": [sha],
            }
        elif patch_id and patch_id in fork_patch_ids:
            record["integration"] = {
                "status": "incorporated_patch_equivalent",
                "fork_commit_shas": fork_patch_ids[patch_id],
            }
        else:
            record["integration"] = {
                "status": "unsynced",
                "fork_commit_shas": [],
            }

    ordered = topological_order(raw_records)
    for index, record in enumerate(ordered):
        record["topological_index"] = index
    return ordered


def _semantic_groups(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        roots = sorted(
            {
                PurePosixPath(path).parts[0]
                for path in record["changed_paths"]
                if PurePosixPath(path).parts
            }
        )
        primary_root = roots[0] if roots else "repository-root"
        grouped.setdefault(primary_root, []).append(record)
    primary_roots = sorted(grouped)
    base_ids = {
        primary_root: (
            f"path-root:{_safe_slug(primary_root)}:"
            f"{sha256_value(primary_root)[:8]}"
        )
        for primary_root in primary_roots
    }
    roots_by_base_id: dict[str, list[str]] = {}
    for primary_root, base_id in base_ids.items():
        roots_by_base_id.setdefault(base_id, []).append(primary_root)
    group_ids: dict[str, str] = {}
    for base_id, colliding_roots in roots_by_base_id.items():
        if len(colliding_roots) == 1:
            group_ids[colliding_roots[0]] = base_id
            continue
        for collision_index, primary_root in enumerate(
            sorted(colliding_roots),
            start=1,
        ):
            group_ids[primary_root] = (
                f"{base_id}:collision-{collision_index:04d}:"
                f"{sha256_value(primary_root)}"
            )

    groups = []
    for primary_root in primary_roots:
        group_records = grouped[primary_root]
        groups.append(
            {
                "id": group_ids[primary_root],
                "label": primary_root,
                "basis": "lexicographically-first-top-level-changed-path",
                "commit_shas": [record["sha"] for record in group_records],
                "changed_paths": sorted(
                    {
                        path
                        for record in group_records
                        for path in record["changed_paths"]
                    }
                ),
                "test_paths": sorted(
                    {
                        path
                        for record in group_records
                        for path in record["test_paths"]
                    }
                ),
            }
        )
    return groups


def _manifest_payload(
    config: Mapping[str, Any],
    source_tip: str,
    fork_tip: str,
    baseline: Optional[str],
    selection_mode: str,
    merge_base: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    for record in records:
        status = record["integration"]["status"]
        statuses[status] = statuses.get(status, 0) + 1
    unique_count = len({item["sha"] for item in records})
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "agentic-agile-forensic-ingest-run",
        "profile_id": config["profile_id"],
        "repository_identity": config["repository_identity"],
        "config_sha256": sha256_value(analysis_config_contract(config)),
        "source": {"ref": config["source_ref"], "tip_sha": source_tip},
        "fork": {"ref": config["fork_ref"], "tip_sha": fork_tip},
        "baseline_sha": baseline,
        "selection_mode": selection_mode,
        "merge_base_sha": merge_base,
        "ordering": (
            "Parent-before-child topological order; committer timestamp and full SHA "
            "break ties between ready commits."
        ),
        "diff_semantics": (
            "Root commits compare with the empty tree; other commits compare with "
            "their first parent; rename detection threshold is 50 percent."
        ),
        "test_path_rules": list(TEST_PATH_RULES),
        "semantic_grouping": {
            "strategy": (
                "Assign each commit exactly once by the lexicographically first "
                "top-level component among its changed paths; use repository-root "
                "when no changed path exists."
            ),
            "groups": _semantic_groups(records),
        },
        "commits": records,
        "coverage": {
            "selected_commit_count": len(records),
            "manifest_commit_count": len(records),
            "unique_commit_count": unique_count,
            "integration_status_counts": dict(sorted(statuses.items())),
            "complete_and_unique": len(records) == unique_count,
        },
        "mutation_guard": {
            "head_refs_and_worktree_unchanged_during_read": True,
            "git_commands_are_read_only": True,
        },
    }


def analyze_repository(
    config_path: Path, state_path: Path, output_path: Path
) -> dict[str, Any]:
    config_path = _canonical_path(config_path)
    state_path = _canonical_path(state_path)
    output_path = _canonical_path(output_path)
    _reject_write_aliases(
        "Analysis output",
        output_path,
        (
            ("configuration", config_path),
            ("ingest state", state_path),
        ),
    )
    config = load_json(config_path)
    validate_config(config)
    state = load_json(state_path, required=False)
    validate_state(state, str(config["profile_id"]))
    repository = _repository_from_config(config)
    before = repository.guard()

    source_tip = repository.resolve_commit(str(config["source_ref"]))
    fork_tip = repository.resolve_commit(str(config["fork_ref"]))
    baseline, selection_mode = _selection_baseline(
        config, state, repository, source_tip, fork_tip
    )
    merge_base = repository.deterministic_merge_base(source_tip, fork_tip)
    selected = repository.selected_shas(baseline, source_tip)
    ordered = _extract_commit_records(
        repository, selected, source_tip, fork_tip
    )
    payload = _manifest_payload(
        config,
        source_tip,
        fork_tip,
        baseline,
        selection_mode,
        merge_base,
        ordered,
    )
    evidence_hash = sha256_value(payload)
    payload["run_id"] = f"run-{evidence_hash[:16]}"
    payload["manifest_sha256"] = sha256_value(payload)

    after = repository.guard()
    if after != before:
        raise ForensicIngestError(
            "Repository HEAD, refs, or worktree changed during analysis; no output written"
        )
    atomic_write_json(output_path, payload)
    return payload


def _hash_without(value: Mapping[str, Any], key: str) -> str:
    copy = dict(value)
    copy.pop(key, None)
    return sha256_value(copy)


def _validate_manifest_commit_shape(record: Any, index: int) -> None:
    prefix = f"Run manifest commit {index}"
    if not isinstance(record, dict):
        raise ForensicIngestError(f"{prefix} must be an object")

    sha_fields = ("sha", "tree_sha")
    for field in sha_fields:
        if not re.fullmatch(r"[0-9a-f]{40}", str(record.get(field, ""))):
            raise ForensicIngestError(f"{prefix}.{field} must be a full SHA")

    parents = record.get("parent_shas")
    if not isinstance(parents, list) or any(
        not isinstance(parent, str)
        or not re.fullmatch(r"[0-9a-f]{40}", parent)
        for parent in parents
    ):
        raise ForensicIngestError(f"{prefix}.parent_shas must be an array of SHAs")

    for field in ("author_timestamp", "committer_timestamp"):
        timestamp = record.get(field)
        if (
            not isinstance(timestamp, dict)
            or not isinstance(timestamp.get("unix_seconds"), int)
            or isinstance(timestamp.get("unix_seconds"), bool)
            or not isinstance(timestamp.get("timezone_offset"), str)
            or not re.fullmatch(
                r"[+-]\d{4}", timestamp.get("timezone_offset", "")
            )
        ):
            raise ForensicIngestError(f"{prefix}.{field} is invalid")

    if not isinstance(record.get("subject"), str):
        raise ForensicIngestError(f"{prefix}.subject must be a string")
    if not re.fullmatch(
        r"[0-9a-f]{64}", str(record.get("message_bytes_sha256", ""))
    ):
        raise ForensicIngestError(
            f"{prefix}.message_bytes_sha256 must be a SHA-256"
        )

    changed_files = record.get("changed_files")
    if not isinstance(changed_files, list):
        raise ForensicIngestError(f"{prefix}.changed_files must be an array")
    for changed_index, changed in enumerate(changed_files):
        changed_prefix = f"{prefix}.changed_files[{changed_index}]"
        if not isinstance(changed, dict):
            raise ForensicIngestError(f"{changed_prefix} must be an object")
        if not isinstance(changed.get("path"), str):
            raise ForensicIngestError(f"{changed_prefix}.path must be a string")
        old_path = changed.get("old_path")
        if old_path is not None and not isinstance(old_path, str):
            raise ForensicIngestError(
                f"{changed_prefix}.old_path must be null or a string"
            )
        if not isinstance(changed.get("status"), str) or not changed["status"]:
            raise ForensicIngestError(
                f"{changed_prefix}.status must be a non-empty string"
            )
        if not isinstance(changed.get("is_test"), bool):
            raise ForensicIngestError(f"{changed_prefix}.is_test must be boolean")

    for field in ("changed_paths", "test_paths"):
        paths = record.get(field)
        if not isinstance(paths, list) or any(
            not isinstance(path, str) for path in paths
        ):
            raise ForensicIngestError(
                f"{prefix}.{field} must be an array of strings"
            )

    patch_id = record.get("stable_patch_id")
    if patch_id is not None and not re.fullmatch(r"[0-9a-f]{40}", str(patch_id)):
        raise ForensicIngestError(
            f"{prefix}.stable_patch_id must be null or a full SHA"
        )

    integration = record.get("integration")
    integration_status = (
        integration.get("status") if isinstance(integration, dict) else None
    )
    if not isinstance(integration_status, str) or integration_status not in (
        "incorporated_exact",
        "incorporated_patch_equivalent",
        "unsynced",
    ):
        raise ForensicIngestError(f"{prefix}.integration status is invalid")
    fork_shas = integration.get("fork_commit_shas")
    if not isinstance(fork_shas, list) or any(
        not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha)
        for sha in fork_shas
    ):
        raise ForensicIngestError(
            f"{prefix}.integration.fork_commit_shas must be an array of SHAs"
        )

    topological_index = record.get("topological_index")
    if not isinstance(topological_index, int) or isinstance(
        topological_index, bool
    ):
        raise ForensicIngestError(f"{prefix}.topological_index must be an integer")


def _validate_manifest_shape(manifest: Mapping[str, Any]) -> None:
    for field in ("profile_id", "repository_identity", "run_id"):
        if not isinstance(manifest.get(field), str) or not manifest[field]:
            raise ForensicIngestError(
                f"Run manifest {field} must be a non-empty string"
            )
    for field in ("config_sha256", "manifest_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get(field, ""))):
            raise ForensicIngestError(f"Run manifest {field} must be a SHA-256")
    for field in ("source", "fork"):
        reference = manifest.get(field)
        if not isinstance(reference, dict):
            raise ForensicIngestError(f"Run manifest {field} must be an object")
        if not isinstance(reference.get("ref"), str) or not reference["ref"]:
            raise ForensicIngestError(
                f"Run manifest {field}.ref must be a non-empty string"
            )
        if not re.fullmatch(
            r"[0-9a-f]{40}",
            str(reference.get("tip_sha", "")),
        ):
            raise ForensicIngestError(
                f"Run manifest {field}.tip_sha must be a full SHA"
            )
    baseline = manifest.get("baseline_sha")
    if baseline is not None and not re.fullmatch(r"[0-9a-f]{40}", str(baseline)):
        raise ForensicIngestError(
            "Run manifest baseline_sha must be null or a full SHA"
        )
    selection_mode = manifest.get("selection_mode")
    if not isinstance(selection_mode, str) or selection_mode not in (
        "all-reachable",
        "after-initial-baseline",
        "after-incorporated-baseline",
    ):
        raise ForensicIngestError("Run manifest selection_mode is invalid")
    if not re.fullmatch(
        r"[0-9a-f]{40}",
        str(manifest.get("merge_base_sha", "")),
    ):
        raise ForensicIngestError("Run manifest merge_base_sha must be a full SHA")

    commits = manifest.get("commits")
    if not isinstance(commits, list):
        raise ForensicIngestError("Run manifest commits must be an array")
    for index, record in enumerate(commits):
        _validate_manifest_commit_shape(record, index)

    grouping = manifest.get("semantic_grouping")
    if not isinstance(grouping, dict):
        raise ForensicIngestError(
            "Run manifest semantic_grouping must be an object"
        )
    if not isinstance(grouping.get("strategy"), str):
        raise ForensicIngestError(
            "Run manifest semantic grouping strategy must be a string"
        )
    groups = grouping.get("groups")
    if not isinstance(groups, list):
        raise ForensicIngestError("Run manifest semantic groups must be an array")
    for index, group in enumerate(groups):
        prefix = f"Run manifest semantic group {index}"
        if not isinstance(group, dict):
            raise ForensicIngestError(f"{prefix} must be an object")
        for field in ("id", "label", "basis"):
            if not isinstance(group.get(field), str) or not group[field]:
                raise ForensicIngestError(
                    f"{prefix}.{field} must be a non-empty string"
                )
        commit_shas = group.get("commit_shas")
        if not isinstance(commit_shas, list) or any(
            not isinstance(sha, str)
            or not re.fullmatch(r"[0-9a-f]{40}", sha)
            for sha in commit_shas
        ):
            raise ForensicIngestError(
                f"{prefix}.commit_shas must be an array of full SHAs"
            )
        for field in ("changed_paths", "test_paths"):
            paths = group.get(field)
            if not isinstance(paths, list) or any(
                not isinstance(path, str) for path in paths
            ):
                raise ForensicIngestError(
                    f"{prefix}.{field} must be an array of strings"
                )


def _validate_manifest_snapshots(
    config: Mapping[str, Any],
    manifest: Mapping[str, Any],
    drafts: Optional[Mapping[str, Any]] = None,
    *,
    state: Optional[Mapping[str, Any]] = None,
    state_supplied: bool = False,
) -> dict[str, Any]:
    validate_config(config)
    if not _supported_schema_version(manifest.get("schema_version")):
        raise ForensicIngestError("Unsupported run manifest schema_version")
    if manifest.get("profile_id") != config["profile_id"]:
        raise ForensicIngestError("Manifest profile_id does not match configuration")
    if manifest.get("manifest_sha256") != _hash_without(
        manifest, "manifest_sha256"
    ):
        raise ForensicIngestError("Run manifest hash is invalid")
    _validate_manifest_shape(manifest)
    commits = manifest["commits"]
    shas = [record["sha"] for record in commits]
    if len(shas) != len(set(shas)):
        raise ForensicIngestError("Run manifest commit coverage is not unique")
    positions = {sha: index for index, sha in enumerate(shas)}
    for record in commits:
        if record.get("topological_index") != positions[record["sha"]]:
            raise ForensicIngestError("Run manifest topological indexes are invalid")
        for parent in record.get("parent_shas", []):
            if parent in positions and positions[parent] >= positions[record["sha"]]:
                raise ForensicIngestError("A manifest commit appears before its parent")
        changed = record.get("changed_files", [])
        expected_paths = sorted({item["path"] for item in changed})
        if record.get("changed_paths") != expected_paths:
            raise ForensicIngestError(
                f"Changed-path inventory is invalid for {record['sha']}"
            )
    repository = _repository_from_config(config)
    repository_guard = repository.guard()
    source_tip = repository.resolve_commit(str(config["source_ref"]))
    fork_tip = repository.resolve_commit(str(config["fork_ref"]))
    if manifest.get("config_sha256") != sha256_value(
        analysis_config_contract(config)
    ):
        raise ForensicIngestError("Run manifest configuration hash is invalid")
    if manifest.get("repository_identity") != config["repository_identity"]:
        raise ForensicIngestError("Run manifest repository identity is invalid")
    if manifest.get("source", {}).get("ref") != config["source_ref"]:
        raise ForensicIngestError("Run manifest source ref is invalid")
    if manifest.get("fork", {}).get("ref") != config["fork_ref"]:
        raise ForensicIngestError("Run manifest fork ref is invalid")
    if source_tip != manifest.get("source", {}).get("tip_sha"):
        raise ForensicIngestError("Configured source ref drifted after analysis")
    if fork_tip != manifest.get("fork", {}).get("tip_sha"):
        raise ForensicIngestError("Configured fork ref drifted after analysis")
    baseline_value = manifest.get("baseline_sha")
    baseline = str(baseline_value) if baseline_value is not None else None
    if baseline is not None and not repository.is_ancestor(baseline, source_tip):
        raise ForensicIngestError("Manifest baseline is rewritten or disconnected")
    selection_mode = str(manifest.get("selection_mode", ""))
    if state_supplied:
        state = state or {}
        validate_state(state, str(config["profile_id"]))
        already_verified = (
            state.get("last_verified_source_sha") == source_tip
            and state.get("last_verified_run_manifest_sha256")
            == manifest.get("manifest_sha256")
        )
        expected_baseline, expected_selection_mode = _selection_baseline(
            config, state, repository, source_tip, fork_tip
        )
        completed_incorporated_rerun = (
            already_verified
            and expected_baseline == source_tip
            and expected_selection_mode == "after-incorporated-baseline"
        )
        if not completed_incorporated_rerun:
            if (
                baseline != expected_baseline
                or selection_mode != expected_selection_mode
            ):
                raise ForensicIngestError(
                    "Run manifest baseline or selection mode differs from ingest state"
                )
    elif selection_mode == "after-incorporated-baseline":
        raise ForensicIngestError(
            "Ingest state is required to validate an incorporated baseline"
        )
    elif config.get("initial_selection", "after-baseline") == "all-reachable":
        if baseline is not None or selection_mode != "all-reachable":
            raise ForensicIngestError(
                "Run manifest baseline differs from all-reachable configuration"
            )
    elif (
        baseline != config.get("initial_baseline_sha")
        or selection_mode != "after-initial-baseline"
    ):
        raise ForensicIngestError(
            "Run manifest baseline differs from the configured initial baseline"
        )
    selected = repository.selected_shas(baseline, source_tip)
    if set(selected) != set(shas) or len(selected) != len(shas):
        raise ForensicIngestError("Run manifest coverage differs from the Git range")
    expected_records = _extract_commit_records(
        repository, selected, source_tip, fork_tip
    )
    if commits != expected_records:
        raise ForensicIngestError(
            "Run manifest commit, path, test, patch, or integration evidence "
            "differs from Git"
        )
    merge_base = repository.deterministic_merge_base(source_tip, fork_tip)
    expected_payload = _manifest_payload(
        config,
        source_tip,
        fork_tip,
        baseline,
        selection_mode,
        merge_base,
        expected_records,
    )
    actual_payload = dict(manifest)
    actual_payload.pop("run_id", None)
    actual_payload.pop("manifest_sha256", None)
    if actual_payload != expected_payload:
        raise ForensicIngestError(
            "Run manifest derived identity, grouping, or coverage differs from Git"
        )
    expected_run_id = f"run-{sha256_value(expected_payload)[:16]}"
    if manifest.get("run_id") != expected_run_id:
        raise ForensicIngestError("Run manifest run_id is not derived from its evidence")
    report = {
        "passed": True,
        "manifest_sha256": manifest["manifest_sha256"],
        "commit_count": len(shas),
        "complete_unique_coverage": True,
        "topological_order": True,
        "semantic_group_count": len(
            expected_payload["semantic_grouping"]["groups"]
        ),
        "source_and_fork_refs_unchanged": True,
        "baseline_connected": True,
    }
    if drafts is not None:
        report["drafts"] = validate_drafts(manifest, drafts)
    if repository.guard() != repository_guard:
        raise ForensicIngestError(
            "Repository HEAD, refs, or worktree changed during manifest validation"
        )
    return report


def validate_manifest(
    config_path: Path,
    manifest_path: Path,
    drafts_path: Optional[Path] = None,
    *,
    state_path: Optional[Path] = None,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    drafts = load_json(drafts_path) if drafts_path is not None else None
    state = (
        load_json(state_path, required=False)
        if state_path is not None
        else None
    )
    return _validate_manifest_snapshots(
        config,
        manifest,
        drafts,
        state=state,
        state_supplied=state_path is not None,
    )


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "root"


def _git_path_glob_matches(path: str, pattern: str) -> bool:
    path_parts = PurePosixPath(path).parts
    pattern_parts = PurePosixPath(pattern).parts
    memo: dict[tuple[int, int], bool] = {}

    def matches(path_index: int, pattern_index: int) -> bool:
        key = (path_index, pattern_index)
        if key in memo:
            return memo[key]
        if pattern_index == len(pattern_parts):
            result = path_index == len(path_parts)
        elif pattern_parts[pattern_index] == "**":
            result = matches(path_index, pattern_index + 1) or (
                path_index < len(path_parts)
                and matches(path_index + 1, pattern_index)
            )
        else:
            result = (
                path_index < len(path_parts)
                and fnmatch.fnmatchcase(
                    path_parts[path_index],
                    pattern_parts[pattern_index],
                )
                and matches(path_index + 1, pattern_index + 1)
            )
        memo[key] = result
        return result

    return matches(0, 0)


def _escape_control_literals(value: Any) -> str:
    return (
        str(value)
        .replace("{{issue:", "&#123;&#123;issue:")
        .replace(
            "<!-- forensic-ingest-id:",
            "&lt;!-- forensic-ingest-id:",
        )
    )


def _printable_git_text(value: Any) -> str:
    decoded = (
        str(value)
        .encode("utf-8", errors="surrogateescape")
        .decode("utf-8", errors="backslashreplace")
    )
    rendered = []
    for character in decoded:
        codepoint = ord(character)
        if unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}:
            rendered.append(
                f"\\x{codepoint:02x}"
                if codepoint <= 0xFF
                else f"\\u{codepoint:04x}"
            )
        else:
            rendered.append(character)
    return "".join(rendered)


MARKDOWN_ACTIVE_CHARACTERS = frozenset("\\`*_{}[]()<>#+!|~&@:.")


def _rendered_git_text(value: Any) -> str:
    """Plain-text Markdown context: every active character becomes an entity."""
    text = _printable_git_text(value)
    return "".join(
        f"&#{ord(character)};" if character in MARKDOWN_ACTIVE_CHARACTERS else character
        for character in text
    ).replace("\r", " ").replace("\n", " ")


def _rendered_git_code(value: Any) -> str:
    """Code-span context: a fence longer than any backtick run inside the value."""
    text = _escape_control_literals(_printable_git_text(value)).replace("@", "&#64;")
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    padding = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{padding}{text}{padding}{fence}"


def _rendered_git_title(value: Any) -> str:
    """Issue titles are plain text; keep them readable but control-free."""
    return _printable_git_text(value).replace("`", "'").replace("@", "&#64;")


def _is_valid_label(label: Any) -> bool:
    return (
        isinstance(label, str)
        and bool(label.strip())
        and label == label.strip()
        and len(label) <= 50
        and "," not in label
        and not any(
            unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
            for character in label
        )
    )


def _deduplicate_labels(labels: Iterable[str]) -> list[str]:
    result = []
    seen = set()
    for label in labels:
        normalized = label.casefold()
        if normalized not in seen:
            seen.add(normalized)
            result.append(label)
    return sorted(result, key=lambda label: (label.casefold(), label))


def _commit_inventory(records: Iterable[Mapping[str, Any]]) -> str:
    lines = []
    for record in records:
        status = record["integration"]["status"]
        subject = _rendered_git_text(record["subject"]).strip()
        lines.append(f"- `{record['sha']}` — **{status}** — {subject}")
    text = "\n".join(lines) if lines else "- No commits selected."
    if len(text.encode("utf-8")) <= 42_000:
        return text
    retained = []
    size = 0
    for line in lines:
        encoded = len((line + "\n").encode("utf-8"))
        if size + encoded > 40_000:
            break
        retained.append(line)
        size += encoded
    retained.append(
        "- Inventory truncated to preserve the GitHub body limit; the run manifest "
        "contains the complete exact commit list."
    )
    return "\n".join(retained)


def _semantic_group_inventory(
    groups: Iterable[Mapping[str, Any]],
    records: Iterable[Mapping[str, Any]],
) -> str:
    records_by_sha = {record["sha"]: record for record in records}
    lines: list[str] = []
    size = 0
    truncated = False
    for group in groups:
        heading = f"### {_rendered_git_code(group['label'])}"
        for line in (heading, ""):
            encoded = len((line + "\n").encode("utf-8"))
            if size + encoded > 40_000:
                truncated = True
                break
            lines.append(line)
            size += encoded
        if truncated:
            break
        for sha in group["commit_shas"]:
            record = records_by_sha.get(sha)
            if record is None:
                raise ForensicIngestError(
                    f"Semantic group references an unknown commit: {sha}"
                )
            status = record["integration"]["status"]
            subject = _rendered_git_text(record["subject"]).strip()
            line = f"- `{sha}` — **{status}** — {subject}"
            encoded = len((line + "\n").encode("utf-8"))
            if size + encoded > 40_000:
                truncated = True
                break
            lines.append(line)
            size += encoded
        if truncated:
            break
        lines.append("")
        size += 1
    if truncated:
        lines.append(
            "- Inventory truncated to preserve the GitHub body limit; the run "
            "manifest contains every semantic group and exact commit assignment."
        )
    text = "\n".join(lines).strip()
    return text or "- No semantic groups recorded."


def _changed_path_inventory(paths: Iterable[str]) -> str:
    lines = [
        f"- {_rendered_git_code(path)}"
        for path in sorted(set(paths))
    ]
    retained: list[str] = []
    size = 0
    for line in lines:
        encoded = len((line + "\n").encode("utf-8"))
        if size + encoded > 12_000:
            break
        retained.append(line)
        size += encoded
    if len(retained) != len(lines):
        retained.append(
            "- Path inventory truncated to preserve the GitHub body limit; the "
            "run manifest contains every changed path."
        )
    return "\n".join(retained) if retained else "- No path changes recorded."


def _limited_title(value: str) -> str:
    return value if len(value) <= 240 else value[:237] + "..."


def _load_template(name: str) -> Template:
    path = Path(__file__).resolve().parent.parent / "templates" / name
    return Template(path.read_text(encoding="utf-8"))


def _historical_group_chunks(
    semantic_groups: list[Mapping[str, Any]],
) -> list[list[Mapping[str, Any]]]:
    return [
        semantic_groups[index : index + MAX_SUB_ISSUES_PER_PARENT]
        for index in range(0, len(semantic_groups), MAX_SUB_ISSUES_PER_PARENT)
    ]


def _historical_parent_id(
    profile: str,
    run_id: str,
    part_index: int,
    part_count: int,
) -> str:
    base = f"{profile}:{run_id}:history"
    if part_count == 1:
        return base
    return f"{base}:part-{part_index:03d}-of-{part_count:03d}"


def render_drafts(manifest_path: Path, output_path: Path) -> dict[str, Any]:
    manifest_path = _canonical_path(manifest_path)
    output_path = _canonical_path(output_path)
    _reject_write_aliases(
        "Draft output",
        output_path,
        (("run manifest", manifest_path),),
    )
    manifest = load_json(manifest_path)
    if not _supported_schema_version(manifest.get("schema_version")):
        raise ForensicIngestError("Unsupported run manifest schema_version")
    if manifest.get("manifest_sha256") != _hash_without(
        manifest, "manifest_sha256"
    ):
        raise ForensicIngestError("Run manifest hash is invalid")
    _validate_manifest_shape(manifest)
    commits = manifest["commits"]
    profile = manifest["profile_id"]
    run_id = manifest["run_id"]
    semantic_groups = manifest["semantic_grouping"]["groups"]
    labels = ["agentic-agile", "forensic-ingest"]
    issues: list[dict[str, Any]] = []
    if commits:
        unsynced = [
            item for item in commits if item["integration"]["status"] == "unsynced"
        ]
        if unsynced:
            logical_id = f"{profile}:{run_id}:decision"
            marker = f"<!-- forensic-ingest-id:{logical_id} -->"
            body = _load_template("upstream-decision.md").substitute(
                marker=marker,
                profile_id=profile,
                baseline_sha=manifest["baseline_sha"] or "(all reachable history)",
                source_tip=manifest["source"]["tip_sha"],
                fork_tip=manifest["fork"]["tip_sha"],
                manifest_sha256=manifest["manifest_sha256"],
                commit_count=len(commits),
                unsynced_count=len(unsynced),
                semantic_group_count=len(semantic_groups),
                semantic_group_inventory=_semantic_group_inventory(
                    semantic_groups, commits
                ),
            )
            issues.append(
                {
                    "logical_id": logical_id,
                    "title": _limited_title(f"Review upstream delta {run_id}"),
                    "body": body,
                    "state": "open",
                    "labels": labels + ["upstream-delta"],
                    "commit_shas": [item["sha"] for item in commits],
                    "semantic_group_ids": [
                        group["id"] for group in semantic_groups
                    ],
                    "dependencies": [],
                }
            )
        else:
            records_by_sha = {record["sha"]: record for record in commits}
            group_chunks = _historical_group_chunks(semantic_groups)
            part_count = len(group_chunks)
            for part_index, group_chunk in enumerate(group_chunks, start=1):
                parent_id = _historical_parent_id(
                    profile,
                    run_id,
                    part_index,
                    part_count,
                )
                marker = f"<!-- forensic-ingest-id:{parent_id} -->"
                chunk_commit_count = sum(
                    len(group["commit_shas"]) for group in group_chunk
                )
                parent_body = _load_template("historical-epic.md").substitute(
                    marker=marker,
                    profile_id=profile,
                    baseline_sha=(
                        manifest["baseline_sha"] or "(all reachable history)"
                    ),
                    source_tip=manifest["source"]["tip_sha"],
                    fork_tip=manifest["fork"]["tip_sha"],
                    manifest_sha256=manifest["manifest_sha256"],
                    commit_count=chunk_commit_count,
                )
                parent_title = f"[Historical] Incorporated source work {run_id}"
                if part_count > 1:
                    parent_title += f" (part {part_index}/{part_count})"
                issues.append(
                    {
                        "logical_id": parent_id,
                        "title": _limited_title(parent_title),
                        "body": parent_body,
                        "state": "closed",
                        "labels": labels + ["historical-backfill", "type:epic"],
                        "commit_shas": [],
                        "semantic_group_ids": [
                            group["id"] for group in group_chunk
                        ],
                        "dependencies": [],
                    }
                )
                for group in group_chunk:
                    rendered_area = _rendered_git_code(group["label"])
                    area_title = _rendered_git_title(group["label"])
                    records = []
                    for sha in group["commit_shas"]:
                        record = records_by_sha.get(sha)
                        if record is None:
                            raise ForensicIngestError(
                                "Semantic group references an unknown commit: "
                                f"{sha}"
                            )
                        records.append(record)
                    child_id = f"{profile}:{run_id}:group:{group['id']}"
                    child_marker = f"<!-- forensic-ingest-id:{child_id} -->"
                    path_text = _changed_path_inventory(group["changed_paths"])
                    body = _load_template("historical-story.md").substitute(
                        marker=child_marker,
                        area=rendered_area,
                        parent_id=parent_id,
                        commit_inventory=_commit_inventory(records),
                        changed_paths=path_text,
                    )
                    issues.append(
                        {
                            "logical_id": child_id,
                            "parent_id": parent_id,
                            "title": _limited_title(
                                "[Historical] Incorporated source area: "
                                f"{area_title}"
                            ),
                            "body": body,
                            "state": "closed",
                            "labels": labels
                            + ["historical-backfill", "type:story"],
                            "commit_shas": [item["sha"] for item in records],
                            "semantic_group_ids": [group["id"]],
                            "dependencies": [],
                        }
                    )
    for issue in issues:
        if len(issue["body"].encode("utf-8")) > MAX_BODY_BYTES:
            raise ForensicIngestError(
                f"Rendered issue exceeds the safe body limit: {issue['logical_id']}"
            )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "agentic-agile-forensic-ingest-drafts",
        "profile_id": profile,
        "run_id": run_id,
        "run_manifest_sha256": manifest["manifest_sha256"],
        "source_tip_sha": manifest["source"]["tip_sha"],
        "semantic_grouping": manifest["semantic_grouping"],
        "all_commits_incorporated": all(
            item["integration"]["status"] != "unsynced" for item in commits
        ),
        "issues": issues,
    }
    payload["drafts_sha256"] = sha256_value(payload)
    validate_drafts(manifest, payload)
    atomic_write_json(output_path, payload)
    return payload


def _issue_dependencies(issue: Mapping[str, Any]) -> set[str]:
    dependencies = set(issue.get("dependencies", []))
    if issue.get("parent_id"):
        dependencies.add(str(issue["parent_id"]))
    body_references = set(
        ISSUE_REFERENCE_PATTERN.findall(str(issue.get("body", "")))
    )
    undeclared = body_references - dependencies
    if undeclared:
        raise ForensicIngestError(
            f"Draft body contains undeclared issue references: {sorted(undeclared)}"
        )
    return dependencies


def _validate_draft_issue_shape(issue: Any, index: int) -> None:
    prefix = f"Draft issue {index}"
    if not isinstance(issue, dict):
        raise ForensicIngestError(f"{prefix} must be an object")
    identifier = issue.get("logical_id")
    if not isinstance(identifier, str) or not identifier:
        raise ForensicIngestError(f"{prefix} requires a non-empty logical_id")
    title = issue.get("title")
    if not isinstance(title, str) or not title or len(title) > 240:
        raise ForensicIngestError(
            f"{prefix}.title must be a non-empty string of at most 240 characters"
        )
    if not isinstance(issue.get("body"), str):
        raise ForensicIngestError(f"{prefix}.body must be a string")
    if not isinstance(issue.get("state"), str) or issue.get("state") not in (
        "open",
        "closed",
    ):
        raise ForensicIngestError(f"{prefix}.state must be open or closed")
    labels = issue.get("labels")
    if not isinstance(labels, list) or not all(
        _is_valid_label(label) for label in labels
    ):
        raise ForensicIngestError(
            f"{prefix}.labels must be non-empty strings of at most 50 "
            "characters without commas, control characters, or surrounding "
            "whitespace"
        )
    commit_shas = issue.get("commit_shas")
    if not isinstance(commit_shas, list) or any(
        not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha)
        for sha in commit_shas
    ):
        raise ForensicIngestError(
            f"{prefix}.commit_shas must be an array of full SHAs"
        )
    for field in ("semantic_group_ids", "dependencies"):
        values = issue.get(field)
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values
        ):
            raise ForensicIngestError(
                f"{prefix}.{field} must be an array of non-empty strings"
            )
    parent_id = issue.get("parent_id")
    if parent_id is not None and (
        not isinstance(parent_id, str) or not parent_id
    ):
        raise ForensicIngestError(
            f"{prefix}.parent_id must be null or a non-empty string"
        )


def dependency_order(
    issues: list[dict[str, Any]], existing_ids: Optional[set[str]] = None
) -> list[str]:
    existing = set(existing_ids or set())
    identifiers = []
    for index, issue in enumerate(issues):
        _validate_draft_issue_shape(issue, index)
        identifier = issue["logical_id"]
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise ForensicIngestError("Draft logical IDs must be unique")
    identifier_set = set(identifiers)
    graph: dict[str, set[str]] = {}
    for issue in issues:
        identifier = str(issue["logical_id"])
        dependencies = _issue_dependencies(issue)
        unknown = dependencies - identifier_set - existing
        if unknown:
            raise ForensicIngestError(
                f"Unknown issue references for {identifier}: {sorted(unknown)}"
            )
        graph[identifier] = dependencies & identifier_set
    ready = set(existing)
    ordered: list[str] = []
    while graph:
        available = sorted(
            identifier
            for identifier, dependencies in graph.items()
            if dependencies <= ready
        )
        if not available:
            raise ForensicIngestError(
                f"Draft dependency cycle: {sorted(graph.keys())}"
            )
        for identifier in available:
            ordered.append(identifier)
            ready.add(identifier)
            del graph[identifier]
    return ordered


def validate_drafts(
    manifest: Mapping[str, Any], drafts: Mapping[str, Any]
) -> dict[str, Any]:
    if not _supported_schema_version(drafts.get("schema_version")):
        raise ForensicIngestError("Unsupported drafts schema_version")
    if drafts.get("run_manifest_sha256") != manifest.get("manifest_sha256"):
        raise ForensicIngestError("Drafts do not reference the run manifest")
    if drafts.get("profile_id") != manifest.get("profile_id"):
        raise ForensicIngestError("Drafts profile_id does not match the run manifest")
    if drafts.get("run_id") != manifest.get("run_id"):
        raise ForensicIngestError("Drafts run_id does not match the run manifest")
    if drafts.get("source_tip_sha") != manifest.get("source", {}).get("tip_sha"):
        raise ForensicIngestError("Drafts source tip does not match the run manifest")
    if drafts.get("semantic_grouping") != manifest.get("semantic_grouping"):
        raise ForensicIngestError(
            "Draft semantic grouping does not match the run manifest"
        )
    if drafts.get("drafts_sha256") != _hash_without(drafts, "drafts_sha256"):
        raise ForensicIngestError("Drafts hash is invalid")
    issues = drafts.get("issues")
    if not isinstance(issues, list):
        raise ForensicIngestError("Draft issues must be an array")
    order = dependency_order(issues)
    expected = [record["sha"] for record in manifest.get("commits", [])]
    assigned = [
        sha for issue in issues for sha in issue.get("commit_shas", [])
    ]
    if len(assigned) != len(set(assigned)):
        raise ForensicIngestError("Draft commit attribution contains duplicates")
    if set(assigned) != set(expected) or len(assigned) != len(expected):
        raise ForensicIngestError("Draft commit attribution is incomplete or foreign")
    expected_incorporated = all(
        record["integration"]["status"] != "unsynced"
        for record in manifest.get("commits", [])
    )
    if drafts.get("all_commits_incorporated") is not expected_incorporated:
        raise ForensicIngestError(
            "Draft incorporation state does not match the run manifest"
        )
    semantic_groups = manifest.get("semantic_grouping", {}).get("groups", [])
    semantic_group_ids = [group["id"] for group in semantic_groups]
    if len(semantic_group_ids) != len(set(semantic_group_ids)):
        raise ForensicIngestError("Manifest semantic group IDs are not unique")
    grouped_shas = [
        sha for group in semantic_groups for sha in group["commit_shas"]
    ]
    if (
        set(grouped_shas) != set(expected)
        or len(grouped_shas) != len(expected)
        or len(grouped_shas) != len(set(grouped_shas))
    ):
        raise ForensicIngestError(
            "Manifest semantic groups do not uniquely cover every commit"
        )
    positions = {sha: index for index, sha in enumerate(expected)}
    for group in semantic_groups:
        group_positions = [positions[sha] for sha in group["commit_shas"]]
        if group_positions != sorted(group_positions):
            raise ForensicIngestError(
                "Manifest semantic group commit order is not topological"
            )
    known_group_ids = set(semantic_group_ids)
    for issue in issues:
        identifier = str(issue["logical_id"])
        expected_marker = f"<!-- forensic-ingest-id:{identifier} -->"
        body = issue["body"]
        if (
            not body.startswith(expected_marker)
            or MARKER_PATTERN.findall(body) != [identifier]
        ):
            raise ForensicIngestError(
                f"Draft requires exactly one matching marker: {identifier}"
            )
        if not isinstance(issue.get("state"), str) or issue.get("state") not in (
            "open",
            "closed",
        ):
            raise ForensicIngestError(f"Invalid draft state: {identifier}")
        issue_group_ids = issue.get("semantic_group_ids", [])
        if (
            not isinstance(issue_group_ids, list)
            or len(issue_group_ids) != len(set(issue_group_ids))
            or not set(issue_group_ids) <= known_group_ids
        ):
            raise ForensicIngestError(
                f"Invalid draft semantic groups: {identifier}"
            )
        if len(str(issue.get("body", "")).encode("utf-8")) > MAX_BODY_BYTES:
            raise ForensicIngestError(f"Draft body exceeds safe size: {identifier}")
    profile = str(manifest["profile_id"])
    run_id = str(manifest["run_id"])
    if expected and not expected_incorporated:
        expected_id = f"{profile}:{run_id}:decision"
        if len(issues) != 1 or issues[0].get("logical_id") != expected_id:
            raise ForensicIngestError(
                "Unsynced drafts must contain one stable decision record"
            )
        decision = issues[0]
        if (
            decision.get("state") != "open"
            or decision.get("parent_id") is not None
            or decision.get("commit_shas") != expected
            or decision.get("semantic_group_ids") != semantic_group_ids
        ):
            raise ForensicIngestError(
                "Unsynced decision lifecycle or attribution is invalid"
            )
    elif expected:
        expected_issues: dict[str, tuple[list[str], list[str], Optional[str]]] = {}
        group_chunks = _historical_group_chunks(semantic_groups)
        part_count = len(group_chunks)
        for part_index, group_chunk in enumerate(group_chunks, start=1):
            parent_id = _historical_parent_id(
                profile,
                run_id,
                part_index,
                part_count,
            )
            expected_issues[parent_id] = (
                [],
                [group["id"] for group in group_chunk],
                None,
            )
            for group in group_chunk:
                child_id = f"{profile}:{run_id}:group:{group['id']}"
                expected_issues[child_id] = (
                    group["commit_shas"],
                    [group["id"]],
                    parent_id,
                )
        if {issue["logical_id"] for issue in issues} != set(expected_issues):
            raise ForensicIngestError(
                "Incorporated drafts do not match deterministic semantic groups"
            )
        for issue in issues:
            commit_shas, group_ids, expected_parent = expected_issues[
                issue["logical_id"]
            ]
            if (
                issue.get("state") != "closed"
                or issue.get("commit_shas") != commit_shas
                or issue.get("semantic_group_ids") != group_ids
                or issue.get("parent_id") != expected_parent
            ):
                raise ForensicIngestError(
                    "Incorporated draft lifecycle or attribution is invalid"
                )
    elif issues:
        raise ForensicIngestError("An empty run must not render issue drafts")
    return {
        "passed": True,
        "issue_count": len(issues),
        "commit_count": len(expected),
        "complete_unique_coverage": True,
        "semantic_group_count": len(semantic_groups),
        "dependency_order": order,
    }


def resolve_issue_references(
    body: str,
    publication: Mapping[str, Any],
    allowed_references: set[str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        identifier = match.group(1)
        if identifier not in allowed_references:
            raise ForensicIngestError(
                f"Undeclared issue reference in rendered body: {identifier}"
            )
        if identifier not in publication:
            raise ForensicIngestError(f"Unresolved issue reference: {identifier}")
        return f"#{publication[identifier]['number']}"

    return ISSUE_REFERENCE_PATTERN.sub(replace, body)


class GitHubClient:
    """Minimal GitHub CLI client used only by publish-github."""

    def __init__(
        self,
        repository: str,
        *,
        hostname: str = "github.com",
        sleep: Callable[[float], None] = time.sleep,
    ):
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or any(part in {".", ".."} for part in repository.split("/"))
        ):
            raise ForensicIngestError("GitHub repository must be owner/name")
        if not re.fullmatch(
            r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?",
            hostname,
        ) or ".." in hostname:
            raise ForensicIngestError("GitHub hostname must be a lowercase DNS name")
        self.repository = repository
        self.hostname = hostname
        self.sleep = sleep
        self.last_write = 0.0
        self.environment = dict(os.environ)
        self.environment.pop("GH_HOST", None)
        self.environment.update(
            GH_PAGER="cat",
            GH_PROMPT_DISABLED="1",
        )

    def api(
        self,
        endpoint: str,
        payload: Optional[dict[str, Any]] = None,
        method: Optional[str] = None,
    ) -> Any:
        prefix = f"repos/{self.repository}/"
        if not endpoint.startswith(prefix):
            raise ForensicIngestError(
                "GitHub publication target is outside the configured repository"
            )
        arguments = [
            "gh",
            "api",
            "--hostname",
            self.hostname,
            endpoint,
        ]
        if payload is not None:
            arguments += ["--method", method or "POST", "--input", "-"]
        elif method:
            arguments += ["--method", method]
        for attempt in range(7):
            if payload is not None:
                delay = max(0.0, 2.0 - (time.monotonic() - self.last_write))
                if delay:
                    self.sleep(delay)
                self.last_write = time.monotonic()
            try:
                result = subprocess.run(
                    arguments,
                    env=self.environment,
                    input=(
                        json.dumps(payload, ensure_ascii=True)
                        if payload is not None
                        else None
                    ),
                    text=True,
                    encoding="utf-8",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=180,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise ForensicIngestError(
                    f"GitHub CLI execution failed: {redact(exc)}"
                ) from exc
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else None
            diagnostic = redact(result.stderr)
            throttled = re.search(
                r"(?i)(secondary rate limit|rate limit exceeded|HTTP 429|abuse detection)",
                diagnostic,
            )
            if not throttled or attempt == 6:
                raise ForensicIngestError(
                    f"GitHub API failed for {endpoint}: {diagnostic}"
                )
            self.sleep(min(300, 30 * (2**attempt)))
        raise AssertionError("Unreachable GitHub retry state")

    def list_all(self, resource: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, MAX_GITHUB_PAGES + 1):
            separator = "&" if "?" in resource else "?"
            batch = self.api(
                f"repos/{self.repository}/{resource}{separator}per_page=100&page={page}"
            )
            if not isinstance(batch, list):
                raise ForensicIngestError(
                    f"Expected a GitHub list response: {resource}"
                )
            items.extend(batch)
            if len(batch) < 100:
                return items
        raise ForensicIngestError(
            f"GitHub pagination exceeded {MAX_GITHUB_PAGES} pages: {resource}"
        )


def _discover_markers(
    remote_issues: Iterable[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    markers: dict[str, Mapping[str, Any]] = {}
    for issue in remote_issues:
        if "pull_request" in issue:
            continue
        for match in MARKER_PATTERN.finditer(str(issue.get("body") or "")):
            identifier = match.group(1)
            if identifier in markers:
                raise DuplicateMarkerError(
                    f"Duplicate remote marker: {identifier}"
                )
            markers[identifier] = issue
    return markers


def _validate_publication_state_issues(
    publication: Mapping[str, Any],
    expected_issue_ids: set[str],
) -> None:
    issues = publication.get("issues")
    if not isinstance(issues, dict):
        raise ForensicIngestError(
            "Publication state issues must be an object"
        )
    unknown = set(issues) - expected_issue_ids
    if unknown:
        raise ForensicIngestError(
            f"Publication state contains unknown issue identifiers: {sorted(unknown)}"
        )
    for identifier, entry in issues.items():
        if not isinstance(identifier, str) or not identifier:
            raise ForensicIngestError(
                "Publication state issue identifiers must be non-empty strings"
            )
        if not isinstance(entry, dict):
            raise ForensicIngestError(
                f"Publication state issue entry must be an object: {identifier}"
            )
        for field in ("number", "id"):
            value = entry.get(field)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
            ):
                raise ForensicIngestError(
                    f"Publication state issue {field} is invalid: {identifier}"
                )
        html_url = entry.get("html_url")
        if html_url is not None and not isinstance(html_url, str):
            raise ForensicIngestError(
                f"Publication state issue html_url is invalid: {identifier}"
            )
        for field in ("parent_linked", "closed", "publisher_created"):
            if not isinstance(entry.get(field), bool):
                raise ForensicIngestError(
                    f"Publication state issue {field} is invalid: {identifier}"
                )


def _validate_creation_intents(
    publication: Mapping[str, Any],
    expected_issue_ids: set[str],
) -> None:
    intents = publication.get("creation_intents", {})
    if not isinstance(intents, dict):
        raise ForensicIngestError(
            "Publication state creation_intents must be an object"
        )
    unknown = set(intents) - expected_issue_ids
    if unknown:
        raise ForensicIngestError(
            "Publication state contains unknown creation intents: "
            f"{sorted(unknown)}"
        )
    for identifier, intent_sha256 in intents.items():
        if (
            not isinstance(identifier, str)
            or not identifier
            or not isinstance(intent_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", intent_sha256)
        ):
            raise ForensicIngestError(
                f"Publication state creation intent is invalid: {identifier}"
            )


def _creation_intent_sha256(
    expected: Mapping[str, Any],
    resolved_body: str,
) -> str:
    return sha256_value(
        {
            "logical_id": expected["logical_id"],
            "title": expected["title"],
            "body": resolved_body,
            "labels": expected["labels"],
        }
    )


def _remote_matches(
    expected: Mapping[str, Any],
    remote: Mapping[str, Any],
    resolved_body: str,
    *,
    allow_pending_close: bool = False,
) -> Optional[str]:
    if remote.get("title") != expected.get("title"):
        return "title"
    if remote.get("body") != resolved_body:
        return "body"
    if allow_pending_close and expected.get("state") == "closed":
        if remote.get("state") not in ("open", "closed"):
            return "state"
        if (
            remote.get("state") == "closed"
            and remote.get("state_reason") != "completed"
        ):
            return "closure reason"
    else:
        if remote.get("state") != expected.get("state"):
            return "state"
        if (
            expected.get("state") == "closed"
            and remote.get("state_reason") != "completed"
        ):
            return "closure reason"
    remote_labels = {
        (
            label["name"] if isinstance(label, dict) else str(label)
        ).casefold()
        for label in remote.get("labels", [])
    }
    expected_labels = {
        str(label).casefold()
        for label in expected.get("labels", [])
    }
    if not expected_labels <= remote_labels:
        return "labels"
    return None


def verify_github_publication(
    drafts: Mapping[str, Any],
    publication: Mapping[str, Any],
    client: GitHubClient,
) -> dict[str, Any]:
    remote_list = [
        issue
        for issue in client.list_all("issues?state=all")
        if "pull_request" not in issue
    ]
    _discover_markers(remote_list)
    remote_by_number = {int(issue["number"]): issue for issue in remote_list}
    failures: list[str] = []
    issue_map = publication.get("issues", {})
    for expected in drafts.get("issues", []):
        identifier = expected["logical_id"]
        entry = issue_map.get(identifier)
        if not entry:
            failures.append(f"Missing publication state: {identifier}")
            continue
        remote = remote_by_number.get(int(entry["number"]))
        if remote is None:
            failures.append(f"Missing remote issue: {identifier}")
            continue
        if remote.get("id") != entry.get("id"):
            failures.append(f"Remote database ID mismatch: {identifier}")
            continue
        body = resolve_issue_references(
            expected["body"],
            issue_map,
            _issue_dependencies(expected),
        )
        mismatch = _remote_matches(expected, remote, body)
        if mismatch:
            failures.append(f"Remote {mismatch} mismatch: {identifier}")
    parent_ids = {
        issue["parent_id"]
        for issue in drafts.get("issues", [])
        if issue.get("parent_id")
    }
    for parent_id in sorted(parent_ids):
        parent = issue_map[parent_id]
        children = client.list_all(f"issues/{parent['number']}/sub_issues")
        actual = {int(child["id"]) for child in children}
        expected_ids = {
            int(issue_map[issue["logical_id"]]["id"])
            for issue in drafts["issues"]
            if issue.get("parent_id") == parent_id
        }
        if not expected_ids <= actual:
            failures.append(f"Native sub-issue hierarchy mismatch: {parent_id}")
    report = {
        "passed": not failures,
        "issue_count": len(drafts.get("issues", [])),
        "failures": failures,
    }
    if failures:
        raise ForensicIngestError(
            "Remote publication verification failed: " + "; ".join(failures)
        )
    return report


def _load_publication_state(
    publication_state_path: Path,
    github: Mapping[str, Any],
    drafts: Mapping[str, Any],
) -> dict[str, Any]:
    repository_name = str(github["repository"])
    hostname = str(github.get("hostname", "github.com"))
    publication = load_json(publication_state_path, required=False)
    publication_contract_sha256 = sha256_value(
        {
            "target_hostname": hostname,
            "target_repository": repository_name,
            "labels": sorted(
                label.casefold() for label in github.get("labels", [])
            ),
        }
    )
    if publication:
        if not _supported_schema_version(publication.get("schema_version")):
            raise ForensicIngestError("Unsupported publication-state schema_version")
        if publication.get("target_repository") != repository_name:
            raise ForensicIngestError("Publication state targets another repository")
        if publication.get("target_hostname") != hostname:
            raise ForensicIngestError("Publication state targets another GitHub host")
        if publication.get("drafts_sha256") != drafts["drafts_sha256"]:
            raise ForensicIngestError(
                "Publication state belongs to different drafts"
            )
        if (
            publication.get("publication_contract_sha256")
            != publication_contract_sha256
        ):
            raise ForensicIngestError(
                "Publication state belongs to different GitHub settings"
            )
        issue_ids = {issue["logical_id"] for issue in drafts["issues"]}
        _validate_publication_state_issues(publication, issue_ids)
        _validate_creation_intents(publication, issue_ids)
        publication.setdefault("creation_intents", {})
        return publication
    return {
        "schema_version": SCHEMA_VERSION,
        "target_hostname": hostname,
        "target_repository": repository_name,
        "drafts_sha256": drafts["drafts_sha256"],
        "publication_contract_sha256": publication_contract_sha256,
        "issues": {},
        "creation_intents": {},
        "remote_verification": None,
    }


def _publish_github_locked(
    config_path: Path,
    manifest_path: Path,
    drafts_path: Path,
    ingest_state_path: Path,
    publication_state_path: Path,
    *,
    client: Optional[GitHubClient] = None,
    expected_target_key: Optional[str] = None,
) -> dict[str, Any]:
    captured_ingest_state = load_json(ingest_state_path, required=False)
    captured_ingest_state_sha256 = sha256_value(captured_ingest_state)
    config = load_json(config_path)
    if (
        expected_target_key is not None
        and publication_target_key(config) != expected_target_key
    ):
        raise ForensicIngestError(
            "Configuration publication target changed while acquiring locks"
        )
    manifest = load_json(manifest_path)
    drafts = load_json(drafts_path)
    manifest_validation = _validate_manifest_snapshots(
        config,
        manifest,
        drafts,
        state=captured_ingest_state,
        state_supplied=True,
    )
    source_tip_sha = str(manifest["source"]["tip_sha"])
    all_commits_incorporated = all(
        record["integration"]["status"] != "unsynced"
        for record in manifest["commits"]
    )
    github = config.get("github")
    if not isinstance(github, dict) or not github.get("repository"):
        raise ForensicIngestError(
            "Configuration github.repository is required for publication"
        )
    repository_name = str(github["repository"])
    hostname = str(github.get("hostname", "github.com"))
    issues = drafts["issues"]
    order = dependency_order(issues)
    issue_by_id = {issue["logical_id"]: issue for issue in issues}
    configured_labels = list(github.get("labels", []))
    for issue in issues:
        issue["labels"] = _deduplicate_labels(
            issue.get("labels", []) + configured_labels
        )
        if len(issue["labels"]) > MAX_LABELS_PER_ISSUE:
            raise ForensicIngestError(
                f"Draft issue exceeds {MAX_LABELS_PER_ISSUE} labels: "
                f"{issue['logical_id']}"
            )

    publication = _load_publication_state(publication_state_path, github, drafts)
    api = client or GitHubClient(repository_name, hostname=hostname)
    if (
        getattr(api, "repository", None) != repository_name
        or getattr(api, "hostname", None) != hostname
    ):
        raise ForensicIngestError(
            "GitHub client target does not match configured publication target"
        )

    remote_issues = api.list_all("issues?state=all")
    by_marker = _discover_markers(remote_issues)
    publication_issues = publication["issues"]
    creation_intents = publication["creation_intents"]
    for identifier, remote in by_marker.items():
        if identifier in issue_by_id and identifier not in publication_issues:
            publication_issues[identifier] = {
                "number": remote["number"],
                "id": remote["id"],
                "html_url": remote.get("html_url"),
                "parent_linked": False,
                "closed": remote.get("state") == "closed",
                "publisher_created": identifier in creation_intents,
            }
    unresolved_intents = sorted(
        identifier for identifier in creation_intents
        if identifier not in by_marker
    )
    intent_sleep = getattr(api, "sleep", time.sleep)
    for identifier in unresolved_intents:
        remote = None
        for attempt in range(5):
            if attempt:
                intent_sleep(min(10, 2 ** (attempt - 1)))
            retry_markers = _discover_markers(
                api.list_all("issues?state=all")
            )
            remote = retry_markers.get(identifier)
            if remote is not None:
                break
        if remote is None:
            raise ForensicIngestError(
                "Publication creation intent exists but its marked "
                f"issue is not visible; refusing duplicate creation: {identifier}"
            )
        publication_issues[identifier] = {
            "number": remote["number"],
            "id": remote["id"],
            "html_url": remote.get("html_url"),
            "parent_linked": False,
            "closed": remote.get("state") == "closed",
            "publisher_created": True,
        }
        by_marker[identifier] = remote

    atomic_write_json(publication_state_path, publication)

    remote_by_number = {
        int(remote["number"]): remote
        for remote in by_marker.values()
        if "number" in remote
    }
    preflight_remotes: dict[str, Mapping[str, Any]] = {}
    for identifier in order:
        entry = publication_issues.get(identifier)
        if entry is None:
            continue
        expected = issue_by_id[identifier]
        dependencies = _issue_dependencies(expected)
        if not dependencies <= set(publication_issues):
            raise ForensicIngestError(
                f"Publication dependencies are unresolved for {identifier}"
            )
        resolved_body = resolve_issue_references(
            expected["body"],
            publication_issues,
            dependencies,
        )
        if len(resolved_body.encode("utf-8")) > MAX_BODY_BYTES:
            raise ForensicIngestError(
                f"Resolved issue body exceeds safe size: {identifier}"
            )
        remote = remote_by_number.get(int(entry["number"]))
        if remote is None:
            raise ForensicIngestError(
                f"Existing marked issue is missing remotely: {identifier}"
            )
        if remote.get("id") != entry.get("id"):
            raise ForensicIngestError(
                f"Existing marked issue has database ID drift: {identifier}"
            )
        creation_intent = creation_intents.get(identifier)
        if creation_intent is not None and creation_intent != _creation_intent_sha256(
            expected,
            resolved_body,
        ):
            raise ForensicIngestError(
                f"Publication creation intent has draft drift: {identifier}"
            )
        pending_close = (
            expected["state"] == "closed"
            and entry.get("publisher_created") is True
            and not entry.get("closed")
        )
        mismatch = _remote_matches(
            expected,
            remote,
            resolved_body,
            allow_pending_close=pending_close,
        )
        if mismatch:
            raise ForensicIngestError(
                f"Existing marked issue has {mismatch} drift: {identifier}"
            )
        preflight_remotes[identifier] = remote
    adopted_intents = set(creation_intents) & set(preflight_remotes)
    for identifier in adopted_intents:
        creation_intents.pop(identifier)
    if adopted_intents:
        atomic_write_json(publication_state_path, publication)

    parent_ids = sorted(
        {
            issue["parent_id"]
            for issue in issues
            if issue.get("parent_id")
        }
    )
    for parent_id in parent_ids:
        parent_entry = publication_issues.get(parent_id)
        if parent_entry is None:
            continue
        remote_children = api.list_all(
            f"issues/{parent_entry['number']}/sub_issues"
        )
        remote_child_ids = {int(child["id"]) for child in remote_children}
        final_child_ids = set(remote_child_ids)
        missing_child_count = 0
        for issue in issues:
            if issue.get("parent_id") != parent_id:
                continue
            child_entry = publication_issues.get(issue["logical_id"])
            if child_entry is None:
                missing_child_count += 1
            else:
                if (
                    child_entry.get("parent_linked")
                    and int(child_entry["id"]) not in remote_child_ids
                ):
                    raise ForensicIngestError(
                        "Recorded sub-issue link is missing remotely: "
                        f"{issue['logical_id']}"
                    )
                final_child_ids.add(int(child_entry["id"]))
        if len(final_child_ids) + missing_child_count > MAX_SUB_ISSUES_PER_PARENT:
            raise ForensicIngestError(
                "Existing parent lacks capacity for planned sub-issues: "
                f"{parent_id}"
            )

    label_names = {
        label["name"].casefold() for label in api.list_all("labels")
    }
    desired_labels = _deduplicate_labels(
        label for issue in issues for label in issue.get("labels", [])
    )
    for label in desired_labels:
        if label.casefold() not in label_names:
            api.api(
                f"repos/{repository_name}/labels",
                {
                    "name": label,
                    "color": "BFD4F2",
                    "description": f"Agentic-Agile {label}",
                },
            )
            label_names.add(label.casefold())

    for identifier in order:
        expected = issue_by_id[identifier]
        dependencies = _issue_dependencies(expected)
        if not dependencies <= set(publication_issues):
            raise ForensicIngestError(
                f"Publication dependencies are unresolved for {identifier}"
            )
        resolved_body = resolve_issue_references(
            expected["body"],
            publication_issues,
            dependencies,
        )
        if len(resolved_body.encode("utf-8")) > MAX_BODY_BYTES:
            raise ForensicIngestError(
                f"Resolved issue body exceeds safe size: {identifier}"
            )
        entry = publication_issues.get(identifier)
        if entry is None:
            intent_sha256 = _creation_intent_sha256(expected, resolved_body)
            existing_intent = creation_intents.get(identifier)
            if existing_intent is not None and existing_intent != intent_sha256:
                raise ForensicIngestError(
                    f"Publication creation intent has draft drift: {identifier}"
                )
            if existing_intent is not None:
                raise ForensicIngestError(
                    f"Unreconciled creation intent reached mutation: {identifier}"
                )
            creation_intents[identifier] = intent_sha256
            atomic_write_json(publication_state_path, publication)
            remote = api.api(
                f"repos/{repository_name}/issues",
                {
                    "title": expected["title"],
                    "body": resolved_body,
                    "labels": expected["labels"],
                },
            )
            entry = {
                "number": remote["number"],
                "id": remote["id"],
                "html_url": remote.get("html_url"),
                "parent_linked": False,
                "closed": False,
                "publisher_created": True,
            }
            publication_issues[identifier] = entry
            creation_intents.pop(identifier)
            atomic_write_json(publication_state_path, publication)
        else:
            remote = preflight_remotes[identifier]
        parent_id = expected.get("parent_id")
        if parent_id and not entry.get("parent_linked"):
            parent_number = publication_issues[parent_id]["number"]
            children = api.list_all(f"issues/{parent_number}/sub_issues")
            if not any(int(child["id"]) == int(entry["id"]) for child in children):
                api.api(
                    f"repos/{repository_name}/issues/{parent_number}/sub_issues",
                    {"sub_issue_id": entry["id"]},
                )
            entry["parent_linked"] = True
            atomic_write_json(publication_state_path, publication)
        if expected["state"] == "closed" and not entry.get("closed"):
            if remote is None or remote.get("state") != "closed":
                api.api(
                    f"repos/{repository_name}/issues/{entry['number']}",
                    {"state": "closed", "state_reason": "completed"},
                    method="PATCH",
                )
            entry["closed"] = True
            atomic_write_json(publication_state_path, publication)

    verification_error: Optional[ForensicIngestError] = None
    verification = None
    verification_sleep = getattr(api, "sleep", time.sleep)
    for attempt in range(5):
        try:
            verification = verify_github_publication(drafts, publication, api)
            verification_error = None
            break
        except DuplicateMarkerError:
            raise
        except ForensicIngestError as exc:
            verification_error = exc
            if attempt == 4:
                break
            verification_sleep(min(10, 2**attempt))
    if verification_error is not None or verification is None:
        raise verification_error or ForensicIngestError(
            "Remote publication verification failed"
        )
    publication["remote_verification"] = verification
    atomic_write_json(publication_state_path, publication)

    current_ingest_state = load_json(ingest_state_path, required=False)
    if sha256_value(current_ingest_state) != captured_ingest_state_sha256:
        raise ForensicIngestError(
            "Ingest state changed concurrently; refusing a stale checkpoint update"
        )
    if captured_ingest_state:
        validate_state(captured_ingest_state, str(config["profile_id"]))
        ingest_state = dict(captured_ingest_state)
    else:
        ingest_state = {
            "schema_version": SCHEMA_VERSION,
            "profile_id": config["profile_id"],
            "last_verified_source_sha": None,
            "last_verified_run_manifest_sha256": None,
            "incorporated_baseline_sha": None,
        }
    ingest_state["last_verified_source_sha"] = source_tip_sha
    ingest_state["last_verified_run_manifest_sha256"] = manifest[
        "manifest_sha256"
    ]
    if all_commits_incorporated:
        ingest_state["incorporated_baseline_sha"] = source_tip_sha
    atomic_write_json(ingest_state_path, ingest_state)
    profile_prefix = f"{config['profile_id']}:"
    superseded_decisions = sorted(
        int(remote["number"])
        for identifier, remote in by_marker.items()
        if identifier.startswith(profile_prefix)
        and identifier.endswith(":decision")
        and identifier not in issue_by_id
        and remote.get("state") == "open"
    )
    return {
        "passed": True,
        "target_repository": repository_name,
        "issue_count": len(issues),
        "manifest_validation": manifest_validation,
        "verification": verification,
        "state_advanced_to": source_tip_sha,
        "incorporated_baseline_advanced": all_commits_incorporated,
        "open_decision_issues_from_other_runs": superseded_decisions,
    }


def _plan_publication(
    config_path: Path,
    manifest_path: Path,
    drafts_path: Path,
    ingest_state_path: Path,
    publication_state_path: Path,
) -> dict[str, Any]:
    """Validate publication inputs locally; never contacts GitHub or writes."""
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    drafts = load_json(drafts_path)
    manifest_validation = _validate_manifest_snapshots(
        config,
        manifest,
        drafts,
        state=load_json(ingest_state_path, required=False),
        state_supplied=True,
    )
    github = config.get("github")
    if not isinstance(github, dict) or not github.get("repository"):
        raise ForensicIngestError(
            "Configuration github.repository is required for publication"
        )
    repository_name = str(github["repository"])
    if (
        not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository_name)
        or any(part in {".", ".."} for part in repository_name.split("/"))
    ):
        raise ForensicIngestError("GitHub repository must be owner/name")
    _load_publication_state(publication_state_path, github, drafts)
    configured_labels = list(github.get("labels", []))
    issues = drafts["issues"]
    for issue in issues:
        labels = _deduplicate_labels(issue.get("labels", []) + configured_labels)
        if len(labels) > MAX_LABELS_PER_ISSUE:
            raise ForensicIngestError(
                f"Draft issue exceeds {MAX_LABELS_PER_ISSUE} labels: "
                f"{issue['logical_id']}"
            )
    return {
        "mode": "dry-run",
        "writes_performed": False,
        "target_hostname": str(github.get("hostname", "github.com")),
        "target_repository": str(github["repository"]),
        "issue_count": len(issues),
        "planned_logical_ids": list(dependency_order(issues)),
        "manifest_validation": manifest_validation,
        "next_step": "Review the plan, then re-run with --execute to publish.",
    }


def publish_github(
    config_path: Path,
    manifest_path: Path,
    drafts_path: Path,
    ingest_state_path: Path,
    publication_state_path: Path,
    *,
    client: Optional[GitHubClient] = None,
    execute: bool = False,
) -> dict[str, Any]:
    config_path = _canonical_path(config_path)
    manifest_path = _canonical_path(manifest_path)
    drafts_path = _canonical_path(drafts_path)
    ingest_state_path = _canonical_path(ingest_state_path)
    publication_state_path = _canonical_path(publication_state_path)
    if _paths_alias(ingest_state_path, publication_state_path):
        raise ForensicIngestError(
            "Ingest state and publication state paths must be distinct"
        )
    read_paths = (
        ("configuration", config_path),
        ("run manifest", manifest_path),
        ("issue drafts", drafts_path),
    )
    _reject_write_aliases("Ingest state", ingest_state_path, read_paths)
    _reject_write_aliases(
        "Publication state",
        publication_state_path,
        read_paths,
    )
    if not execute:
        return _plan_publication(
            config_path,
            manifest_path,
            drafts_path,
            ingest_state_path,
            publication_state_path,
        )
    lock_paths = sorted(
        (ingest_state_path, publication_state_path),
        key=lambda path: os.path.normcase(str(checkpoint_lock_path(path))),
    )
    target_key = publication_target_key(load_json(config_path))
    with exclusive_checkpoint_lock(
        publication_state_path,
        lock_path=publication_target_lock_path(target_key),
    ):
        with exclusive_checkpoint_lock(lock_paths[0]):
            with exclusive_checkpoint_lock(lock_paths[1]):
                return _publish_github_locked(
                    config_path,
                    manifest_path,
                    drafts_path,
                    ingest_state_path,
                    publication_state_path,
                    client=client,
                    expected_target_key=target_key,
                )


def recommend_upstream_contribution(
    config_path: Path, output_path: Path
) -> dict[str, Any]:
    config_path = _canonical_path(config_path)
    output_path = _canonical_path(output_path)
    _reject_write_aliases(
        "Recommendation output",
        output_path,
        (("configuration", config_path),),
    )
    config = load_json(config_path)
    validate_config(config)
    repository = _repository_from_config(config)
    before = repository.guard()
    source_tip = repository.resolve_commit(str(config["source_ref"]))
    fork_tip = repository.resolve_commit(str(config["fork_ref"]))
    suppression = config.get("contribution_suppression") or {}
    path_globs = list(suppression.get("path_globs", []))
    subject_regexes = [
        re.compile(pattern) for pattern in suppression.get("subject_regexes", [])
    ]
    source_patch_equivalent = repository.source_patch_equivalent_fork_shas(
        source_tip,
        fork_tip,
    )
    raw_records: dict[str, dict[str, Any]] = {}
    for sha in repository.fork_only_shas(fork_tip, source_tip):
        record = repository.read_commit(sha)
        changed = repository.changed_files(sha, record["parent_shas"])
        record["changed_paths"] = sorted({item["path"] for item in changed})
        if sha in source_patch_equivalent:
            record["recommendation"] = "exclude_source_patch_equivalent"
            record["reasons"] = [
                "stable patch equivalent is already present in the source history"
            ]
            raw_records[sha] = record
            continue
        affected_paths = sorted(
            {
                path
                for item in changed
                for path in (item["old_path"], item["path"])
                if path
            }
        )
        reasons = []
        path_overlay = bool(affected_paths) and all(
            any(_git_path_glob_matches(path, pattern) for pattern in path_globs)
            for path in affected_paths
        )
        subject_overlay = any(
            pattern.search(record["subject"]) for pattern in subject_regexes
        )
        if len(record["parent_shas"]) > 1:
            reasons.append("merge commit is not a standalone contribution candidate")
        if path_overlay:
            reasons.append("all changed paths match configured overlay suppression")
        if not record["changed_paths"] and subject_overlay:
            reasons.append("subject matches configured overlay suppression")
        record["recommendation"] = (
            "suppress_process_governance_overlay"
            if reasons
            else "include_for_human_review"
        )
        record["reasons"] = reasons or [
            "fork-only change is not fully covered by configured suppression rules"
        ]
        raw_records[sha] = record
    ordered = topological_order(raw_records)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "agentic-agile-upstream-contribution-recommendations",
        "profile_id": config["profile_id"],
        "source_tip_sha": source_tip,
        "fork_tip_sha": fork_tip,
        "policy": {
            "path_globs": path_globs,
            "subject_regexes": list(suppression.get("subject_regexes", [])),
            "upstream_mutations_permitted": False,
        },
        "candidates": [
            record
            for record in ordered
            if record["recommendation"] == "include_for_human_review"
        ],
        "suppressed": [
            record
            for record in ordered
            if record["recommendation"] == "suppress_process_governance_overlay"
        ],
        "already_in_source": [
            record
            for record in ordered
            if record["recommendation"] == "exclude_source_patch_equivalent"
        ],
    }
    payload["report_sha256"] = sha256_value(payload)
    after = repository.guard()
    if before != after:
        raise ForensicIngestError(
            "Repository HEAD, refs, or worktree changed during recommendation analysis"
        )
    atomic_write_json(output_path, payload)
    return payload
