from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set, using mock responses")
            self._client = None
            return None

        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        except ImportError:
            logger.warning("google-genai not installed, using mock responses")
            self._client = None

        return self._client

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        client = self._get_client()
        if client is None:
            return _mock_gemini_response(prompt, system_instruction)

        contents = []
        if system_instruction:
            contents.append({"role": "system", "parts": [{"text": system_instruction}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                logger.warning("Gemini API rate limited (429), using fallback")
            elif "500" in error_str or "503" in error_str:
                logger.warning("Gemini API server error, using fallback")
            else:
                logger.error("Gemini API call failed: %s", e)
            return _mock_gemini_response(prompt, system_instruction)

    async def generate_json(
        self, prompt: str, system_instruction: str | None = None
    ) -> dict:
        text = await self.generate(prompt, system_instruction)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {"score": 0.5, "feedback": text, "understanding": "partial"}


def _mock_gemini_response(prompt: str, system_instruction: str | None = None) -> str:
    if system_instruction and "evaluat" in system_instruction.lower():
        return json.dumps({
            "score": 0.8,
            "feedback": "Good understanding shown. You correctly identified the key concepts.",
            "understanding": "strong",
        })
    if system_instruction and "question" in system_instruction.lower():
        return (
            "What is the key idea behind this concept? "
            "Explain how it applies to real-world scenarios."
        )
    if system_instruction and "example" in system_instruction.lower():
        return (
            "Here is a practical example to illustrate this concept. "
            "Consider a real-world scenario where this concept applies... "
            "This example demonstrates the core principle by showing how it works in practice."
        )
    return (
        "This concept is about understanding the fundamental principles. "
        "Let me explain it step by step. First, we need to understand the basic idea. "
        "Then we can build upon it to grasp more complex aspects."
    )
