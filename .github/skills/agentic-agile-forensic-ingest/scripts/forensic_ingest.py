#!/usr/bin/env python3
"""Deterministic Agentic-Agile forensic ingest command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from forensic_ingest_lib import (
    ForensicIngestError,
    analyze_repository,
    publish_github,
    recommend_upstream_contribution,
    redact,
    render_drafts,
    validate_manifest,
)


def _path(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze immutable Git evidence, render deterministic issue drafts, "
            "and explicitly publish verified records to GitHub."
        )
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    analyze = subparsers.add_parser(
        "analyze",
        help="Create a deterministic, host-neutral run manifest without network writes.",
    )
    analyze.add_argument("--config", required=True, type=_path)
    analyze.add_argument("--state", required=True, type=_path)
    analyze.add_argument("--output", required=True, type=_path)

    validate = subparsers.add_parser(
        "validate",
        help="Validate hashes, coverage, topology, refs, baseline, and optional drafts.",
    )
    validate.add_argument("--config", required=True, type=_path)
    validate.add_argument("--manifest", required=True, type=_path)
    validate.add_argument("--drafts", type=_path)
    validate.add_argument(
        "--state",
        type=_path,
        help="Optional ingest state used to verify the recurring selection baseline.",
    )

    render = subparsers.add_parser(
        "render",
        help="Render local GitHub-neutral issue drafts; performs no remote writes.",
    )
    render.add_argument("--manifest", required=True, type=_path)
    render.add_argument("--output", required=True, type=_path)

    publish = subparsers.add_parser(
        "publish-github",
        help=(
            "Dry-run by default: validate inputs and print the plan without "
            "contacting GitHub. With --execute, create/verify GitHub issues and "
            "native sub-issues, then advance state after remote verification."
        ),
    )
    publish.add_argument("--config", required=True, type=_path)
    publish.add_argument("--manifest", required=True, type=_path)
    publish.add_argument("--drafts", required=True, type=_path)
    publish.add_argument("--state", required=True, type=_path)
    publish.add_argument("--publication-state", required=True, type=_path)
    publish.add_argument(
        "--execute",
        action="store_true",
        help="Perform GitHub writes and state checkpoints; omitted means dry-run.",
    )

    recommend = subparsers.add_parser(
        "recommend-upstream-contribution",
        help=(
            "Create a local fork-only recommendation report; never contacts or "
            "mutates upstream."
        ),
    )
    recommend.add_argument("--config", required=True, type=_path)
    recommend.add_argument("--output", required=True, type=_path)
    return parser


def main(arguments: list[str] | None = None) -> int:
    parser = build_parser()
    options = parser.parse_args(arguments)
    try:
        if options.operation == "analyze":
            result = analyze_repository(options.config, options.state, options.output)
        elif options.operation == "validate":
            result = validate_manifest(
                options.config,
                options.manifest,
                options.drafts,
                state_path=options.state,
            )
        elif options.operation == "render":
            result = render_drafts(options.manifest, options.output)
        elif options.operation == "publish-github":
            result = publish_github(
                options.config,
                options.manifest,
                options.drafts,
                options.state,
                options.publication_state,
                execute=options.execute,
            )
        elif options.operation == "recommend-upstream-contribution":
            result = recommend_upstream_contribution(options.config, options.output)
        else:
            parser.error(f"Unsupported operation: {options.operation}")
            return 2
    except (ForensicIngestError, OSError, ValueError) as exc:
        print(f"forensic-ingest failed: {redact(exc)}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
