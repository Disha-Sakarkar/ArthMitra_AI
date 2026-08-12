import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from app.services.gemini_service import _run_tool


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


if __name__ == "__main__":
    unittest.main()
