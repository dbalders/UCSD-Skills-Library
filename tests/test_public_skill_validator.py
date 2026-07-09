from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import public_skill_validator as validator  # noqa: E402


class PublicSkillValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_skill(
        self,
        collection: str = "community",
        folder: str = "example-skill",
        *,
        name: str | None = None,
        description: str = "Use when testing a public example skill.",
        maintainer: str | None = "Example Team",
        extra: str = "",
    ) -> Path:
        skill = self.root / collection / folder / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        fields = [f"name: {name or folder}", f"description: {description}"]
        if maintainer is not None:
            fields.append(f"maintainer: {maintainer}")
        if extra:
            fields.append(extra)
        skill.write_text("---\n" + "\n".join(fields) + "\n---\n\n# Example\n", encoding="utf-8")
        return skill

    def test_tritonai_change_without_allowlist_is_advisory(self) -> None:
        result = validator.validate_contributor_placement(
            "someone", [Path("tritonai/example-skill/SKILL.md")]
        )

        self.assertTrue(result.ok)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("maintainer verification", result.warnings[0])
        self.assertNotIn("someone", result.output())

    def test_allowlisted_tritonai_author_has_no_public_action(self) -> None:
        allowlist = self.root / "allowlist.txt"
        allowlist.write_text("@Trusted-Author # team member\n", encoding="utf-8")

        result = validator.validate_contributor_placement(
            "https://github.com/trusted-author/",
            [Path("tritonai/example-skill/SKILL.md")],
            allowlist,
        )

        self.assertTrue(result.ok)
        self.assertFalse(result.warnings)
        self.assertIn("No public contributor placement action", result.output())

    def test_non_allowlisted_tritonai_author_is_blocked(self) -> None:
        allowlist = self.root / "allowlist.txt"
        allowlist.write_text("trusted-author\n", encoding="utf-8")

        result = validator.validate_contributor_placement(
            "other-author", [Path("tritonai/example-skill/SKILL.md")], allowlist
        )

        self.assertFalse(result.ok)
        self.assertIn("community/<skill-name>/", result.output())
        self.assertNotIn("trusted-author", result.output())
        self.assertNotIn("other-author", result.output())

    def test_valid_public_skill_format_passes(self) -> None:
        self.write_skill()

        result = validator.validate_public_skill_format(self.root)

        self.assertTrue(result.ok, result.output())
        self.assertIn("Skills found: 1", result.output())

    def test_community_skill_requires_maintainer(self) -> None:
        self.write_skill(maintainer=None)

        result = validator.validate_public_skill_format(self.root)

        self.assertFalse(result.ok)
        self.assertIn("must include frontmatter maintainer", result.output())

    def test_name_mismatch_and_storefront_metadata_are_blocked(self) -> None:
        self.write_skill(name="different-name", extra="catalog: public")

        result = validator.validate_public_skill_format(self.root)

        self.assertFalse(result.ok)
        self.assertIn("frontmatter name must match", result.output())
        self.assertIn("catalog", result.output())

    def test_root_level_skill_is_blocked(self) -> None:
        self.write_skill()
        root_skill = self.root / "misplaced-skill" / "SKILL.md"
        root_skill.parent.mkdir()
        root_skill.write_text("---\nname: misplaced-skill\ndescription: Test.\n---\n", encoding="utf-8")

        result = validator.validate_public_skill_format(self.root)

        self.assertFalse(result.ok)
        self.assertIn("not at repo root", result.output())

    def test_token_is_detected_without_echoing_value(self) -> None:
        path = Path("community/example-skill/reference.txt")
        target = self.root / path
        target.parent.mkdir(parents=True)
        token = "ghp_" + ("A" * 36)
        target.write_text(f"credential={token}\n", encoding="utf-8")

        result = validator.validate_changed_file_leaks(self.root, [path])

        self.assertFalse(result.ok)
        self.assertIn("GitHub token", result.output())
        self.assertNotIn(token, result.output())

    def test_placeholder_credentials_are_allowed(self) -> None:
        path = Path("community/example-skill/reference.txt")
        target = self.root / path
        target.parent.mkdir(parents=True)
        target.write_text('api_key="REPLACE_ME_WITH_TOKEN"\npassword=$PASSWORD\n', encoding="utf-8")

        result = validator.validate_changed_file_leaks(self.root, [path])

        self.assertTrue(result.ok, result.output())

    def test_redactor_scrubs_short_credential_url(self) -> None:
        credential_url = "https://" + "user:shortpass" + "@github.com"

        redacted = validator.redact_public_text(credential_url)

        self.assertEqual(redacted, "https://***@github.com")

    def test_redactor_scrubs_unquoted_credential_assignment(self) -> None:
        assignment = "api_key=" + ("s" * 16)

        redacted = validator.redact_public_text(assignment)

        self.assertEqual(redacted, "api_key=***")

    def test_sensitive_file_type_is_blocked(self) -> None:
        path = Path("community/example-skill/private.key")
        target = self.root / path
        target.parent.mkdir(parents=True)
        target.write_text("placeholder\n", encoding="utf-8")

        result = validator.validate_changed_file_leaks(self.root, [path])

        self.assertFalse(result.ok)
        self.assertIn("sensitive file type", result.output())

    def test_parent_traversal_changed_path_is_blocked(self) -> None:
        result = validator.validate_changed_file_leaks(self.root, [Path("../outside.txt")])

        self.assertFalse(result.ok)
        self.assertIn("repository-relative", result.output())


if __name__ == "__main__":
    unittest.main()
