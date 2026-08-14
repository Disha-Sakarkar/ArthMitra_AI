import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

from app.memory import get_user, save_user
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.prompts.government_scheme_specialist import GOVERNMENT_SCHEME_SPECIALIST_PROMPT
from app.services.escalation_service import create_escalation
from app.services.exchange_rate_service import get_live_exchange_rate
from app.services.scheme_service import lookup_government_scheme
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
logger = logging.getLogger(__name__)

TEMPORARY_UNAVAILABLE_RESPONSE = (
    "I am sorry, ArthMitra is temporarily unavailable. Please try again in a moment."
)


@dataclass(frozen=True)
class AgentReply:
    """A reply plus the agent that should handle the caller's next turn."""

    text: str
    active_agent: str = "main"
    handed_off: bool = False


AGENT_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="transfer_to_government_scheme_specialist",
            description=(
                "Hand the conversation to the Government Scheme Specialist when the caller asks "
                "about eligibility, benefits, documents, enrolment, ministry, or the official "
                "portal for a named Indian central-government scheme or abbreviation such as "
                "PMJDY, PMSBY, PMJJBY, APY, or PMMY. Do not use for general financial education, "
                "banking, payments, fraud, exchange rates, or unnamed schemes. The specialist "
                "receives the complete conversation and continues the caller's current request."
            ),
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
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
        types.FunctionDeclaration(
            name="create_escalation",
            description=(
                "Create a local human-help request ONLY after the caller explicitly agrees to share "
                "the short summary. Use only when the caller reports suspected fraud or needs a "
                "decision ArthMitra cannot make. Never include a transcript, OTP, PIN, password, "
                "account/card number, Aadhaar, PAN, CVV, or any credential."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "caller_id": types.Schema(type="STRING"),
                    "caller_name": types.Schema(type="STRING"),
                    "reason": types.Schema(type="STRING", description="suspected_fraud or decision_required"),
                    "what_happened": types.Schema(type="STRING"),
                    "checks_completed": types.Schema(type="STRING"),
                    "urgency": types.Schema(type="STRING", description="low, medium, high, or critical"),
                    "language": types.Schema(type="STRING"),
                    "follow_up_method": types.Schema(type="STRING"),
                    "consent": types.Schema(type="BOOLEAN"),
                },
                required=["caller_id", "reason", "what_happened", "checks_completed", "urgency", "language", "follow_up_method", "consent"],
            ),
        ),
    ]
)


SCHEME_SPECIALIST_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="lookup_government_scheme",
            description=(
                "Look up a named Indian central-government scheme in ArthMitra's local curated "
                "dataset before answering about its eligibility, benefits, documents, enrolment, "
                "ministry, or official portal. The result includes its as-of date and official portal."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={"scheme_query": types.Schema(type="STRING")},
                required=["scheme_query"],
            ),
        )
    ]
)


# ✅ FIXED: Matches affirmative keywords within full user responses
AFFIRMATIVE_CONSENT = re.compile(
    r"\b(?:yes|yeah|yep|ok|okay|agree|i agree|please do|haan|han|ha|ji|"
    r"हाँ|हां|जी|अनुमति|परमिशन)\b",
    re.IGNORECASE,
)


def _has_escalation_consent(messages: list[dict[str, str]] | None) -> bool:
    """Verify that the latest caller turn approves a prior summary-sharing request."""
    if not messages or messages[-1].get("role") != "user":
        return False

    user_text = messages[-1].get("content", "").lower()
    # Check for affirmative words (substring match)
    affirmative_words = {
        "yes", "yeah", "yep", "ok", "okay", "agree", "i agree", "please do",
        "haan", "han", "ha", "ji",
        "हाँ", "हां", "जी", "अनुमति", "परमिशन"
    }
    if not any(word in user_text for word in affirmative_words):
        return False

    # Find the immediately preceding assistant message
    for msg in reversed(messages[:-1]):
        if msg.get("role") == "assistant":
            assistant_text = msg.get("content", "").lower()
            # Check for any permission/consent related words
            permission_words = {
                "permission", "consent", "share", "summary", "escalate",
                "team", "representative", "human", "support", "agent",
                "allow", "approval",
                "अनुमति", "स्वीकृति", "दर्ज", "साझा", "टीम", "मानव", "विशेषज्ञ"
            }
            if any(word in assistant_text for word in permission_words):
                return True
            break  # only check the immediate previous assistant message
    return False


def _run_tool(
    name: str,
    arguments: dict[str, Any],
    active_caller_id: str | None,
    messages: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    try:
        if name == "transfer_to_government_scheme_specialist":
            return {"transferred": True}
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
        if name == "create_escalation":
            if not _has_escalation_consent(messages):
                return {
                    "created": "false",
                    "error": "The caller has not explicitly approved a prior human-summary sharing request",
                }
            return create_escalation(active_caller_id=active_caller_id, arguments=arguments)
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


def _handoff_message(specialist_reply: str) -> str:
    """Make both the transfer and the specialist's arrival audible to the caller."""
    return (
        "I will connect you to our government schemes specialist. "
        f"Government Schemes Specialist here. {specialist_reply}"
    )


def _generate_with_tools(
    messages: list[dict[str, str]],
    caller_id: str | None,
    system_instruction: str,
    tools: types.Tool,
    active_agent: str,
) -> AgentReply:
    """Generate one agent turn, retaining the full caller transcript for a handoff."""
    contents: list[Any] = [_prompt_from_messages(messages, caller_id)]
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[tools],
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
            return AgentReply(response.text or "I am sorry, I could not prepare a response.", active_agent)

        # A transfer tool ends the main agent's turn. The specialist starts with
        # the exact same transcript, so the caller never has to repeat the ask.
        if active_agent == "main" and any(
            call.name == "transfer_to_government_scheme_specialist" for call in function_calls
        ):
            specialist = _generate_with_tools(
                messages,
                caller_id,
                GOVERNMENT_SCHEME_SPECIALIST_PROMPT,
                SCHEME_SPECIALIST_TOOLS,
                "government_scheme_specialist",
            )
            return AgentReply(_handoff_message(specialist.text), specialist.active_agent, True)

        contents.append(response.candidates[0].content)
        for call in function_calls:
            result = _run_tool(call.name, dict(call.args or {}), caller_id, messages)
            contents.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=call.name, response={"result": result})]))
    return AgentReply("I am sorry, I could not complete that request right now.", active_agent)


def get_agent_response(
    messages: list[dict[str, str]], caller_id: str | None = None, active_agent: str = "main"
) -> AgentReply:
    """Route a turn to the main agent or the focused government-scheme specialist."""
    try:
        if active_agent == "government_scheme_specialist":
            return _generate_with_tools(
                messages, caller_id, GOVERNMENT_SCHEME_SPECIALIST_PROMPT,
                SCHEME_SPECIALIST_TOOLS, active_agent,
            )
        return _generate_with_tools(messages, caller_id, SYSTEM_PROMPT, AGENT_TOOLS, "main")
    except Exception:
        # logger.exception includes the original provider error and traceback in
        # the Uvicorn terminal logs without exposing caller transcript content.
        logger.exception("Gemini generation failed for active_agent=%s", active_agent)
        return AgentReply(TEMPORARY_UNAVAILABLE_RESPONSE, active_agent)


def get_ai_response(messages: list[dict[str, str]], caller_id: str | None = None) -> str:
    """Compatibility wrapper for REST callers that need reply text only."""
    return get_agent_response(messages, caller_id).text


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
        logger.exception("Gemini outbound reminder generation failed")
        return "The application deadline is approaching. Please check the official scheme portal for the next step."
