from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.memory.extraction import MemoryExtractor
from app.ai.memory.retrieval import MemoryRetriever
from app.ai.memory.schemas import MemoryContext, MemoryObservation, MemoryQuery
from app.ai.memory.service import MemoryService
from app.ai.nodes.retrieve_memories import retrieve_memories_node
from app.ai.state import TeacherAction, TeacherState


def _make_state(**overrides) -> TeacherState:
    state: TeacherState = {
        "session_id": "ses-1",
        "student_id": "sp-1",
        "concept_id": "con-1",
        "lesson_id": "lsn-1",
        "current_action": None,
        "conversation_history": [],
        "student_response": None,
        "mastery_estimate": 0.0,
        "teaching_content": None,
        "question": None,
        "evaluation": None,
        "example_content": None,
        "errors": [],
        "concept_title": "Variables",
        "concept_description": "Understanding variables in programming",
        "concept_content": [],
        "examples": [],
        "prerequisite_concepts": [],
        "recommended_action": None,
        "diagnosis_result": None,
        "expected_answer": None,
        "memory_context": None,
        "memory_observations": [],
    }
    state.update(overrides)
    return state


class TestMemoryExtraction:
    def setup_method(self) -> None:
        self.extractor = MemoryExtractor()

    def test_extract_struggles_low_mastery(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="I don't know",
            mastery_estimate=0.3,
            evaluation="Not quite",
            diagnosis_type="knowledge_gap",
            misconception=None,
            misconception_category=None,
            knowledge_gap="Missing prerequisite understanding",
            recommended_action="prerequisite",
        )
        keys = [o.memory_key for o in obs]
        assert "struggles_with" in keys
        struggle = next(o for o in obs if o.memory_key == "struggles_with")
        assert "Missing prerequisite understanding" in struggle.memory_text
        assert struggle.confidence == pytest.approx(0.7, abs=0.01)

    def test_extract_no_struggles_high_mastery(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="A variable stores data",
            mastery_estimate=0.85,
            evaluation="Great!",
            diagnosis_type="mastered",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )
        keys = [o.memory_key for o in obs]
        assert "struggles_with" not in keys

    def test_extract_excels_high_mastery(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Correct answer",
            mastery_estimate=0.9,
            evaluation="Excellent",
            diagnosis_type="mastered",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )
        keys = [o.memory_key for o in obs]
        assert "excels_at" in keys
        excels = next(o for o in obs if o.memory_key == "excels_at")
        assert excels.confidence == 0.9

    def test_extract_no_excels_low_mastery(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Wrong",
            mastery_estimate=0.3,
            evaluation="Not quite",
            diagnosis_type="misconception",
            misconception="Confuses with functions",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="reteach",
        )
        keys = [o.memory_key for o in obs]
        assert "excels_at" not in keys

    def test_extract_misconception_pattern(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="A variable is a function",
            mastery_estimate=0.3,
            evaluation="Wrong",
            diagnosis_type="misconception",
            misconception="Confuses variables with functions",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="reteach",
        )
        keys = [o.memory_key for o in obs]
        assert "misconception_pattern" in keys
        mc = next(o for o in obs if o.memory_key == "misconception_pattern")
        assert "conceptual" in mc.memory_text
        assert mc.confidence == 0.8

    def test_extract_no_misconception_when_not_diagnosed(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Correct",
            mastery_estimate=0.9,
            evaluation="Great",
            diagnosis_type="mastered",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )
        keys = [o.memory_key for o in obs]
        assert "misconception_pattern" not in keys

    def test_extract_learning_preference_example(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Partial answer",
            mastery_estimate=0.6,
            evaluation="Mostly right",
            diagnosis_type="minor_error",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="example",
        )
        keys = [o.memory_key for o in obs]
        assert "learning_preference" in keys
        pref = next(o for o in obs if o.memory_key == "learning_preference")
        assert "worked examples" in pref.memory_text

    def test_extract_no_learning_preference_when_not_example(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Correct",
            mastery_estimate=0.9,
            evaluation="Great",
            diagnosis_type="mastered",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )
        keys = [o.memory_key for o in obs]
        assert "learning_preference" not in keys

    def test_extract_pacing_pattern_slow(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="I don't understand",
            mastery_estimate=0.2,
            evaluation="Very weak",
            diagnosis_type="misconception",
            misconception="Fundamental confusion",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="reteach",
        )
        keys = [o.memory_key for o in obs]
        assert "pacing_pattern" in keys
        pace = next(o for o in obs if o.memory_key == "pacing_pattern")
        assert "slower pacing" in pace.memory_text

    def test_extract_pacing_pattern_fast(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Perfect answer",
            mastery_estimate=0.9,
            evaluation="Excellent",
            diagnosis_type="mastered",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            recommended_action="continue",
        )
        keys = [o.memory_key for o in obs]
        assert "pacing_pattern" in keys
        pace = next(o for o in obs if o.memory_key == "pacing_pattern")
        assert "accelerated pacing" in pace.memory_text

    def test_extract_multiple_observations(self) -> None:
        obs = self.extractor.extract(
            concept_title="Variables",
            student_response="Wrong answer",
            mastery_estimate=0.2,
            evaluation="Incorrect",
            diagnosis_type="misconception",
            misconception="Fundamental confusion",
            misconception_category="conceptual",
            knowledge_gap=None,
            recommended_action="reteach",
        )
        assert len(obs) >= 3  # struggles + misconception + pacing


class TestMemoryRetrieval:
    @pytest.mark.asyncio
    async def test_retrieve_from_db_empty(self) -> None:
        db = MagicMock()
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        retriever = MemoryRetriever(db)
        query = MemoryQuery(student_id="sp-1", concept_id="con-1", lesson_id="lsn-1")
        context = await retriever.retrieve(query)

        assert isinstance(context, MemoryContext)
        assert len(context.observations) == 0
        assert len(context.relevant_memories) == 0

    @pytest.mark.asyncio
    async def test_retrieve_empty_context_without_db(self) -> None:
        retriever = MemoryRetriever(db=None)
        query = MemoryQuery(student_id="sp-1", concept_id="con-1", lesson_id="lsn-1")
        context = await retriever.retrieve(query)

        assert isinstance(context, MemoryContext)
        assert len(context.observations) == 0
        assert len(context.relevant_memories) == 0

    @pytest.mark.asyncio
    async def test_misconception_retrieval(self) -> None:
        db = MagicMock()
        mock_misconception = MagicMock()
        mock_misconception.category = "conceptual"
        mock_misconception.description = "Confuses variables with functions"
        mock_misconception.frequency = 3
        mock_misconception.evidence = ["previous session"]

        mock_empty_result = MagicMock()
        mock_empty_result.unique.return_value.scalars.return_value.all.return_value = []

        mock_mc_result = MagicMock()
        mock_mc_result.unique.return_value.scalars.return_value.all.return_value = [mock_misconception]

        db.execute = AsyncMock(side_effect=[mock_empty_result, mock_mc_result])

        retriever = MemoryRetriever(db)
        query = MemoryQuery(student_id="sp-1", concept_id="con-1", lesson_id="lsn-1")
        context = await retriever.retrieve(query)

        assert len(context.recurring_misconceptions) > 0
        assert "3 times" in context.recurring_misconceptions[0]

    @pytest.mark.asyncio
    async def test_store_embedding_graceful_without_qdrant(self) -> None:
        retriever = MemoryRetriever(db=None)
        obs = MemoryObservation(
            memory_key="struggles_with",
            memory_text="Student struggles with variables",
            confidence=0.7,
        )
        result = await retriever.store_embedding(obs, "sp-1", "ses-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_ensure_collection_graceful_without_qdrant(self) -> None:
        retriever = MemoryRetriever(db=None)
        await retriever.ensure_collection()

    def test_mock_embedding_is_list_of_768(self) -> None:
        retriever = MemoryRetriever(db=None)
        embedding = retriever._mock_embedding("test text")
        assert len(embedding) == 768
        assert all(-1.0 <= v <= 1.0 for v in embedding)

    def test_mock_embedding_is_deterministic(self) -> None:
        retriever = MemoryRetriever(db=None)
        e1 = retriever._mock_embedding("same text")
        e2 = retriever._mock_embedding("same text")
        assert e1 == e2


class TestMemoryService:
    @pytest.mark.asyncio
    async def test_extract_and_store_no_db(self) -> None:
        service = MemoryService(db=None)
        obs = await service.extract_and_store(
            student_id="sp-1",
            session_id="ses-1",
            concept_title="Variables",
            student_response="Wrong answer",
            mastery_estimate=0.3,
            diagnosis_type="misconception",
            misconception="Confuses variables with functions",
            misconception_category="conceptual",
            recommended_action="reteach",
        )
        assert len(obs) >= 2

    @pytest.mark.asyncio
    async def test_persist_new_observation(self) -> None:
        db = MagicMock()
        db.flush = AsyncMock()
        db.execute = AsyncMock()

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        service = MemoryService(db)
        obs = MemoryObservation(
            memory_key="struggles_with",
            memory_text="Student struggles with variables",
            confidence=0.7,
        )
        entry = await service._persist_observation("sp-1", "ses-1", obs)

        assert entry is not None
        assert entry.memory_key == "struggles_with"
        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_persist_existing_observation_updates_confidence(self) -> None:
        db = MagicMock()
        db.flush = AsyncMock()

        existing = MagicMock()
        existing.confidence = 0.5

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = existing
        db.execute = AsyncMock(return_value=mock_result)

        service = MemoryService(db)
        obs = MemoryObservation(
            memory_key="struggles_with",
            memory_text="Student struggles with variables",
            confidence=0.8,
        )
        entry = await service._persist_observation("sp-1", "ses-1", obs)

        assert entry is not None
        assert entry.confidence == 0.8  # max(0.5, 0.8)
        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_persist_without_db_returns_none(self) -> None:
        service = MemoryService(db=None)
        obs = MemoryObservation(
            memory_key="struggles_with",
            memory_text="Test",
            confidence=0.5,
        )
        result = await service._persist_observation("sp-1", "ses-1", obs)
        assert result is None

    @pytest.mark.asyncio
    async def test_retrieve_relevant_empty(self) -> None:
        service = MemoryService(db=None)
        context = await service.retrieve_relevant(
            student_id="sp-1",
            concept_id="con-1",
            lesson_id="lsn-1",
        )
        assert isinstance(context, MemoryContext)
        assert len(context.observations) == 0

    @pytest.mark.asyncio
    async def test_format_memory_context_no_memories(self) -> None:
        service = MemoryService(db=None)
        text = await service.format_memory_context("sp-1", "con-1", "lsn-1")
        assert text == "No prior observations for this student."

    @pytest.mark.asyncio
    async def test_format_memory_context_with_memories(self) -> None:
        db = MagicMock()
        mock_empty = MagicMock()
        mock_empty.unique.return_value.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_empty)

        service = MemoryService(db)
        text = await service.format_memory_context("sp-1", "con-1", "lsn-1")
        assert isinstance(text, str)


class TestRetrieveMemoriesNode:
    @pytest.mark.asyncio
    async def test_retrieve_node_returns_context(self) -> None:
        state = _make_state()

        with patch(
            "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
            new_callable=AsyncMock,
        ) as mock_retrieve:
            mock_retrieve.return_value = MemoryContext(
                observations=[],
                relevant_memories=[],
                recurring_misconceptions=[],
                learning_signals=[],
            )
            with patch(
                "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                new_callable=AsyncMock,
            ) as mock_format:
                mock_format.return_value = "Student learns best from examples."

                result = await retrieve_memories_node(state)

                assert result["memory_context"] == "Student learns best from examples."
                assert result["memory_observations"] == []

    @pytest.mark.asyncio
    async def test_retrieve_node_with_observations(self) -> None:
        state = _make_state()

        with patch(
            "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
            new_callable=AsyncMock,
        ) as mock_retrieve:
            mock_retrieve.return_value = MemoryContext(
                observations=[
                    MemoryObservation(
                        memory_key="struggles_with",
                        memory_text="Student struggles with fractions",
                        confidence=0.8,
                    ),
                ],
                relevant_memories=["Student struggles with fractions"],
                recurring_misconceptions=[],
                learning_signals=[],
            )
            with patch(
                "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                new_callable=AsyncMock,
            ) as mock_format:
                mock_format.return_value = "Student Memory Context:\n- Student struggles with fractions"

                result = await retrieve_memories_node(state)

                assert "struggles with fractions" in result["memory_context"]
                assert len(result["memory_observations"]) == 1
                assert result["memory_observations"][0]["memory_key"] == "struggles_with"


class TestGraphMemoryIntegration:
    @pytest.mark.asyncio
    async def test_graph_retrieve_memories_before_teach(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_state()

        with patch(
            "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
            new_callable=AsyncMock,
        ) as mock_retrieve:
            mock_retrieve.return_value = MemoryContext(
                observations=[
                    MemoryObservation(
                        memory_key="struggles_with",
                        memory_text="Student struggles with variables",
                        confidence=0.7,
                    ),
                ],
                relevant_memories=["Student struggles with variables"],
                recurring_misconceptions=[],
                learning_signals=[],
            )
            with patch(
                "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                new_callable=AsyncMock,
            ) as mock_format:
                mock_format.return_value = "Student Memory Context:\n- Student struggles with variables"
                with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_teach:
                    mock_teach.return_value = "Let me explain variables..."
                    with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_q:
                        mock_q.return_value = "What is a variable?"

                        result = await teacher_graph.ainvoke(state)

                        assert result["memory_context"] is not None
                        assert "struggles with variables" in result["memory_context"]
                        assert result["teaching_content"] is not None

    @pytest.mark.asyncio
    async def test_graph_teach_uses_memory_in_prompt(self) -> None:
        from app.ai.nodes.teach import teach_node

        state = _make_state(
            memory_context="Student learns best from worked examples",
            memory_observations=[
                {
                    "memory_key": "learning_preference",
                    "memory_text": "Student learns best from worked examples",
                    "confidence": 0.6,
                }
            ],
        )

        with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Teaching content with examples..."

            result = await teach_node(state)

            assert result["teaching_content"] is not None
            mock_gen.assert_called_once()
            prompt_arg = mock_gen.call_args[0][0]
            assert "Student learns best" in prompt_arg

    @pytest.mark.asyncio
    async def test_graph_reteach_goes_through_retrieve_memories(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="Wrong answer",
            teaching_content="Variables are containers.",
            question="What is a variable?",
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.3,
                "feedback": "Not quite.",
                "understanding": "weak",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
            ) as mock_diag:
                from app.ai.diagnosis.schemas import DiagnosisResult
                from app.common.types import MisconceptionCategory

                mock_diag.return_value = DiagnosisResult(
                    diagnosis_type="misconception",
                    misconception="Confuses variables with functions",
                    misconception_category=MisconceptionCategory.CONCEPTUAL,
                    knowledge_gap=None,
                    prerequisite_concepts=[],
                    recommended_action="reteach",
                    evidence=["confusion"],
                    remediation="Re-teach variables",
                )
                with patch(
                    "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
                    new_callable=AsyncMock,
                ) as mock_retrieve:
                    mock_retrieve.return_value = MemoryContext(
                        observations=[],
                        relevant_memories=[],
                        recurring_misconceptions=[],
                        learning_signals=[],
                    )
                    with patch(
                        "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                        new_callable=AsyncMock,
                    ) as mock_format:
                        mock_format.return_value = "No prior observations."
                        with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_teach:
                            mock_teach.return_value = "Let me re-explain..."
                            with patch(
                                "app.ai.nodes.ask_question.GeminiService.generate",
                                new_callable=AsyncMock,
                            ) as mock_q:
                                mock_q.return_value = "New question?"

                                result = await teacher_graph.ainvoke(state)

                                assert result["memory_context"] is not None
                                assert result["teaching_content"] is not None
                                assert result["question"] is not None
