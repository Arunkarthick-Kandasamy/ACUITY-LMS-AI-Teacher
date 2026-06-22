from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.ai.memory.extraction import MemoryExtractor
from app.ai.memory.schemas import MemoryObservation


class TestMemoryExtractionFlow:
    def test_extract_struggles_low_mastery(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Variables",
            student_response="I don't understand",
            mastery_estimate=0.2,
            evaluation=None,
            diagnosis_type="knowledge_gap",
            misconception=None,
            misconception_category=None,
            knowledge_gap="Missing variable fundamentals",
            recommended_action="reteach",
        )

        struggles = [o for o in observations if o.memory_key == "struggles_with"]
        assert len(struggles) == 1
        assert "Missing variable fundamentals" in struggles[0].memory_text
        assert struggles[0].confidence > 0.5

    def test_extract_excels_high_mastery(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Variables",
            student_response="A variable stores data that can change.",
            mastery_estimate=0.9,
            evaluation="Excellent understanding!",
            diagnosis_type=None,
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )

        excels = [o for o in observations if o.memory_key == "excels_at"]
        assert len(excels) == 1
        assert excels[0].confidence >= 0.7

    def test_extract_misconception_pattern(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Variables",
            student_response="Variables are constant.",
            mastery_estimate=0.3,
            evaluation=None,
            diagnosis_type="misconception",
            misconception="Thinks variables cannot change",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="example",
        )

        mc = [o for o in observations if o.memory_key == "misconception_pattern"]
        assert len(mc) == 1
        assert "conceptual" in mc[0].memory_text

    def test_extract_learning_preference_example(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Functions",
            student_response="Show me how it works",
            mastery_estimate=0.4,
            evaluation=None,
            diagnosis_type=None,
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="example",
        )

        prefs = [o for o in observations if o.memory_key == "learning_preference"]
        assert len(prefs) == 1
        assert "worked examples" in prefs[0].memory_text

    def test_extract_pacing_pattern_slow(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Algebra",
            student_response="This is too hard",
            mastery_estimate=0.2,
            evaluation=None,
            diagnosis_type="knowledge_gap",
            misconception=None,
            misconception_category=None,
            knowledge_gap="Missing prerequisites",
            recommended_action="reteach",
        )

        pacing = [o for o in observations if o.memory_key == "pacing_pattern"]
        assert len(pacing) == 1
        assert "slower pacing" in pacing[0].memory_text

    def test_extract_multiple_observations(self) -> None:
        extractor = MemoryExtractor()
        observations = extractor.extract(
            concept_title="Variables",
            student_response="I think variables are fixed values.",
            mastery_estimate=0.25,
            evaluation="Does not understand reassignment",
            diagnosis_type="misconception",
            misconception="Thinks variables are immutable",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="example",
            evaluation_score=0.25,
        )

        assert len(observations) >= 2
        keys = {o.memory_key for o in observations}
        assert "struggles_with" in keys
        assert "misconception_pattern" in keys
