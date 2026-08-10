"""Live exchange-rate lookup used by ArthMitra's Gemini function tool."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/{base_currency}"

REQUEST_TIMEOUT_SECONDS = 5


def get_live_exchange_rate(base_currency: str, quote_currency: str) -> dict[str, Any]:
    """Return a current public-market exchange rate, or a safe unavailable result."""
    base = (base_currency or "").strip().upper()
    quote = (quote_currency or "").strip().upper()
    if len(base) != 3 or not base.isalpha() or len(quote) != 3 or not quote.isalpha():
        return {"available": False, "error": "Use three-letter currency codes, for example USD and INR."}

    try:
        response = requests.get(EXCHANGE_RATE_URL.format(base_currency=base), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        rate = payload.get("rates", {}).get(quote)
        if payload.get("result") != "success" or not isinstance(rate, (int, float)):
            return {"available": False, "error": "The requested currency pair is not available from the live source."}

        as_of = payload.get("time_last_update_utc") or datetime.now(timezone.utc).isoformat()
        return {
            "available": True,
            "base_currency": base,
            "quote_currency": quote,
            "rate": rate,
            "as_of": as_of,
            "source": "ExchangeRate-API open access feed",
            "note": "Reference market rate; banks and money changers may quote a different rate.",
        }
    except (requests.RequestException, ValueError):
        return {"available": False, "error": "The live exchange-rate service is temporarily unavailable."}
