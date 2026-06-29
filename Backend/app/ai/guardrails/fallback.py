from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


FALLBACK_RESPONSES: dict[str, Any] = {
    "evaluate_response": {
        "score": 0.5,
        "feedback": "Unable to evaluate the response at this time. Please try again.",
        "understanding": "partial",
    },
    "diagnose": {
        "diagnosis_type": "minor_error",
        "misconception": None,
        "misconception_category": None,
        "knowledge_gap": None,
        "prerequisite_concepts": [],
        "recommended_action": "example",
        "evidence": [],
        "remediation": "Provide additional practice and examples.",
    },
    "generate_report": {
        "title": "Weekly Learning Progress Report",
        "executive_summary": "This report provides an overview of the student's recent learning activities, "
        "mastery progress, and areas that may need additional attention.",
        "strengths": [
            {
                "description": "The student is actively engaged in learning sessions",
                "category": "engagement",
                "evidence": [],
            }
        ],
        "challenges": [
            {
                "description": "Some concepts may need additional practice to reach mastery",
                "category": "conceptual",
                "severity": "medium",
                "concept_title": None,
            }
        ],
        "recommendations": [
            {
                "description": "Encourage regular practice sessions to reinforce learning",
                "priority": "medium",
                "category": "practice",
            }
        ],
        "risk_indicators": [],
    },
    "memory_extract": {
        "struggles": [],
        "excels": [],
        "misconceptions": [],
        "learning_preferences": [],
        "pacing_notes": "Insufficient data to determine pacing patterns.",
    },
    "teach": (
        "Let me explain this concept step by step. "
        "First, we need to understand the basic idea, "
        "then we can build upon it to grasp more complex aspects."
    ),
    "ask_question": (
        "What is the key idea behind this concept? "
        "Explain how it applies to real-world scenarios."
    ),
    "provide_example": (
        "Here is a practical example to illustrate this concept. "
        "Consider a real-world scenario where this concept applies. "
        "This example demonstrates the core principle by showing how it works in practice."
    ),
}


class FallbackHandler:
    def get_fallback(self, prompt_name: str) -> Any:
        return FALLBACK_RESPONSES.get(prompt_name, FALLBACK_RESPONSES["teach"])

    def to_json(self, prompt_name: str) -> dict[str, Any]:
        fallback = self.get_fallback(prompt_name)
        if isinstance(fallback, dict):
            return fallback
        return {"text": str(fallback), "score": 0.5, "understanding": "partial"}
