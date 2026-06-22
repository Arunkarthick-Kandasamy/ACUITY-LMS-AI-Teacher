from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class HallucinationPreventer:
    CONFIDENCE_FLOOR = 0.1
    MAX_SCORE_CEILING = 1.0

    DISCLAIMER_PATTERNS = [
        re.compile(r"\bI'?m?\s*(not|can'?t|unable|cannot)\s*(sure|certain|confirm|verify|answer)\b", re.IGNORECASE),
        re.compile(r"\bas an?\s+(AI|language model|LLM)\b", re.IGNORECASE),
        re.compile(r"\bI\s+don'?t\s+(have|know|understand)\b", re.IGNORECASE),
    ]

    FACTUAL_OVERRIDE_PATTERNS = [
        re.compile(r"\b(mastered|perfect|excellent|outstanding)\b", re.IGNORECASE),
        re.compile(r"\balways\s+(understands|gets|knows)\b", re.IGNORECASE),
    ]

    def check_response(self, text: str, data: dict[str, Any] | None) -> list[str]:
        warnings: list[str] = []

        for pattern in self.DISCLAIMER_PATTERNS:
            if pattern.search(text):
                warnings.append("response_contains_disclaimer")
                break

        if data and "score" in data:
            score = data.get("score", 0.5)
            if isinstance(score, (int, float)):
                if score < self.CONFIDENCE_FLOOR:
                    warnings.append("score_below_confidence_floor")
                if score > self.MAX_SCORE_CEILING:
                    warnings.append("score_above_max_ceiling")

        factual_overrides = 0
        for pattern in self.FACTUAL_OVERRIDE_PATTERNS:
            matches = pattern.findall(text)
            factual_overrides += len(matches)

        if factual_overrides >= 3:
            warnings.append("excessive_factual_overrides")

        return warnings

    def check_data_consistency(
        self, data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> list[str]:
        warnings: list[str] = []

        if not data:
            return warnings

        if "score" in data and context and "max_possible_score" in context:
            if data["score"] > context["max_possible_score"]:
                warnings.append("score_exceeds_maximum")

        return warnings
