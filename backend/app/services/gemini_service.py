import json
import os
from typing import Any

from app.memory import get_user, save_user
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.exchange_rate_service import get_live_exchange_rate
from app.services.scheme_service import lookup_government_scheme
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

TEMPORARY_UNAVAILABLE_RESPONSE = (
    "I am sorry, ArthMitra is temporarily unavailable. Please try again in a moment."
)


AGENT_TOOLS = types.Tool(
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
        types.FunctionDeclaration(
            name="lookup_government_scheme",
            description=(
                "Look up a named Indian central-government scheme in ArthMitra's local curated "
                "dataset. Call this before answering about the eligibility, benefits, documents, "
                "enrolment, ministry, or official portal of a specific scheme or common scheme "
                "abbreviation, such as PMJDY, PMSBY, PMJJBY, APY, or PMMY. Do not call it for "
                "generic financial education or a scheme that the caller has not named. This is "
                "local reference data and the result includes its as-of date and official portal."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={"scheme_query": types.Schema(type="STRING", description="The scheme name or common abbreviation stated by the caller")},
                required=["scheme_query"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_live_exchange_rate",
            description=(
                "Fetch the current reference market exchange rate for a specific pair of "
                "three-letter currencies, such as USD to INR. Call this whenever the caller "
                "asks for today's, current, latest, or live exchange rate, or asks to convert "
                "an amount using a current rate. Do not call it for general explanations of "
                "foreign exchange, historical rates, or bank-account questions. The response "
                "includes when the source was last updated and may say unavailable."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "base_currency": types.Schema(type="STRING", description="Three-letter source currency code, e.g. USD"),
                    "quote_currency": types.Schema(type="STRING", description="Three-letter target currency code, e.g. INR"),
                },
                required=["base_currency", "quote_currency"],
            ),
        ),
    ]
)


def _run_tool(
    name: str, arguments: dict[str, Any], active_caller_id: str | None
) -> dict[str, Any]:
    try:
        memory_function_names = {"lookup_caller", "save_caller_memory"}
        if name in memory_function_names and (
            not active_caller_id or arguments.get("user_id") != active_caller_id
        ):
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
        if name == "get_live_exchange_rate":
            return get_live_exchange_rate(
                arguments.get("base_currency", ""), arguments.get("quote_currency", "")
            )
        if name == "lookup_government_scheme":
            return lookup_government_scheme(arguments.get("scheme_query", ""))
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
    try:
        contents: list[Any] = [_prompt_from_messages(messages, caller_id)]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[AGENT_TOOLS],
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
                contents.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=call.name, response={"result": result})]))
        return "I am sorry, I could not complete that request right now."
    except Exception:
        return TEMPORARY_UNAVAILABLE_RESPONSE


def get_outbound_scheme_response(
    caller_speech: str, scheme_name: str, deadline: str, eligibility_note: str
) -> str:
    """Respond to a reminder call without accessing or storing caller memory."""
    prompt = f"""You are ArthMitra on an outbound scheme-deadline reminder call.
Scheme: {scheme_name}
Deadline: {deadline}
Eligibility context: {eligibility_note}
Caller said: {caller_speech or '[no speech detected]'}

Reply in at most two short, warm sentences. State only the supplied scheme and deadline.
Never ask for or disclose personal, account, Aadhaar, PAN, OTP, PIN, card, or bank details.
If they decline, ask to stop, say wrong person, or ask for a human, acknowledge it and end.
Do not claim an application is approved. Offer the official scheme portal or a nearby authorised help centre for the next step."""
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return response.text or "The application deadline is approaching. You can confirm the next step on the official scheme portal."
    except Exception:
        return "The application deadline is approaching. Please check the official scheme portal for the next step."
