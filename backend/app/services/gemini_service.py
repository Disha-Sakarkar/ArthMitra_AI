import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_ai_response(messages):

    prompt = ""

    for msg in messages:

        prompt += f"{msg['role'].upper()}:\n{msg['content']}\n\n"

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=prompt

    )

    return response.text