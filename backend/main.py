import json
from html import escape

from app.memory import get_open_escalations, init_db
from app.routes.outbound import router as outbound_router
from app.services.conversation_manager import ConversationManager
from app.services.deepgram_service import transcribe
from app.services.gemini_service import TEMPORARY_UNAVAILABLE_RESPONSE, get_ai_response
from app.services.murf_service import generate_audio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="ArthMitra AI")
app.include_router(outbound_router)


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

    try:

        while True:

            message = await websocket.receive()

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

                # Gemini with history

                reply = get_ai_response(conversation.get_messages(), caller_id)

                # Store assistant reply

                conversation.add_assistant_message(reply)

                await send_assistant_reply(
                    websocket,
                    reply,
                    reply == TEMPORARY_UNAVAILABLE_RESPONSE,
                )

    except WebSocketDisconnect:

        print("❌ Client Disconnected")
