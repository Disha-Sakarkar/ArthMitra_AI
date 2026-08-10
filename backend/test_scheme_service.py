import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from app.services import scheme_service


class GovernmentSchemeLookupTests(unittest.TestCase):
    def test_finds_a_scheme_by_its_abbreviation(self):
        result = scheme_service.lookup_government_scheme("PMSBY eligibility")

        self.assertTrue(result["found"])
        self.assertEqual(result["data_type"], "local curated dataset")
        self.assertEqual(result["scheme"]["name"], "Pradhan Mantri Suraksha Bima Yojana")
        self.assertIn("official_url", result["scheme"])

    def test_unknown_scheme_does_not_invent_information(self):
        result = scheme_service.lookup_government_scheme("Example Benefit Scheme")

        self.assertFalse(result["found"])
        self.assertIn("not in ArthMitra", result["error"])

    @patch.object(scheme_service, "DATASET_PATH", Path("missing-schemes.json"))
    def test_dataset_failure_returns_a_safe_result(self):
        result = scheme_service.lookup_government_scheme("PMSBY")

        self.assertFalse(result["found"])
        self.assertIn("temporarily unavailable", result["error"])


if __name__ == "__main__":
    unittest.main()
