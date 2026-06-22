from __future__ import annotations

import logging

from app.ai.memory.schemas import MemoryObservation

logger = logging.getLogger(__name__)


class MemoryExtractor:
    def extract(
        self,
        concept_title: str,
        student_response: str,
        mastery_estimate: float,
        evaluation: str | None,
        diagnosis_type: str | None,
        misconception: str | None,
        misconception_category: str | None,
        knowledge_gap: str | None,
        recommended_action: str | None,
        evaluation_score: float | None = None,
    ) -> list[MemoryObservation]:
        observations: list[MemoryObservation] = []

        struggles_obs = self._extract_struggles(
            mastery_estimate, recommended_action, knowledge_gap
        )
        if struggles_obs:
            observations.append(struggles_obs)

        excels_obs = self._extract_excels(
            mastery_estimate, recommended_action, evaluation, evaluation_score
        )
        if excels_obs:
            observations.append(excels_obs)

        misconception_obs = self._extract_misconception_pattern(
            diagnosis_type, misconception, misconception_category
        )
        if misconception_obs:
            observations.append(misconception_obs)

        preference_obs = self._extract_learning_preference(recommended_action)
        if preference_obs:
            observations.append(preference_obs)

        pacing_obs = self._extract_pacing_pattern(mastery_estimate, recommended_action)
        if pacing_obs:
            observations.append(pacing_obs)

        return observations

    def _extract_struggles(
        self,
        mastery_estimate: float,
        recommended_action: str | None,
        knowledge_gap: str | None,
    ) -> MemoryObservation | None:
        if mastery_estimate >= 0.5:
            return None
        text = "Student struggles with this topic"
        if knowledge_gap:
            text += f" ({knowledge_gap})"
        return MemoryObservation(
            memory_key="struggles_with",
            memory_text=text,
            confidence=1.0 - mastery_estimate,
            category="struggle",
            evidence=[f"mastery_estimate={mastery_estimate}"] if not knowledge_gap else [],
        )

    def _extract_excels(
        self,
        mastery_estimate: float,
        recommended_action: str | None,
        evaluation: str | None,
        evaluation_score: float | None = None,
    ) -> MemoryObservation | None:
        if mastery_estimate < 0.7:
            return None
        text = f"Student excels at this topic (mastery={mastery_estimate:.2f})"
        return MemoryObservation(
            memory_key="excels_at",
            memory_text=text,
            confidence=mastery_estimate,
            category="strength",
            evidence=[],
        )

    def _extract_misconception_pattern(
        self,
        diagnosis_type: str | None,
        misconception: str | None,
        misconception_category: str | None,
    ) -> MemoryObservation | None:
        if diagnosis_type != "misconception" or not misconception:
            return None
        text = f"Shows {misconception_category or 'conceptual'} misconception: {misconception}"
        return MemoryObservation(
            memory_key="misconception_pattern",
            memory_text=text,
            confidence=0.8,
            category="misconception",
            evidence=[],
        )

    def _extract_learning_preference(
        self, recommended_action: str | None
    ) -> MemoryObservation | None:
        if recommended_action == "example":
            return MemoryObservation(
                memory_key="learning_preference",
                memory_text="Student responds well to worked examples",
                confidence=0.6,
                category="preference",
                evidence=[],
            )
        return None

    def _extract_pacing_pattern(
        self,
        mastery_estimate: float,
        recommended_action: str | None,
    ) -> MemoryObservation | None:
        if mastery_estimate < 0.3 and recommended_action in ("reteach", "prerequisite"):
            return MemoryObservation(
                memory_key="pacing_pattern",
                memory_text="Student needs slower pacing with more reinforcement",
                confidence=0.7,
                category="pacing",
                evidence=[],
            )
        if mastery_estimate >= 0.8:
            return MemoryObservation(
                memory_key="pacing_pattern",
                memory_text="Student shows fast mastery, ready for accelerated pacing",
                confidence=0.7,
                category="pacing",
                evidence=[],
            )
        return None
