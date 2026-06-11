import logging
from datetime import datetime

from google import genai
from google.genai import errors as genai_errors

from config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Provide accurate, concise, professional, "
    "and context-aware responses."
)

FALLBACK_MESSAGE = "Sorry, I am currently unavailable. Please try again in a few moments."

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _build_prompt(messages: list[dict]) -> str:
    now = datetime.now()
    current_time_str = now.strftime("%A, %B %d, %Y, %I:%M:%S %p")
    dynamic_system_prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"Current date and time: {current_time_str}."
    )
    lines = [dynamic_system_prompt, ""]
    for message in messages:
        role_label = "User" if message["role"] == "user" else "Assistant"
        lines.append(f"{role_label}: {message['content']}")
    lines.append("Assistant:")
    return "\n".join(lines)


def generate_response(messages: list[dict]) -> str:
    context_messages = messages[-10:]
    prompt = _build_prompt(context_messages)
    client = _get_client()

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            if not response or not response.text:
                logger.warning("Gemini model %s returned an empty response", model_name)
                continue

            return response.text.strip()

        except genai_errors.ClientError as exc:
            logger.error("Gemini API error for model %s: %s", model_name, exc)
            if exc.code == 401:
                logger.error(
                    "Authentication failed. If using an AQ.* auth key, ensure it is "
                    "active in Google AI Studio and not blocked due to exposure."
                )
            continue
        except Exception as exc:
            logger.error("Unexpected Gemini error for model %s: %s", model_name, exc)
            continue

    return FALLBACK_MESSAGE
