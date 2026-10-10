from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import public_pr_review_service as service  # noqa: E402


class PublicPrReviewServiceTests(unittest.TestCase):
    def test_default_model_is_gpt_56_sol(self) -> None:
        self.assertEqual(service.DEFAULT_CODEX_MODEL, "gpt-5.6-sol")

if __name__ == "__main__":
    unittest.main()
