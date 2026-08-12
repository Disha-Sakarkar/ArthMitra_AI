"""Privacy-safe human-help requests for cases ArthMitra cannot resolve."""

import re
import secrets
from typing import Any

from app.memory import contains_sensitive_data, create_escalation_record

ALLOWED_REASONS = {"suspected_fraud", "decision_required"}
ALLOWED_URGENCY = {"low", "medium", "high", "critical"}
MAX_FIELD_LENGTH = 500
PRIVATE_TERMS = re.compile(
    r"\b(?:otp|one[ -]?time password|pin|password|cvv|account number|card number|aadhaar|pan|ifsc)\b",
    re.IGNORECASE,
)


def _safe_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not (text := value.strip()):
        raise ValueError(f"{field} is required")
    if len(text) > MAX_FIELD_LENGTH:
        raise ValueError(f"{field} is too long")
    if PRIVATE_TERMS.search(text) or contains_sensitive_data(text):
        raise ValueError("Sensitive data cannot be included in an escalation")
    return text


def create_escalation(*, active_caller_id: str | None, arguments: dict[str, Any]) -> dict[str, str]:
    """Create a real local help request only after explicit caller consent."""
    if not active_caller_id or arguments.get("caller_id") != active_caller_id:
        return {"created": "false", "error": "Escalations may only be created for the active caller"}
    if arguments.get("consent") is not True:
        return {"created": "false", "error": "Caller permission is required before sharing a summary"}

    reason = arguments.get("reason")
    urgency = arguments.get("urgency")
    if reason not in ALLOWED_REASONS:
        return {"created": "false", "error": "Unsupported escalation reason"}
    if urgency not in ALLOWED_URGENCY:
        return {"created": "false", "error": "Unsupported urgency"}

    try:
        saved = create_escalation_record(
            reference_id=f"ESC-{secrets.token_hex(6).upper()}",
            caller_id=active_caller_id,
            caller_name=_safe_text(arguments.get("caller_name", "Caller"), "caller_name"),
            reason=reason,
            what_happened=_safe_text(arguments.get("what_happened"), "what_happened"),
            checks_completed=_safe_text(arguments.get("checks_completed"), "checks_completed"),
            urgency=urgency,
            language=_safe_text(arguments.get("language", "English"), "language"),
            follow_up_method=_safe_text(arguments.get("follow_up_method", "phone call"), "follow_up_method"),
        )
    except ValueError as error:
        return {"created": "false", "error": str(error)}

    return {
        "created": "true",
        "reference_id": saved["reference_id"],
        "status": "open",
        "next_step": "A human support team will review the request and use the requested follow-up method. Do not promise an immediate reply.",
    }
