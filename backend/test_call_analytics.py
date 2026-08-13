import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import app.memory as memory


class CallAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = memory.DB_PATH
        memory.DB_PATH = Path(self.temp_directory.name) / "analytics.db"
        memory.init_db()

    def tearDown(self):
        memory.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_successful_document_call_increases_total_and_successful_counts(self):
        call_id = memory.start_call("browser")
        memory.finish_call(call_id, successful=True, completion_kind="document_list")

        analytics = memory.get_call_analytics()
        self.assertEqual(analytics["total_calls"], 1)
        self.assertEqual(analytics["successful_calls"], 1)
        self.assertEqual(analytics["failed_calls"], 0)
        self.assertEqual(analytics["success_rate"], 100)
        self.assertEqual(analytics["recent_calls"][0]["completion_kind"], "document_list")

    def test_incomplete_call_is_counted_as_failed(self):
        call_id = memory.start_call("browser")
        memory.finish_call(call_id)

        self.assertEqual(memory.get_call_analytics()["failed_calls"], 1)
        self.assertEqual(memory.get_call_analytics()["failure_reasons"]["incomplete"], 1)


if __name__ == "__main__":
    unittest.main()
