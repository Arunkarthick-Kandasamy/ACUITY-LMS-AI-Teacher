from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class JsonValidator:
    REQUIRED_FIELDS: dict[str, list[str]] = {
        "evaluate_response": ["score", "feedback", "understanding"],
        "diagnose": [
            "diagnosis_type",
            "misconception",
            "misconception_category",
            "knowledge_gap",
            "recommended_action",
        ],
        "generate_report": [
            "title",
            "executive_summary",
            "strengths",
            "challenges",
            "recommendations",
        ],
        "memory_extract": [
            "struggles",
            "excels",
            "misconceptions",
            "learning_preferences",
            "pacing_notes",
        ],
    }

    def validate(
        self, text: str, prompt_name: str = "evaluate_response"
    ) -> tuple[dict[str, Any] | None, str | None]:
        text = text.strip()
        if not text:
            return None, "Empty response text"

        cleaned = self._strip_code_fences(text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            extracted = self._extract_json_substring(cleaned)
            if extracted is not None:
                try:
                    data = json.loads(extracted)
                except json.JSONDecodeError:
                    return None, f"Invalid JSON: {e}"
            else:
                return None, f"Invalid JSON: {e}"

        if not isinstance(data, dict):
            return None, "JSON response is not an object"

        required = self.REQUIRED_FIELDS.get(prompt_name, [])
        missing = [f for f in required if f not in data]
        if missing:
            return None, f"Missing required fields: {missing}"

        if "score" in data:
            try:
                data["score"] = float(data["score"])
                data["score"] = max(0.0, min(1.0, data["score"]))
            except (ValueError, TypeError):
                data["score"] = 0.5

        return data, None

    def _strip_code_fences(self, text: str) -> str:
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text.strip()

    def _extract_json_substring(self, text: str) -> str | None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return None
