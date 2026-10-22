from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Cover the bounded native lookup plus real validation on slow test hosts.
CONCURRENT_PUBLISHER_TIMEOUT = 120

from forensic_ingest_lib import (  # noqa: E402
    ForensicIngestError,
    GitHubClient,
    analyze_repository,
    checkpoint_lock_path,
    exclusive_checkpoint_lock,
    load_json,
    publication_target_lock_path,
    publish_github as _publish_github,
    render_drafts,
    sha256_value,
    validate_drafts,
    validate_manifest,
)
from test_support import GitFixture  # noqa: E402


def publish_github(*arguments, **options):
    options.setdefault("execute", True)
    return _publish_github(*arguments, **options)


class FakeGitHub:
    def __init__(self) -> None:
        self.hostname = "github.com"
        self.repository = "example/fork"
        self.issues: dict[int, dict] = {}
        self.labels: set[str] = set()
        self.children: dict[int, list[int]] = {}
        self.mutations = 0
        self.fail_issue_create_number: int | None = None
        self.fail_close_once = False
        self.create_attempts = 0
        self.hidden_issue_reads_after_create = 0
        self.issue_reads = 0
        self.duplicate_marker_on_issue_read: int | None = None
        self.issue_read_hook = None
        self.sleeps: list[float] = []
        self.sleep = self.sleeps.append

    def list_all(self, resource: str) -> list[dict]:
        if resource.startswith("issues?"):
            self.issue_reads += 1
            if self.issue_read_hook is not None:
                self.issue_read_hook(self.issue_reads)
            if (
                self.duplicate_marker_on_issue_read == self.issue_reads
                and self.issues
            ):
                number = max(self.issues) + 1
                duplicate = dict(next(iter(self.issues.values())))
                duplicate["number"] = number
                duplicate["id"] = number * 100
                duplicate["html_url"] = (
                    f"https://example.invalid/issues/{number}"
                )
                self.issues[number] = duplicate
            if self.issues and self.hidden_issue_reads_after_create:
                self.hidden_issue_reads_after_create -= 1
                return []
            return list(self.issues.values())
        if resource == "labels":
            return [{"name": label} for label in sorted(self.labels)]
        if resource.endswith("/sub_issues"):
            parent = int(resource.split("/")[1])
            return [self.issues[number] for number in self.children.get(parent, [])]
        raise AssertionError(resource)

    def api(self, endpoint: str, payload=None, method=None):
        if endpoint.endswith("/labels"):
            self.mutations += 1
            self.labels.add(payload["name"])
            return {"name": payload["name"]}
        if endpoint.endswith("/issues"):
            self.create_attempts += 1
            if self.fail_issue_create_number == self.create_attempts:
                raise ForensicIngestError("simulated partial publication")
            self.mutations += 1
            number = len(self.issues) + 1
            issue = {
                **payload,
                "number": number,
                "id": number * 100,
                "html_url": f"https://example.invalid/issues/{number}",
                "state": "open",
                "state_reason": None,
                "labels": [{"name": label} for label in payload["labels"]],
            }
            self.issues[number] = issue
            return issue
        if endpoint.endswith("/sub_issues"):
            self.mutations += 1
            parent = int(endpoint.split("/")[-2])
            child = next(
                number
                for number, issue in self.issues.items()
                if issue["id"] == payload["sub_issue_id"]
            )
            self.children.setdefault(parent, []).append(child)
            return self.issues[child]
        if payload and payload.get("state") == "closed" and self.fail_close_once:
            self.fail_close_once = False
            raise ForensicIngestError("simulated close interruption")
        self.mutations += 1
        number = int(endpoint.split("/")[-1])
        issue = self.issues[number]
        issue.update(payload)
        return issue


class PublicationCheckpointInputTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "publication.json"
        self.github = {"repository": "example/fork"}
        self.drafts = {"drafts_sha256": "0" * 64, "issues": []}

    def test_existing_empty_publication_state_is_not_missing(self) -> None:
        self.path.write_text("{}\n", encoding="utf-8")
        checkpoint_before = self.path.read_bytes()
        with self.assertRaisesRegex(
            ForensicIngestError, "Unsupported publication-state schema_version"
        ):
            sys.modules["forensic_ingest_lib"]._load_publication_state(
                self.path, self.github, self.drafts
            )
        self.assertEqual(checkpoint_before, self.path.read_bytes())

    def test_missing_and_valid_empty_progress_checkpoints_are_supported(self) -> None:
        loader = sys.modules["forensic_ingest_lib"]._load_publication_state
        initial = loader(self.path, self.github, self.drafts)
        self.assertFalse(self.path.exists())
        self.assertEqual({}, initial["issues"])
        self.assertEqual({}, initial["creation_intents"])
        self.path.write_text(json.dumps(initial), encoding="utf-8")
        self.assertEqual(initial, loader(self.path, self.github, self.drafts))

    def test_optional_ingest_json_still_supports_empty_objects(self) -> None:
        self.assertEqual({}, load_json(self.path, required=False))
        with self.assertRaisesRegex(ForensicIngestError, "does not exist"):
            load_json(self.path)
        self.path.write_text("{}", encoding="utf-8")
        self.assertEqual({}, load_json(self.path, required=False))

    def test_optional_json_read_errors_are_not_treated_as_missing(self) -> None:
        with mock.patch.object(
            Path, "exists", return_value=False
        ), mock.patch.object(
            Path, "read_text", side_effect=PermissionError("unreadable checkpoint")
        ), self.assertRaisesRegex(ForensicIngestError, "Invalid JSON file"):
            load_json(self.path, required=False)


class SharedPublicationDirectoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = SCRIPTS / "shared-lock-fixture"

    def validate(self) -> None:
        sys.modules["forensic_ingest_lib"]._validate_publication_lock_directory(
            self.directory
        )

    def test_root_owned_sticky_directory_is_accepted_without_mutation(self) -> None:
        metadata = mock.Mock(st_uid=0, st_mode=stat.S_IFDIR | 0o1777)
        with mock.patch("forensic_ingest_lib.os.name", "posix"), mock.patch.object(
            Path, "lstat", return_value=metadata
        ), mock.patch.object(Path, "mkdir") as mkdir, mock.patch.object(
            os, "chmod"
        ) as chmod, mock.patch.object(os, "chown", create=True) as chown:
            self.validate()
        mkdir.assert_not_called()
        chmod.assert_not_called()
        chown.assert_not_called()

    def test_untrusted_owner_modes_and_file_types_fail_closed(self) -> None:
        cases = (
            (1000, stat.S_IFDIR | 0o1777),
            (0, stat.S_IFDIR | 0o755),
            (0, stat.S_IFDIR | 0o777),
            (0, stat.S_IFDIR | 0o1770),
            (0, stat.S_IFDIR | 0o3777),
            (0, stat.S_IFREG | 0o1777),
            (0, stat.S_IFLNK | 0o1777),
        )
        for owner, mode in cases:
            with self.subTest(owner=owner, mode=oct(mode)):
                metadata = mock.Mock(st_uid=owner, st_mode=mode)
                with mock.patch(
                    "forensic_ingest_lib.os.name", "posix"
                ), mock.patch.object(
                    Path, "lstat", return_value=metadata
                ), mock.patch.object(Path, "mkdir") as mkdir, self.assertRaisesRegex(
                    ForensicIngestError, "administrator.*root-owned.*01777"
                ):
                    self.validate()
                mkdir.assert_not_called()

    def test_missing_and_unreadable_directories_are_not_created(self) -> None:
        for error in (FileNotFoundError("missing"), PermissionError("unreadable")):
            with self.subTest(error=type(error).__name__):
                with mock.patch(
                    "forensic_ingest_lib.os.name", "posix"
                ), mock.patch.object(
                    Path, "lstat", side_effect=error
                ), mock.patch.object(Path, "mkdir") as mkdir, self.assertRaisesRegex(
                    ForensicIngestError, "administrator.*root-owned.*01777"
                ):
                    self.validate()
                mkdir.assert_not_called()

    def test_windows_does_not_apply_posix_permission_bits(self) -> None:
        with mock.patch("forensic_ingest_lib.os.name", "nt"), mock.patch.object(
            Path, "lstat"
        ) as inspect:
            self.validate()
        inspect.assert_not_called()

    def test_directory_is_validated_before_target_lock_creation(self) -> None:
        module = sys.modules["forensic_ingest_lib"]
        lock = self.directory / "publication-fixture.lock"
        with mock.patch(
            "forensic_ingest_lib.publication_target_lock_path", return_value=lock
        ), mock.patch(
            "forensic_ingest_lib._validate_publication_lock_directory",
            side_effect=ForensicIngestError("unsafe shared directory"),
        ) as validate, mock.patch(
            "forensic_ingest_lib.exclusive_checkpoint_lock"
        ) as acquire, self.assertRaisesRegex(
            ForensicIngestError, "unsafe shared directory"
        ):
            with module.exclusive_publication_target_lock(
                self.directory / "state.json", "0" * 64
            ):
                self.fail("Unsafe shared directory was accepted")
        validate.assert_called_once_with(self.directory)
        acquire.assert_not_called()


@unittest.skipUnless(
    os.name == "posix" and os.geteuid() == 0,
    "Cross-account DAC coverage requires an isolated POSIX root test process",
)
class SharedPublicationDirectoryIntegrationTests(unittest.TestCase):
    def test_cross_account_targets_contend_without_unlinking_active_locks(self) -> None:
        child = """
import os, sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, sys.argv[1])
from forensic_ingest_lib import ForensicIngestError, exclusive_publication_target_lock
directory, key, operation, ready = sys.argv[2:]
directory = Path(directory)
os.umask(0o077)
lock = directory / ("publication-" + key + ".lock")
if operation == "unlink":
    try:
        lock.unlink()
    except PermissionError:
        print("protected", flush=True)
    else:
        raise AssertionError("Another account removed the active lock")
else:
    with mock.patch("forensic_ingest_lib.publication_target_lock_path", return_value=lock):
        try:
            with exclusive_publication_target_lock(
                directory / ("state-" + str(os.geteuid()) + ".json"), key
            ):
                print("acquired", flush=True)
                if operation == "hold":
                    Path(ready).write_text("ready", encoding="ascii")
                    sys.stdin.readline()
        except ForensicIngestError as error:
            if operation == "invalid" and "administrator provisioning" in str(error):
                print("invalid", flush=True)
            elif "checkpoint lock already exists" in str(error):
                print("blocked", flush=True)
            else:
                raise
"""
        with tempfile.TemporaryDirectory(
            prefix="forensic-shared-lock-test-", dir="/tmp"
        ) as temporary:
            directory = Path(temporary)
            directory.chmod(0o1777)
            original = directory.stat()

            def start(uid, key, operation, target_directory=directory):
                def drop_credentials():
                    os.setgroups([])
                    os.setgid(uid)
                    os.setuid(uid)

                return subprocess.Popen(
                    [
                        sys.executable, "-I", "-c", child, str(SCRIPTS),
                        str(target_directory), key, operation,
                        str(target_directory / f"ready-{uid}"),
                    ],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, encoding="utf-8",
                    preexec_fn=drop_credentials,
                )

            def run(uid, key, operation, target_directory=directory):
                process = start(uid, key, operation, target_directory)
                try:
                    output, errors = process.communicate(timeout=CONCURRENT_PUBLISHER_TIMEOUT)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=CONCURRENT_PUBLISHER_TIMEOUT)
                    raise
                self.assertEqual(0, process.returncode, errors)
                return output.strip()

            for first, second in ((65534, 65533), (65533, 65534)):
                with self.subTest(holder_uid=first, contender_uid=second):
                    key = "0" * 64
                    lock = directory / f"publication-{key}.lock"
                    holder = start(first, key, "hold")
                    try:
                        deadline = time.monotonic() + CONCURRENT_PUBLISHER_TIMEOUT
                        while not (directory / f"ready-{first}").exists():
                            self.assertIsNone(holder.poll(), "Publisher exited before ready")
                            self.assertLess(time.monotonic(), deadline, "Publisher not ready")
                            time.sleep(0.02)
                        self.assertEqual(first, lock.stat().st_uid)
                        self.assertEqual("blocked", run(second, key, "once"))
                        self.assertEqual("acquired", run(second, "1" * 64, "once"))
                        self.assertEqual("protected", run(second, key, "unlink"))
                        self.assertTrue(lock.exists())
                    finally:
                        try:
                            output, errors = holder.communicate(
                                "\n", timeout=CONCURRENT_PUBLISHER_TIMEOUT
                            )
                        except subprocess.TimeoutExpired:
                            holder.kill()
                            holder.communicate(timeout=CONCURRENT_PUBLISHER_TIMEOUT)
                            raise
                    self.assertEqual(0, holder.returncode, errors)
                    self.assertEqual("acquired", output.strip())
                    self.assertFalse(lock.exists())
                    self.assertEqual(
                        (original.st_uid, stat.S_IMODE(original.st_mode)),
                        (directory.stat().st_uid, stat.S_IMODE(directory.stat().st_mode)),
                    )
            for name, owner, mode in (
                ("private", 0, 0o755),
                ("no-sticky-bit", 0, 0o777),
                ("caller-owned", 65534, 0o1777),
            ):
                with self.subTest(invalid_directory=name):
                    invalid = directory / name
                    invalid.mkdir()
                    os.chown(invalid, owner, 0)
                    invalid.chmod(mode)
                    before = invalid.stat()
                    self.assertEqual("invalid", run(65533, "0" * 64, "invalid", invalid))
                    after = invalid.stat()
                    self.assertEqual(
                        (before.st_uid, before.st_mode), (after.st_uid, after.st_mode)
                    )
                    self.assertEqual([], list(invalid.iterdir()))
            missing = directory / "missing"
            self.assertEqual("invalid", run(65533, "0" * 64, "invalid", missing))
            self.assertFalse(missing.exists())
            alias = directory / "symlink"
            alias.symlink_to(directory, target_is_directory=True)
            self.assertEqual("invalid", run(65533, "0" * 64, "invalid", alias))
            self.assertTrue(alias.is_symlink())


class PublicationTestBudgetTests(unittest.TestCase):
    def test_process_thread_and_readiness_waits_use_the_shared_budget(self) -> None:
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                operation = node.func.attr
                subprocess_run = (
                    operation == "run"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "subprocess"
                )
                if subprocess_run or operation in {"communicate", "wait", "join"}:
                    timeout = next(
                        (item.value for item in node.keywords if item.arg == "timeout"),
                        None,
                    )
                    if timeout is None and operation in {"wait", "join"} and node.args:
                        timeout = node.args[0]
                    with self.subTest(line=node.lineno, operation=operation):
                        self.assertIsInstance(timeout, ast.Name)
                        self.assertEqual("CONCURRENT_PUBLISHER_TIMEOUT", timeout.id)
            if (
                isinstance(node, ast.BinOp)
                and isinstance(node.left, ast.Call)
                and isinstance(node.left.func, ast.Attribute)
                and node.left.func.attr == "monotonic"
            ):
                with self.subTest(line=node.lineno, operation="readiness deadline"):
                    self.assertIsInstance(node.op, ast.Add)
                    self.assertIsInstance(node.right, ast.Name)
                    self.assertEqual("CONCURRENT_PUBLISHER_TIMEOUT", node.right.id)


class PublicationLockTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("system-a", "system-b"):
            (self.root / name / "ProgramData").mkdir(parents=True)
        self.target_key = sha256_value({"fixture": str(self.root)})
        self.environments = (
            {"ProgramData": str(self.root / "data-a")},
            {
                "ProgramData": str(self.root / "data-b"),
                "ALLUSERSPROFILE": str(self.root / "all-users"),
                "TEMP": str(self.root / "temp"),
                "TMP": str(self.root / "tmp"),
                "TMPDIR": str(self.root / "tmpdir"),
            },
            {
                "ProgramData": str(self.root / "data-c"),
                "HOME": str(self.root / "home"),
                "USERPROFILE": str(self.root / "profile"),
                "SYSTEMROOT": str(self.root / "windows"),
                "WINDIR": str(self.root / "windows"),
                "SystemDrive": str(self.root / "system-a"),
            },
            {"SystemDrive": str(self.root / "system-b")},
        )

    @unittest.skipUnless(os.name == "nt", "Real native namespace check requires Windows")
    def test_real_windows_namespace_ignores_cold_process_environments(self) -> None:
        lock_path = publication_target_lock_path(self.target_key)
        child = (
            "import json, sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from forensic_ingest_lib import publication_target_lock_path\n"
            "print(json.dumps(str(publication_target_lock_path(sys.argv[2]))))\n"
        )
        for environment in self.environments:
            with self.subTest(environment=tuple(environment)):
                result = subprocess.run(
                    [
                        sys.executable, "-I", "-c", child,
                        str(SCRIPTS), self.target_key,
                    ],
                    env={**os.environ, **environment},
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8",
                    timeout=CONCURRENT_PUBLISHER_TIMEOUT, check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(lock_path, Path(json.loads(result.stdout)))

    def test_target_lock_contends_across_process_environments(self) -> None:
        lock_path = self.root / "target-locks" / f"publication-{self.target_key}.lock"
        child = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[3])\n"
            "from forensic_ingest_lib import ForensicIngestError, exclusive_checkpoint_lock\n"
            "try:\n"
            "    with exclusive_checkpoint_lock(Path(sys.argv[1]), lock_path=Path(sys.argv[2])):\n"
            "        print('unexpected acquisition')\n"
            "except ForensicIngestError as error:\n"
            "    if 'checkpoint lock already exists' not in str(error):\n"
            "        raise\n"
            "    print('blocked')\n"
        )
        with exclusive_checkpoint_lock(
            self.root / "first-state.json", lock_path=lock_path
        ):
            for environment in self.environments:
                with self.subTest(environment=tuple(environment)):
                    result = subprocess.run(
                        [
                            sys.executable, "-I", "-c", child,
                            str(self.root / "independent-state.json"),
                            str(lock_path), str(SCRIPTS),
                        ],
                        env={**os.environ, **environment},
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, encoding="utf-8",
                        timeout=CONCURRENT_PUBLISHER_TIMEOUT, check=False,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual("blocked", result.stdout.strip())
                    self.assertTrue(lock_path.exists())
        self.assertFalse(lock_path.exists())


class WindowsCommonDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shell32 = mock.Mock()
        self.ole32 = mock.Mock()
        self.ole32.CoInitializeEx.return_value = 0
        self.libraries = {"shell32": self.shell32, "ole32": self.ole32}
        patcher = mock.patch(
            "ctypes.WinDLL",
            side_effect=lambda name, **options: self.libraries[name],
            create=True,
        )
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)

    def lookup(self) -> Path:
        return sys.modules["forensic_ingest_lib"]._windows_common_data_path_from_api()

    def test_lookup_balances_com_and_frees_the_folder_pointer(self) -> None:
        def return_folder(identifier, flags, token, output):
            self.assertEqual(16, len(identifier))
            self.assertEqual(0, flags)
            self.assertIsNone(token)
            output._obj.value = str(SCRIPTS)
            return 0

        self.shell32.SHGetKnownFolderPath.side_effect = return_folder
        for status in (0, 1, -2147417850):
            with self.subTest(com_status=status):
                self.shell32.reset_mock()
                self.ole32.reset_mock()
                self.factory.reset_mock()
                self.ole32.CoInitializeEx.return_value = status
                self.assertEqual(SCRIPTS, self.lookup())
                self.ole32.CoTaskMemFree.assert_called_once()
                self.assertEqual(
                    1 if status >= 0 else 0,
                    self.ole32.CoUninitialize.call_count,
                )
                self.factory.assert_has_calls(
                    [
                        mock.call("shell32", winmode=0x800),
                        mock.call("ole32", winmode=0x800),
                    ]
                )

    def test_lookup_failures_free_memory_and_balance_com(self) -> None:
        for status, value in (
            (-2147024891, str(SCRIPTS)),
            (1, str(SCRIPTS)),
            (0, None),
            (0, ""),
            (0, "relative-folder"),
        ):
            with self.subTest(status=status, folder=value):
                self.ole32.reset_mock()

                def return_folder(identifier, flags, token, output):
                    output._obj.value = value
                    return status

                self.shell32.SHGetKnownFolderPath.side_effect = return_folder
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "Cannot resolve Windows common application data directory",
                ):
                    self.lookup()
                self.ole32.CoTaskMemFree.assert_called_once()
                self.ole32.CoUninitialize.assert_called_once()

    def test_library_and_com_initialization_errors_fail_closed(self) -> None:
        self.factory.side_effect = OSError("native lookup unavailable")
        with self.assertRaisesRegex(ForensicIngestError, "native lookup unavailable"):
            self.lookup()
        self.ole32.CoInitializeEx.assert_not_called()
        self.factory.side_effect = lambda name, **options: self.libraries[name]
        self.ole32.CoInitializeEx.return_value = -2147467259
        with self.assertRaisesRegex(ForensicIngestError, "COM initialization failed"):
            self.lookup()
        self.shell32.SHGetKnownFolderPath.assert_not_called()
        self.ole32.CoTaskMemFree.assert_not_called()
        self.ole32.CoUninitialize.assert_not_called()


class WindowsIsolatedLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        resolver = sys.modules["forensic_ingest_lib"]._windows_common_data_path
        resolver.cache_clear()
        self.addCleanup(resolver.cache_clear)
        self.kernel32 = mock.Mock()

        def return_windows_directory(output, capacity):
            output.value = "X:\\Windows"
            return len(output.value)

        self.kernel32.GetSystemWindowsDirectoryW.side_effect = return_windows_directory
        patcher = mock.patch("ctypes.WinDLL", return_value=self.kernel32, create=True)
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)

    def lookup(self) -> Path:
        return sys.modules["forensic_ingest_lib"]._windows_common_data_path()

    def test_successful_lookup_is_reused_across_environment_changes(self) -> None:
        completed = subprocess.CompletedProcess(
            [], 0, stdout=json.dumps(str(SCRIPTS)), stderr=""
        )
        with mock.patch(
            "forensic_ingest_lib.subprocess.run", return_value=completed
        ) as runner:
            for drive in ("Y:", "Z:"):
                with mock.patch.dict(
                    os.environ, {"SystemDrive": drive, "ProgramData": drive + "\\data"}
                ):
                    self.assertEqual(SCRIPTS, self.lookup())
        runner.assert_called_once()
        self.factory.assert_called_once_with("kernel32", winmode=0x800)

    def test_failed_lookup_is_retried_then_success_is_cached(self) -> None:
        completed = subprocess.CompletedProcess(
            [], 0, stdout=json.dumps(str(SCRIPTS)), stderr=""
        )
        with mock.patch(
            "forensic_ingest_lib.subprocess.run",
            side_effect=[
                subprocess.TimeoutExpired("folder lookup", 30),
                completed,
                completed,
            ],
        ) as runner:
            with self.assertRaisesRegex(
                ForensicIngestError,
                "Cannot resolve Windows common application data directory",
            ):
                self.lookup()
            self.assertEqual(SCRIPTS, self.lookup())
            self.assertEqual(SCRIPTS, self.lookup())
        self.assertEqual(2, runner.call_count)

    def test_child_environment_contains_only_kernel_derived_values(self) -> None:
        completed = subprocess.CompletedProcess(
            [], 0, stdout=json.dumps(str(SCRIPTS)), stderr=""
        )
        with mock.patch(
            "forensic_ingest_lib.subprocess.run", return_value=completed
        ) as runner, mock.patch.dict(
            os.environ, {"SystemDrive": "Y:", "ProgramData": "untrusted"}
        ):
            self.assertEqual(SCRIPTS, self.lookup())
        self.factory.assert_called_once_with("kernel32", winmode=0x800)
        self.assertEqual(
            {"SystemRoot": "X:\\Windows", "WINDIR": "X:\\Windows", "SystemDrive": "X:"},
            runner.call_args.kwargs["env"],
        )
        self.assertIn("-I", runner.call_args.args[0])
        self.assertEqual(30, runner.call_args.kwargs["timeout"])

    def test_kernel_failure_never_launches_a_child(self) -> None:
        for length, path in ((0, ""), (32768, "X:\\Windows"), (8, "relative")):
            with self.subTest(length=length, path=path):
                def return_bad_directory(output, capacity):
                    output.value = path
                    return length

                self.kernel32.GetSystemWindowsDirectoryW.side_effect = return_bad_directory
                with mock.patch(
                    "forensic_ingest_lib.subprocess.run"
                ) as runner, self.assertRaisesRegex(
                    ForensicIngestError, "system Windows directory lookup failed"
                ):
                    self.lookup()
                runner.assert_not_called()

    def test_failed_or_invalid_child_output_has_no_fallback(self) -> None:
        for result in (
            subprocess.CompletedProcess([], 1, stdout="", stderr="lookup failed"),
            subprocess.CompletedProcess([], 0, stdout="not json", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="null", stderr=""),
            subprocess.CompletedProcess([], 0, stdout='""', stderr=""),
            subprocess.CompletedProcess([], 0, stdout='"relative"', stderr=""),
            subprocess.CompletedProcess([], 0, stdout="{}", stderr=""),
        ):
            with self.subTest(output=result.stdout, code=result.returncode):
                with mock.patch(
                    "forensic_ingest_lib.subprocess.run", return_value=result
                ), self.assertRaisesRegex(
                    ForensicIngestError,
                    "Cannot resolve Windows common application data directory",
                ):
                    self.lookup()

    def test_child_startup_errors_and_timeouts_fail_closed(self) -> None:
        for error in (
            OSError("child startup failed"),
            subprocess.TimeoutExpired("folder lookup", 30),
        ):
            with self.subTest(error=type(error).__name__):
                with mock.patch(
                    "forensic_ingest_lib.subprocess.run", side_effect=error
                ), self.assertRaisesRegex(
                    ForensicIngestError,
                    "Cannot resolve Windows common application data directory",
                ):
                    self.lookup()


class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()
        patcher = mock.patch(
            "forensic_ingest_lib.publication_target_lock_path",
            side_effect=lambda key: (
                self.fixture.root / "target-locks" / f"publication-{key}.lock"
            ),
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        if os.name == "posix":
            # FakeGitHub scenarios are separate from the real cross-UID DAC tests.
            patcher = mock.patch(
                "forensic_ingest_lib._validate_publication_lock_directory"
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("switch", "-c", "source")
        self.fixture.commit("source one", {"src/one.py": "one = 1\n"})
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit("equivalent one", {"src/one.py": "one = 1\n"})
        self.config = self.fixture.config(baseline)
        self.state = self.fixture.state()
        self.manifest = self.fixture.root / "manifest.json"
        self.drafts = self.fixture.root / "drafts.json"
        self.publication = self.fixture.root / "publication.json"
        analyze_repository(self.config, self.state, self.manifest)
        render_drafts(self.manifest, self.drafts)

    def tearDown(self) -> None:
        self.fixture.close()

    def test_fake_publication_target_locks_belong_to_the_fixture(self) -> None:
        module = sys.modules["forensic_ingest_lib"]
        with mock.patch(
            "forensic_ingest_lib._windows_common_data_path",
            side_effect=AssertionError("FakeGitHub accessed the machine-wide root"),
        ):
            for key in ("0" * 64, "1" * 64):
                self.assertEqual(
                    self.fixture.root / "target-locks" / f"publication-{key}.lock",
                    module.publication_target_lock_path(key),
                )
            report = publish_github(
                self.config, self.manifest, self.drafts,
                self.state, self.publication, client=FakeGitHub(),
            )
        self.assertTrue(report["passed"])
        self.assertEqual([], list((self.fixture.root / "target-locks").iterdir()))

    def test_unsafe_shared_directory_precedes_checkpoint_and_remote_access(self) -> None:
        client = FakeGitHub()
        with mock.patch(
            "forensic_ingest_lib._validate_publication_lock_directory",
            side_effect=ForensicIngestError("unsafe shared directory"),
        ), self.assertRaisesRegex(ForensicIngestError, "unsafe shared directory"):
            publish_github(
                self.config, self.manifest, self.drafts,
                self.state, self.publication, client=client,
            )
        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)
        for path in (self.state, self.publication):
            self.assertFalse(path.exists())
            self.assertFalse(checkpoint_lock_path(path).exists())

    def test_dry_run_needs_no_shared_directory_provisioning(self) -> None:
        client = FakeGitHub()
        with mock.patch(
            "forensic_ingest_lib._validate_publication_lock_directory",
            side_effect=ForensicIngestError("unsafe shared directory"),
        ) as validate:
            publish_github(
                self.config, self.manifest, self.drafts,
                self.state, self.publication, client=client, execute=False,
            )
        validate.assert_not_called()
        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)
        self.assertFalse(self.state.exists())
        self.assertFalse(self.publication.exists())

    def test_partial_publication_resumes_and_rerun_is_idempotent(self) -> None:
        client = FakeGitHub()
        client.fail_issue_create_number = 2
        with self.assertRaisesRegex(ForensicIngestError, "partial publication"):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        saved = json.loads(self.publication.read_text(encoding="utf-8"))
        self.assertEqual(1, len(saved["issues"]))
        self.assertEqual(1, len(saved["creation_intents"]))

        checkpoint_before = self.publication.read_bytes()
        reads_before = client.issue_reads
        mutations_before = client.mutations
        report = publish_github(
            self.config, self.manifest, self.drafts, self.state,
            self.publication, client=client, execute=False,
        )
        self.assertEqual("dry-run", report["mode"])
        self.assertEqual(checkpoint_before, self.publication.read_bytes())
        self.assertFalse(self.state.exists())
        self.assertEqual(reads_before, client.issue_reads)
        self.assertEqual(mutations_before, client.mutations)

        client.fail_issue_create_number = None
        client.labels.clear()
        before_failed_resume = client.mutations
        with self.assertRaisesRegex(
            ForensicIngestError,
            "refusing duplicate creation",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(before_failed_resume, client.mutations)
        self.assertFalse(client.labels)
        saved["creation_intents"].clear()
        self.publication.write_text(json.dumps(saved), encoding="utf-8")
        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertTrue(report["verification"]["passed"])
        self.assertEqual({1: [2]}, client.children)
        state = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(
            json.loads(self.manifest.read_text())["source"]["tip_sha"],
            state["incorporated_baseline_sha"],
        )

        before = client.mutations
        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertTrue(report["passed"])
        self.assertEqual(before, client.mutations)

    def test_prior_run_open_decision_issue_is_reported_not_mutated(self) -> None:
        client = FakeGitHub()
        profile = json.loads(self.config.read_text(encoding="utf-8"))["profile_id"]
        client.issues[1] = {
            "number": 1,
            "id": 100,
            "html_url": "https://example.invalid/issues/1",
            "state": "open",
            "title": "Review upstream delta old",
            "body": f"<!-- forensic-ingest-id:{profile}:old-run:decision -->",
            "labels": [],
        }
        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertEqual([1], report["open_decision_issues_from_other_runs"])
        self.assertEqual("open", client.issues[1]["state"])

    def test_creation_intent_resumes_after_create_before_checkpoint(self) -> None:
        client = FakeGitHub()
        client.hidden_issue_reads_after_create = 2
        original_atomic_write = sys.modules[
            "forensic_ingest_lib"
        ].atomic_write_json
        interrupted = False

        def interrupt_after_create(path: Path, value: dict) -> None:
            nonlocal interrupted
            if (
                path == self.publication
                and value.get("issues")
                and not value.get("creation_intents")
                and not interrupted
            ):
                interrupted = True
                raise ForensicIngestError("simulated post-create crash")
            original_atomic_write(path, value)

        with mock.patch(
            "forensic_ingest_lib.atomic_write_json",
            side_effect=interrupt_after_create,
        ):
            with self.assertRaisesRegex(
                ForensicIngestError,
                "simulated post-create crash",
            ):
                publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    self.state,
                    self.publication,
                    client=client,
                )

        saved = json.loads(self.publication.read_text(encoding="utf-8"))
        self.assertFalse(saved["issues"])
        self.assertEqual(1, len(saved["creation_intents"]))
        self.assertEqual(1, len(client.issues))
        self.assertEqual("open", client.issues[1]["state"])

        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )

        self.assertTrue(report["passed"])
        self.assertEqual([1], client.sleeps)
        self.assertTrue(
            all(issue["state"] == "closed" for issue in client.issues.values())
        )
        saved = json.loads(self.publication.read_text(encoding="utf-8"))
        self.assertFalse(saved["creation_intents"])
        self.assertTrue(
            all(
                entry["publisher_created"]
                for entry in saved["issues"].values()
            )
        )

    def test_publication_uses_exact_validated_input_snapshots(self) -> None:
        client = FakeGitHub()
        original_config = json.loads(self.config.read_text(encoding="utf-8"))
        original_drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        original_validate = sys.modules[
            "forensic_ingest_lib"
        ]._validate_manifest_snapshots

        def mutate_files_after_validation(*args, **kwargs):
            report = original_validate(*args, **kwargs)
            changed_config = dict(original_config)
            changed_config["github"] = {
                "repository": "attacker/other",
                "labels": ["changed"],
            }
            self.config.write_text(json.dumps(changed_config), encoding="utf-8")
            changed_drafts = dict(original_drafts)
            changed_drafts["issues"] = [
                {
                    **issue,
                    "title": f"changed {issue['title']}",
                }
                for issue in original_drafts["issues"]
            ]
            self.drafts.write_text(json.dumps(changed_drafts), encoding="utf-8")
            return report

        with mock.patch(
            "forensic_ingest_lib._validate_manifest_snapshots",
            side_effect=mutate_files_after_validation,
        ):
            report = publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertEqual("example/fork", report["target_repository"])
        self.assertEqual(
            [issue["title"] for issue in original_drafts["issues"]],
            [client.issues[number]["title"] for number in sorted(client.issues)],
        )

    def test_github_label_matching_is_case_insensitive(self) -> None:
        client = FakeGitHub()
        client.labels.add("Fixture")
        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )

        self.assertTrue(report["passed"])
        self.assertIn("Fixture", client.labels)
        self.assertNotIn("fixture", client.labels)
        self.assertEqual(
            1,
            sum(label.casefold() == "fixture" for label in client.labels),
        )
        for issue in client.issues.values():
            issue["labels"] = [
                {"name": label["name"].upper()}
                for label in issue["labels"]
            ]
        before = client.mutations
        rerun = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertTrue(rerun["passed"])
        self.assertEqual(before, client.mutations)

    def test_repository_change_during_validation_blocks_remote_access(self) -> None:
        client = FakeGitHub()
        source_tip = self.fixture.git("rev-parse", "source")
        repository_type = sys.modules["forensic_ingest_lib"].GitRepository
        original_guard = repository_type.guard
        guard_calls = 0

        def move_fork_before_final_guard(repository):
            nonlocal guard_calls
            guard_calls += 1
            if guard_calls == 2:
                self.fixture.git(
                    "update-ref",
                    "refs/heads/fork",
                    source_tip,
                )
            return original_guard(repository)

        with mock.patch.object(
            repository_type,
            "guard",
            side_effect=move_fork_before_final_guard,
            autospec=True,
        ):
            with self.assertRaisesRegex(
                ForensicIngestError,
                "changed during manifest validation",
            ):
                publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    self.state,
                    self.publication,
                    client=client,
                )

        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

    def test_duplicate_remote_marker_is_rejected_before_mutation(self) -> None:
        client = FakeGitHub()
        logical_id = json.loads(self.drafts.read_text())["issues"][0]["logical_id"]
        for number in (1, 2):
            body = f"<!-- forensic-ingest-id:{logical_id} -->"
            if number == 2:
                body = (
                    "<!-- forensic-ingest-id:unrelated -->\n"
                    f"{body}"
                )
            client.issues[number] = {
                "number": number,
                "id": number * 100,
                "title": "duplicate",
                "body": body,
                "state": "open",
                "state_reason": None,
                "labels": [],
            }
        with self.assertRaisesRegex(ForensicIngestError, "Duplicate remote marker"):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(0, client.mutations)

    def test_duplicate_created_concurrently_blocks_checkpoint_update(self) -> None:
        client = FakeGitHub()
        client.duplicate_marker_on_issue_read = 2
        with self.assertRaisesRegex(
            ForensicIngestError,
            "Duplicate remote marker",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertFalse(self.state.exists())

    def test_marker_only_open_historical_issue_is_not_closed(self) -> None:
        client = FakeGitHub()
        drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        parent = next(
            issue for issue in drafts["issues"] if not issue.get("parent_id")
        )
        client.issues[1] = {
            "number": 1,
            "id": 100,
            "title": parent["title"],
            "body": parent["body"],
            "state": "open",
            "state_reason": None,
            "labels": [
                {"name": label}
                for label in sorted(set(parent["labels"] + ["fixture"]))
            ],
        }

        with self.assertRaisesRegex(
            ForensicIngestError,
            "state drift",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertEqual(0, client.mutations)
        self.assertEqual("open", client.issues[1]["state"])
        saved = json.loads(self.publication.read_text(encoding="utf-8"))
        self.assertFalse(saved["issues"][parent["logical_id"]]["publisher_created"])

    def test_missing_recorded_sub_issue_link_fails_preflight(self) -> None:
        client = FakeGitHub()
        publish_github(
            self.config, self.manifest, self.drafts, self.state,
            self.publication, client=client,
        )
        client.children.clear()
        before = client.mutations
        with self.assertRaisesRegex(
            ForensicIngestError, "Recorded sub-issue link is missing"
        ):
            publish_github(
                self.config, self.manifest, self.drafts, self.state,
                self.publication, client=client,
            )
        self.assertEqual(before, client.mutations)

    def test_malformed_publication_state_is_rejected_before_remote_access(
        self,
    ) -> None:
        drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        logical_id = drafts["issues"][0]["logical_id"]
        base = {
            "schema_version": 1,
            "target_hostname": "github.com",
            "target_repository": "example/fork",
            "drafts_sha256": drafts["drafts_sha256"],
            "publication_contract_sha256": sha256_value(
                {
                    "target_hostname": "github.com",
                    "target_repository": "example/fork",
                    "labels": ["fixture"],
                }
            ),
            "creation_intents": {},
            "remote_verification": None,
        }
        cases = (
            ("{not json", "Invalid JSON file"),
            ("[]", "JSON root must be an object"),
            ("", "Invalid JSON file"),
            ("null", "JSON root must be an object"),
            ("false", "JSON root must be an object"),
            ("0", "JSON root must be an object"),
            ('""', "JSON root must be an object"),
            (
                {**base, "schema_version": True, "issues": {}},
                "Unsupported publication-state schema_version",
            ),
            (
                {**base, "target_repository": "example/other", "issues": {}},
                "another repository",
            ),
            (
                {**base, "target_hostname": "github.example.invalid", "issues": {}},
                "another GitHub host",
            ),
            (
                {**base, "drafts_sha256": "0" * 64, "issues": {}},
                "different drafts",
            ),
            (
                {**base, "publication_contract_sha256": "0" * 64, "issues": {}},
                "different GitHub settings",
            ),
            ({**base, "issues": []}, "issues must be an object"),
            (
                {**base, "issues": {"unknown": {}}},
                "unknown issue identifiers",
            ),
            (
                {**base, "issues": {logical_id: []}},
                "issue entry must be an object",
            ),
            (
                {
                    **base,
                    "issues": {
                        logical_id: {
                            "number": 1,
                            "id": 100,
                            "html_url": None,
                            "parent_linked": False,
                            "closed": False,
                        }
                    },
                },
                "publisher_created is invalid",
            ),
            (
                {
                    **base,
                    "issues": {},
                    "creation_intents": {logical_id: "invalid"},
                },
                "creation intent is invalid",
            ),
            (
                {**base, "issues": {}, "creation_intents": []},
                "creation_intents must be an object",
            ),
            (
                {**base, "issues": {}, "creation_intents": {"unknown": "0" * 64}},
                "unknown creation intents",
            ),
            ({}, "Unsupported publication-state schema_version"),
        )
        for publication, message in cases:
            for execute in (False, True):
                with self.subTest(message=message, execute=execute):
                    self.publication.write_text(
                        publication if isinstance(publication, str)
                        else json.dumps(publication),
                        encoding="utf-8",
                    )
                    checkpoint_before = self.publication.read_bytes()
                    client = FakeGitHub()
                    with mock.patch(
                        "forensic_ingest_lib.GitHubClient",
                        side_effect=AssertionError("local validation must not build a client"),
                    ), self.assertRaisesRegex(ForensicIngestError, message):
                        publish_github(
                            self.config,
                            self.manifest,
                            self.drafts,
                            self.state,
                            self.publication,
                            client=client if execute else None,
                            execute=execute,
                        )
                    self.assertEqual(checkpoint_before, self.publication.read_bytes())
                    self.assertFalse(self.state.exists())
                    self.assertEqual(0, client.issue_reads)
                    self.assertEqual(0, client.mutations)

    def test_empty_checkpoint_after_interruption_blocks_duplicate_creation(
        self,
    ) -> None:
        client = FakeGitHub()
        client.fail_close_once = True
        with self.assertRaisesRegex(ForensicIngestError, "close interruption"):
            publish_github(
                self.config, self.manifest, self.drafts, self.state,
                self.publication, client=client,
            )
        self.assertEqual(1, len(client.issues))
        client.hidden_issue_reads_after_create = 100
        self.publication.write_text("{}\n", encoding="utf-8")
        checkpoint_before = self.publication.read_bytes()
        reads_before = client.issue_reads
        mutations_before = client.mutations
        creates_before = client.create_attempts
        for execute in (False, True):
            with self.subTest(execute=execute):
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "Unsupported publication-state schema_version",
                ):
                    publish_github(
                        self.config, self.manifest, self.drafts, self.state,
                        self.publication, client=client, execute=execute,
                    )
                self.assertEqual(checkpoint_before, self.publication.read_bytes())
                self.assertFalse(self.state.exists())
                self.assertEqual(reads_before, client.issue_reads)
                self.assertEqual(mutations_before, client.mutations)
                self.assertEqual(creates_before, client.create_attempts)
                self.assertEqual(1, len(client.issues))

    def test_publication_state_cannot_resume_on_another_hostname(self) -> None:
        client = FakeGitHub()
        publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        changed = json.loads(self.config.read_text(encoding="utf-8"))
        changed["github"]["hostname"] = "github.example.invalid"
        self.config.write_text(json.dumps(changed), encoding="utf-8")
        other_host = FakeGitHub()
        other_host.hostname = "github.example.invalid"

        with self.assertRaisesRegex(
            ForensicIngestError,
            "another GitHub host",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=other_host,
            )

        self.assertEqual(0, other_host.mutations)

    def test_github_client_pins_hostname_and_ignores_gh_host(self) -> None:
        response = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="[]",
            stderr="",
        )
        with mock.patch.dict(
            os.environ,
            {"GH_HOST": "wrong.example.invalid"},
        ):
            client = GitHubClient("example/fork", hostname="github.com")
        with mock.patch(
            "forensic_ingest_lib.subprocess.run",
            return_value=response,
        ) as run:
            client.api("repos/example/fork/issues")

        self.assertNotIn("GH_HOST", client.environment)
        self.assertEqual(
            [
                "gh",
                "api",
                "--hostname",
                "github.com",
                "repos/example/fork/issues",
            ],
            run.call_args.args[0],
        )

    def test_github_client_rejects_path_injection_in_repository(self) -> None:
        for value in (
            "owner/name?x", "owner/name#x", "owner/na%2fme", "../name",
            "owner/..", "owner/name/extra", "owner/na me", "owner/name\n",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ForensicIngestError):
                    GitHubClient(value)

    def test_github_client_paginates_beyond_one_hundred_pages(self) -> None:
        client = GitHubClient("example/fork")

        def page_response(endpoint: str) -> list[dict]:
            page = int(endpoint.rsplit("page=", 1)[1])
            count = 100 if page <= 100 else 1
            return [
                {"page": page, "index": index}
                for index in range(count)
            ]

        with mock.patch.object(
            client,
            "api",
            side_effect=page_response,
        ) as api:
            items = client.list_all("issues?state=all")

        self.assertEqual(10_001, len(items))
        self.assertEqual(101, api.call_count)

    def test_merged_label_limit_is_checked_before_remote_access(self) -> None:
        config = json.loads(self.config.read_text(encoding="utf-8"))
        config["github"]["labels"] = [
            f"configured-{index}"
            for index in range(98)
        ]
        self.config.write_text(json.dumps(config), encoding="utf-8")
        client = FakeGitHub()

        with self.assertRaisesRegex(
            ForensicIngestError,
            "exceeds 100 labels",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

    def test_publication_state_database_id_drift_is_rejected_before_mutation(
        self,
    ) -> None:
        client = FakeGitHub()
        publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        publication = json.loads(self.publication.read_text(encoding="utf-8"))
        child_id = next(
            identifier
            for identifier, entry in publication["issues"].items()
            if entry["number"] == 2
        )
        publication["issues"][child_id]["id"] = client.issues[1]["id"]
        publication["issues"][child_id]["parent_linked"] = False
        self.publication.write_text(json.dumps(publication), encoding="utf-8")
        before = client.mutations

        with self.assertRaisesRegex(
            ForensicIngestError,
            "database ID drift",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertEqual(before, client.mutations)
        self.assertEqual({1: [2]}, client.children)

    def test_existing_issue_drift_is_rejected_before_label_creation(self) -> None:
        client = FakeGitHub()
        publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        client.labels.remove("fixture")
        client.issues[1]["title"] = "human-modified title"
        before = client.mutations
        with self.assertRaisesRegex(
            ForensicIngestError,
            "title drift",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(before, client.mutations)
        self.assertNotIn("fixture", client.labels)

    def test_existing_parent_capacity_is_checked_before_mutation(self) -> None:
        client = FakeGitHub()
        drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        parent = next(
            issue for issue in drafts["issues"] if not issue.get("parent_id")
        )
        client.issues[1] = {
            "number": 1,
            "id": 100,
            "html_url": "https://example.invalid/issues/1",
            "title": parent["title"],
            "body": parent["body"],
            "state": "closed",
            "state_reason": "completed",
            "labels": [
                {"name": label}
                for label in sorted(set(parent["labels"] + ["fixture"]))
            ],
        }
        for number in range(2, 102):
            client.issues[number] = {
                "number": number,
                "id": number * 100,
                "html_url": f"https://example.invalid/issues/{number}",
                "title": f"unrelated {number}",
                "body": "",
                "state": "open",
                "state_reason": None,
                "labels": [],
            }
        client.children[1] = list(range(2, 102))

        with self.assertRaisesRegex(
            ForensicIngestError,
            "lacks capacity",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertEqual(0, client.mutations)
        self.assertFalse(client.labels)
        self.assertEqual(101, len(client.issues))

    def test_remote_verification_retries_eventual_consistency(self) -> None:
        client = FakeGitHub()
        client.hidden_issue_reads_after_create = 1
        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertTrue(report["verification"]["passed"])
        self.assertEqual([1], client.sleeps)

    def test_publication_resumes_after_creation_before_closure(self) -> None:
        client = FakeGitHub()
        client.fail_close_once = True
        with self.assertRaisesRegex(
            ForensicIngestError, "simulated close interruption"
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        saved = json.loads(self.publication.read_text(encoding="utf-8"))
        first_entry = next(iter(saved["issues"].values()))
        self.assertFalse(first_entry["closed"])
        self.assertEqual("open", client.issues[first_entry["number"]]["state"])

        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        self.assertTrue(report["verification"]["passed"])
        self.assertTrue(
            all(issue["state"] == "closed" for issue in client.issues.values())
        )

    def test_publication_rejects_human_reopen_after_recorded_closure(self) -> None:
        client = FakeGitHub()
        publish_github(
            self.config,
            self.manifest,
            self.drafts,
            self.state,
            self.publication,
            client=client,
        )
        reopened = client.issues[1]
        reopened["state"] = "open"
        reopened["state_reason"] = None
        with self.assertRaisesRegex(
            ForensicIngestError,
            "state drift",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

    def test_concurrent_ingest_state_change_blocks_stale_checkpoint(self) -> None:
        client = FakeGitHub()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        newer_state = {
            "schema_version": 1,
            "profile_id": "fixture",
            "last_verified_source_sha": manifest["source"]["tip_sha"],
            "last_verified_run_manifest_sha256": "f" * 64,
            "incorporated_baseline_sha": manifest["source"]["tip_sha"],
        }

        def update_state(issue_read: int) -> None:
            if issue_read == 2:
                self.state.write_text(
                    json.dumps(newer_state),
                    encoding="utf-8",
                )

        client.issue_read_hook = update_state
        with self.assertRaisesRegex(
            ForensicIngestError,
            "changed concurrently",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(
            newer_state,
            json.loads(self.state.read_text(encoding="utf-8")),
        )

    def test_checkpoint_compare_and_write_hold_exclusive_lock(self) -> None:
        client = FakeGitHub()
        lock_paths = (
            checkpoint_lock_path(self.state),
            checkpoint_lock_path(self.publication),
        )
        client.issue_read_hook = lambda _: self.assertTrue(
            all(path.exists() for path in lock_paths)
        )
        original_atomic_write = sys.modules[
            "forensic_ingest_lib"
        ].atomic_write_json

        def assert_locked_write(path: Path, value: dict) -> None:
            if path in (self.state, self.publication):
                self.assertTrue(all(item.exists() for item in lock_paths))
            original_atomic_write(path, value)

        with mock.patch(
            "forensic_ingest_lib.atomic_write_json",
            side_effect=assert_locked_write,
        ):
            report = publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertTrue(report["passed"])
        self.assertTrue(all(not path.exists() for path in lock_paths))

    def test_distinct_ingest_states_share_publication_lock(self) -> None:
        first_client = FakeGitHub()
        second_client = FakeGitHub()
        first_ready = threading.Event()
        release_first = threading.Event()
        outcome: dict[str, object] = {}

        def pause_first_publisher(issue_read: int) -> None:
            if issue_read == 1:
                first_ready.set()
                if not release_first.wait(CONCURRENT_PUBLISHER_TIMEOUT):
                    raise AssertionError("Timed out waiting to release first publisher")

        def run_first_publisher() -> None:
            try:
                outcome["report"] = publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    self.state,
                    self.publication,
                    client=first_client,
                )
            except BaseException as exc:
                outcome["error"] = exc
                first_ready.set()

        first_client.issue_read_hook = pause_first_publisher
        thread = threading.Thread(target=run_first_publisher)
        thread.start()
        second_state = self.fixture.root / "second-state.json"
        try:
            self.assertTrue(first_ready.wait(CONCURRENT_PUBLISHER_TIMEOUT))
            self.assertNotIn("error", outcome)
            self.assertEqual(1, first_client.issue_reads)
            self.assertEqual(0, first_client.mutations)
            with self.assertRaisesRegex(
                ForensicIngestError,
                "checkpoint lock already exists",
            ):
                publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    second_state,
                    self.publication,
                    client=second_client,
                )
        finally:
            release_first.set()
            thread.join(CONCURRENT_PUBLISHER_TIMEOUT)

        self.assertFalse(thread.is_alive())
        self.assertNotIn("error", outcome)
        self.assertTrue(outcome["report"]["passed"])
        self.assertEqual(0, second_client.issue_reads)
        self.assertEqual(0, second_client.mutations)

    def test_independent_state_paths_share_target_transaction_lock(self) -> None:
        first_client = FakeGitHub()
        second_client = FakeGitHub()
        first_ready = threading.Event()
        release_first = threading.Event()
        outcome: dict[str, object] = {}

        def pause_first_publisher(issue_read: int) -> None:
            if issue_read == 1:
                first_ready.set()
                if not release_first.wait(CONCURRENT_PUBLISHER_TIMEOUT):
                    raise AssertionError("Timed out waiting to release first publisher")

        def run_first_publisher() -> None:
            try:
                outcome["report"] = publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    self.state,
                    self.publication,
                    client=first_client,
                )
            except BaseException as exc:
                outcome["error"] = exc
                first_ready.set()

        first_client.issue_read_hook = pause_first_publisher
        thread = threading.Thread(target=run_first_publisher)
        thread.start()
        second_state = self.fixture.root / "independent-state.json"
        second_publication = self.fixture.root / "independent-publication.json"
        try:
            self.assertTrue(first_ready.wait(CONCURRENT_PUBLISHER_TIMEOUT))
            self.assertNotIn("error", outcome)
            self.assertEqual(1, first_client.issue_reads)
            self.assertEqual(0, first_client.mutations)
            with self.assertRaisesRegex(
                ForensicIngestError,
                "checkpoint lock already exists",
            ):
                publish_github(
                    self.config,
                    self.manifest,
                    self.drafts,
                    second_state,
                    second_publication,
                    client=second_client,
                )
        finally:
            release_first.set()
            thread.join(CONCURRENT_PUBLISHER_TIMEOUT)

        self.assertFalse(thread.is_alive())
        self.assertNotIn("error", outcome)
        self.assertTrue(outcome["report"]["passed"])
        self.assertEqual(0, second_client.issue_reads)
        self.assertEqual(0, second_client.mutations)

    def test_existing_checkpoint_lock_fails_closed(self) -> None:
        client = FakeGitHub()
        lock_path = checkpoint_lock_path(self.state)
        lock_path.write_text("other publisher\n", encoding="utf-8")

        with self.assertRaisesRegex(
            ForensicIngestError,
            "checkpoint lock already exists",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )

        self.assertFalse(self.state.exists())
        self.assertEqual("other publisher\n", lock_path.read_text(encoding="utf-8"))
        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

    def test_aliased_state_paths_are_rejected_before_remote_access(self) -> None:
        client = FakeGitHub()
        with self.assertRaisesRegex(
            ForensicIngestError,
            "state paths must be distinct",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.state,
                client=client,
            )

        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

        self.state.write_text("{}\n", encoding="utf-8")
        hardlink = self.fixture.root / "publication-hardlink.json"
        os.link(self.state, hardlink)
        with self.assertRaisesRegex(
            ForensicIngestError,
            "state paths must be distinct",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                hardlink,
                client=client,
            )
        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

        with self.assertRaisesRegex(
            ForensicIngestError,
            "Publication state path must be distinct from run manifest",
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.manifest,
                client=client,
            )
        self.assertEqual(0, client.issue_reads)
        self.assertEqual(0, client.mutations)

    def test_symlinked_state_path_updates_canonical_checkpoint(self) -> None:
        target = self.fixture.root / "canonical-state.json"
        target.write_text("{}\n", encoding="utf-8")
        alias = self.fixture.root / "state-alias.json"
        try:
            alias.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"File symlinks are unavailable: {exc}")

        report = publish_github(
            self.config,
            self.manifest,
            self.drafts,
            alias,
            self.publication,
            client=FakeGitHub(),
        )

        self.assertTrue(report["passed"])
        self.assertTrue(alias.is_symlink())
        checkpoint = json.loads(target.read_text(encoding="utf-8"))
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["source"]["tip_sha"],
            checkpoint["last_verified_source_sha"],
        )
        self.assertEqual(
            manifest["source"]["tip_sha"],
            checkpoint["incorporated_baseline_sha"],
        )

    def test_publication_rejects_forged_incorporation_before_remote_writes(
        self,
    ) -> None:
        self.fixture.git("switch", "source")
        self.fixture.commit("source two", {"src/two.py": "two = 2\n"})
        self.fixture.git("switch", "fork")
        analyze_repository(self.config, self.state, self.manifest)
        drafts = render_drafts(self.manifest, self.drafts)
        self.assertFalse(drafts["all_commits_incorporated"])
        drafts["all_commits_incorporated"] = True
        drafts["drafts_sha256"] = sha256_value(
            {key: value for key, value in drafts.items() if key != "drafts_sha256"}
        )
        self.drafts.write_text(json.dumps(drafts), encoding="utf-8")
        client = FakeGitHub()
        with self.assertRaisesRegex(
            ForensicIngestError, "incorporation state"
        ):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(0, client.mutations)

    def test_dependency_cycle_is_rejected_before_remote_access(self) -> None:
        drafts = json.loads(self.drafts.read_text())
        first = drafts["issues"][0]
        second = drafts["issues"][1]
        first["dependencies"] = [second["logical_id"]]
        second["dependencies"] = [first["logical_id"]]
        drafts["drafts_sha256"] = sha256_value(
            {key: value for key, value in drafts.items() if key != "drafts_sha256"}
        )
        self.drafts.write_text(json.dumps(drafts), encoding="utf-8")
        client = FakeGitHub()
        with self.assertRaisesRegex(ForensicIngestError, "dependency cycle"):
            publish_github(
                self.config,
                self.manifest,
                self.drafts,
                self.state,
                self.publication,
                client=client,
            )
        self.assertEqual(0, client.mutations)

    def test_malformed_draft_issue_is_rejected_without_traceback(self) -> None:
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        malformed_issues = (
            [[]],
            [
                {
                    **drafts["issues"][0],
                    "labels": "not-an-array",
                }
            ],
            [
                {
                    **drafts["issues"][0],
                    "state": ["open"],
                }
            ],
        )
        for issues in malformed_issues:
            with self.subTest(issues=issues):
                altered = dict(drafts)
                altered["issues"] = issues
                altered["drafts_sha256"] = sha256_value(
                    {
                        key: value
                        for key, value in altered.items()
                        if key != "drafts_sha256"
                    }
                )
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "Draft issue 0",
                ):
                    validate_drafts(manifest, altered)

    def test_undeclared_body_reference_is_rejected(self) -> None:
        manifest = json.loads(self.manifest.read_text())
        drafts = json.loads(self.drafts.read_text())
        drafts["issues"][0]["body"] += "\n{{issue:not-a-dependency}}"
        drafts["drafts_sha256"] = sha256_value(
            {key: value for key, value in drafts.items() if key != "drafts_sha256"}
        )
        with self.assertRaisesRegex(
            ForensicIngestError, "undeclared issue references"
        ):
            validate_drafts(manifest, drafts)

    def test_draft_requires_exactly_one_matching_marker(self) -> None:
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        drafts = json.loads(self.drafts.read_text(encoding="utf-8"))
        drafts["issues"][0]["body"] += (
            "\n<!-- forensic-ingest-id:foreign-logical-id -->"
        )
        drafts["drafts_sha256"] = sha256_value(
            {
                key: value
                for key, value in drafts.items()
                if key != "drafts_sha256"
            }
        )
        with self.assertRaisesRegex(
            ForensicIngestError,
            "exactly one matching marker",
        ):
            validate_drafts(manifest, drafts)

    def test_body_limit_is_rejected(self) -> None:
        manifest = json.loads(self.manifest.read_text())
        drafts = json.loads(self.drafts.read_text())
        drafts["issues"][0]["body"] = (
            drafts["issues"][0]["body"].split("\n", 1)[0]
            + "\n"
            + ("x" * 60_001)
        )
        drafts["drafts_sha256"] = sha256_value(
            {key: value for key, value in drafts.items() if key != "drafts_sha256"}
        )
        with self.assertRaisesRegex(ForensicIngestError, "safe size"):
            validate_drafts(manifest, drafts)


class GitPolicyPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()
        self.addCleanup(self.fixture.close)
        patcher = mock.patch(
            "forensic_ingest_lib.publication_target_lock_path",
            side_effect=lambda key: (
                self.fixture.root / "target-locks" / f"publication-{key}.lock"
            ),
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        if os.name == "posix":
            patcher = mock.patch(
                "forensic_ingest_lib._validate_publication_lock_directory"
            )
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_interrupted_publication_resumes_across_diff_configuration_changes(self) -> None:
        fixture = self.fixture
        baseline, changed, _ = fixture.create_submodule_divergence()
        config = fixture.config(baseline)
        state = fixture.state()
        manifest = fixture.root / "manifest.json"
        drafts = fixture.root / "drafts.json"
        publication = fixture.root / "publication.json"
        analyze_repository(config, state, manifest)
        render_drafts(manifest, drafts)
        client = FakeGitHub()
        client.fail_close_once = True
        with self.assertRaisesRegex(ForensicIngestError, "close interruption"):
            publish_github(
                config, manifest, drafts, state, publication, client=client
            )
        numbers_before = set(client.issues)
        for key, value in {
            "color.diff": "always",
            "diff.renames": "copies",
            "diff.renameLimit": "1",
            "diff.submodule": "diff",
            "diff.ignoreSubmodules": "all",
            "submodule.module.ignore": "all",
            "core.quotePath": "false",
            "diff.relative": "true",
            "diff.orderFile": "missing-order-file",
            "log.showRoot": "false",
            "patchid.verbatim": "true",
        }.items():
            fixture.git("config", key, value)
        self.assertTrue(
            validate_manifest(config, manifest, drafts, state_path=state)["passed"]
        )
        report = publish_github(
            config, manifest, drafts, state, publication, client=client
        )
        self.assertTrue(report["verification"]["passed"])
        self.assertTrue(numbers_before.issubset(client.issues))
        self.assertEqual(2, len(client.issues))
        self.assertEqual(2, client.create_attempts)
        checkpoint = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(changed, checkpoint["incorporated_baseline_sha"])
        mutations = client.mutations
        report = publish_github(
            config, manifest, drafts, state, publication, client=client
        )
        self.assertTrue(report["passed"])
        self.assertEqual(mutations, client.mutations)


if __name__ == "__main__":
    unittest.main()
