from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
from app.services.murf_service import generate_audio
from app.services.gemini_service import get_ai_response
from app.services.deepgram_service import transcribe
app = FastAPI(title="Swasthya Saathi")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Swasthya Saathi Backend Running"
    }


@app.post("/chat")
def chat(data: ChatRequest):

    reply = get_ai_response(data.message)

    return {
        "reply": reply
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("✅ Client Connected")

    try:

        while True:

            message = await websocket.receive()

            # JSON messages
            if message.get("text") is not None:

                data = json.loads(message["text"])

                print("Received JSON:", data)

                await websocket.send_json({
                    "type": "reply",
                    "text": f"Backend received: {data.get('message')}"
                })

            # Binary audio
            elif message.get("bytes") is not None:

                audio = message["bytes"]

                print(f"Received {len(audio)} bytes")

                transcript = transcribe(audio)

                print("Transcript:", transcript)

                await websocket.send_json({
                    "type": "transcript",
                    "text": transcript
                })

                reply = get_ai_response(transcript)
                print(type(reply))
                print(reply)
                print(len(str(reply)))
                audio_url = generate_audio(reply)

                await websocket.send_json({

                    "type":"reply",

                    "text": reply,

                    "audio": audio_url

})
    except WebSocketDisconnect:

        print("❌ Client Disconnected")