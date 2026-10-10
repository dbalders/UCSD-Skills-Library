from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import public_skill_validator as validator  # noqa: E402
import sync_external_skills as sync  # noqa: E402


LICENSE = "MIT License\n\nCopyright (c) 2026 Example\n"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class SyncExternalSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        base = Path(self.tempdir.name)
        self.root = base / "library"
        self.root.mkdir()
        (self.root / "LICENSE").write_text(LICENSE, encoding="utf-8")
        self.remotes = base / "remotes"
        self.upstream = self.remotes / "example" / "kit.git"
        self.upstream.mkdir(parents=True)
        git(self.upstream, "init", "-q", "-b", "main")
        git(self.upstream, "config", "user.email", "test@example.com")
        git(self.upstream, "config", "user.name", "Test")
        (self.upstream / "LICENSE").write_text(LICENSE, encoding="utf-8")
        self.write_upstream_skill()
        self.tag("v1.0.0")
        patcher = mock.patch.dict(os.environ, {"EXTERNAL_SKILLS_GIT_BASE": f"file://{self.remotes}"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_upstream_skill(self, body: str = "# Example\n", name: str = "example-skill") -> None:
        skill = self.upstream / "library" / "example-skill"
        (skill / "references").mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Use when testing sync.\n---\n\n{body}",
            encoding="utf-8",
        )
        (skill / "references" / "notes.md").write_text("notes\n", encoding="utf-8")
        (skill / ".DS_Store").write_text("noise", encoding="utf-8")

    def tag(self, tag: str) -> None:
        git(self.upstream, "add", "-A")
        git(self.upstream, "commit", "-q", "-m", tag)
        git(self.upstream, "tag", tag)

    def entry(self, **overrides: str) -> dict:
        entry = {
            "name": "example-skill",
            "collection": "community",
            "repository": "example/kit",
            "path": "library/example-skill",
            "track": "pinned",
            "ref": "v1.0.0",
        }
        entry.update(overrides)
        return entry

    def test_sync_copies_folder_with_license_and_records_commit(self) -> None:
        entry = self.entry()

        result = sync.sync_skill(self.root, entry)

        destination = self.root / "community" / "example-skill"
        self.assertIsNotNone(result)
        self.assertEqual((destination / "LICENSE").read_text(encoding="utf-8"), LICENSE)
        self.assertTrue((destination / "references" / "notes.md").is_file())
        self.assertFalse((destination / ".DS_Store").exists())
        self.assertEqual(entry["commit"], git(self.upstream, "rev-parse", "v1.0.0"))
        self.assertIsNone(sync.sync_skill(self.root, entry))

    def test_latest_release_moves_ref_and_replaces_removed_files(self) -> None:
        entry = self.entry(track="latest-release")
        with mock.patch.object(sync, "latest_release_tag", return_value="v1.0.0"):
            sync.sync_skill(self.root, entry)
        (self.upstream / "library" / "example-skill" / "references" / "notes.md").unlink()
        self.write_upstream_skill(body="# Updated\n")
        (self.upstream / "library" / "example-skill" / "references" / "notes.md").unlink()
        self.tag("v1.1.0")

        with mock.patch.object(sync, "latest_release_tag", return_value="v1.1.0"):
            result = sync.sync_skill(self.root, entry)

        destination = self.root / "community" / "example-skill"
        self.assertEqual((result.previous_ref, result.ref), ("v1.0.0", "v1.1.0"))
        self.assertEqual(entry["ref"], "v1.1.0")
        self.assertIn("# Updated", (destination / "SKILL.md").read_text(encoding="utf-8"))
        self.assertFalse((destination / "references" / "notes.md").exists())

    def test_release_without_folder_changes_keeps_manifest(self) -> None:
        entry = self.entry(track="latest-release")
        with mock.patch.object(sync, "latest_release_tag", return_value="v1.0.0"):
            sync.sync_skill(self.root, entry)
        (self.upstream / "README.md").write_text("unrelated\n", encoding="utf-8")
        self.tag("v1.0.1")

        with mock.patch.object(sync, "latest_release_tag", return_value="v1.0.1"):
            self.assertIsNone(sync.sync_skill(self.root, entry))
        self.assertEqual(entry["ref"], "v1.0.0")

    def test_rejects_upstream_with_different_license(self) -> None:
        (self.upstream / "LICENSE").write_text("Apache License\n", encoding="utf-8")
        self.tag("v2.0.0")

        with self.assertRaisesRegex(sync.SyncError, "differs from this repository's LICENSE"):
            sync.sync_skill(self.root, self.entry(ref="v2.0.0"))
        self.assertFalse((self.root / "community" / "example-skill").exists())

    def test_rejects_frontmatter_name_mismatch(self) -> None:
        self.write_upstream_skill(name="other-skill")
        self.tag("v2.0.0")

        with self.assertRaisesRegex(sync.SyncError, "frontmatter name"):
            sync.sync_skill(self.root, self.entry(ref="v2.0.0"))

    def test_rejects_symlinks(self) -> None:
        (self.upstream / "library" / "example-skill" / "link").symlink_to("/etc/hosts")
        self.tag("v2.0.0")

        with self.assertRaisesRegex(sync.SyncError, "symlinks"):
            sync.sync_skill(self.root, self.entry(ref="v2.0.0"))

    def test_rejects_unsafe_entries(self) -> None:
        for overrides in (
            {"path": "../outside"},
            {"collection": "skills"},
            {"repository": "not-a-repo"},
            {"track": "main"},
            {"ref": "--upload-pack=x"},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(sync.SyncError):
                    sync.validate_entry(self.entry(**overrides))

    def test_validator_warns_on_hand_edits_to_synced_skills(self) -> None:
        (self.root / "external-skills.json").write_text(
            '{"skills": [{"name": "example-skill", "collection": "community", '
            '"repository": "example/kit"}]}',
            encoding="utf-8",
        )
        edited = Path("community/example-skill/SKILL.md")

        hand_edit = validator.validate_external_skill_edits(self.root, [edited])
        synced = validator.validate_external_skill_edits(
            self.root, [edited, Path("external-skills.json")]
        )

        self.assertTrue(hand_edit.ok)
        self.assertEqual(len(hand_edit.warnings), 1)
        self.assertIn("example/kit", hand_edit.warnings[0])
        self.assertEqual(synced.warnings, ())


if __name__ == "__main__":
    unittest.main()
