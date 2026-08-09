import json
import os
from typing import Any

from app.memory import get_user, save_user
from app.prompts.system_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


MEMORY_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="lookup_caller",
            description="Look up the current caller's consented memory before greeting them or continuing a previous topic.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"user_id": types.Schema(type="STRING")},
                required=["user_id"],
            ),
        ),
        types.FunctionDeclaration(
            name="save_caller_memory",
            description="Save the caller's name, language, and permitted scheme or eligibility facts only after they explicitly agree to memory storage.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "user_id": types.Schema(type="STRING"),
                    "name": types.Schema(type="STRING"),
                    "language_preference": types.Schema(type="STRING"),
                    "facts": types.Schema(type="OBJECT"),
                    "consent": types.Schema(type="BOOLEAN"),
                },
                required=["user_id", "consent"],
            ),
        ),
    ]
)


def _run_tool(
    name: str, arguments: dict[str, Any], active_caller_id: str | None
) -> dict[str, Any]:
    try:
        if not active_caller_id or arguments.get("user_id") != active_caller_id:
            return {"error": "Memory functions may only access the active caller"}
        if name == "lookup_caller":
            caller = get_user(arguments["user_id"])
            return {"caller": caller, "found": caller is not None}
        if name == "save_caller_memory":
            caller = save_user(
                user_id=arguments["user_id"],
                name=arguments.get("name"),
                language_preference=arguments.get("language_preference"),
                facts=arguments.get("facts"),
                consent=arguments.get("consent", False),
            )
            return {"saved": True, "caller": caller}
        return {"error": "Unknown memory function"}
    except (KeyError, PermissionError, ValueError) as error:
        return {"saved": False, "error": str(error)}


def _prompt_from_messages(messages: list[dict[str, str]], caller_id: str | None) -> str:
    transcript = "\n\n".join(
        f"{message['role'].upper()}:\n{message['content']}" for message in messages
    )
    if caller_id:
        transcript += f"\n\nSYSTEM EVENT: Current caller ID is {caller_id}."
    return transcript


def get_ai_response(messages: list[dict[str, str]], caller_id: str | None = None) -> str:
    """Generate a response, allowing Gemini to call the consented-memory functions."""
    contents: list[Any] = [_prompt_from_messages(messages, caller_id)]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[MEMORY_TOOLS],
        temperature=0.3,
    )

    for _ in range(4):
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=contents,
            config=config,
        )
        function_calls = response.function_calls or []
        if not function_calls:
            return response.text or "I am sorry, I could not prepare a response."

        contents.append(response.candidates[0].content)
        for call in function_calls:
            result = _run_tool(call.name, dict(call.args or {}), caller_id)
            contents.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=call.name,
                            response={"result": result},
                        )
                    ],
                )
            )

    return "I am sorry, I could not complete that memory request."
