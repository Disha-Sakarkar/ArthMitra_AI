import json
from html import escape

from app.memory import (
    finish_call,
    get_call_analytics,
    get_open_escalations,
    init_db,
    start_call,
)
from app.routes.outbound import router as outbound_router
from app.services.conversation_manager import ConversationManager
from app.services.deepgram_service import transcribe
from app.services.gemini_service import TEMPORARY_UNAVAILABLE_RESPONSE, get_ai_response
from app.services.murf_service import generate_audio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="ArthMitra AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=[],
)
app.include_router(outbound_router)


def _is_document_request(text: str) -> bool:
    return any(term in text.casefold() for term in ("document", "documents", "paperwork", "what do i need", "what should i bring"))


def _has_document_list(text: str) -> bool:
    normalised = text.casefold()
    return any(marker in normalised for marker in ("document", "kyc", "identity proof", "address proof", "enrolment form"))


def _is_eligibility_request(text: str) -> bool:
    normalised = text.casefold()
    return "eligib" in normalised or "am i eligible" in normalised or "can i apply" in normalised or "qualify" in normalised


def _has_eligibility_answer(text: str) -> bool:
    normalised = text.casefold()
    return "eligib" in normalised and any(term in normalised for term in ("age", "must", "need", "can apply", "cannot", "eligible"))


@app.on_event("startup")
def initialise_memory() -> None:
    init_db()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "ArthMitra AI Backend Running"
    }


@app.get("/api/escalations")
def open_escalations():
    """Real local queue for staff or a lightweight help desk integration."""
    return {"requests": get_open_escalations()}


@app.get("/api/call-analytics")
def call_analytics():
    """Aggregate-only analytics; caller details and transcripts are never returned."""
    return get_call_analytics()


@app.get("/analytics", response_class=HTMLResponse)
def analytics_dashboard():
    metrics = get_call_analytics()
    return f"""<!doctype html><html><head><title>ArthMitra call analytics</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>body{{font-family:system-ui;background:#f5f8f6;color:#162a23;margin:0;padding:3rem;max-width:900px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}.card{{background:#fff;border:1px solid #d9e4dc;border-radius:14px;padding:1.25rem;box-shadow:0 2px 8px #162a2310}}.number{{font-size:2.4rem;font-weight:700;margin:.25rem 0}}@media(max-width:600px){{.cards{{grid-template-columns:1fr}}}}</style>
    </head><body><h1>Call analytics</h1><p>Success: the caller completes an eligibility check or receives a scheme document list.</p>
    <section class='cards'><article class='card'><div>Total calls</div><div class='number'>{metrics['total_calls']}</div></article><article class='card'><div>Successful calls</div><div class='number'>{metrics['successful_calls']}</div></article><article class='card'><div>Failed calls</div><div class='number'>{metrics['failed_calls']}</div></article></section>
    <p>Completed calls only. This dashboard displays aggregate counts—never caller details or transcripts.</p></body></html>"""


@app.get("/escalations", response_class=HTMLResponse)
def escalation_dashboard():
    """Small operator dashboard showing only the safe summaries awaiting review."""
    rows = get_open_escalations()
    headers = [
        "Reference", "Caller", "Reason", "What happened", "Checked", "Urgency",
        "Language", "Follow-up", "Created",
    ]
    rendered_rows = "".join(
        "<tr>" + "".join(
            f"<td>{escape(str(row.get(key, '')))}</td>"
            for key in (
                "reference_id", "caller_name", "reason", "what_happened", "checks_completed",
                "urgency", "language", "follow_up_method", "created_at",
            )
        ) + "</tr>"
        for row in rows
    ) or "<tr><td colspan='9'>No open human-help requests.</td></tr>"
    table_headers = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return f"""<!doctype html><html><head><title>ArthMitra help requests</title>
    <style>body{{font-family:system-ui;margin:2rem;color:#162a23}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #cbd5d1;padding:.65rem;text-align:left;vertical-align:top}}th{{background:#e8f3ed}}</style>
    </head><body><h1>Open human-help requests</h1><p>Privacy-filtered summaries only.</p>
    <table><thead><tr>{table_headers}</tr></thead><tbody>{rendered_rows}</tbody></table></body></html>"""


@app.post("/chat")
def chat(data: ChatRequest):
    reply = get_ai_response([{"role": "user", "content": data.message}])

    return {
        "reply": reply
    }


async def send_assistant_reply(
    websocket: WebSocket, text: str, service_unavailable: bool = False
) -> None:
    """Always send visible text; audio failure must not break the conversation."""
    audio_url = None
    audio_error = False
    try:
        audio_url = generate_audio(text)
    except Exception:
        audio_error = True
    await websocket.send_json(
        {
            "type": "reply",
            "text": text,
            "audio": audio_url,
            "audio_error": audio_error,
            "service_unavailable": service_unavailable,
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("✅ Client Connected")

    # New conversation for every websocket session; durable memory is looked up by Gemini.
    conversation = ConversationManager()
    caller_id = None
    call_id = start_call("browser")
    completion_kind = None
    caller_turns = 0

    try:

        while True:

            message = await websocket.receive()

            # Starlette returns this normal close event rather than always raising
            # WebSocketDisconnect. Finalize it before leaving the receive loop.
            if message.get("type") == "websocket.disconnect":
                finish_call(
                    call_id,
                    successful=completion_kind is not None,
                    completion_kind=completion_kind,
                    failure_reason=None if completion_kind else (
                        "no_response" if caller_turns == 0 else "incomplete"
                    ),
                )
                return

            # -----------------------------
            # JSON
            # -----------------------------

            if message.get("text") is not None:

                data = json.loads(message["text"])

                if data.get("type") == "session_init" and data.get("user_id"):
                    caller_id = str(data["user_id"])
                    conversation.add_user_message("A new voice call has started. Greet the caller.")
                    greeting = get_ai_response(conversation.get_messages(), caller_id)
                    conversation.add_assistant_message(greeting)
                    await send_assistant_reply(
                        websocket,
                        greeting,
                        greeting == TEMPORARY_UNAVAILABLE_RESPONSE,
                    )

            # -----------------------------
            # AUDIO
            # -----------------------------

            elif message.get("bytes") is not None:

                audio = message["bytes"]

                print(f"Received {len(audio)} bytes")

                try:
                    transcript = transcribe(audio)
                except Exception:
                    await send_assistant_reply(
                        websocket,
                        "I could not process that audio right now. Please try speaking again in a moment.",
                        service_unavailable=True,
                    )
                    continue

                print("Transcript:", transcript)

                await websocket.send_json({

                    "type": "transcript",

                    "text": transcript

                })

                # Add user message

                conversation.add_user_message(transcript)
                caller_turns += 1

                # Gemini with history

                reply = get_ai_response(conversation.get_messages(), caller_id)

                # Store assistant reply

                conversation.add_assistant_message(reply)

                if _is_document_request(transcript) and _has_document_list(reply) and reply != TEMPORARY_UNAVAILABLE_RESPONSE:
                    completion_kind = "document_list"
                elif _is_eligibility_request(transcript) and _has_eligibility_answer(reply):
                    completion_kind = "eligibility_check"

                await send_assistant_reply(
                    websocket,
                    reply,
                    reply == TEMPORARY_UNAVAILABLE_RESPONSE,
                )

    except WebSocketDisconnect:
        finish_call(
            call_id,
            successful=completion_kind is not None,
            completion_kind=completion_kind,
            failure_reason=None if completion_kind else ("no_response" if caller_turns == 0 else "incomplete"),
        )

        print("❌ Client Disconnected")
