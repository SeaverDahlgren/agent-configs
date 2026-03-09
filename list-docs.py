#!/usr/bin/env python3
"""
Scan a docs directory for Markdown files and print a simple docs listing.

Expected front matter keys:
  - summary: short description of the document
  - read_when: list of hints/triggers for when the document is useful
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable


DEFAULT_IGNORED_DIRS = {"archive", "research"}
AGENT_INSTRUCTIONS = (
    'NOTE: Keep docs up to date as behavior changes. When your task matches any "Read '
    'when" hint above, read that doc before coding, and suggest new coverage when it '
    'is missing.'
)


def walk_markdown_files(root: Path, ignored_dirs: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def _extract_front_matter_block(text: str) -> str | None:
    # Front matter must be at the start of file and wrapped with --- delimiters.
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.DOTALL)
    return match.group(1) if match else None


def parse_front_matter(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    block = _extract_front_matter_block(text)
    if not block:
        return "", []

    summary = ""
    read_when: list[str] = []
    lines = block.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if stripped.startswith("summary:"):
            value = stripped[len("summary:") :].strip().strip("'\"")
            summary = value
            i += 1
            continue

        if stripped.startswith("read_when:"):
            remainder = stripped[len("read_when:") :].strip()

            # Inline list: read_when: [foo, bar]
            if remainder.startswith("[") and remainder.endswith("]"):
                inner = remainder[1:-1].strip()
                if inner:
                    read_when.extend(
                        item.strip().strip("'\"")
                        for item in inner.split(",")
                        if item.strip()
                    )
                i += 1
                continue

            # Single inline string: read_when: database work
            if remainder:
                read_when.append(remainder.strip("'\""))
                i += 1
                continue

            # Multi-line YAML list:
            # read_when:
            #   - React hooks
            #   - API refactors
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped:
                    i += 1
                    continue
                if re.match(r"^\s*-\s+", next_line):
                    item = re.sub(r"^\s*-\s+", "", next_line).strip().strip("'\"")
                    if item:
                        read_when.append(item)
                    i += 1
                    continue
                # Stop if next key begins or list ends.
                if re.match(r"^\s*\w[\w-]*\s*:", next_line):
                    break
                i += 1
            continue

        i += 1

    return summary, read_when


def render_listing(rows: Iterable[tuple[Path, str, list[str]]]) -> str:
    lines = ["Listing all markdown files in docs folder:"]

    for path, summary, read_when in rows:
        summary_text = summary if summary else "No summary"
        hints_text = "; ".join(read_when) if read_when else "None"
        lines.append(f"{path.name} - {summary_text}")
        lines.append(f"  Read when: {hints_text}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown table of contents from docs front matter."
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Directory to scan for markdown files (default: docs).",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=sorted(DEFAULT_IGNORED_DIRS),
        help="Directory names to ignore anywhere in the path.",
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"Error: docs directory not found: {docs_dir}")
        return 1

    ignored = set(args.ignore)
    files = walk_markdown_files(docs_dir, ignored)
    rows = [(path, *parse_front_matter(path)) for path in files]

    print(render_listing(rows))
    print(AGENT_INSTRUCTIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
