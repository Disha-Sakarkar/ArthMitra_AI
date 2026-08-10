import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

sys.path.insert(0, str(Path(__file__).parent))
from app.services.exchange_rate_service import get_live_exchange_rate


class ExchangeRateServiceTests(unittest.TestCase):
    @patch("app.services.exchange_rate_service.requests.get")
    def test_returns_live_rate_and_provider_timestamp(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "result": "success",
            "time_last_update_utc": "Mon, 10 Aug 2026 00:02:01 +0000",
            "rates": {"INR": 87.5},
        }
        mock_get.return_value = response

        result = get_live_exchange_rate("usd", "inr")

        self.assertTrue(result["available"])
        self.assertEqual(result["rate"], 87.5)
        self.assertEqual(result["as_of"], "Mon, 10 Aug 2026 00:02:01 +0000")

    @patch("app.services.exchange_rate_service.requests.get", side_effect=requests.Timeout("offline"))
    def test_returns_spoken_fallback_data_when_source_fails(self, _mock_get):
        result = get_live_exchange_rate("USD", "INR")

        self.assertFalse(result["available"])
        self.assertIn("temporarily unavailable", result["error"])

    def test_rejects_invalid_currency_codes_without_a_network_call(self):
        result = get_live_exchange_rate("dollar", "INR")

        self.assertFalse(result["available"])
        self.assertIn("three-letter", result["error"])


if __name__ == "__main__":
    unittest.main()
