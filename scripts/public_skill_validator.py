#!/usr/bin/env python3
"""Validate public UCSD skill layout, contributor placement, and leak safety."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ALLOWED_ROOTS = {"tritonai", "community"}
FORBIDDEN_FRONTMATTER = {"catalog", "tier", "publicationStatus", "category", "status"}
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".woff",
    ".woff2",
    ".ttf",
}
SENSITIVE_FILENAMES = {".env", ".npmrc", ".pypirc"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
LEAK_PATTERNS = (
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID"),
    (re.compile(r"https://[A-Za-z0-9._~!$&+,;=:%_-]+@github\.com"), "credential-bearing GitHub URL"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub fine-grained token"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN[A-Z ]*PRIVATE KEY-----"), "private key block"),
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)[\"']?\b(?:[a-z0-9]+[_-])*(api[_-]?key|secret|token|password|passwd|pwd)"
    r"(?:[_-][a-z0-9]+)*\b[\"']?\s*[:=]\s*"
    r"(?:(?P<quote>[\"'])(?P<quoted>[^\n\"']{12,})(?P=quote)|(?P<bare>[A-Za-z0-9_./+=:@-]{12,}))"
)
PLACEHOLDER_MARKERS = (
    "...",
    "changeme",
    "dummy",
    "example",
    "fake",
    "placeholder",
    "redacted",
    "replace-me",
)


@dataclass(frozen=True)
class ValidationResult:
    label: str
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    def output(self) -> str:
        lines = [
            *(f"WARN {redact_public_text(item)}" for item in self.warnings),
            *(f"ERROR {redact_public_text(item)}" for item in self.errors),
            *(redact_public_text(item) for item in self.notes),
        ]
        return "\n".join(lines) or f"{self.label}: OK"


def validate_repository(
    root: Path,
    changed_files: Iterable[Path],
    contributor: str,
    allowlist_path: Path | None = None,
) -> list[ValidationResult]:
    root = root.resolve()
    changed = tuple(changed_files)
    return [
        validate_contributor_placement(contributor, changed, allowlist_path),
        validate_public_skill_format(root),
        validate_changed_file_leaks(root, changed),
    ]


def validate_contributor_placement(
    contributor: str,
    changed_files: Iterable[Path],
    allowlist_path: Path | None = None,
) -> ValidationResult:
    tritonai_changes = sorted(
        str(path) for path in changed_files if path.parts and path.parts[0] == "tritonai"
    )
    if not tritonai_changes:
        return ValidationResult(
            "Contributor placement",
            notes=("No public contributor placement action is being reported.",),
        )

    if allowlist_path is None or not allowlist_path.exists():
        return ValidationResult(
            "Contributor placement",
            warnings=(
                "TritonAI placement requires maintainer verification before merge; "
                "the private author allowlist is unavailable in this validation context.",
            ),
            notes=(f"Changed tritonai/ path count: {len(tritonai_changes)}",),
        )

    try:
        allowed = read_allowlist(allowlist_path)
    except OSError as exc:
        return ValidationResult(
            "Contributor placement",
            errors=(f"Could not read the private author allowlist: {exc}",),
        )

    if normalize_github_login(contributor) in allowed:
        return ValidationResult(
            "Contributor placement",
            notes=("No public contributor placement action is being reported.",),
        )

    errors = [
        "TritonAI placement requires maintainer verification before merge.",
        "Move the skill contribution to community/<skill-name>/ and add frontmatter "
        "maintainer: unless a maintainer confirms private placement approval.",
        *(f"Changed tritonai/ path: {path}" for path in tritonai_changes[:50]),
    ]
    if len(tritonai_changes) > 50:
        errors.append(f"... and {len(tritonai_changes) - 50} more tritonai/ path(s).")
    return ValidationResult("Contributor placement", errors=tuple(errors))


def read_allowlist(path: Path) -> set[str]:
    allowed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        allowed.update(
            normalized
            for token in re.split(r"[\s,]+", line)
            if (normalized := normalize_github_login(token))
        )
    return allowed


def normalize_github_login(value: str) -> str:
    value = value.strip().lower()
    value = value.removeprefix("@")
    value = value.removeprefix("https://github.com/")
    value = value.removeprefix("http://github.com/")
    value = value.strip("/")
    if "/" in value:
        value = value.rsplit("/", 1)[-1]
    return value


def validate_public_skill_format(root: Path) -> ValidationResult:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    skill_files = sorted(
        path for root_name in ALLOWED_ROOTS for path in root.glob(f"{root_name}/*/SKILL.md")
    )
    if not skill_files:
        errors.append(
            "No public skills found. Add tritonai/<skill-name>/SKILL.md or "
            "community/<skill-name>/SKILL.md."
        )

    for path in sorted(root.glob("*/SKILL.md")):
        rel = path.relative_to(root)
        if rel.parts[0] not in ALLOWED_ROOTS and not rel.parts[0].startswith("."):
            errors.append(f"{rel}: public skills must live under tritonai/ or community/, not at repo root.")

    if (root / "skills").exists():
        errors.append("Do not create a top-level skills/ folder in this public repository.")

    name_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    for skill in skill_files:
        rel = skill.relative_to(root)
        collection = rel.parts[0]
        folder = skill.parent.name
        meta = parse_frontmatter(skill, root, errors)
        if not name_re.fullmatch(folder):
            errors.append(f"{rel}: skill folder must be lowercase hyphenated: {folder}")
        if meta.get("name", "").strip("'\"") != folder:
            errors.append(f"{rel}: frontmatter name must match folder name '{folder}'.")
        if not meta.get("description"):
            errors.append(f"{rel}: frontmatter description is required.")
        if collection == "community" and not meta.get("maintainer"):
            errors.append(f"{rel}: community skills must include frontmatter maintainer:")
        extra = FORBIDDEN_FRONTMATTER & set(meta)
        if extra:
            errors.append(
                f"{rel}: remove generated catalog/storefront metadata: " + ", ".join(sorted(extra))
            )
        if "allowed-tools" in meta:
            tools = [tool.strip() for tool in meta["allowed-tools"].split(",") if tool.strip()]
            if len(tools) > 6:
                warnings.append(f"{rel}: allowed-tools has {len(tools)} entries; confirm each one is needed.")

    return ValidationResult(
        "Public skill format",
        errors=tuple(errors),
        warnings=tuple(warnings),
        notes=(f"Skills found: {len(skill_files)}",),
    )


def parse_frontmatter(path: Path, root: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(root)
    if not text.startswith("---\n"):
        errors.append(f"{rel}: SKILL.md must start with YAML frontmatter.")
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{rel}: YAML frontmatter is not closed.")
        return {}
    data: dict[str, str] = {}
    for raw in parts[1].splitlines():
        if not raw or raw[:1].isspace() or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_changed_file_leaks(root: Path, changed_files: Iterable[Path]) -> ValidationResult:
    root = root.resolve()
    findings: list[str] = []
    for rel in changed_files:
        if rel.is_absolute() or ".." in rel.parts:
            findings.append(f"{rel}: changed path must be repository-relative.")
            continue
        for label in scan_text_for_leaks(str(rel)):
            findings.append(f"{rel}: changed path contains possible {label}.")
        path = root / rel
        if not path.exists() or not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if path.name in SENSITIVE_FILENAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append(f"{rel}: sensitive file type should not be committed.")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for regex, label in LEAK_PATTERNS:
            match = regex.search(text)
            if match:
                findings.append(f"{rel}:{line_for(text, match.start())}: possible {label}.")
        for match in CREDENTIAL_ASSIGNMENT.finditer(text):
            value = (match.group("quoted") or match.group("bare") or "").strip()
            if is_placeholder_value(value):
                continue
            findings.append(
                f"{rel}:{line_for(text, match.start())}: possible hardcoded credential-looking value."
            )
            break
    return ValidationResult("High-confidence leak scan", errors=tuple(findings))


def scan_text_for_leaks(text: str) -> list[str]:
    labels = [label for regex, label in LEAK_PATTERNS if regex.search(text)]
    for match in CREDENTIAL_ASSIGNMENT.finditer(text):
        value = (match.group("quoted") or match.group("bare") or "").strip()
        if not is_placeholder_value(value):
            labels.append("hardcoded credential-looking value")
            break
    return labels


def is_placeholder_value(value: str) -> bool:
    normalized = value.strip()
    lowered = normalized.lower()
    if re.fullmatch(r"[A-Z][A-Z0-9_]{5,}", normalized):
        return True
    if normalized.startswith(("$", "{{", "<")):
        return True
    if lowered.startswith(("env.", "os.environ", "process.env", "secrets.")):
        return True
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def line_for(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def redact_public_text(text: str) -> str:
    redacted = re.sub(r"https://x-access-token:[^@\s]+@", "https://x-access-token:***@", text)
    redacted = re.sub(
        r"https://(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})@github\.com",
        "https://***@github.com",
        redacted,
    )
    redacted = re.sub(
        r"https://([^/\s:@]+):(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|[^@\s]{20,})@github\.com",
        r"https://\1:***@github.com",
        redacted,
    )
    redacted = re.sub(r"github_pat_[A-Za-z0-9_]{20,}", "github_pat_***", redacted)
    redacted = re.sub(r"gh[pousr]_[A-Za-z0-9]{30,}", "gh*_***", redacted)
    redacted = re.sub(r"AKIA[0-9A-Z]{16}", "AKIA***", redacted)
    redacted = re.sub(r"xox[baprs]-[A-Za-z0-9-]{10,}", "xox*-***", redacted)
    redacted = re.sub(
        r"(?i)([\"']?\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|secret|token|password|passwd|pwd)"
        r"(?:[_-][a-z0-9]+)*\b[\"']?\s*[:=]\s*([\"']))[^\n\"']{12,}([\"'])",
        r"\1***\3",
        redacted,
    )
    return redacted


def write_summary(path: Path, results: Iterable[ValidationResult]) -> None:
    lines = ["# Public Skill Preflight", ""]
    for result in results:
        lines.extend((f"## {result.label}", ""))
        lines.extend(f"- Error: {redact_public_text(item)}" for item in result.errors)
        lines.extend(f"- Warning: {redact_public_text(item)}" for item in result.warnings)
        lines.extend(f"- {redact_public_text(item)}" for item in result.notes)
        if not result.errors and not result.warnings and not result.notes:
            lines.append("- Passed.")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def github_escape(value: str) -> str:
    return redact_public_text(value).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--changed-files", type=Path, required=True)
    parser.add_argument("--contributor", default="")
    parser.add_argument("--allowlist", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--github-annotations", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed = [
        Path(line.strip())
        for line in args.changed_files.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results = validate_repository(args.root, changed, args.contributor, args.allowlist)
    if args.summary:
        write_summary(args.summary, results)
    for result in results:
        for warning in result.warnings:
            prefix = "::warning::" if args.github_annotations else "WARN "
            print(prefix + github_escape(warning))
        for error in result.errors:
            prefix = "::error::" if args.github_annotations else "ERROR "
            print(prefix + github_escape(error))
        for note in result.notes:
            print(redact_public_text(note))
    return 1 if any(not result.ok for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
