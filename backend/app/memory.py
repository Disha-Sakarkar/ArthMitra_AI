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
