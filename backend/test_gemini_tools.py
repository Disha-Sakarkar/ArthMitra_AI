import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from app.services.gemini_service import AGENT_TOOLS, _handoff_message, _run_tool
from app.prompts.government_scheme_specialist import GOVERNMENT_SCHEME_SPECIALIST_PROMPT


class GeminiToolDispatchTests(unittest.TestCase):
    @patch("app.services.gemini_service.get_live_exchange_rate")
    def test_live_rate_tool_is_not_blocked_by_caller_memory_guard(self, mock_rate):
        mock_rate.return_value = {"available": True, "rate": 87.5}

        result = _run_tool(
            "get_live_exchange_rate",
            {"base_currency": "USD", "quote_currency": "INR"},
            active_caller_id=None,
        )

        self.assertEqual(result["rate"], 87.5)
        mock_rate.assert_called_once_with("USD", "INR")

    def test_escalation_is_blocked_without_a_prior_permission_request(self):
        result = _run_tool(
            "create_escalation",
            {"caller_id": "caller-1", "consent": True},
            active_caller_id="caller-1",
            messages=[{"role": "user", "content": "yes"}],
        )

        self.assertEqual(result["created"], "false")

    def test_handoff_is_limited_to_a_named_scheme_specialist(self):
        declaration = next(
            item for item in AGENT_TOOLS.function_declarations
            if item.name == "transfer_to_government_scheme_specialist"
        )
        self.assertIn("named Indian central-government scheme", declaration.description)
        self.assertIn("Do not use for general financial education", declaration.description)
        self.assertIn("one job", GOVERNMENT_SCHEME_SPECIALIST_PROMPT)

    def test_handoff_tells_the_caller_and_introduces_the_specialist(self):
        reply = _handoff_message("PMSBY is in our local reference data.")
        self.assertIn("I will connect you", reply)
        self.assertIn("Government Schemes Specialist here", reply)


if __name__ == "__main__":
    unittest.main()
