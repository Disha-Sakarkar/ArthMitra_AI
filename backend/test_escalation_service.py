import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import app.memory as memory
from app.services.escalation_service import create_escalation


class EscalationServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = memory.DB_PATH
        memory.DB_PATH = Path(self.temp_directory.name) / "escalations.db"
        memory.init_db()
        self.arguments = {
            "caller_id": "caller-7",
            "caller_name": "Ramesh",
            "reason": "suspected_fraud",
            "what_happened": "Caller reports an unfamiliar payment request.",
            "checks_completed": "Explained official bank fraud channels and credential safety.",
            "urgency": "high",
            "language": "Hindi",
            "follow_up_method": "phone call",
            "consent": True,
        }

    def tearDown(self):
        memory.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_creates_a_minimum_summary_after_permission(self):
        result = create_escalation(active_caller_id="caller-7", arguments=self.arguments)

        self.assertEqual(result["created"], "true")
        self.assertTrue(result["reference_id"].startswith("ESC-"))
        request = memory.get_open_escalations()[0]
        self.assertEqual(request["reason"], "suspected_fraud")
        self.assertEqual(request["urgency"], "high")

    def test_does_not_create_request_without_permission(self):
        self.arguments["consent"] = False
        result = create_escalation(active_caller_id="caller-7", arguments=self.arguments)

        self.assertEqual(result["created"], "false")
        self.assertEqual(memory.get_open_escalations(), [])

    def test_rejects_private_credentials_in_summary(self):
        self.arguments["what_happened"] = "Caller said their OTP was shared."
        result = create_escalation(active_caller_id="caller-7", arguments=self.arguments)

        self.assertEqual(result["created"], "false")
        self.assertEqual(memory.get_open_escalations(), [])


if __name__ == "__main__":
    unittest.main()
