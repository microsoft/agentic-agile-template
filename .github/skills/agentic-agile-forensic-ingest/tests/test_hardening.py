from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import forensic_ingest  # noqa: E402
from forensic_ingest_lib import (  # noqa: E402
    analyze_repository,
    publish_github,
    render_drafts,
)
from test_support import GitFixture  # noqa: E402

ALLOWED_FORTY_HEX = {
    "4b825dc642cb6eb9a060e54bf8d69288fbee4904",  # Git's empty-tree object
    "0" * 40,  # template baseline sentinel
}
PUBLISHED_SUFFIXES = {".md", ".json", ".py"}


def published_files() -> list[Path]:
    roots = [SKILL, SKILL.parent / "README.md"]
    files: list[Path] = []
    for root in roots:
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in candidates:
            if (
                path.is_file()
                and path.suffix in PUBLISHED_SUFFIXES
                and "__pycache__" not in path.parts
                and "tests" not in path.relative_to(SKILL.parent).parts[1:2]
            ):
                files.append(path)
    return files


def run_cli(arguments: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = forensic_ingest.main(arguments)
        except SystemExit as exc:
            code = int(exc.code)
    return code, out.getvalue(), err.getvalue()


class PublishDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()
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

    def arguments(self, *extra: str) -> list[str]:
        return [
            "publish-github",
            "--config", str(self.config),
            "--manifest", str(self.manifest),
            "--drafts", str(self.drafts),
            "--state", str(self.state),
            "--publication-state", str(self.publication),
            *extra,
        ]

    def test_default_is_dry_run_without_remote_access_or_writes(self) -> None:
        state_before = self.state.read_bytes() if self.state.exists() else None
        with mock.patch(
            "forensic_ingest_lib.GitHubClient",
            side_effect=AssertionError("dry-run must not build a GitHub client"),
        ), mock.patch(
            "forensic_ingest_lib.subprocess.run",
            wraps=__import__("subprocess").run,
        ) as runner:
            code, out, err = run_cli(self.arguments())
        self.assertEqual(0, code, err)
        for call in runner.call_args_list:
            self.assertNotEqual("gh", Path(str(call.args[0][0])).stem)
        report = json.loads(out)
        self.assertEqual("dry-run", report["mode"])
        self.assertFalse(report["writes_performed"])
        self.assertEqual(len(report["planned_logical_ids"]), report["issue_count"])
        self.assertFalse(self.publication.exists())
        state_after = self.state.read_bytes() if self.state.exists() else None
        self.assertEqual(state_before, state_after)

    def test_library_default_is_dry_run(self) -> None:
        report = publish_github(
            self.config, self.manifest, self.drafts, self.state, self.publication
        )
        self.assertEqual("dry-run", report["mode"])
        self.assertFalse(self.publication.exists())

    def test_execute_flag_is_the_only_switch_to_writes(self) -> None:
        with mock.patch.object(forensic_ingest, "publish_github") as publish:
            publish.return_value = {}
            run_cli(self.arguments())
            self.assertFalse(publish.call_args.kwargs["execute"])
            run_cli(self.arguments("--execute"))
            self.assertTrue(publish.call_args.kwargs["execute"])

    def test_dry_run_rejects_malformed_inputs_deterministically(self) -> None:
        self.drafts.write_text("{not json", encoding="utf-8")
        code, out, err = run_cli(self.arguments())
        self.assertEqual(1, code)
        self.assertEqual("", out)
        self.assertTrue(err.startswith("forensic-ingest failed: "))
        self.assertFalse(self.publication.exists())

    def test_dry_run_rejects_state_aliasing_inputs(self) -> None:
        arguments = self.arguments()
        arguments[arguments.index("--publication-state") + 1] = str(self.state)
        code, _, err = run_cli(arguments)
        self.assertEqual(1, code)
        self.assertIn("distinct", err)

    def test_dry_run_diagnostics_redact_credentials(self) -> None:
        secret = "ghp_" + "A" * 36
        self.config.write_text(
            f"{{not json {secret} Authorization: Bearer abc.def", encoding="utf-8"
        )
        code, _, err = run_cli(self.arguments())
        self.assertEqual(1, code)
        self.assertNotIn(secret, err)
        self.assertNotIn("abc.def", err)

    def test_unknown_operation_and_missing_arguments_exit_with_usage_code(
        self,
    ) -> None:
        self.assertEqual(2, run_cli(["bogus"])[0])
        self.assertEqual(2, run_cli(["publish-github"])[0])


class PublishedContentTests(unittest.TestCase):
    """Class-level scan: published skill files carry no site-specific data."""

    def test_no_absolute_paths_identities_or_credentials(self) -> None:
        forbidden = {
            "absolute path": re.compile(
                r"(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/]|/Users/|/home/)"
            ),
            "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
            "credential": re.compile(
                r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
            ),
            "placeholder marker": re.compile(
                r"\b(?:TODO|FIXME|TBD)\b|\[Project Name\]|<your[- ]"
            ),
        }
        allowed_lines = ("ProgramData",)
        for path in published_files():
            text = path.read_text(encoding="utf-8")
            for label, pattern in forbidden.items():
                for match in pattern.finditer(text):
                    line = text[: match.start()].count("\n")
                    source_line = text.splitlines()[line]
                    if any(token in source_line for token in allowed_lines):
                        continue
                    self.fail(f"{label} in {path.name}:{line + 1}")

    def test_only_allowlisted_commit_shas_are_published(self) -> None:
        for path in published_files():
            for match in re.finditer(
                r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])",
                path.read_text(encoding="utf-8"),
            ):
                self.assertIn(match.group(0), ALLOWED_FORTY_HEX, path.name)

    def test_skill_md_is_small_and_links_resolve(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(skill.splitlines()), 500)
        paths = [SKILL / "SKILL.md"]
        parent_readme = SKILL.parent / "README.md"
        if parent_readme.is_file():
            paths.append(parent_readme)
        for path in paths:
            for target in re.findall(
                r"\]\((?!https?:|#)([^)#\s]+)", path.read_text(encoding="utf-8")
            ):
                self.assertTrue(
                    (path.parent / target).exists(), f"{path.name}: {target}"
                )

    def test_frontmatter_has_valid_name_and_description(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", skill, re.S)
        self.assertIsNotNone(match)
        fields = dict(
            line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
        )
        name = fields["name"].strip()
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertEqual(SKILL.name, name)
        self.assertGreater(len(fields["description"].strip()), 40)

    def test_line_endings_are_pinned_for_byte_identical_installs(self) -> None:
        attributes = (SKILL / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* -text", attributes.splitlines())

    def test_bytecode_is_not_tracked_or_unignored(self) -> None:
        ignore = (SKILL / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", ignore)


class PublishedContentRegressionTests(unittest.TestCase):
    def test_scan_diagnostics_do_not_echo_matched_content(self) -> None:
        cases = (
            ("absolute path", "C:" + "\\private\\file"),
            ("email address", "fixture" + "@example.invalid"),
            ("credential", "ghp_" + "A" * 36),
            ("credential", "github_pat_" + "B" * 40),
            ("placeholder marker", "TO" + "DO"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scan.md"
            for label, content in cases:
                with self.subTest(violation=label):
                    path.write_text("Heading\n" + content + "\n", encoding="utf-8")
                    case = PublishedContentTests(
                        "test_no_absolute_paths_identities_or_credentials"
                    )
                    with mock.patch(
                        __name__ + ".published_files", return_value=[path]
                    ), self.assertRaises(AssertionError) as raised:
                        case.test_no_absolute_paths_identities_or_credentials()
                    self.assertTrue(
                        str(raised.exception) == f"{label} in scan.md:2",
                        "Scan diagnostics must contain only type and location",
                    )

    def test_standalone_skill_passes_bundled_content_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / SKILL.name
            shutil.copytree(
                SKILL,
                installed,
                ignore=shutil.ignore_patterns("__pycache__", "tmp*"),
            )
            self.assertFalse((installed.parent / "README.md").exists())
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(
                PublishedContentTests
            )
            result = unittest.TestResult()
            with mock.patch(__name__ + ".SKILL", installed):
                suite.run(result)
            self.assertTrue(
                result.wasSuccessful(),
                f"Standalone content validation failed: {result.errors + result.failures}",
            )

    def test_present_parent_readme_links_are_still_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / SKILL.name
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            (skill.parent / "README.md").write_text(
                "[Missing](missing.md)\n", encoding="utf-8"
            )
            with mock.patch(__name__ + ".SKILL", skill):
                case = PublishedContentTests(
                    "test_skill_md_is_small_and_links_resolve"
                )
                with self.assertRaisesRegex(AssertionError, "README.md: missing.md"):
                    case.test_skill_md_is_small_and_links_resolve()


if __name__ == "__main__":
    unittest.main()
