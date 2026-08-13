"""Twilio Voice webhooks and the authenticated outbound-call API."""

from __future__ import annotations

import os
from typing import Annotated
from urllib.parse import urlencode

from app.memory import record_outbound_opt_out
from app.services.gemini_service import get_outbound_scheme_response
from app.services.murf_service import generate_audio
from app.services.outbound_call_service import (
    SchemeReminder,
    create_outbound_call,
    is_valid_phone_number,
    validate_reminder,
)
from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import Gather, VoiceResponse

router = APIRouter(tags=["outbound-calls"])


class OutboundCallRequest(BaseModel):
    to_number: str = Field(description="Recipient phone number in E.164 format")
    scheme_name: str
    deadline: str
    eligibility_note: str = "You were previously found eligible based on the details you chose to share."


class OutboundCallResponse(BaseModel):
    call_sid: str
    status: str


def _twiml(response: VoiceResponse) -> str:
    return str(response)


async def _twilio_form(request: Request) -> dict[str, str]:
    form = await request.form()
    values = {key: str(value) for key, value in form.items()}
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    # Twilio signs all production callbacks. This deliberately fails closed whenever
    # credentials have been configured; local testing can use an empty token.
    if auth_token:
        signature = request.headers.get("X-Twilio-Signature", "")
        validator = RequestValidator(auth_token)
        public_base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
        signed_url = f"{public_base_url}{request.url.path}"
        if request.url.query:
            signed_url = f"{signed_url}?{request.url.query}"
        if not validator.validate(signed_url, values, signature):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature")
    return values


def _context_from_values(values: dict[str, str]) -> SchemeReminder:
    try:
        return validate_reminder(
            SchemeReminder(
                scheme_name=values.get("scheme_name", ""),
                deadline=values.get("deadline", ""),
                eligibility_note=values.get("eligibility_note", ""),
            )
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _is_opt_out_request(speech: str, digit: str) -> bool:
    normalised = speech.casefold()
    opt_out_phrases = (
        "stop",
        "opt out",
        "unsubscribe",
        "do not call",
        "don't call",
        "dont call",
        "stop calling",
        "do not contact",
        "remove me",
    )
    return digit == "9" or any(phrase in normalised for phrase in opt_out_phrases)


def _gather(response: VoiceResponse, prompt: str, reminder: SchemeReminder) -> None:
    query = urlencode(
        {
            "scheme_name": reminder.scheme_name,
            "deadline": reminder.deadline,
            "eligibility_note": reminder.eligibility_note,
        }
    )
    gather = Gather(
        input="speech dtmf",
        num_digits=1,
        speech_timeout="auto",
        action=f"/twilio/respond?{query}",
        method="POST",
        language="en-IN",
        timeout=7,
    )
    # Murf gives the reminder an Indian voice. Twilio's built-in Say remains the
    # reliable fallback if the TTS provider is unavailable.
    try:
        gather.play(generate_audio(prompt))
    except Exception:
        gather.say(prompt, voice="alice", language="en-IN")
    response.append(gather)
    response.say("We did not receive a response. To stop future reminder calls, contact ArthMitra through the number on our website. Goodbye.")


@router.post("/outbound/call", response_model=OutboundCallResponse)
def start_outbound_call(
    call_request: OutboundCallRequest,
    x_outbound_api_key: Annotated[str | None, Header()] = None,
) -> OutboundCallResponse:
    """Place one reminder call. Protect this endpoint before deploying it publicly."""
    configured_key = os.getenv("OUTBOUND_API_KEY", "").strip()
    if configured_key and x_outbound_api_key != configured_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid outbound API key")
    if not is_valid_phone_number(call_request.to_number):
        raise HTTPException(status_code=422, detail="to_number must be E.164 format")
    try:
        call_sid = create_outbound_call(
            call_request.to_number,
            SchemeReminder(
                scheme_name=call_request.scheme_name,
                deadline=call_request.deadline,
                eligibility_note=call_request.eligibility_note,
            ),
        )
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return OutboundCallResponse(call_sid=call_sid, status="queued")


@router.post("/twilio/voice")
async def twilio_voice(request: Request):
    values = await _twilio_form(request)
    reminder = _context_from_values({**dict(request.query_params), **values})
    opening = (
        f"Hello, this is ArthMitra, a financial guidance assistant calling because {reminder.scheme_name} "
        f"has an approaching application deadline of {reminder.deadline}. "
        "To stop future reminder calls, say stop or press 9. "
        "Would you like the deadline and the next step?"
    )
    response = VoiceResponse()
    _gather(response, opening, reminder)
    return Response(content=_twiml(response), media_type="application/xml")


@router.post("/twilio/respond")
async def twilio_respond(request: Request):
    values = await _twilio_form(request)
    reminder = _context_from_values({**dict(request.query_params), **values})
    response = VoiceResponse()
    speech = values.get("SpeechResult", "").strip()
    digit = values.get("Digits", "")
    if _is_opt_out_request(speech, digit):
        from_number = values.get("From", "")
        if is_valid_phone_number(from_number):
            record_outbound_opt_out(from_number)
        response.say("You have been opted out of future ArthMitra scheme reminder calls. Goodbye.", voice="alice", language="en-IN")
        return Response(content=_twiml(response), media_type="application/xml")

    reply = get_outbound_scheme_response(speech, reminder.scheme_name, reminder.deadline, reminder.eligibility_note)
    _gather(response, reply, reminder)
    return Response(content=_twiml(response), media_type="application/xml")


@router.post("/twilio/status", status_code=status.HTTP_204_NO_CONTENT)
async def twilio_status(request: Request):
    await _twilio_form(request)
    # Keep the webhook explicit for observability; Twilio remains the source of truth
    # for delivery status in its console.
    return None
