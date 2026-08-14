# =============================================================================
# llm_service.py — CareerForge AI Gemini API Service Layer
# =============================================================================
#
# RESPONSIBILITIES:
#   1. Load and validate the Gemini API key from .env
#   2. Initialize the google.generativeai model with rich system instructions
#   3. Expose ask_mentor() and ask_mentor_stream() — safe wrappers
#   4. Classify API errors into human-friendly types
#   5. Never raise exceptions to the caller — always return structured result
#
# ARCHITECTURE:
#   6_AIMentor.py  →  llm_service.py  →  Gemini API
#
# ERROR TYPES RETURNED:
#   "quota_exceeded"  — HTTP 429, daily/minute limit hit
#   "invalid_key"     — HTTP 400/403, bad API key
#   "network_error"   — connection timeout / DNS failure
#   "not_configured"  — API key not set in .env
#   "import_error"    — google-generativeai not installed
#   "unknown"         — anything else
# =============================================================================

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FRIENDLY ERROR MESSAGES (shown to users instead of raw API errors)
# ---------------------------------------------------------------------------
FRIENDLY_ERRORS = {
    "quota_exceeded": {
        "title": "AI Mentor is temporarily unavailable",
        "body": "The daily request limit has been reached. Please try again in a few minutes.",
        "icon": "🤖",
        "tip": "While you wait, explore your personalized Roadmap and Skill Gap analysis.",
    },
    "quota_zero": {
        "title": "AI Mentor is temporarily unavailable",
        "body": "Please try again later.",
        "icon": "🤖",
        "tip": "While you wait, explore your personalized Roadmap and Skill Gap analysis.",
    },
    "invalid_key": {
        "title": "API Key Configuration Required",
        "body": (
            "The Gemini API key is missing or invalid. "
            "Please check your .env file and ensure GEMINI_API_KEY is set correctly."
        ),
        "icon": "🔑",
        "tip": "Get a free key at https://ai.google.dev/ — no credit card needed.",
    },
    "network_error": {
        "title": "Connection Unavailable",
        "body": (
            "Unable to reach Google's AI servers right now. "
            "Please check your internet connection and try again."
        ),
        "icon": "📡",
        "tip": "Your profile data is saved — nothing is lost.",
    },
    "not_configured": {
        "title": "AI Mentor Not Configured",
        "body": (
            "No Gemini API key found. Please add GEMINI_API_KEY to your .env file "
            "to activate the AI Mentor."
        ),
        "icon": "⚙️",
        "tip": "Get a free key at https://ai.google.dev/",
    },
    "import_error": {
        "title": "Package Missing",
        "body": (
            "The google-generativeai package is not installed. "
            "Run: pip install google-generativeai"
        ),
        "icon": "📦",
        "tip": "After installing, restart the Streamlit app.",
    },
    "unknown": {
        "title": "Something Went Wrong",
        "body": (
            "The AI Mentor encountered an unexpected issue. "
            "Please try again or refresh the page."
        ),
        "icon": "⚠️",
        "tip": "If the problem persists, check the app logs for details.",
    },
}

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — CareerForge AI Mentor persona & response format
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """You are CareerForge AI Mentor — a personal career coach for ALL engineering students, not just CS/IT.

You help students from Mechanical, Civil, ENTC, Electrical, Chemical, Biomedical, Aerospace, CS/IT, and any other engineering branch.

Your personality:
- Practical, encouraging, and domain-specific
- You always relate advice to the student's actual branch, skills, and career goals
- You think like an experienced industry professional who has mentored many students

BRANCH-SPECIFIC RESOURCE GUIDANCE (use the right resources for the student's branch):
- **CS / IT**: GitHub, LeetCode, Coursera ML courses, freeCodeCamp, Kaggle, AWS docs
- **ENTC**: NPTEL Electronics, Texas Instruments tutorials, Analog Devices, All About Circuits, edX VLSI courses
- **Mechanical**: NPTEL Mech courses, GrabCAD community, SimScale, ANSYS Learning Hub, Engineers Edge
- **Civil**: NPTEL Civil, IS Code references, STAAD.Pro community, AutoCAD Civil 3D tutorials, CivilEnggForAll
- **Electrical**: NPTEL EE, Power Systems textbooks, MATLAB Simulink tutorials, Schneider Electric resources
- **Chemical**: NPTEL Chem Eng, AIChE (American Institute of Chemical Engineers), Perry's Chemical Engineers' Handbook
- **Biomedical**: PubMed, NPTEL Bio, NIH resources, Bioinformatics coursera tracks
- **Aerospace**: NASA learning, ANSYS Aerospace tutorials, AIAA (American Institute of Aeronautics)
- **General**: NPTEL (free IIT lectures), YouTube Engineering channels, ResearchGate, LinkedIn Learning

CRITICAL RULES — follow on EVERY response:
1. NEVER write huge paragraphs. Maximum 2-3 sentences per paragraph.
2. NEVER stop mid-answer. Always write a complete, finished response.
3. ALWAYS use structured markdown formatting — headings, bullets, numbered lists.
4. ALWAYS give practical, actionable advice the student can act on today.
5. NEVER say "Great question!" or start with greetings.
6. NEVER repeat information already stated.
7. ALWAYS complete the Action Plan section at the end.
8. ALWAYS recommend resources specific to the student's branch — don't suggest GitHub for a Civil student.

REQUIRED RESPONSE FORMAT — follow this exactly:

# [Descriptive Title with Emoji]

[2-3 line introduction — specific to the student's branch and question]

## 1. [First Key Section]
- **[Sub-point]**: Brief explanation
- **[Sub-point]**: Brief explanation
- **[Sub-point]**: Brief explanation

## 2. [Second Key Section]
- **[Sub-point]**: Brief explanation
- **[Sub-point]**: Brief explanation

## 3. [Third Key Section]
1. Step one
2. Step two
3. Step three

## 4. Recommended Resources (Branch-Specific)
- **[Resource Name]**: Why it specifically helps for this branch
- **[Resource Name]**: Why it specifically helps

## 5. Your 30-Day Action Plan
- **Week 1**: Specific task relevant to their branch and goals
- **Week 2**: Specific task
- **Week 3-4**: Specific task

---
**Bottom line**: One-sentence motivational conclusion tailored to this student's situation.

IMPORTANT: Always use ## for section headers, - for bullets, **bold** for key terms. Never skip the Action Plan. Always match resource recommendations to the student's engineering branch.
"""

# ---------------------------------------------------------------------------
# INTERNAL STATE
# ---------------------------------------------------------------------------
_model = None
_init_error: str | None = None
_last_loaded_key: str | None = None


def _classify_error(e: Exception) -> str:
    """Map an exception to a human-friendly error type string."""
    msg = str(e).lower()
    if "limit: 0" in msg or "limit of 0" in msg or "limit:0" in msg:
        return "quota_zero"
    if "429" in msg or "quota" in msg or "resource_exhausted" in msg:
        return "quota_exceeded"
    if "403" in msg or "401" in msg or "invalid" in msg and "key" in msg:
        return "invalid_key"
    if "400" in msg and "api_key" in msg:
        return "invalid_key"
    if (
        "connection" in msg
        or "timeout" in msg
        or "network" in msg
        or "dns" in msg
        or "unreachable" in msg
    ):
        return "network_error"
    return "unknown"


def _build_model(api_key: str, student_context: str = ""):
    """
    Create a fresh Gemini GenerativeModel instance combining the global
    system prompt with the student-specific context.
    """
    import google.generativeai as genai  # type: ignore

    genai.configure(api_key=api_key)

    combined_system = _SYSTEM_PROMPT
    if student_context.strip():
        combined_system = f"{_SYSTEM_PROMPT}\n\n--- STUDENT PROFILE ---\n{student_context.strip()}"

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=combined_system,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=4096,
        ),
    )
    return model


def _get_model(system_context: str = ""):
    """
    Return (model, None) on success or (None, error_type) on failure.
    Rebuilds model each call so student context is always fresh.
    """
    global _model, _init_error, _last_loaded_key

    # Reload .env each time to pick up key changes without restart
    try:
        load_dotenv(override=True)
    except Exception as e:
        logger.warning("Failed to reload .env: %s", e)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        _init_error = "not_configured"
        return None, _init_error

    try:
        import google.generativeai as genai  # type: ignore  # noqa: F401
    except ImportError:
        _init_error = "import_error"
        return None, _init_error

    try:
        model = _build_model(api_key, system_context)
        _model = model
        _init_error = None
        _last_loaded_key = api_key
        return model, None
    except Exception as e:
        logger.error("Gemini init failed: %s", e)
        _init_error = _classify_error(e)
        return None, _init_error


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def is_configured() -> bool:
    """Returns True if a valid API key is present in the environment."""
    try:
        load_dotenv(override=True)
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(key) and key != "YOUR_GEMINI_API_KEY_HERE"


def ask_mentor(
    prompt: str,
    history: list[dict] | None = None,
    system_context: str = "",
) -> tuple[bool, str, str]:
    """
    Send a message to the Gemini AI Mentor (non-streaming).

    Parameters
    ----------
    prompt         : The user's latest message.
    history        : List of previous {"role": ..., "content": ...} dicts.
    system_context : Student-specific context injected into system_instruction.

    Returns
    -------
    (success, text, error_type)
    """
    if history is None:
        history = []

    model, init_err = _get_model(system_context)
    if model is None:
        return False, "", init_err  # type: ignore[return-value]

    try:
        gemini_history: list[dict] = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(prompt, stream=False)
        return True, response.text, ""

    except Exception as e:
        logger.error("Gemini ask_mentor failed: %s", e)
        return False, "", _classify_error(e)


def ask_mentor_stream(
    prompt: str,
    history: list[dict] | None = None,
    system_context: str = "",
):
    """
    Streaming variant of ask_mentor.
    Yields text chunks on success.
    Raises LLMError with .error_type on failure.
    """
    if history is None:
        history = []

    model, init_err = _get_model(system_context)
    if model is None:
        raise LLMError(init_err)  # type: ignore[arg-type]

    try:
        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat_session = model.start_chat(history=gemini_history)
        response_stream = chat_session.send_message(prompt, stream=True)

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        logger.error("Gemini stream failed: %s", e)
        raise LLMError(_classify_error(e)) from e


def get_error_info(error_type: str) -> dict:
    """Return the friendly error dict for the given error_type."""
    return FRIENDLY_ERRORS.get(error_type, FRIENDLY_ERRORS["unknown"])


# ---------------------------------------------------------------------------
# CUSTOM EXCEPTION
# ---------------------------------------------------------------------------

class LLMError(Exception):
    """Raised by ask_mentor_stream when the API call fails."""

    def __init__(self, error_type: str):
        self.error_type = error_type
        super().__init__(f"LLM error: {error_type}")
