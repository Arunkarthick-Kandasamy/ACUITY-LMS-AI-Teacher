from __future__ import annotations

from app.ai.prompts.v1.diagnosis import PROMPT_DIAGNOSE, SYSTEM_DIAGNOSE
from app.ai.prompts.v1.memory import PROMPT_MEMORY_EXTRACT
from app.ai.prompts.v1.reporting import PROMPT_REPORT_GENERATION, SYSTEM_REPORT_GENERATION
from app.ai.prompts.v1.teaching import (
    PROMPT_ASK_QUESTION,
    PROMPT_EVALUATE_RESPONSE,
    PROMPT_PROVIDE_EXAMPLE,
    PROMPT_TEACH,
    SYSTEM_ASK_QUESTION,
    SYSTEM_EVALUATE_RESPONSE,
    SYSTEM_PROVIDE_EXAMPLE,
    SYSTEM_TEACH,
)

VERSION = "1.0.0"
VERSION_LABEL = "v1"

PROMPT_REGISTRY: dict[str, dict[str, str]] = {
    "teach": {"system": SYSTEM_TEACH, "user": PROMPT_TEACH},
    "ask_question": {"system": SYSTEM_ASK_QUESTION, "user": PROMPT_ASK_QUESTION},
    "evaluate_response": {"system": SYSTEM_EVALUATE_RESPONSE, "user": PROMPT_EVALUATE_RESPONSE},
    "provide_example": {"system": SYSTEM_PROVIDE_EXAMPLE, "user": PROMPT_PROVIDE_EXAMPLE},
    "diagnose": {"system": SYSTEM_DIAGNOSE, "user": PROMPT_DIAGNOSE},
    "generate_report": {"system": SYSTEM_REPORT_GENERATION, "user": PROMPT_REPORT_GENERATION},
    "memory_extract": {"system": "", "user": PROMPT_MEMORY_EXTRACT},
}


def get_prompt(name: str) -> dict[str, str] | None:
    return PROMPT_REGISTRY.get(name)


def list_prompts() -> list[str]:
    return list(PROMPT_REGISTRY.keys())


__all__ = [
    "VERSION",
    "VERSION_LABEL",
    "PROMPT_REGISTRY",
    "get_prompt",
    "list_prompts",
    "SYSTEM_TEACH",
    "PROMPT_TEACH",
    "SYSTEM_ASK_QUESTION",
    "PROMPT_ASK_QUESTION",
    "SYSTEM_EVALUATE_RESPONSE",
    "PROMPT_EVALUATE_RESPONSE",
    "SYSTEM_PROVIDE_EXAMPLE",
    "PROMPT_PROVIDE_EXAMPLE",
    "SYSTEM_DIAGNOSE",
    "PROMPT_DIAGNOSE",
    "SYSTEM_REPORT_GENERATION",
    "PROMPT_REPORT_GENERATION",
    "PROMPT_MEMORY_EXTRACT",
]
