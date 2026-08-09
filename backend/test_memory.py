import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))
import app.memory as memory


class CallerMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = memory.DB_PATH
        memory.DB_PATH = Path(self.temp_directory.name) / "memory.db"
        memory.init_db()

    def tearDown(self):
        memory.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_persists_allowed_facts_after_explicit_consent(self):
        memory.save_user(
            "caller-1",
            name="Ramesh",
            language_preference="hi",
            facts={
                "schemes_checked": ["PM Jan Dhan"],
                "follow_up_topic": "account opening",
            },
            consent=True,
        )

        caller = memory.get_user("caller-1")

        self.assertEqual(caller["name"], "Ramesh")
        self.assertEqual(caller["facts"]["follow_up_topic"], "account opening")

    def test_rejects_a_save_without_consent(self):
        with self.assertRaises(PermissionError):
            memory.save_user("caller-1", name="Ramesh")

    def test_rejects_sensitive_financial_data(self):
        with self.assertRaises(ValueError):
            memory.save_user(
                "caller-1",
                facts={"account_number": "1234567890"},
                consent=True,
            )


if __name__ == "__main__":
    unittest.main()
