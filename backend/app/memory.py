"""Durable, consent-gated caller memory for ArthMitra."""

import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parents[1] / "arthmitra.db"
ALLOWED_FACT_KEYS = {
    "schemes_checked",
    "scheme_interest",
    "eligibility_answers",
    "follow_up_topic",
}
SENSITIVE_KEY_WORDS = {
    "account",
    "aadhaar",
    "card",
    "cvv",
    "ifsc",
    "otp",
    "pan",
    "password",
    "pin",
}
LONG_NUMBER = re.compile(r"\d[\d -]{6,}\d")
ESCALATION_REFERENCE = re.compile(r"^ESC-[A-Z0-9]{12}$")


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_db()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL DEFAULT '',
                language_preference TEXT NOT NULL DEFAULT 'en',
                facts TEXT NOT NULL DEFAULT '{}',
                last_interaction TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                reference_id TEXT PRIMARY KEY,
                caller_id TEXT NOT NULL,
                caller_name TEXT NOT NULL DEFAULT '',
                reason TEXT NOT NULL,
                what_happened TEXT NOT NULL,
                checks_completed TEXT NOT NULL,
                urgency TEXT NOT NULL,
                language TEXT NOT NULL,
                follow_up_method TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS outbound_opt_outs (
                phone_number TEXT PRIMARY KEY,
                opted_out_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def get_user(user_id: str) -> Optional[dict[str, Any]]:
    connection = get_db()
    try:
        row = connection.execute(
            "SELECT user_id, name, language_preference, facts, last_interaction "
            "FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    user = dict(row)
    user["facts"] = json.loads(user["facts"] or "{}")
    return user


def _contains_sensitive_data(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            any(word in str(key).lower() for word in SENSITIVE_KEY_WORDS)
            or _contains_sensitive_data(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sensitive_data(item) for item in value)
    return isinstance(value, str) and bool(LONG_NUMBER.search(value))


def _safe_facts(facts: Optional[dict[str, Any]]) -> dict[str, Any]:
    facts = facts or {}
    if not isinstance(facts, dict):
        raise ValueError("facts must be an object")

    invalid_keys = set(facts) - ALLOWED_FACT_KEYS
    if invalid_keys:
        raise ValueError("Only scheme and eligibility facts may be saved")
    if _contains_sensitive_data(facts):
        raise ValueError("Sensitive financial or identity data cannot be saved")
    return facts


def save_user(
    user_id: str,
    name: Optional[str] = None,
    language_preference: Optional[str] = None,
    facts: Optional[dict[str, Any]] = None,
    *,
    consent: bool = False,
) -> dict[str, Any]:
    """Save permitted memory only after the caller has explicitly agreed."""
    if consent is not True:
        raise PermissionError("Caller consent is required before saving memory")

    safe_facts = _safe_facts(facts)
    existing = get_user(user_id)
    timestamp = datetime.now(UTC).isoformat()
    merged_facts = {**(existing["facts"] if existing else {}), **safe_facts}
    saved_name = name if name is not None else (existing["name"] if existing else "")
    saved_language = language_preference if language_preference is not None else (
        existing["language_preference"] if existing else "en"
    )

    connection = get_db()
    try:
        connection.execute(
            """
            INSERT INTO users (user_id, name, language_preference, facts, last_interaction)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                language_preference = excluded.language_preference,
                facts = excluded.facts,
                last_interaction = excluded.last_interaction
            """,
            (user_id, saved_name, saved_language, json.dumps(merged_facts), timestamp),
        )
        connection.commit()
    finally:
        connection.close()

    return get_user(user_id) or {}


def record_outbound_opt_out(phone_number: str) -> None:
    """Keep the minimum necessary do-not-call record for scheme reminders."""
    init_db()
    connection = get_db()
    try:
        connection.execute(
            "INSERT OR REPLACE INTO outbound_opt_outs (phone_number, opted_out_at) VALUES (?, ?)",
            (phone_number, datetime.now(UTC).isoformat()),
        )
        connection.commit()
    finally:
        connection.close()


def is_outbound_opted_out(phone_number: str) -> bool:
    init_db()
    connection = get_db()
    try:
        return connection.execute(
            "SELECT 1 FROM outbound_opt_outs WHERE phone_number = ?", (phone_number,)
        ).fetchone() is not None
    finally:
        connection.close()


def contains_sensitive_data(value: Any) -> bool:
    """Public validation helper for narrowly scoped records such as escalations."""
    return _contains_sensitive_data(value)


def create_escalation_record(
    *,
    reference_id: str,
    caller_id: str,
    caller_name: str,
    reason: str,
    what_happened: str,
    checks_completed: str,
    urgency: str,
    language: str,
    follow_up_method: str,
) -> dict[str, str]:
    """Store the minimum privacy-filtered information needed for human follow-up."""
    if not ESCALATION_REFERENCE.fullmatch(reference_id):
        raise ValueError("Invalid escalation reference")

    record = {
        "caller_name": caller_name,
        "reason": reason,
        "what_happened": what_happened,
        "checks_completed": checks_completed,
        "urgency": urgency,
        "language": language,
        "follow_up_method": follow_up_method,
    }
    if _contains_sensitive_data(record):
        raise ValueError("Sensitive data cannot be included in an escalation")

    created_at = datetime.now(UTC).isoformat()
    connection = get_db()
    try:
        connection.execute(
            """
            INSERT INTO escalations (
                reference_id, caller_id, caller_name, reason, what_happened,
                checks_completed, urgency, language, follow_up_method, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                reference_id, caller_id, caller_name, reason, what_happened,
                checks_completed, urgency, language, follow_up_method, created_at,
            ),
        )
        connection.commit()
    finally:
        connection.close()

    return {"reference_id": reference_id, "status": "open", "created_at": created_at}


def get_open_escalations() -> list[dict[str, str]]:
    init_db()
    connection = get_db()
    try:
        rows = connection.execute(
            """SELECT reference_id, caller_name, reason, what_happened, checks_completed,
                      urgency, language, follow_up_method, status, created_at
               FROM escalations WHERE status = 'open' ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
