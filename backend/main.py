from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json

from app.services.deepgram_service import transcribe
from app.services.gemini_service import get_ai_response
from app.services.murf_service import generate_audio
from app.services.conversation_manager import ConversationManager
from app.memory import init_db

app = FastAPI(title="ArthMitra AI")


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


@app.post("/chat")
def chat(data: ChatRequest):
    reply = get_ai_response([{"role": "user", "content": data.message}])

    return {
        "reply": reply
    }


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
                    await websocket.send_json({
                        "type": "reply",
                        "text": greeting,
                        "audio": generate_audio(greeting),
                    })

            # -----------------------------
            # AUDIO
            # -----------------------------

            elif message.get("bytes") is not None:

                audio = message["bytes"]

                print(f"Received {len(audio)} bytes")

                transcript = transcribe(audio)

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

                audio_url = generate_audio(reply)

                await websocket.send_json({

                    "type": "reply",

                    "text": reply,

                    "audio": audio_url

                })

    except WebSocketDisconnect:

        print("❌ Client Disconnected")
