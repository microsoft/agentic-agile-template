from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from forensic_ingest_lib import (  # noqa: E402
    ForensicIngestError,
    GitRepository,
    MAX_SUB_ISSUES_PER_PARENT,
    _semantic_groups,
    analysis_config_contract,
    analyze_repository,
    is_test_path,
    recommend_upstream_contribution,
    render_drafts,
    sha256_value,
    validate_config,
    validate_manifest,
    validate_state,
)
from test_support import GitFixture  # noqa: E402


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_linear_history_is_deterministic_and_complete(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        state = self.fixture.state()
        first_output = self.fixture.root / "first.json"
        second_output = self.fixture.root / "second.json"

        first_manifest = analyze_repository(config, state, first_output)
        second_manifest = analyze_repository(config, state, second_output)

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual([first, second], [c["sha"] for c in first_manifest["commits"]])
        self.assertEqual(2, first_manifest["coverage"]["unique_commit_count"])
        self.assertTrue(first_manifest["coverage"]["complete_and_unique"])
        self.assertEqual(
            {"unsynced": 2},
            first_manifest["coverage"]["integration_status_counts"],
        )
        grouped_shas = [
            sha
            for group in first_manifest["semantic_grouping"]["groups"]
            for sha in group["commit_shas"]
        ]
        self.assertEqual({first, second}, set(grouped_shas))
        self.assertEqual(2, len(grouped_shas))
        self.assertTrue(validate_manifest(config, first_output)["passed"])

    def test_merge_base_selection_is_deterministic(self) -> None:
        repository = GitRepository(self.fixture.repo)
        first = "1" * 40
        second = "2" * 40
        with mock.patch.object(
            repository,
            "run",
            return_value=f"{second}\n{first}\n",
        ) as run:
            self.assertEqual(
                first,
                repository.deterministic_merge_base("source", "fork"),
            )
        run.assert_called_once_with(
            "merge-base",
            "--all",
            "source",
            "fork",
        )

    def test_semantic_group_id_collisions_are_disambiguated(self) -> None:
        prefix = "a" * 48
        records = [
            {
                "sha": character * 40,
                "changed_paths": [f"{prefix}-{character}/file.py"],
                "test_paths": [],
            }
            for character in ("1", "2")
        ]
        with mock.patch(
            "forensic_ingest_lib.sha256_value",
            return_value="a" * 64,
        ):
            groups = _semantic_groups(records)

        identifiers = [group["id"] for group in groups]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(":collision-" in value for value in identifiers))

    def test_git_replacement_refs_do_not_change_recorded_evidence(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        original = self.fixture.commit(
            "original subject",
            {"src/original.py": "original = True\n"},
        )
        self.fixture.git("switch", "-c", "replacement", baseline)
        replacement = self.fixture.commit(
            "replacement subject",
            {"src/replacement.py": "replacement = True\n"},
        )
        self.fixture.git("replace", original, replacement)
        self.fixture.git("switch", "source")

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )

        self.assertEqual([original], [item["sha"] for item in manifest["commits"]])
        self.assertEqual("original subject", manifest["commits"][0]["subject"])
        self.assertEqual(
            ["src/original.py"],
            manifest["commits"][0]["changed_paths"],
        )

    def test_git_repository_routing_environment_is_ignored(self) -> None:
        expected = self.fixture.commit("expected", {"expected.txt": "expected\n"})
        other = GitFixture()
        try:
            other.commit("other", {"other.txt": "other\n"})
            with mock.patch.dict(
                os.environ,
                {
                    "GIT_DIR": str(other.repo / ".git"),
                    "GIT_WORK_TREE": str(other.repo),
                    "GIT_INDEX_FILE": str(other.repo / ".git" / "index"),
                    "GIT_OBJECT_DIRECTORY": str(other.repo / ".git" / "objects"),
                    "GIT_SHALLOW_FILE": str(other.repo / ".git" / "shallow"),
                },
            ):
                repository = GitRepository(self.fixture.repo)
                self.assertEqual(expected, repository.resolve_commit("HEAD"))
                for key in (
                    "GIT_DIR",
                    "GIT_WORK_TREE",
                    "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY",
                    "GIT_SHALLOW_FILE",
                ):
                    self.assertNotIn(key, repository.environment)
                self.assertEqual(
                    "1",
                    repository.environment["GIT_NO_LAZY_FETCH"],
                )
                self.assertEqual(
                    "1",
                    repository.environment["GIT_ATTR_NOSYSTEM"],
                )
        finally:
            other.close()

    def test_git_2_45_or_later_is_required(self) -> None:
        self.fixture.commit("baseline", {"README.md": "base\n"})

        with mock.patch.object(
            GitRepository,
            "_installed_git_version",
            return_value=(2, 44, 9),
        ):
            with self.assertRaisesRegex(
                ForensicIngestError,
                r"Git 2\.45\.0 or later is required; found 2\.44\.9",
            ):
                GitRepository(self.fixture.repo)

    def test_apple_git_version_suffix_is_accepted(self) -> None:
        repository = object.__new__(GitRepository)
        repository.environment = {}
        result = subprocess.CompletedProcess(
            ["git", "--version"],
            0,
            stdout=b"git version 2.45.4 (Apple Git-150.1)\n",
            stderr=b"",
        )

        with mock.patch("forensic_ingest_lib.subprocess.run", return_value=result):
            self.assertEqual(
                (2, 45, 4),
                repository._installed_git_version(),
            )

    def test_history_rewriting_repository_state_is_rejected(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        grafts = self.fixture.repo / ".git" / "info" / "grafts"
        grafts.write_text(f"{baseline}\n", encoding="utf-8")
        with self.assertRaisesRegex(ForensicIngestError, "info/grafts rewrites"):
            GitRepository(self.fixture.repo)
        grafts.unlink()

        shallow = self.fixture.repo / ".git" / "shallow"
        shallow.write_text(f"{baseline}\n", encoding="utf-8")
        with self.assertRaisesRegex(ForensicIngestError, "[Ss]hallow"):
            GitRepository(self.fixture.repo)

    def test_empty_attribute_tree_is_builtin_and_not_stored(self) -> None:
        self.fixture.commit("baseline", {"README.md": "base\n"})
        empty = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
        loose = self.fixture.repo / ".git" / "objects" / empty[:2] / empty[2:]
        self.assertFalse(loose.exists())
        repository = GitRepository(self.fixture.repo)
        self.assertEqual(repository.run("cat-file", "-t", empty).strip(), "tree")
        self.assertFalse(loose.exists())

    def test_non_utf8_commit_subject_is_preserved_losslessly(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        tree = self.fixture.git("rev-parse", f"{baseline}^{{tree}}").strip()
        raw = (
            f"tree {tree}\nparent {baseline}\n"
            "author A <a@example.com> 1 +0000\n"
            "committer A <a@example.com> 1 +0000\n\n"
        ).encode("ascii") + b"caf\xe9 one\n"
        first = subprocess.run(
            ["git", "hash-object", "-t", "commit", "-w", "--stdin", "--literally"],
            cwd=self.fixture.repo,
            input=raw,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.decode().strip()
        second = subprocess.run(
            ["git", "hash-object", "-t", "commit", "-w", "--stdin", "--literally"],
            cwd=self.fixture.repo,
            input=raw.replace(b"\xe9", b"\xe8"),
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.decode().strip()
        repository = GitRepository(self.fixture.repo)
        one = repository.read_commit(first)["subject"]
        two = repository.read_commit(second)["subject"]
        self.assertNotEqual(one, two)
        self.assertNotIn("\ufffd", one + two)

    def test_case_only_path_differences_alias_before_creation(self) -> None:
        from forensic_ingest_lib import _paths_alias, checkpoint_lock_path

        first = self.fixture.root / "state.json"
        second = self.fixture.root / "STATE.json"
        self.assertTrue(_paths_alias(first, second))
        self.assertTrue(
            _paths_alias(checkpoint_lock_path(first), checkpoint_lock_path(second))
        )
        self.assertFalse(_paths_alias(first, self.fixture.root / "other.json"))

    def test_case_only_lock_paths_alias_with_posix_normalization(self) -> None:
        from forensic_ingest_lib import _paths_alias, checkpoint_lock_path

        with mock.patch(
            "forensic_ingest_lib.os.path.normcase",
            side_effect=lambda path: path,
        ):
            for first_name, second_name in (
                ("state.json", "STATE.json"),
                ("Mixed-State.json", "mIXED-sTATE.json"),
                ("nested/state.json", "NESTED/STATE.json"),
            ):
                with self.subTest(first=first_name, second=second_name):
                    first = self.fixture.root / first_name
                    second = self.fixture.root / second_name
                    other = self.fixture.root / "other.json"
                    first_lock = checkpoint_lock_path(first)
                    second_lock = checkpoint_lock_path(second)
                    self.assertFalse(first.exists())
                    self.assertFalse(second.exists())
                    self.assertNotEqual(str(first_lock), str(second_lock))
                    self.assertTrue(_paths_alias(first, second))
                    self.assertTrue(_paths_alias(first_lock, second_lock))
                    self.assertFalse(_paths_alias(first, other))
                    self.assertFalse(
                        _paths_alias(first_lock, checkpoint_lock_path(other))
                    )

    def test_repository_local_attributes_are_rejected(self) -> None:
        self.fixture.commit("baseline", {"README.md": "base\n"})
        attributes = self.fixture.repo / ".git" / "info" / "attributes"
        attributes.write_text("*.bin diff=unsafe\n", encoding="utf-8")

        with self.assertRaisesRegex(
            ForensicIngestError,
            "Repository-local info/attributes is not allowed",
        ):
            GitRepository(self.fixture.repo)

    def test_repository_fsmonitor_hook_is_not_executed(self) -> None:
        self.fixture.commit("baseline", {"README.md": "base\n"})
        marker = self.fixture.root / "fsmonitor-executed"
        script = self.fixture.root / "fsmonitor.py"
        script.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "Path(sys.argv[1]).write_text('executed', encoding='utf-8')\n",
            encoding="utf-8",
        )
        command = subprocess.list2cmdline(
            [sys.executable, str(script), str(marker)]
        )
        self.fixture.git("config", "core.fsmonitor", command)

        repository = GitRepository(self.fixture.repo)
        repository.guard()

        self.assertFalse(marker.exists())

    def test_repository_gpg_program_is_not_executed(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit(
            "signed change",
            {"src/signed.py": "signed = True\n"},
        )
        raw = subprocess.run(
            ["git", "cat-file", "commit", changed],
            cwd=self.fixture.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, raw.returncode, raw.stderr.decode("utf-8"))
        headers, separator, message = raw.stdout.partition(b"\n\n")
        self.assertEqual(b"\n\n", separator)
        signed_commit = (
            headers
            + b"\n"
            + b"gpgsig -----BEGIN PGP SIGNATURE-----\n"
            + b" \n"
            + b" ZmFrZQ==\n"
            + b" -----END PGP SIGNATURE-----\n\n"
            + message
        )
        result = subprocess.run(
            ["git", "hash-object", "-t", "commit", "-w", "--stdin"],
            cwd=self.fixture.repo,
            input=signed_commit,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8"))
        self.fixture.git(
            "update-ref",
            "refs/heads/source",
            result.stdout.decode("ascii").strip(),
        )
        marker = self.fixture.root / "gpg-executed"
        script = self.fixture.root / "gpg.py"
        script.write_text(
            f"#!{Path(sys.executable).as_posix()}\n"
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
        self.fixture.git("config", "log.showSignature", "true")
        self.fixture.git("config", "gpg.program", str(script))
        control = subprocess.run(
            ["git", "log", "--show-signature", "-1", "source"],
            cwd=self.fixture.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, control.returncode, control.stderr)
        self.assertTrue(
            marker.exists(),
            f"stdout={control.stdout!r} stderr={control.stderr!r}",
        )
        marker.unlink()

        analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )

        self.assertFalse(marker.exists())

    def test_patch_evidence_does_not_execute_textconv(self) -> None:
        baseline = self.fixture.commit(
            "baseline",
            {
                ".gitattributes": "*.dat diff=unsafe\n",
                "payload.dat": "before\n",
            },
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit(
            "change payload",
            {"payload.dat": "after\n"},
        )
        marker = self.fixture.root / "textconv-executed"
        script = self.fixture.root / "textconv.py"
        script.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "Path(sys.argv[1]).write_text('executed', encoding='utf-8')\n",
            encoding="utf-8",
        )
        command = subprocess.list2cmdline(
            [sys.executable, str(script), str(marker)]
        )
        self.fixture.git("config", "diff.unsafe.textconv", command)

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )

        record = next(item for item in manifest["commits"] if item["sha"] == changed)
        self.assertIsNotNone(record["stable_patch_id"])
        self.assertFalse(marker.exists())

    def test_patch_evidence_ignores_worktree_binary_attributes(self) -> None:
        baseline = self.fixture.commit(
            "baseline",
            {
                ".gitattributes": "*.txt binary\n",
                "payload.txt": "before\n",
            },
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit(
            "change payload",
            {"payload.txt": "after\n"},
        )
        config = self.fixture.config(baseline)

        binary = analyze_repository(
            config,
            self.fixture.state(),
            self.fixture.root / "binary.json",
        )
        self.fixture.write(".gitattributes", "*.txt text\n")
        text = analyze_repository(
            config,
            self.fixture.state(),
            self.fixture.root / "text.json",
        )

        binary_record = next(
            item for item in binary["commits"] if item["sha"] == changed
        )
        text_record = next(
            item for item in text["commits"] if item["sha"] == changed
        )
        self.assertEqual(
            binary_record["stable_patch_id"],
            text_record["stable_patch_id"],
        )
        self.assertEqual(
            binary["manifest_sha256"],
            text["manifest_sha256"],
        )

    def test_portable_config_contract_excludes_local_and_github_fields(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(self.fixture.config(baseline).read_text(encoding="utf-8"))
        contract = analysis_config_contract(config)
        self.assertNotIn("repository_path", contract)
        self.assertNotIn("github", contract)

    def test_config_rejects_malformed_github_labels(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        for labels in ("team", ["team", 7], [""], ["x" * 51]):
            with self.subTest(labels=labels):
                altered = copy.deepcopy(config)
                altered["github"]["labels"] = labels
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "github.labels must be an array of non-empty strings",
                ):
                    validate_config(altered)

    def test_config_rejects_case_insensitive_duplicate_labels(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        config["github"]["labels"] = ["Upstream-Delta", "upstream-delta"]
        with self.assertRaisesRegex(
            ForensicIngestError,
            "case-insensitive duplicates",
        ):
            validate_config(config)

    def test_boolean_schema_versions_are_rejected(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config_path = self.fixture.config(baseline)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        boolean_config = copy.deepcopy(config)
        boolean_config["schema_version"] = True
        with self.assertRaisesRegex(
            ForensicIngestError,
            "configuration schema_version",
        ):
            validate_config(boolean_config)

        boolean_state = {
            "schema_version": True,
            "profile_id": "fixture",
            "last_verified_source_sha": None,
            "last_verified_run_manifest_sha256": None,
            "incorporated_baseline_sha": None,
        }
        with self.assertRaisesRegex(
            ForensicIngestError,
            "state schema_version",
        ):
            validate_state(boolean_state, "fixture")

        state_path = self.fixture.state()
        manifest_path = self.fixture.root / "manifest.json"
        drafts_path = self.fixture.root / "drafts.json"
        manifest = analyze_repository(config_path, state_path, manifest_path)
        drafts = render_drafts(manifest_path, drafts_path)

        boolean_manifest = copy.deepcopy(manifest)
        boolean_manifest["schema_version"] = True
        manifest_path.write_text(
            json.dumps(boolean_manifest),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ForensicIngestError,
            "run manifest schema_version",
        ):
            validate_manifest(config_path, manifest_path)
        with self.assertRaisesRegex(
            ForensicIngestError,
            "run manifest schema_version",
        ):
            render_drafts(manifest_path, drafts_path)

        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        boolean_drafts = copy.deepcopy(drafts)
        boolean_drafts["schema_version"] = True
        drafts_path.write_text(json.dumps(boolean_drafts), encoding="utf-8")
        with self.assertRaisesRegex(
            ForensicIngestError,
            "drafts schema_version",
        ):
            validate_manifest(
                config_path,
                manifest_path,
                drafts_path,
            )

    def test_config_rejects_non_string_identity_and_selection_fields(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        cases = (
            ("profile_id", 7, "profile_id must be a non-empty string"),
            (
                "repository_path",
                ["repository"],
                "repository_path must be a non-empty string",
            ),
            (
                "repository_identity",
                7,
                "repository_identity must be a non-empty string",
            ),
            (
                "source_ref",
                {"ref": "source"},
                "source_ref must be a non-empty string",
            ),
            ("fork_ref", True, "fork_ref must be a non-empty string"),
            (
                "initial_selection",
                ["after-baseline"],
                "initial_selection must be after-baseline or all-reachable",
            ),
            (
                "initial_baseline_sha",
                7,
                "initial_baseline_sha must be null or a full SHA",
            ),
        )
        for field, value, message in cases:
            with self.subTest(field=field):
                altered = copy.deepcopy(config)
                altered[field] = value
                with self.assertRaisesRegex(ForensicIngestError, message):
                    validate_config(altered)

    def test_config_rejects_malformed_contribution_suppression(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        cases = (
            ([], "configuration must be an object"),
            (
                {"path_globs": [" "], "subject_regexes": []},
                "path_globs must be an array of non-empty strings",
            ),
            (
                {"path_globs": [], "subject_regexes": "valid"},
                "subject_regexes must be an array of non-empty strings",
            ),
            (
                {"path_globs": [], "subject_regexes": ["valid", 7]},
                "subject_regexes must be an array of non-empty strings",
            ),
            (
                {"path_globs": [], "subject_regexes": ["["]},
                "contains an invalid regular expression",
            ),
        )
        for suppression, message in cases:
            with self.subTest(suppression=suppression):
                altered = copy.deepcopy(config)
                altered["contribution_suppression"] = suppression
                with self.assertRaisesRegex(ForensicIngestError, message):
                    validate_config(altered)

    def test_state_rejects_incomplete_and_non_string_sha_fields(self) -> None:
        valid = {
            "schema_version": 1,
            "profile_id": "fixture",
            "last_verified_source_sha": None,
            "last_verified_run_manifest_sha256": None,
            "incorporated_baseline_sha": None,
        }
        cases = (
            (
                {
                    key: value
                    for key, value in valid.items()
                    if key != "incorporated_baseline_sha"
                },
                "State fields are required",
            ),
            (
                {**valid, "last_verified_source_sha": 1},
                "last_verified_source_sha must be null or a full SHA",
            ),
            (
                {**valid, "last_verified_run_manifest_sha256": 1},
                "last_verified_run_manifest_sha256 must be null or a SHA-256",
            ),
            (
                {**valid, "incorporated_baseline_sha": 1},
                "incorporated_baseline_sha must be null or a full SHA",
            ),
            (
                {
                    **valid,
                    "last_verified_source_sha": "a" * 40,
                },
                "last verified source SHA and manifest SHA-256",
            ),
            (
                {
                    **valid,
                    "last_verified_run_manifest_sha256": "a" * 64,
                },
                "last verified source SHA and manifest SHA-256",
            ),
            (
                {
                    **valid,
                    "incorporated_baseline_sha": "a" * 40,
                },
                "incorporated baseline requires a last verified source SHA",
            ),
        )
        for state, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ForensicIngestError, message):
                    validate_state(state, "fixture")

    def test_config_rejects_common_credential_keys(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        for key in (
            "token",
            "github_token",
            "api_key",
            "authorization",
            "clientSecret",
        ):
            with self.subTest(key=key):
                altered = copy.deepcopy(config)
                altered["github"][key] = "forbidden-value"
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "Credential-like configuration key is forbidden",
                ):
                    validate_config(altered)

    def test_config_rejects_credential_values_under_allowed_keys(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        credential_values = (
            "gh" + "p_" + ("x" * 40),
            "github_" + "pat_" + ("x" * 30),
            "Bearer " + ("x" * 24),
            "ssh://u:p@x.invalid/r",
            "https://u:p@x.invalid/r",
            "https://x.invalid/r?token=credential",
            "https://x.invalid/r?api_key=credential",
            "https://x.invalid/r?client-secret=credential",
            "https://x.invalid/r?github%5Ftoken=credential",
        )
        for credential in credential_values:
            with self.subTest(credential_type=credential.split(":", 1)[0]):
                altered = copy.deepcopy(config)
                altered["github"]["labels"] = [credential]
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    r"Credential-like configuration value is forbidden: "
                    r"\$\.github\.labels\[0\]",
                ) as raised:
                    validate_config(altered)
                self.assertNotIn(credential, str(raised.exception))

    def test_config_rejects_pem_private_key_values(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = json.loads(
            self.fixture.config(baseline).read_text(encoding="utf-8")
        )
        private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "cHJpdmF0ZS1rZXktbWF0ZXJpYWw=\n"
            "-----END PRIVATE KEY-----"
        )
        config["repository_identity"] = private_key

        with self.assertRaisesRegex(
            ForensicIngestError,
            r"Credential-like configuration value is forbidden: "
            r"\$\.repository_identity",
        ) as raised:
            validate_config(config)

        self.assertNotIn(private_key, str(raised.exception))

    def test_patch_evidence_ignores_local_diff_configuration(self) -> None:
        before = "D\nA\nA\nD\nC\nB\nC\nD\nD\nB\nC\nB\nD\nB\n"
        after = "D\nA\nC\nD\nC\nC\nD\nB\nC\nD\nB\n"
        baseline = self.fixture.commit("baseline", {"ambiguous.txt": before})
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit("ambiguous change", {"ambiguous.txt": after})
        config = self.fixture.config(baseline)

        self.fixture.git("config", "diff.algorithm", "histogram")
        self.fixture.git("config", "diff.indentHeuristic", "true")
        histogram = analyze_repository(
            config,
            self.fixture.state(),
            self.fixture.root / "histogram.json",
        )

        self.fixture.git("config", "diff.algorithm", "myers")
        self.fixture.git("config", "diff.indentHeuristic", "false")
        myers = analyze_repository(
            config,
            self.fixture.state(),
            self.fixture.root / "myers.json",
        )

        histogram_record = next(
            item for item in histogram["commits"] if item["sha"] == changed
        )
        myers_record = next(
            item for item in myers["commits"] if item["sha"] == changed
        )
        self.assertEqual(
            histogram_record["stable_patch_id"],
            myers_record["stable_patch_id"],
        )
        self.assertEqual(
            histogram["manifest_sha256"],
            myers["manifest_sha256"],
        )

    def test_patch_evidence_ignores_local_color_and_rename_configuration(self) -> None:
        first = "first\n" + "original first content\n" * 12
        second = "second\n" + "original second content\n" * 12
        baseline = self.fixture.commit(
            "baseline", {"old-first.txt": first, "old-second.txt": second}
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        self.fixture.git("mv", "old-first.txt", "new-first.txt")
        self.fixture.git("mv", "old-second.txt", "new-second.txt")
        changed = self.fixture.commit(
            "rename and edit",
            {
                "new-first.txt": first + "changed\n",
                "new-second.txt": second + "changed\n",
            },
        )
        self.fixture.git("switch", "fork")
        self.fixture.git("cherry-pick", "--no-commit", changed)
        incorporated = self.fixture.commit("independent fork rename", {})
        config = self.fixture.config(baseline)
        refs_before = self.fixture.git("show-ref")
        variants = (
            ("never", "never", "true", "0"),
            ("always", "always", "true", "0"),
            ("always", "never", "false", "0"),
            ("never", "always", "copies", "1"),
            ("never", "never", "true", "1"),
        )
        expected = None
        for index, values in enumerate(variants):
            with self.subTest(settings=values):
                for key, value in zip(
                    ("color.ui", "color.diff", "diff.renames", "diff.renameLimit"),
                    values,
                ):
                    self.fixture.git("config", key, value)
                repository = GitRepository(self.fixture.repo)
                patch_id = repository.stable_patch_id(changed, [baseline])
                if patch_id is None:
                    self.fail("Nonempty rename commit must have a stable patch ID")
                self.assertRegex(patch_id, r"^[0-9a-f]{40}$")
                reachable = repository.reachable_patch_id_shas(incorporated)
                self.assertIn(patch_id, reachable)
                self.assertIn(incorporated, reachable[patch_id])
                files = repository.changed_files(changed, [baseline])
                self.assertEqual(
                    [
                        ("new-first.txt", "old-first.txt"),
                        ("new-second.txt", "old-second.txt"),
                    ],
                    [(item["path"], item["old_path"]) for item in files],
                )
                self.assertTrue(all(item["status"].startswith("R") for item in files))
                manifest = analyze_repository(
                    config,
                    self.fixture.state(),
                    self.fixture.root / f"color-rename-{index}.json",
                )
                record = next(
                    item for item in manifest["commits"] if item["sha"] == changed
                )
                self.assertEqual(
                    "incorporated_patch_equivalent", record["integration"]["status"]
                )
                evidence = (patch_id, reachable, manifest)
                if expected is None:
                    expected = evidence
                self.assertEqual(expected, evidence)
                self.assertEqual(refs_before, self.fixture.git("show-ref"))
                self.assertEqual("", self.fixture.git("status", "--porcelain=v1"))

    def test_diff_policy_preserves_root_and_nested_directory_evidence(self) -> None:
        path = "src/\u00e9.txt"
        baseline = self.fixture.commit(
            "baseline",
            {
                "nested/keep.txt": "keep\n",
                path: "first\n\nmiddle\n\nend\n",
                "src/two.txt": "one\ntwo\nthree\nfour\n",
            },
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit(
            "source change",
            {path: "first\n\nchanged\n\nend\n", "src/two.txt": "changed\n"},
        )
        self.fixture.git("switch", "fork")
        self.fixture.git("cherry-pick", "--no-commit", changed)
        incorporated = self.fixture.commit("independent fork change", {})
        config_path = self.fixture.config(baseline)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["repository_path"] = str(self.fixture.repo / "nested")
        config_path.write_text(json.dumps(config), encoding="utf-8")
        repository = GitRepository(self.fixture.repo / "nested")

        def evidence() -> dict[str, object]:
            return {
                "patch_id": repository.stable_patch_id(changed, [baseline]),
                "root_id": repository.stable_patch_id(baseline, []),
                "reachable": repository.reachable_patch_id_shas(incorporated),
                "files": repository.changed_files(changed, [baseline]),
                "source_equivalent": repository.source_patch_equivalent_fork_shas(
                    changed, incorporated
                ),
            }

        canonical = {
            "core.quotePath": "true",
            "core.bigFileThreshold": "512m",
            "diff.relative": "false",
            "diff.orderFile": os.devnull,
            "diff.suppressBlankEmpty": "false",
            "log.showRoot": "true",
            "patchid.verbatim": "false",
            "patchid.stable": "true",
        }
        for key, value in canonical.items():
            self.fixture.git("config", key, value)
        expected = evidence()
        self.assertIsNotNone(expected["patch_id"])
        self.assertIsNotNone(expected["root_id"])
        self.assertEqual({incorporated}, expected["source_equivalent"])
        self.assertEqual(
            ["src/two.txt", path],
            [item["path"] for item in repository.changed_files(changed, [baseline])],
        )
        manifest_path = self.fixture.root / "canonical.json"
        manifest = analyze_repository(
            config_path, self.fixture.state(), manifest_path
        )
        ordering = self.fixture.root / "order.txt"
        ordering.write_text(f"{path}\nsrc/two.txt\n", encoding="utf-8")
        variants = (
            {"core.quotePath": "false"},
            {"core.bigFileThreshold": "1"},
            {"diff.relative": "true"},
            {"log.showRoot": "false"},
            {"diff.orderFile": str(ordering)},
            {"diff.orderFile": "missing-order-file"},
            {"diff.suppressBlankEmpty": "true"},
            {"patchid.verbatim": "true", "patchid.stable": "false"},
        )
        combined = {key: value for variant in variants for key, value in variant.items()}
        for settings in (*variants, combined):
            with self.subTest(settings=settings):
                for key, value in {**canonical, **settings}.items():
                    self.fixture.git("config", key, value)
                self.assertEqual(expected, evidence())
        self.assertTrue(
            validate_manifest(
                config_path, manifest_path, state_path=self.fixture.state()
            )["passed"]
        )
        self.assertEqual(
            manifest,
            analyze_repository(
                config_path, self.fixture.state(), self.fixture.root / "hostile.json"
            ),
        )

    def test_submodule_evidence_ignores_local_diff_configuration(self) -> None:
        baseline, changed, fork_tip = self.fixture.create_submodule_divergence(
            same_patch=False
        )
        self.fixture.git(
            "config", "-f", ".gitmodules", "submodule.module.ignore", "all"
        )
        self.fixture.git("config", "submodule.module.ignore", "none")
        repository = GitRepository(self.fixture.repo)
        config = self.fixture.config(baseline)

        def evidence() -> dict[str, object]:
            return {
                "patch_id": repository.stable_patch_id(changed, [baseline]),
                "reachable": repository.reachable_patch_id_shas(fork_tip),
                "files": repository.changed_files(changed, [baseline]),
                "source_equivalent": repository.source_patch_equivalent_fork_shas(
                    changed, fork_tip
                ),
            }

        expected = evidence()
        self.assertIsNotNone(expected["patch_id"])
        self.assertEqual(set(), expected["source_equivalent"])
        self.assertEqual(
            ["module"],
            [item["path"] for item in repository.changed_files(changed, [baseline])],
        )
        manifest_path = self.fixture.root / "submodule.json"
        manifest = analyze_repository(config, self.fixture.state(), manifest_path)
        record = next(item for item in manifest["commits"] if item["sha"] == changed)
        self.assertEqual("unsynced", record["integration"]["status"])
        variants = (
            ("log", "none", "none"),
            ("diff", "none", "none"),
            ("short", "all", "all"),
            ("log", "dirty", "all"),
            ("diff", "untracked", None),
        )
        for output, global_ignore, local_ignore in variants:
            with self.subTest(settings=(output, global_ignore, local_ignore)):
                self.fixture.git("config", "diff.submodule", output)
                self.fixture.git("config", "diff.ignoreSubmodules", global_ignore)
                if local_ignore is None:
                    self.fixture.git("config", "--unset-all", "submodule.module.ignore")
                else:
                    self.fixture.git(
                        "config", "submodule.module.ignore", local_ignore
                    )
                self.assertEqual(expected, evidence())
        self.assertTrue(
            validate_manifest(
                config, manifest_path, state_path=self.fixture.state()
            )["passed"]
        )
        self.assertEqual(
            manifest,
            analyze_repository(
                config, self.fixture.state(), self.fixture.root / "hostile-module.json"
            ),
        )

    def test_guard_detects_changes_in_ignored_submodules(self) -> None:
        configuration = self.fixture.root / "inherited.gitconfig"
        configuration.write_text("[core]\n\tautocrlf = true\n", encoding="utf-8")
        environments = (
            {"GIT_CONFIG_GLOBAL": str(configuration)},
            {"GIT_CONFIG_SYSTEM": str(configuration)},
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.autocrlf",
                "GIT_CONFIG_VALUE_0": "true",
            },
            {"GIT_CONFIG_PARAMETERS": "'core.autocrlf'='true'"},
        )
        for environment in environments:
            with self.subTest(environment=tuple(environment)), mock.patch.dict(
                os.environ, environment
            ):
                fixture = GitFixture()
                try:
                    fixture.create_submodule_divergence()
                    fixture.git("config", "submodule.module.ignore", "all")
                    readme = fixture.repo / "module" / "README.md"
                    metadata = readme.stat()
                    # Require content inspection, not a coincidentally clean stat cache.
                    os.utime(
                        readme,
                        ns=(metadata.st_atime_ns, metadata.st_mtime_ns - 2_000_000_000),
                    )
                    repository = GitRepository(fixture.repo)
                    self.assertEqual(
                        b"",
                        repository.run_bytes(
                            "status", "--porcelain=v1", "-z", "--untracked-files=all"
                        ),
                        "Inherited configuration dirtied the canonical fixture baseline",
                    )
                    before = repository.guard()
                    fixture.write("module/README.md", "concurrent worktree change\n")
                    self.assertNotEqual(before, repository.guard())
                finally:
                    fixture.close()

    def test_source_equivalence_compares_only_divergent_history(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork")
        self.fixture.git("rm", "README.md")
        self.fixture.commit("remove original", {})
        self.fixture.commit("restore original", {"README.md": "base\n"})
        repository = GitRepository(self.fixture.repo)
        self.assertEqual(
            set(),
            repository.source_patch_equivalent_fork_shas(
                baseline, self.fixture.git("rev-parse", "fork")
            ),
        )

    def test_patch_evidence_ignores_local_diff_prefix_configuration(self) -> None:
        baseline = self.fixture.commit(
            "baseline",
            {"src/prefix.txt": "before\n"},
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        changed = self.fixture.commit(
            "change prefix evidence",
            {"src/prefix.txt": "after\n"},
        )
        config = self.fixture.config(baseline)
        variants = (
            {
                "diff.noprefix": "true",
                "diff.mnemonicPrefix": "false",
                "diff.srcPrefix": "a/",
                "diff.dstPrefix": "b/",
            },
            {
                "diff.noprefix": "false",
                "diff.mnemonicPrefix": "true",
                "diff.srcPrefix": "a/",
                "diff.dstPrefix": "b/",
            },
            {
                "diff.noprefix": "false",
                "diff.mnemonicPrefix": "false",
                "diff.srcPrefix": "old/",
                "diff.dstPrefix": "new/",
            },
            {
                "diff.noprefix": "false",
                "diff.mnemonicPrefix": "false",
                "diff.srcPrefix": "a/",
                "diff.dstPrefix": "b/",
            },
        )
        manifests = []
        for index, settings in enumerate(variants):
            for key, value in settings.items():
                self.fixture.git("config", key, value)
            manifests.append(
                analyze_repository(
                    config,
                    self.fixture.state(),
                    self.fixture.root / f"prefix-{index}.json",
                )
            )

        patch_ids = {
            next(
                item for item in manifest["commits"] if item["sha"] == changed
            )["stable_patch_id"]
            for manifest in manifests
        }
        self.assertEqual(1, len(patch_ids))
        self.assertEqual(
            1,
            len({manifest["manifest_sha256"] for manifest in manifests}),
        )

    def test_reachable_patch_ids_stream_git_history(self) -> None:
        baseline, _, source_tip = self.fixture.create_divergence()
        repository = GitRepository(self.fixture.repo)

        with mock.patch.object(
            repository,
            "run_bytes",
            side_effect=AssertionError("patch history must not be buffered"),
        ):
            evidence = repository.reachable_patch_id_shas(source_tip)

        self.assertIn(
            source_tip,
            {
                sha
                for commit_shas in evidence.values()
                for sha in commit_shas
            },
        )
        self.assertNotEqual(baseline, source_tip)

    def test_stable_patch_id_streams_single_commit(self) -> None:
        baseline, source_commit, _ = self.fixture.create_divergence()
        repository = GitRepository(self.fixture.repo)

        with mock.patch.object(
            repository,
            "run_bytes",
            side_effect=AssertionError("single-commit patch must not be buffered"),
        ):
            patch_id = repository.stable_patch_id(source_commit, [baseline])

        self.assertRegex(patch_id or "", r"^[0-9a-f]{40}$")

    def test_initial_reconstruction_includes_all_reachable_commits(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        config = self.fixture.config(baseline, initial_selection="all-reachable")
        value = json.loads(config.read_text(encoding="utf-8"))
        value["initial_baseline_sha"] = None
        config.write_text(json.dumps(value), encoding="utf-8")
        manifest = analyze_repository(
            config, self.fixture.state(), self.fixture.root / "manifest.json"
        )
        self.assertIsNone(manifest["baseline_sha"])
        self.assertEqual("all-reachable", manifest["selection_mode"])
        self.assertEqual(
            [baseline, first, second], [item["sha"] for item in manifest["commits"]]
        )

    def test_merge_uses_first_parent_and_preserves_topology(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        main_commit = self.fixture.commit("main work", {"src/main.py": "main = 1\n"})
        self.fixture.git("switch", "-c", "feature", baseline)
        feature_commit = self.fixture.commit(
            "feature work", {"src/feature.py": "feature = 1\n"}
        )
        self.fixture.git("switch", "source")
        self.fixture.git("merge", "--no-ff", "feature", "-m", "merge feature")
        merge_commit = self.fixture.git("rev-parse", "HEAD")

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )
        positions = {item["sha"]: index for index, item in enumerate(manifest["commits"])}
        self.assertLess(positions[main_commit], positions[merge_commit])
        self.assertLess(positions[feature_commit], positions[merge_commit])
        merge = next(item for item in manifest["commits"] if item["sha"] == merge_commit)
        self.assertEqual(2, len(merge["parent_shas"]))
        self.assertEqual(["src/feature.py"], merge["changed_paths"])

    def test_rename_keeps_destination_and_test_source_semantics(self) -> None:
        baseline = self.fixture.commit(
            "baseline", {"src/old_test.py": "assert True\n"}
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        self.fixture.git("mv", "src/old_test.py", "src/renamed.py")
        self.fixture.git("commit", "-m", "rename test helper")
        renamed_sha = self.fixture.git("rev-parse", "HEAD")

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )
        record = next(item for item in manifest["commits"] if item["sha"] == renamed_sha)
        self.assertEqual(["src/renamed.py"], record["changed_paths"])
        self.assertEqual(["src/old_test.py"], record["test_paths"])
        self.assertEqual("src/old_test.py", record["changed_files"][0]["old_path"])

    def test_rename_detection_ignores_local_rename_limit(self) -> None:
        original = "".join(f"line {index}\n" for index in range(30))
        baseline = self.fixture.commit(
            "baseline",
            {
                "src/old_a.py": original,
                "src/old_b.py": original.replace("line", "value"),
            },
        )
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source", baseline)
        self.fixture.git("config", "diff.renameLimit", "1")
        self.fixture.git("mv", "src/old_a.py", "src/new_a.py")
        self.fixture.git("mv", "src/old_b.py", "src/new_b.py")
        (self.fixture.repo / "src" / "new_a.py").write_text(
            original + "added = True\n",
            encoding="utf-8",
        )
        (self.fixture.repo / "src" / "new_b.py").write_text(
            original.replace("line", "value") + "added = True\n",
            encoding="utf-8",
        )
        self.fixture.git("add", ".")
        self.fixture.git("commit", "-m", "rename similar files")
        renamed_sha = self.fixture.git("rev-parse", "HEAD")

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )

        record = next(item for item in manifest["commits"] if item["sha"] == renamed_sha)
        renames = [item for item in record["changed_files"] if item["status"].startswith("R")]
        self.assertEqual(
            [("src/old_a.py", "src/new_a.py"), ("src/old_b.py", "src/new_b.py")],
            [(item["old_path"], item["path"]) for item in renames],
        )

    def test_patch_equivalent_incorporation_is_detected(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("switch", "-c", "source")
        source_sha = self.fixture.commit(
            "source implementation", {"src/feature.py": "value = 1\n"}
        )
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit(
            "independent equivalent implementation", {"src/feature.py": "value = 1\n"}
        )

        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )
        record = next(item for item in manifest["commits"] if item["sha"] == source_sha)
        self.assertEqual(
            "incorporated_patch_equivalent", record["integration"]["status"]
        )
        drafts = render_drafts(
            self.fixture.root / "manifest.json", self.fixture.root / "drafts.json"
        )
        self.assertTrue(drafts["all_commits_incorporated"])
        self.assertTrue(all(issue["state"] == "closed" for issue in drafts["issues"]))
        self.assertTrue(any(issue.get("parent_id") for issue in drafts["issues"]))

    def test_patch_equivalent_shared_source_commit_is_detected(self) -> None:
        self.fixture.commit("baseline", {"README.md": "base\n"})
        common = self.fixture.commit(
            "common product change",
            {"src/product.py": "enabled = True\n"},
        )
        self.fixture.git("branch", "fork", common)
        self.fixture.git("switch", "-c", "source", common)
        self.fixture.git("revert", "--no-edit", common)
        selection_baseline = self.fixture.git("rev-parse", "HEAD")
        reapplied = self.fixture.commit(
            "reapply product change",
            {"src/product.py": "enabled = True\n"},
        )

        manifest = analyze_repository(
            self.fixture.config(selection_baseline),
            self.fixture.state(),
            self.fixture.root / "manifest.json",
        )

        record = next(item for item in manifest["commits"] if item["sha"] == reapplied)
        self.assertEqual(
            "incorporated_patch_equivalent",
            record["integration"]["status"],
        )
        self.assertEqual([common], record["integration"]["fork_commit_shas"])

    def test_large_incorporated_history_partitions_parent_issues(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        original = manifest["commits"][0]
        records = []
        for index in range(MAX_SUB_ISSUES_PER_PARENT + 1):
            sha = f"{index + 1:040x}"
            path = f"area-{index:03d}/file.py"
            record = copy.deepcopy(original)
            record.update(
                {
                    "sha": sha,
                    "parent_shas": [],
                    "changed_files": [
                        {
                            "path": path,
                            "old_path": None,
                            "status": "A",
                            "is_test": False,
                        }
                    ],
                    "changed_paths": [path],
                    "test_paths": [],
                    "integration": {
                        "status": "incorporated_exact",
                        "fork_commit_shas": [sha],
                    },
                    "topological_index": index,
                }
            )
            records.append(record)
        manifest["commits"] = records
        manifest["semantic_grouping"]["groups"] = _semantic_groups(records)
        manifest["manifest_sha256"] = sha256_value(
            {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        drafts = render_drafts(
            manifest_path,
            self.fixture.root / "drafts.json",
        )

        parents = [issue for issue in drafts["issues"] if not issue.get("parent_id")]
        children = [issue for issue in drafts["issues"] if issue.get("parent_id")]
        self.assertEqual(2, len(parents))
        self.assertEqual(MAX_SUB_ISSUES_PER_PARENT + 1, len(children))
        child_counts = {
            parent["logical_id"]: sum(
                child.get("parent_id") == parent["logical_id"]
                for child in children
            )
            for parent in parents
        }
        self.assertEqual(
            [1, MAX_SUB_ISSUES_PER_PARENT],
            sorted(child_counts.values()),
        )

    def test_render_rejects_semantic_group_unknown_commit(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("switch", "-c", "source")
        self.fixture.commit("source one", {"src/one.py": "one = 1\n"})
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit("equivalent one", {"src/one.py": "one = 1\n"})
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        manifest["semantic_grouping"]["groups"][0]["commit_shas"] = ["f" * 40]
        manifest["manifest_sha256"] = sha256_value(
            {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(
            ForensicIngestError,
            "Semantic group references an unknown commit",
        ):
            render_drafts(
                manifest_path,
                self.fixture.root / "drafts.json",
            )

    def test_rewritten_baseline_is_rejected(self) -> None:
        baseline, first, _ = self.fixture.create_divergence()
        state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": first,
                "last_verified_run_manifest_sha256": "a" * 64,
                "incorporated_baseline_sha": baseline,
            }
        )
        self.fixture.git("switch", "source")
        self.fixture.git("reset", "--hard", baseline)
        self.fixture.commit("rewritten source", {"src/replacement.py": "new = 1\n"})
        with self.assertRaisesRegex(ForensicIngestError, "rewritten, disconnected"):
            analyze_repository(
                self.fixture.config(baseline),
                state,
                self.fixture.root / "manifest.json",
            )

    def test_validation_rejects_duplicate_and_foreign_coverage(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        manifest = analyze_repository(config, self.fixture.state(), output)
        altered = copy.deepcopy(manifest)
        altered["commits"].append(copy.deepcopy(altered["commits"][0]))
        altered["manifest_sha256"] = sha256_value(
            {key: value for key, value in altered.items() if key != "manifest_sha256"}
        )
        output.write_text(json.dumps(altered), encoding="utf-8")
        with self.assertRaisesRegex(ForensicIngestError, "not unique"):
            validate_manifest(config, output)

    def test_validation_rejects_rehashed_path_evidence_drift(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        manifest = analyze_repository(config, self.fixture.state(), output)
        altered = copy.deepcopy(manifest)
        altered["commits"][0]["changed_files"][0]["path"] = "invented/path.txt"
        altered["commits"][0]["changed_paths"] = ["invented/path.txt"]
        altered["manifest_sha256"] = sha256_value(
            {key: value for key, value in altered.items() if key != "manifest_sha256"}
        )
        output.write_text(json.dumps(altered), encoding="utf-8")
        with self.assertRaisesRegex(ForensicIngestError, "differs from Git"):
            validate_manifest(config, output)

    def test_validation_rejects_rehashed_derived_field_drift(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        manifest = analyze_repository(config, self.fixture.state(), output)
        alterations = {
            "run_id": lambda value: value.__setitem__(
                "run_id", "run-arbitraryduplicate"
            ),
            "coverage": lambda value: value["coverage"].update(
                {
                    "selected_commit_count": 999,
                    "integration_status_counts": {"incorporated_exact": 999},
                }
            ),
            "semantic_grouping": lambda value: value["semantic_grouping"][
                "groups"
            ][0].__setitem__("label", "invented-group"),
        }
        for name, alter in alterations.items():
            with self.subTest(name=name):
                altered = copy.deepcopy(manifest)
                alter(altered)
                altered["manifest_sha256"] = sha256_value(
                    {
                        key: value
                        for key, value in altered.items()
                        if key != "manifest_sha256"
                    }
                )
                output.write_text(json.dumps(altered), encoding="utf-8")
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "derived|run_id",
                ):
                    validate_manifest(config, output)

    def test_validation_rejects_malformed_commit_shapes(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        original = analyze_repository(config, self.fixture.state(), output)
        malformed_records = (
            {},
            {
                **copy.deepcopy(original["commits"][0]),
                "changed_files": [{}],
            },
            {
                **copy.deepcopy(original["commits"][0]),
                "integration": {
                    **copy.deepcopy(original["commits"][0]["integration"]),
                    "status": ["unsynced"],
                },
            },
        )
        for record in malformed_records:
            with self.subTest(record=record):
                altered = copy.deepcopy(original)
                altered["commits"] = [record]
                altered.pop("manifest_sha256")
                altered["manifest_sha256"] = sha256_value(altered)
                output.write_text(json.dumps(altered), encoding="utf-8")
                with self.assertRaisesRegex(
                    ForensicIngestError,
                    "Run manifest commit 0",
                ):
                    validate_manifest(config, output)

    def test_validation_rejects_non_string_selection_mode(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        manifest = analyze_repository(config, self.fixture.state(), output)
        manifest["selection_mode"] = ["after-initial-baseline"]
        manifest["manifest_sha256"] = sha256_value(
            {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        )
        output.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ForensicIngestError, "selection_mode is invalid"):
            validate_manifest(config, output)

    def test_manifest_container_shapes_are_validated_before_use(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        output = self.fixture.root / "manifest.json"
        original = analyze_repository(config, self.fixture.state(), output)

        invalid_source = copy.deepcopy(original)
        invalid_source["source"] = []
        invalid_source.pop("manifest_sha256")
        invalid_source["manifest_sha256"] = sha256_value(invalid_source)
        output.write_text(json.dumps(invalid_source), encoding="utf-8")
        with self.assertRaisesRegex(
            ForensicIngestError,
            "source must be an object",
        ):
            validate_manifest(config, output)

        invalid_grouping = copy.deepcopy(original)
        invalid_grouping["semantic_grouping"] = []
        invalid_grouping.pop("manifest_sha256")
        invalid_grouping["manifest_sha256"] = sha256_value(invalid_grouping)
        output.write_text(json.dumps(invalid_grouping), encoding="utf-8")
        with self.assertRaisesRegex(
            ForensicIngestError,
            "semantic_grouping must be an object",
        ):
            render_drafts(output, self.fixture.root / "drafts.json")

    def test_validation_without_state_cannot_relocate_baseline(self) -> None:
        baseline, first, _ = self.fixture.create_divergence()
        self.fixture.git("switch", "fork")
        self.fixture.commit(
            "fork equivalent one",
            {"src/one.py": "one = 1\n"},
        )
        config = self.fixture.config(baseline)
        state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": first,
                "last_verified_run_manifest_sha256": "a" * 64,
                "incorporated_baseline_sha": first,
            }
        )
        output = self.fixture.root / "manifest.json"
        manifest = analyze_repository(config, state, output)
        with self.assertRaisesRegex(
            ForensicIngestError,
            "state is required",
        ):
            validate_manifest(config, output)

        relocated = copy.deepcopy(manifest)
        relocated["selection_mode"] = "after-initial-baseline"
        relocated.pop("run_id")
        relocated.pop("manifest_sha256")
        unsigned = copy.deepcopy(relocated)
        relocated["run_id"] = f"run-{sha256_value(unsigned)[:16]}"
        relocated["manifest_sha256"] = sha256_value(relocated)
        output.write_text(json.dumps(relocated), encoding="utf-8")
        with self.assertRaisesRegex(
            ForensicIngestError,
            "configured initial baseline",
        ):
            validate_manifest(config, output)

    def test_incorporated_baseline_must_cover_incorporated_history(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": second,
                "last_verified_run_manifest_sha256": "a" * 64,
                "incorporated_baseline_sha": first,
            }
        )

        with self.assertRaisesRegex(
            ForensicIngestError,
            "source commits not proven incorporated",
        ):
            analyze_repository(
                self.fixture.config(baseline),
                state,
                self.fixture.root / "manifest.json",
            )

    def test_already_verified_manifest_still_reproves_incorporated_state(
        self,
    ) -> None:
        baseline, first, second = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            config,
            self.fixture.state(),
            manifest_path,
        )
        forged_state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": second,
                "last_verified_run_manifest_sha256": manifest["manifest_sha256"],
                "incorporated_baseline_sha": first,
            }
        )

        with self.assertRaisesRegex(
            ForensicIngestError,
            "source commits not proven incorporated",
        ):
            validate_manifest(
                config,
                manifest_path,
                state_path=forged_state,
            )

    def test_already_verified_exception_requires_completed_baseline(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        self.fixture.git("switch", "fork")
        self.fixture.commit("fork equivalent one", {"src/one.py": "one = 1\n"})
        self.fixture.commit("fork equivalent two", {"src/two.py": "two = 2\n"})
        config = self.fixture.config(baseline)
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            config,
            self.fixture.state(),
            manifest_path,
        )
        incomplete_state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": second,
                "last_verified_run_manifest_sha256": manifest["manifest_sha256"],
                "incorporated_baseline_sha": first,
            }
        )

        with self.assertRaisesRegex(
            ForensicIngestError,
            "baseline or selection mode differs",
        ):
            validate_manifest(
                config,
                manifest_path,
                state_path=incomplete_state,
            )

        complete_state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": second,
                "last_verified_run_manifest_sha256": manifest["manifest_sha256"],
                "incorporated_baseline_sha": second,
            }
        )
        self.assertTrue(
            validate_manifest(
                config,
                manifest_path,
                state_path=complete_state,
            )["passed"]
        )

    def test_generated_outputs_cannot_alias_durable_inputs(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        state = self.fixture.state()
        config_before = config.read_bytes()

        for output, message in (
            (config, "Analysis output path must be distinct from configuration"),
            (state, "Analysis output path must be distinct from ingest state"),
        ):
            with self.subTest(operation="analyze", output=output.name):
                with self.assertRaisesRegex(ForensicIngestError, message):
                    analyze_repository(config, state, output)

        manifest = self.fixture.root / "manifest.json"
        analyze_repository(config, state, manifest)
        manifest_before = manifest.read_bytes()
        with self.assertRaisesRegex(
            ForensicIngestError,
            "Draft output path must be distinct from run manifest",
        ):
            render_drafts(manifest, manifest)
        self.assertEqual(manifest_before, manifest.read_bytes())

        with self.assertRaisesRegex(
            ForensicIngestError,
            "Recommendation output path must be distinct from configuration",
        ):
            recommend_upstream_contribution(config, config)
        self.assertEqual(config_before, config.read_bytes())

    def test_only_allowlisted_environment_reaches_git(self) -> None:
        injected = {
            "GIT_EXTERNAL_DIFF": "x",
            "GIT_EXEC_PATH": "x",
            "GIT_PAGER_IN_USE": "1",
            "GIT_SSH_COMMAND": "x",
            "GIT_TRACE": "1",
            "GH_TOKEN": "secret",
            "PAGER": "x",
        }
        with mock.patch.dict(os.environ, injected):
            repository = GitRepository(self.fixture.repo)
        for key in injected:
            self.assertNotIn(key, repository.environment)
        self.assertIn("PATH", {key.upper() for key in repository.environment})

    def test_diff_context_overrides_are_not_inherited(self) -> None:
        baseline, source_commit, _ = self.fixture.create_divergence()
        expected = GitRepository(self.fixture.repo).stable_patch_id(
            source_commit, [baseline]
        )
        subprocess.run(
            ["git", "config", "diff.context", "0"],
            cwd=self.fixture.repo,
            check=True,
        )
        with mock.patch.dict(os.environ, {"GIT_DIFF_OPTS": "-U0"}):
            repository = GitRepository(self.fixture.repo)
            self.assertNotIn("GIT_DIFF_OPTS", repository.environment)
            self.assertEqual(
                expected, repository.stable_patch_id(source_commit, [baseline])
            )
        self.assertIn("diff.context=3", repository._git_command("show"))

    def test_test_path_classifier_ignores_ordinary_test_suffix_words(self) -> None:
        for path in ("src/latest.py", "a/contest.js", "src/protest.go", "A/Latest.java"):
            self.assertFalse(is_test_path(path), path)
        for path in (
            "FooTest.java",
            "FooTests.cs",
            "a/foo.spec.ts",
            "a/foo_test.go",
            "a/foo-test.js",
            "test.py",
        ):
            self.assertTrue(is_test_path(path), path)

    def test_null_contribution_suppression_is_treated_as_omitted(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        value = json.loads(config.read_text(encoding="utf-8"))
        value["contribution_suppression"] = None
        config.write_text(json.dumps(value), encoding="utf-8")
        output = self.fixture.root / "recommendations.json"

        recommend_upstream_contribution(config, output)

        self.assertTrue(output.exists())

    def test_incorporated_baseline_cannot_exceed_verified_history(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        config = self.fixture.config(baseline)
        cases = (
            (
                {
                    "schema_version": 1,
                    "profile_id": "fixture",
                    "last_verified_source_sha": None,
                    "last_verified_run_manifest_sha256": None,
                    "incorporated_baseline_sha": first,
                },
                "incorporated baseline requires a last verified source SHA",
            ),
            (
                {
                    "schema_version": 1,
                    "profile_id": "fixture",
                    "last_verified_source_sha": first,
                    "last_verified_run_manifest_sha256": "a" * 64,
                    "incorporated_baseline_sha": second,
                },
                "Incorporated baseline is not an ancestor",
            ),
        )
        for state, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ForensicIngestError, message):
                    analyze_repository(
                        config,
                        self.fixture.state(state),
                        self.fixture.root / "manifest.json",
                    )

    def test_unsynced_verified_tip_remains_selected_until_incorporated(self) -> None:
        baseline, first, second = self.fixture.create_divergence()
        state = self.fixture.state(
            {
                "schema_version": 1,
                "profile_id": "fixture",
                "last_verified_source_sha": second,
                "last_verified_run_manifest_sha256": "a" * 64,
                "incorporated_baseline_sha": baseline,
            }
        )
        manifest = analyze_repository(
            self.fixture.config(baseline),
            state,
            self.fixture.root / "manifest.json",
        )
        self.assertEqual("after-incorporated-baseline", manifest["selection_mode"])
        self.assertEqual([first, second], [item["sha"] for item in manifest["commits"]])
        self.assertEqual(
            {"unsynced": 2},
            manifest["coverage"]["integration_status_counts"],
        )

    def test_unsynced_render_is_one_open_decision_record(self) -> None:
        baseline, _, _ = self.fixture.create_divergence()
        manifest_path = self.fixture.root / "manifest.json"
        analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        drafts = render_drafts(manifest_path, self.fixture.root / "drafts.json")
        self.assertEqual(1, len(drafts["issues"]))
        self.assertEqual("open", drafts["issues"][0]["state"])
        self.assertEqual(2, len(drafts["issues"][0]["commit_shas"]))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["semantic_grouping"],
            drafts["semantic_grouping"],
        )
        self.assertIn(
            "## Semantic groups and commit inventory",
            drafts["issues"][0]["body"],
        )

    def test_git_subject_issue_literal_is_not_a_control_reference(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "fork", baseline)
        self.fixture.git("switch", "-c", "source")
        self.fixture.commit(
            (
                "preserve {{issue:not-a-reference}} and "
                "<!-- forensic-ingest-id:injected --> literally"
            ),
            {"src/example.py": "value = 1\n"},
        )
        manifest_path = self.fixture.root / "manifest.json"
        analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        drafts = render_drafts(
            manifest_path,
            self.fixture.root / "drafts.json",
        )
        body = drafts["issues"][0]["body"]
        self.assertIn(
            "preserve &#123;&#123;issue&#58;not-a-reference&#125;&#125; and "
            "&#60;&#33;-- forensic-ingest-id&#58;injected --&#62; literally",
            body,
        )
        self.assertNotIn("{{issue:not-a-reference}}", body)
        self.assertNotIn("<!-- forensic-ingest-id:injected -->", body)

    def test_git_derived_markdown_is_neutralized_in_every_context(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "source")
        self.fixture.commit("source one", {"src/one.py": "one = 1\n"})
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit("equivalent one", {"src/one.py": "one = 1\n"})
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        hostile = "<!-- hide [link](http://evil.example) `tick` *b* _i_ <img src=x>"
        group = manifest["semantic_grouping"]["groups"][0]
        group["label"] = hostile
        group["changed_paths"] = ["src/`x`" + hostile + ".py"]
        manifest["commits"][0]["subject"] = hostile
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = sha256_value(manifest)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        drafts = render_drafts(manifest_path, self.fixture.root / "drafts.json")
        child = next(issue for issue in drafts["issues"] if issue.get("parent_id"))
        subject_line = next(
            line for line in child["body"].splitlines() if line.startswith("- `")
        )
        path_line = next(
            line for line in child["body"].splitlines() if line.startswith("- ``")
        )
        self.assertTrue(path_line.endswith("``"))
        self.assertNotIn("<!--", subject_line)
        self.assertNotIn("<img", subject_line)
        subject_text = subject_line.split("** — ", 1)[1]
        for token in ("<", ">", "[", "]", "(", ")", "`", "*", "_"):
            self.assertNotIn(token, subject_text)
        area_line = next(
            line
            for line in child["body"].splitlines()
            if line.startswith("Record incorporated source commits for area ")
        )
        self.assertTrue(area_line.endswith("``."))
        self.assertNotIn("`", child["title"])

    def test_label_values_reject_control_commas_and_whitespace(self) -> None:
        from forensic_ingest_lib import _is_valid_label

        for bad in ("a,b", " a", "a ", "a\nb", "a\u202eb", "", "x" * 51):
            self.assertFalse(_is_valid_label(bad), repr(bad))
        self.assertTrue(_is_valid_label("type:story"))

    def test_non_utf8_git_paths_render_as_printable_text(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "source")
        self.fixture.commit("source one", {"src/one.py": "one = 1\n"})
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit("equivalent one", {"src/one.py": "one = 1\n"})
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        invalid_path = "src-\udcff/file.py"
        group = manifest["semantic_grouping"]["groups"][0]
        group["label"] = "src-\udcff"
        group["changed_paths"] = [invalid_path]
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = sha256_value(manifest)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        drafts = render_drafts(
            manifest_path,
            self.fixture.root / "drafts.json",
        )
        child = next(issue for issue in drafts["issues"] if issue.get("parent_id"))
        self.assertIn(r"src-\xff", child["title"])
        self.assertIn(r"src-\xff/file.py", child["body"])
        child["title"].encode("utf-8")
        child["body"].encode("utf-8")

    def test_git_control_characters_render_as_display_text(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "source")
        self.fixture.commit("source one", {"src/one.py": "one = 1\n"})
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.commit("equivalent one", {"src/one.py": "one = 1\n"})
        manifest_path = self.fixture.root / "manifest.json"
        manifest = analyze_repository(
            self.fixture.config(baseline),
            self.fixture.state(),
            manifest_path,
        )
        group = manifest["semantic_grouping"]["groups"][0]
        group["label"] = "src\tarea\x1b\u202e@team"
        group["changed_paths"] = ["src/\nfile\t\u2028@owner.py"]
        manifest["commits"][0]["subject"] = (
            "subject\twith\x1bcontrol\u202e@octocat"
        )
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = sha256_value(manifest)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        drafts = render_drafts(
            manifest_path,
            self.fixture.root / "drafts.json",
        )
        child = next(issue for issue in drafts["issues"] if issue.get("parent_id"))
        self.assertIn(r"src\x09area\x1b\u202e&#64;team", child["title"])
        self.assertIn(
            r"subject&#92;x09with&#92;x1bcontrol&#92;u202e&#64;octocat",
            child["body"],
        )
        self.assertIn(
            r"src/\x0afile\x09\u2028&#64;owner.py",
            child["body"],
        )
        self.assertNotRegex(child["title"], r"[\x00-\x1f\x7f]")
        self.assertNotRegex(child["body"], r"[\x00-\x08\x0b-\x1f\x7f]")
        self.assertNotIn("\t", child["body"])
        self.assertNotIn("\x1b", child["body"])
        self.assertNotIn("\u2028", child["body"])
        self.assertNotIn("\u202e", child["body"])
        self.assertNotIn("@team", child["title"])
        self.assertNotIn("@octocat", child["body"])
        self.assertNotIn("@owner", child["body"])


if __name__ == "__main__":
    unittest.main()
