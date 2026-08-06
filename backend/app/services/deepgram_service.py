import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPGRAM_API_KEY")

URL = (
    "https://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&smart_format=true"
    "&punctuate=true"
    "&detect_language=true"
)

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "audio/webm"
}


def transcribe(audio_bytes):
    response = requests.post(
        URL,
        headers=HEADERS,
        data=audio_bytes,
        timeout=60
    )

    print("Status Code:", response.status_code)
    print("Response:")
    print(response.text)

    response.raise_for_status()

    result = response.json()

    return result["results"]["channels"][0]["alternatives"][0]["transcript"]