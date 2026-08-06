import os

from dotenv import load_dotenv
from murf import Murf

load_dotenv()

client = Murf(
    api_key=os.getenv("MURF_API_KEY")
)


def generate_audio(text: str):

    response = client.text_to_speech.generate(
        text=text,
        voice_id="en-IN-priya",
        format="MP3",
        sample_rate=24000,
    )

    return response.audio_file