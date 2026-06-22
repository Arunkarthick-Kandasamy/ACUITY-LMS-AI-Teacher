from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class EmptyResponseDetector:
    MIN_CONTENT_LENGTH = 10
    MIN_JSON_KEYS = 1
    BOILERPLATE_PHRASES = [
        "i cannot answer",
        "i don't know",
        "i am not sure",
        "i'm not sure",
        "as an ai",
        "i cannot provide",
        "i'm unable to",
        "i am unable to",
        "sorry, but",
        "i apologize",
    ]

    def is_empty(self, text: str | None) -> bool:
        if not text:
            return True
        stripped = text.strip()
        if not stripped:
            return True
        if len(stripped) < self.MIN_CONTENT_LENGTH:
            return True
        return False

    def is_boilerplate(self, text: str | None) -> bool:
        if not text:
            return True
        lower = text.lower().strip()
        for phrase in self.BOILERPLATE_PHRASES:
            if lower.startswith(phrase):
                return True
        return False

    def is_empty_json(self, data: dict | None) -> bool:
        if data is None:
            return True
        if len(data) < self.MIN_JSON_KEYS:
            return True
        return False

    def detect(self, text: str | None) -> str | None:
        if self.is_empty(text):
            return "empty_response"
        if self.is_boilerplate(text):
            return "boilerplate_response"
        return None

    def detect_json(self, data: dict | None) -> str | None:
        if self.is_empty_json(data):
            return "empty_json_response"
        return None
