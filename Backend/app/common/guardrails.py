from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

CONTENT_BLOCKLIST: list[re.Pattern] = [
    re.compile(r"\b(hate|violence|explicit|harmful|dangerous)\b", re.IGNORECASE),
]


def validate_content(content: str | None) -> bool:
    if not content or not content.strip():
        return False
    lower = content.lower()
    for pattern in CONTENT_BLOCKLIST:
        if pattern.search(lower):
            logger.warning("Content blocked by guardrail: matched pattern %s", pattern.pattern)
            return False
    return True


def validate_response(response: str, context: dict[str, Any] | None = None) -> tuple[bool, str]:
    if not response or not response.strip():
        return False, "empty_response"
    lower = response.lower()
    for pattern in CONTENT_BLOCKLIST:
        if pattern.search(lower):
            return False, f"response contains blocked content matching: {pattern.pattern}"
    disclaimers = [
        "i cannot answer",
        "i don't know",
        "as an ai",
        "i cannot provide",
        "i'm unable to",
        "i am unable to",
    ]
    for phrase in disclaimers:
        if lower.startswith(phrase):
            logger.warning("Response contains disclaimer phrase: %s", phrase)
            return False, "response_contains_disclaimer"
    return True, ""
