"""Repository-local fixtures for forensic ingest tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from forensic_ingest_lib import GIT_ENVIRONMENT_ALLOWLIST


TEST_ROOT = Path(__file__).resolve().parent


class GitFixture:
    def __init__(self) -> None:
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in GIT_ENVIRONMENT_ALLOWLIST
        }
        self.environment.update(
            GIT_ATTR_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_SYSTEM=os.devnull,
            GIT_TERMINAL_PROMPT="0",
        )
        self.temporary = tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture User")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgSign", "false")

    def close(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise AssertionError(
                f"git {' '.join(arguments)} failed:\n{result.stdout}\n{result.stderr}"
            )
        return result.stdout.strip()

    def write(self, relative: str, content: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message: str, files: dict[str, str]) -> str:
        for path, content in files.items():
            self.write(path, content)
        self.git("add", "--all")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def config(
        self,
        baseline: str,
        *,
        source_ref: str = "source",
        fork_ref: str = "fork",
        initial_selection: str = "after-baseline",
    ) -> Path:
        path = self.root / "config.json"
        value: dict[str, Any] = {
            "schema_version": 1,
            "profile_id": "fixture",
            "repository_path": str(self.repo),
            "repository_identity": "example/repository",
            "source_ref": source_ref,
            "fork_ref": fork_ref,
            "initial_selection": initial_selection,
            "initial_baseline_sha": baseline,
            "github": {
                "repository": "example/fork",
                "labels": ["fixture"],
            },
            "contribution_suppression": {
                "path_globs": [
                    ".agentic-agile/**",
                    ".github/skills/**",
                    "docs/agentic-agile/**",
                ],
                "subject_regexes": ["(?i)governance overlay"],
            },
        }
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def state(self, value: dict[str, Any] | None = None) -> Path:
        path = self.root / "state.json"
        if value is not None:
            path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def create_divergence(self) -> tuple[str, str, str]:
        baseline = self.commit("baseline", {"README.md": "baseline\n"})
        self.git("branch", "fork", baseline)
        self.git("switch", "-c", "source")
        first = self.commit("source one", {"src/one.py": "one = 1\n"})
        second = self.commit("source two", {"src/two.py": "two = 2\n"})
        return baseline, first, second

    def create_submodule_divergence(
        self, *, same_patch: bool = True
    ) -> tuple[str, str, str]:
        """Create gitlink updates with a populated, entirely local submodule."""
        first = self.commit("first anchor", {"README.md": "first\n"})
        second = self.commit("second anchor", {"README.md": "second\n"})
        third = self.commit("third anchor", {"README.md": "third\n"})
        self.git("clone", "--no-hardlinks", str(self.repo), "module")
        self.git("-C", "module", "checkout", "--detach", first)
        self.write(
            ".gitmodules",
            '[submodule "module"]\n'
            "\tpath = module\n"
            "\turl = https://example.invalid/module\n",
        )
        baseline = self.commit("baseline gitlink", {})
        self.git("branch", "fork", baseline)
        self.git("switch", "-c", "source")
        self.git("-C", "module", "checkout", "--detach", second)
        changed = self.commit("source module update", {})
        self.git("switch", "fork")
        self.git(
            "-C", "module", "checkout", "--detach",
            second if same_patch else third,
        )
        incorporated = self.commit("independent fork module update", {})
        return baseline, changed, incorporated
