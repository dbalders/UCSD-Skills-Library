#!/usr/bin/env python3
"""Copy skills maintained in other repositories into this library.

Each entry in external-skills.json names a source repository, the skill folder
inside it, and where the copy lives here. The sync replaces the local folder
with the upstream folder at the selected release, adds the repository LICENSE,
and records the synced ref and commit in the manifest so reviewers can see
exactly what changed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from public_skill_validator import ALLOWED_ROOTS, parse_frontmatter  # noqa: E402


MANIFEST_NAME = "external-skills.json"
TRACK_MODES = {"latest-release", "pinned"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
REQUIRED_FIELDS = ("name", "collection", "repository", "path", "track", "ref")


class SyncError(Exception):
    pass


@dataclass
class SyncResult:
    name: str
    repository: str
    previous_ref: str
    ref: str
    commit: str


def load_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncError(f"{MANIFEST_NAME} not found at {root}") from exc
    except json.JSONDecodeError as exc:
        raise SyncError(f"{MANIFEST_NAME} is not valid JSON: {exc}") from exc
    entries = manifest.get("skills")
    if not isinstance(entries, list):
        raise SyncError(f'{MANIFEST_NAME} must contain a "skills" list.')
    seen: set[str] = set()
    for entry in entries:
        validate_entry(entry)
        if entry["name"] in seen:
            raise SyncError(f"Duplicate external skill name: {entry['name']}")
        seen.add(entry["name"])
    return manifest


def write_manifest(root: Path, manifest: dict) -> None:
    (root / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def validate_entry(entry: object) -> None:
    if not isinstance(entry, dict):
        raise SyncError("Each external skill entry must be an object.")
    missing = [field for field in REQUIRED_FIELDS if not entry.get(field)]
    label = entry.get("name") or "<unnamed>"
    if missing:
        raise SyncError(f"{label}: missing required field(s): {', '.join(missing)}")
    if not NAME_RE.fullmatch(entry["name"]):
        raise SyncError(f"{label}: name must be lowercase hyphenated.")
    if entry["collection"] not in ALLOWED_ROOTS:
        raise SyncError(f"{label}: collection must be one of {sorted(ALLOWED_ROOTS)}.")
    if not REPOSITORY_RE.fullmatch(entry["repository"]):
        raise SyncError(f"{label}: repository must look like owner/name.")
    source_path = Path(entry["path"])
    if source_path.is_absolute() or ".." in source_path.parts or not source_path.parts:
        raise SyncError(f"{label}: path must be relative to the source repository root.")
    if entry["track"] not in TRACK_MODES:
        raise SyncError(f"{label}: track must be one of {sorted(TRACK_MODES)}.")
    if not REF_RE.fullmatch(entry["ref"]):
        raise SyncError(f"{label}: ref must be a tag or branch name.")


def latest_release_tag(repository: str) -> str:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
    )
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None
    if github_token is not None:
        request.add_header("Authorization", f"Bearer {github_token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            tag = json.load(response).get("tag_name", "")
    except OSError as exc:
        raise SyncError(f"Could not read the latest release of {repository}: {exc}") from exc
    if not tag or not REF_RE.fullmatch(tag):
        raise SyncError(f"{repository} has no usable latest release tag.")
    return tag


def checkout_source(repository: str, ref: str, path: str, destination: Path) -> str:
    """Sparse-clone one folder of repository at ref and return the commit SHA."""
    base = os.environ.get("EXTERNAL_SKILLS_GIT_BASE", "https://github.com").rstrip("/")
    git = ["git", "-c", "advice.detachedHead=false"]
    run([*git, "clone", "--quiet", "--depth", "1", "--branch", ref, "--filter=blob:none",
         "--sparse", f"{base}/{repository}.git", str(destination)])
    run([*git, "-C", str(destination), "sparse-checkout", "set", path])
    return run([*git, "-C", str(destination), "rev-parse", "HEAD"]).strip()


def run(command: list[str]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SyncError(f"{' '.join(command[:4])} failed: {completed.stderr.strip()}")
    return completed.stdout


def sync_skill(root: Path, entry: dict) -> SyncResult | None:
    """Sync one entry in place. Returns a result only when the copy changed."""
    previous_ref = entry["ref"]
    ref = latest_release_tag(entry["repository"]) if entry["track"] == "latest-release" else previous_ref
    expected_license = (root / "LICENSE").read_bytes()
    destination = root / entry["collection"] / entry["name"]

    with tempfile.TemporaryDirectory() as tmp:
        checkout = Path(tmp) / "source"
        commit = checkout_source(entry["repository"], ref, entry["path"], checkout)
        source = checkout / entry["path"]
        check_source(entry, checkout, source, expected_license)

        staged = Path(tmp) / "staged"
        shutil.copytree(source, staged, ignore=ignore_dotfiles)
        (staged / "LICENSE").write_bytes(expected_license)

        # A release that leaves this folder untouched is not worth a pull request;
        # the manifest keeps pointing at the last release whose content we took.
        if destination.exists() and same_tree(staged, destination) and entry.get("commit"):
            return None
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged, destination)

    entry["ref"] = ref
    entry["commit"] = commit
    return SyncResult(entry["name"], entry["repository"], previous_ref, ref, commit)


def check_source(entry: dict, checkout: Path, source: Path, expected_license: bytes) -> None:
    label = f"{entry['name']} ({entry['repository']}:{entry['path']})"
    if not (source / "SKILL.md").is_file():
        raise SyncError(f"{label}: SKILL.md not found at the selected ref.")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise SyncError(f"{label}: symlinks are not allowed ({path.relative_to(source)}).")
    errors: list[str] = []
    meta = parse_frontmatter(source / "SKILL.md", checkout, errors)
    if errors:
        raise SyncError(f"{label}: {'; '.join(errors)}")
    if meta.get("name", "").strip("'\"") != entry["name"]:
        raise SyncError(f"{label}: frontmatter name does not match '{entry['name']}'.")
    # Only take upstream content published under the same MIT terms and copyright
    # holder, so adding this repository's LICENSE keeps the upstream notice intact.
    repository_license = checkout / "LICENSE"
    folder_license = source / "LICENSE"
    for license_path in (repository_license, folder_license):
        if license_path is folder_license and not license_path.exists():
            continue
        if not license_path.is_file() or license_path.read_bytes() != expected_license:
            raise SyncError(
                f"{label}: {license_path.relative_to(checkout)} is missing or differs from "
                "this repository's LICENSE; review the upstream license manually."
            )


def ignore_dotfiles(_directory: str, names: list[str]) -> list[str]:
    return [name for name in names if name.startswith(".")]


def same_tree(left: Path, right: Path) -> bool:
    def files(base: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(base)): path.read_bytes()
            for path in base.rglob("*")
            if path.is_file()
        }

    return files(left) == files(right)


def write_pull_request(directory: Path, results: list[SyncResult]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    if len(results) == 1:
        result = results[0]
        title = f"Sync {result.name} from {result.repository} {result.ref}"
    else:
        title = f"Sync {len(results)} external skills"
    lines = [
        f"Automated sync from `{MANIFEST_NAME}`.",
        "",
    ]
    for result in results:
        source = f"https://github.com/{result.repository}"
        line = f"- `{result.name}` from [{result.repository}]({source}) at `{result.ref}` ({result.commit[:12]})"
        if result.previous_ref != result.ref:
            line += f": [changes since {result.previous_ref}]({source}/compare/{result.previous_ref}...{result.ref})"
        lines.append(line)
    lines += [
        "",
        "Review the upstream changes before merging. Local edits to synced folders are",
        "overwritten by the next sync, so request changes upstream instead.",
    ]
    (directory / "title.txt").write_text(title + "\n", encoding="utf-8")
    (directory / "body.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--skill", action="append", help="Sync only this skill (repeatable).")
    parser.add_argument("--list", action="store_true", help="Print managed skill names and exit.")
    parser.add_argument("--pr-output", type=Path, help="Write title.txt and body.md when anything changed.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        manifest = load_manifest(root)
        entries = manifest["skills"]
        if args.list:
            print("\n".join(entry["name"] for entry in entries))
            return 0
        if args.skill:
            unknown = set(args.skill) - {entry["name"] for entry in entries}
            if unknown:
                raise SyncError(f"Not in {MANIFEST_NAME}: {', '.join(sorted(unknown))}")
            entries = [entry for entry in entries if entry["name"] in args.skill]

        results: list[SyncResult] = []
        for entry in entries:
            result = sync_skill(root, entry)
            if result is None:
                print(f"{entry['name']}: up to date at {entry['ref']}")
                continue
            results.append(result)
            print(f"{result.name}: synced {result.repository} {result.ref} ({result.commit[:12]})")
    except SyncError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    if results:
        write_manifest(root, manifest)
        if args.pr_output:
            write_pull_request(args.pr_output, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
