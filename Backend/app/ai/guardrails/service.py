from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.ai.guardrails.empty_detector import EmptyResponseDetector
from app.ai.guardrails.fallback import FallbackHandler
from app.ai.guardrails.hallucination import HallucinationPreventer
from app.ai.guardrails.json_validator import JsonValidator

logger = logging.getLogger(__name__)


@dataclass
class GuardrailResult:
    passed: bool
    data: dict[str, Any] | str | None = None
    warnings: list[str] = field(default_factory=list)
    fallback_used: bool = False
    error: str | None = None


class GuardrailService:
    def __init__(self) -> None:
        self.json_validator = JsonValidator()
        self.empty_detector = EmptyResponseDetector()
        self.hallucination_preventer = HallucinationPreventer()
        self.fallback_handler = FallbackHandler()

    async def check_json_response(
        self, text: str, prompt_name: str = "evaluate_response"
    ) -> GuardrailResult:
        empty_issue = self.empty_detector.detect(text)
        if empty_issue:
            logger.warning("Guardrail: %s for prompt %s", empty_issue, prompt_name)
            fallback = self.fallback_handler.to_json(prompt_name)
            return GuardrailResult(
                passed=False,
                data=fallback,
                fallback_used=True,
                error=empty_issue,
            )

        data, error = self.json_validator.validate(text, prompt_name)
        if error:
            logger.warning("Guardrail: JSON validation failed for %s: %s", prompt_name, error)
            fallback = self.fallback_handler.to_json(prompt_name)
            return GuardrailResult(
                passed=False,
                data=fallback,
                fallback_used=True,
                error=error,
            )

        empty_json_issue = self.empty_detector.detect_json(data)
        if empty_json_issue:
            logger.warning("Guardrail: %s for prompt %s", empty_json_issue, prompt_name)
            fallback = self.fallback_handler.to_json(prompt_name)
            return GuardrailResult(
                passed=False,
                data=fallback,
                fallback_used=True,
                error=empty_json_issue,
            )

        warnings = self.hallucination_preventer.check_response(text, data)
        if warnings:
            logger.warning("Guardrail: hallucination warnings for %s: %s", prompt_name, warnings)

        return GuardrailResult(
            passed=True,
            data=data,
            warnings=warnings,
        )

    async def check_text_response(
        self, text: str, prompt_name: str = "teach"
    ) -> GuardrailResult:
        empty_issue = self.empty_detector.detect(text)
        if empty_issue:
            logger.warning("Guardrail: %s for prompt %s", empty_issue, prompt_name)
            fallback = self.fallback_handler.get_fallback(prompt_name)
            return GuardrailResult(
                passed=False,
                data=fallback,
                fallback_used=True,
                error=empty_issue,
            )

        warnings = self.hallucination_preventer.check_response(text, None)
        if warnings:
            logger.warning("Guardrail: hallucination warnings for %s: %s", prompt_name, warnings)

        return GuardrailResult(
            passed=True,
            data=text,
            warnings=warnings,
        )
