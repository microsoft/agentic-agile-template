from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from forensic_ingest_lib import (  # noqa: E402
    GitHubClient,
    atomic_write_text,
    recommend_upstream_contribution,
    redact,
)
from test_support import GitFixture  # noqa: E402


class RecommendationAndCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_fixture_disables_inherited_commit_signing(self) -> None:
        self.fixture.close()
        with tempfile.TemporaryDirectory() as directory:
            global_config = Path(directory) / "gitconfig"
            global_config.write_text(
                "[commit]\n"
                "\tgpgSign = true\n"
                "[gpg]\n"
                "\tprogram = missing-fixture-signing-program\n",
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"GIT_CONFIG_GLOBAL": str(global_config)},
            ):
                self.fixture = GitFixture()
                commit = self.fixture.commit(
                    "unsigned fixture",
                    {"README.md": "fixture\n"},
                )

        self.assertRegex(commit, r"^[0-9a-f]{40}$")

    def test_product_change_is_included_and_overlay_is_suppressed(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork", baseline)
        overlay = self.fixture.commit(
            "governance overlay",
            {".github/skills/example/SKILL.md": "overlay\n"},
        )
        product = self.fixture.commit(
            "agentic-agile product integration", {"src/product.py": "enabled = True\n"}
        )
        report = recommend_upstream_contribution(
            self.fixture.config(baseline),
            self.fixture.root / "recommendations.json",
        )
        self.assertEqual([product], [item["sha"] for item in report["candidates"]])
        self.assertEqual([overlay], [item["sha"] for item in report["suppressed"]])
        self.assertFalse(report["policy"]["upstream_mutations_permitted"])

    def test_overlay_suppression_uses_case_sensitive_git_path_matching(
        self,
    ) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork", baseline)
        product = self.fixture.commit(
            "product change",
            {"src/product.py": "enabled = True\n"},
        )
        config_path = self.fixture.config(baseline)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["contribution_suppression"]["path_globs"] = ["SRC/**"]
        config["contribution_suppression"]["subject_regexes"] = []
        config_path.write_text(json.dumps(config), encoding="utf-8")
        with mock.patch(
            "forensic_ingest_lib.fnmatch.fnmatch",
            side_effect=AssertionError("OS-dependent fnmatch must not be used"),
        ):
            report = recommend_upstream_contribution(
                config_path,
                self.fixture.root / "recommendations.json",
            )
        self.assertEqual([product], [item["sha"] for item in report["candidates"]])
        self.assertEqual([], report["suppressed"])

    def test_single_star_suppression_does_not_cross_directories(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork", baseline)
        product = self.fixture.commit(
            "nested product change",
            {"src/nested/product.py": "enabled = True\n"},
        )
        config_path = self.fixture.config(baseline)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["contribution_suppression"]["path_globs"] = ["src/*.py"]
        config["contribution_suppression"]["subject_regexes"] = []
        config_path.write_text(json.dumps(config), encoding="utf-8")

        report = recommend_upstream_contribution(
            config_path,
            self.fixture.root / "recommendations.json",
        )
        self.assertEqual([product], [item["sha"] for item in report["candidates"]])

        config["contribution_suppression"]["path_globs"] = ["src/**/*.py"]
        config_path.write_text(json.dumps(config), encoding="utf-8")
        recursive = recommend_upstream_contribution(
            config_path,
            self.fixture.root / "recursive-recommendations.json",
        )
        self.assertEqual(
            [product],
            [item["sha"] for item in recursive["suppressed"]],
        )

    def test_subject_suppression_does_not_match_commit_body_lines(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork", baseline)
        self.fixture.git(
            "commit",
            "--allow-empty",
            "-m",
            "product change\ngovernance overlay",
        )
        product = self.fixture.git("rev-parse", "HEAD")
        report = recommend_upstream_contribution(
            self.fixture.config(baseline),
            self.fixture.root / "recommendations.json",
        )
        self.assertEqual([product], [item["sha"] for item in report["candidates"]])
        self.assertEqual("product change", report["candidates"][0]["subject"])
        self.assertEqual([], report["suppressed"])

    def test_rename_source_must_also_match_overlay_suppression(self) -> None:
        baseline = self.fixture.commit(
            "baseline",
            {"src/product.py": "enabled = True\n"},
        )
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "-c", "fork", baseline)
        (self.fixture.repo / ".github" / "skills").mkdir(parents=True)
        self.fixture.git(
            "mv",
            "src/product.py",
            ".github/skills/product.py",
        )
        self.fixture.git("commit", "-m", "move product into overlay")
        renamed = self.fixture.git("rev-parse", "HEAD")
        report = recommend_upstream_contribution(
            self.fixture.config(baseline),
            self.fixture.root / "recommendations.json",
        )
        self.assertEqual([renamed], [item["sha"] for item in report["candidates"]])
        self.assertEqual([], report["suppressed"])

    def test_patch_equivalent_already_in_source_is_not_a_candidate(self) -> None:
        baseline = self.fixture.commit("baseline", {"README.md": "base\n"})
        self.fixture.git("branch", "source", baseline)
        self.fixture.git("switch", "source")
        self.fixture.commit(
            "source product change",
            {"src/product.py": "enabled = True\n"},
        )
        self.fixture.git("switch", "-c", "fork", baseline)
        equivalent = self.fixture.commit(
            "re-authored product change",
            {"src/product.py": "enabled = True\n"},
        )
        report = recommend_upstream_contribution(
            self.fixture.config(baseline),
            self.fixture.root / "recommendations.json",
        )
        self.assertEqual([], report["candidates"])
        self.assertEqual([], report["suppressed"])
        self.assertEqual(
            [equivalent],
            [item["sha"] for item in report["already_in_source"]],
        )

    def test_diagnostics_redact_credentials(self) -> None:
        token = "gh" + "p_" + ("x" * 40)
        message = (
            "https://user:secret@example.invalid/repo "
            f"Authorization: Bearer token-value {token}"
        )
        result = redact(message)
        self.assertNotIn("token-value", result)
        self.assertNotIn("gh" + "p_", result)
        self.assertNotIn("user:secret@", result)
        api_key = "query-api-key-value"
        client_secret = "query-client-secret-value"
        query_result = redact(
            f"https://example.invalid/?api_key={api_key}"
            f"&client-secret={client_secret}"
        )
        self.assertNotIn(api_key, query_result)
        self.assertNotIn(client_secret, query_result)

    def test_diagnostics_redact_complete_authorization_headers(self) -> None:
        authorization_secret = "opaque-" + "credential-value"
        proxy_secret = "proxy-" + "credential-value"
        message = (
            f"Authorization: custom {authorization_secret}\n"
            f"Proxy-Authorization: scheme {proxy_secret}\n"
            "retained diagnostic"
        )

        result = redact(message)

        self.assertNotIn(authorization_secret, result)
        self.assertNotIn(proxy_secret, result)
        self.assertIn("Authorization: [REDACTED]", result)
        self.assertIn("Proxy-Authorization: [REDACTED]", result)
        self.assertIn("retained diagnostic", result)

    def test_diagnostics_redact_complete_pem_private_keys(self) -> None:
        private_key = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "cHJpdmF0ZS1rZXktbWF0ZXJpYWw=\n"
            "-----END RSA PRIVATE KEY-----"
        )

        result = redact(f"before\n{private_key}\nafter")

        self.assertNotIn("cHJpdmF0ZS1rZXktbWF0ZXJpYWw", result)
        self.assertIn("[REDACTED PRIVATE KEY]", result)
        self.assertIn("before", result)
        self.assertIn("after", result)

    def test_secondary_rate_limit_is_retried(self) -> None:
        responses = [
            subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="HTTP 429 secondary rate limit",
            ),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout='{"ok": true}',
                stderr="",
            ),
        ]
        sleeps: list[float] = []
        client = GitHubClient("example/fork", sleep=sleeps.append)
        with mock.patch("forensic_ingest_lib.subprocess.run", side_effect=responses):
            result = client.api("repos/example/fork/issues?state=all")
        self.assertEqual({"ok": True}, result)
        self.assertEqual([30], sleeps)

    def test_atomic_write_uses_exclusive_randomized_temporary_file(self) -> None:
        output = self.fixture.root / "atomic.txt"
        with mock.patch.object(
            Path,
            "open",
            side_effect=AssertionError("Predictable Path.open must not be used"),
        ):
            with mock.patch(
                "forensic_ingest_lib.tempfile.mkstemp",
                wraps=tempfile.mkstemp,
            ) as create_temporary:
                atomic_write_text(output, "one\ntwo\n")
        create_temporary.assert_called_once()
        self.assertEqual(str(output.parent), create_temporary.call_args.kwargs["dir"])
        self.assertEqual(".atomic.txt.", create_temporary.call_args.kwargs["prefix"])
        self.assertEqual(".tmp", create_temporary.call_args.kwargs["suffix"])
        self.assertEqual(b"one\ntwo\n", output.read_bytes())

    def test_python_sources_parse_with_python_3_9_grammar(self) -> None:
        for path in sorted(SCRIPTS.parent.rglob("*.py")):
            with self.subTest(path=path.relative_to(SCRIPTS.parent)):
                ast.parse(
                    path.read_text(encoding="utf-8"),
                    filename=str(path),
                    feature_version=(3, 9),
                )

    def test_safe_workflow_is_a_five_step_activation_outline(self) -> None:
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        workflow = skill.split("## Safe Workflow", 1)[1].split("```text", 1)[0]
        self.assertEqual(5, len(re.findall(r"(?m)^[1-9]\. ", workflow)))

    def test_help_for_every_operation(self) -> None:
        cli = SCRIPTS / "forensic_ingest.py"
        operations = (
            None,
            "analyze",
            "validate",
            "render",
            "publish-github",
            "recommend-upstream-contribution",
        )
        for operation in operations:
            arguments = [sys.executable, str(cli)]
            if operation:
                arguments.append(operation)
            arguments.append("--help")
            result = subprocess.run(
                arguments,
                cwd=Path(__file__).resolve().parents[3],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("usage:", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
