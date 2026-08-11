"""Twilio helpers for opt-in scheme-deadline reminder calls."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlencode

from app.memory import is_outbound_opted_out
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

E164_NUMBER = re.compile(r"^\+[1-9]\d{7,14}$")


@dataclass(frozen=True)
class SchemeReminder:
    """The minimum, non-sensitive context permitted in an outbound reminder."""

    scheme_name: str
    deadline: str
    eligibility_note: str = "You were previously found eligible based on the details you chose to share."


def _required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is not configured")
    return value


def _validate_phone_number(value: str, field: str = "phone_number") -> str:
    value = value.strip()
    if not E164_NUMBER.fullmatch(value):
        raise ValueError(f"{field} must be an E.164 phone number, for example +919876543210")
    return value


def validate_reminder(reminder: SchemeReminder) -> SchemeReminder:
    if not reminder.scheme_name.strip() or not reminder.deadline.strip():
        raise ValueError("scheme_name and deadline are required")
    return reminder


def create_outbound_call(to_number: str, reminder: SchemeReminder) -> str:
    """Ask Twilio to ring ``to_number`` and return Twilio's call SID.

    The call's content is passed in signed server-to-server webhook parameters, never
    through a browser. Only public scheme context is included.
    """
    to_number = _validate_phone_number(to_number, "to_number")
    reminder = validate_reminder(reminder)
    if is_outbound_opted_out(to_number):
        raise ValueError("This number has opted out of ArthMitra reminder calls")
    account_sid = _required_setting("TWILIO_ACCOUNT_SID")
    auth_token = _required_setting("TWILIO_AUTH_TOKEN")
    from_number = _validate_phone_number(_required_setting("TWILIO_PHONE_NUMBER"), "TWILIO_PHONE_NUMBER")
    public_base_url = _required_setting("PUBLIC_BASE_URL").rstrip("/")
    if not public_base_url.startswith("https://"):
        raise ValueError("PUBLIC_BASE_URL must be a public HTTPS URL for Twilio webhooks")

    parameters = urlencode(
        {
            "scheme_name": reminder.scheme_name,
            "deadline": reminder.deadline,
            "eligibility_note": reminder.eligibility_note,
        }
    )
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url=f"{public_base_url}/twilio/voice?{parameters}",
        #method="POST",
        #status_callback=f"{public_base_url}/twilio/status",
       # status_callback_method="POST",
        #status_callback_event=["initiated", "ringing", "answered", "completed"],
    )
    return call.sid


def is_valid_phone_number(value: str) -> bool:
    return bool(E164_NUMBER.fullmatch(value.strip()))
