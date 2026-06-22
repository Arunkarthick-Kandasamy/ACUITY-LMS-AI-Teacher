# AI Implementation Audit

> Audit based on actual source files in `app/ai/`. No assumptions about planned or documented behavior from ARCHITECTURE.md or IMPLEMENTATION_PLAN.md used as evidence of implementation.

---

## Teacher Graph (LangGraph)

**File:** `app/ai/graphs/teacher.py`
**State Type:** `TeacherState` (TypedDict) — `app/ai/state.py:16`
**Action Enum:** `TeacherAction` — `app/ai/state.py:7`

### Graph Structure

```
                    ┌──────────────────┐
                    │  decide_entry()  │
                    │  (conditional)   │
                    └────────┬─────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
               ▼             │             ▼
    ┌──────────────────┐     │   ┌──────────────────┐
    │ retrieve_memories │     │   │ evaluate_response│
    └────────┬─────────┘     │   └────────┬─────────┘
             │               │            │
             ▼               │            ▼
    ┌──────────────────┐     │   ┌──────────────────┐
    │      teach       │     │   │     diagnose     │
    └────────┬─────────┘     │   └────────┬─────────┘
             │               │     ┌──────┴──────┐
             ▼               │     │  conditional │
    ┌──────────────────┐     │     │  (decide_    │
    │   ask_question   │     │     │  after_      │
    └────────┬─────────┘     │     │  diagnosis)  │
             │               │     └──────┬──────┘
             ▼               │     ┌──────┼──────┐
    ┌──────────────────┐     │     ▼      ▼      ▼
    │       END        │     │ ┌──────┐┌──────┐┌──────┐
    └──────────────────┘     │ │example││complete││ reteach│
                             │ └──┬───┘└──┬───┘ └──┬───┘
                             │    │       │        │
                             │    ▼       ▼        │
                             │ ask_question  END   │
                             │                     │
                             └─────────────────────┘
                                         │
                                         ▼
                                      merge (END)
```

### Graph Nodes (7 total)

| Node | Function | File | Implements |
|------|----------|------|------------|
| `decide_entry` | Conditional router | `app/ai/graphs/teacher.py:25` | Routes to `retrieve_memories` (new) or `evaluate_response` (has response) |
| `retrieve_memories` | Memory retrieval | `app/ai/graphs/teacher.py:35` | Loads student memories via `app/ai/memory/retrieval.py` |
| `teach` | Content delivery | `app/ai/nodes/teach.py:12` | Generates teaching content via Gemini |
| `ask_question` | Quiz generation | `app/ai/nodes/teach.py:45` | Generates exercise/prompt via Gemini |
| `evaluate_response` | Grading | `app/ai/nodes/evaluate.py:15` | Evaluates student response, assigns score |
| `diagnose` | Misconception detection | `app/ai/nodes/diagnose.py:12` | Detects misconception patterns, updates DB |
| `provide_example` | Example demonstration | `app/ai/nodes/teach.py:70` | Generates worked example |
| `complete_concept` | Progression | `app/ai/nodes/teach.py:95` | Marks concept as complete, updates mastery |

### Graph Edges

| From | To | Condition |
|------|----|-----------|
| decide_entry | retrieve_memories | No `student_response` in state |
| decide_entry | evaluate_response | `student_response` present |
| retrieve_memories | teach | Always |
| teach | ask_question | Always |
| ask_question | END | Always |
| evaluate_response | diagnose | Always |
| diagnose | decide_after_diagnosis | Always |
| decide_after_diagnosis | retrieve_memories | reteach / prerequisite |
| decide_after_diagnosis | provide_example | example |
| decide_after_diagnosis | complete_concept | continue / complete |
| provide_example | ask_question | Always |
| complete_concept | merge | Always |
| merge | END | Always |

---

## AI Service Architecture

### Gemini Integration

**File:** `app/ai/services/gemini.py`

**Class:** `GeminiService`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(api_key: str, model: str = "gemini-pro")` | Initialize with API key |
| `generate` | `(prompt: str, response_type: str = "text")` | Generate text or JSON response |
| `generate_json` | `(prompt: str)` | Generate structured JSON output |

**Behavior:**
- `app/ai/services/gemini.py:39` — If `api_key` is empty or missing, falls back to `_mock_response()` returning hard-coded sample data
- `app/config.py:46` — `gemini_api_key` defaults to `""`
- **Without explicit env configuration, the AI system operates entirely in mock mode**

### Memory System

**File:** `app/ai/memory/retrieval.py`

| Function | Purpose |
|----------|---------|
| `retrieve_memories(student_id, session_id, limit=10)` | Load recent memories from DB |
| `extract_memories(conversation_history)` | Extract key observations from conversation |
| `store_memory(student_id, key, value, importance)` | Persist memory to DB |
| `semantic_search(query, limit=5)` | Qdrant-based semantic search (falls back to mock) |

**Qdrant integration:**
- `app/ai/memory/retrieval.py:151` — `QdrantClient(host="localhost", port=6333)`
- `app/ai/memory/retrieval.py:213` — On connection failure, returns empty results (silent fallback)
- Qdrant is NOT in `docker-compose.yml`
- Qdrant is listed as optional dependency in `pyproject.toml:31-33`

### Guardrail System

**File:** `app/ai/guardrails/service.py`

| Method | Purpose | Called From? |
|--------|---------|-------------|
| `validate_json_output(text)` | Ensure LLM response is valid JSON | **None** |
| `detect_empty_response(text)` | Catch empty/truncated responses | **None** |
| `detect_hallucination(text, context)` | Check response against known context | **None** |
| `sanitize_output(text)` | Strip harmful content | **None** |

**Status:** 5 files in `app/ai/guardrails/` — zero calls from any node or router. Not integrated.

### Evaluation Harness

**File:** `app/ai/evaluation/`

| Scenario | Description | File |
|----------|-------------|------|
| Basic Teaching | Basic teach → quiz → evaluate loop | `app/ai/evaluation/scenarios.py:10` |
| Misconception | Student makes repeated errors | `app/ai/evaluation/scenarios.py:50` |
| Prerequisite Gap | Student lacks prerequisite knowledge | `app/ai/evaluation/scenarios.py:90` |
| Mixed Review | Revision + new concept interleaving | `app/ai/evaluation/scenarios.py:130` |

**Metrics tracked:** response time, accuracy, concept coverage, misconception detection rate, guardrail trigger rate.

---

## Tests (AI Module)

| File | Tests | Type | Mock? |
|------|:-----:|------|-------|
| `tests/test_teacher_graph.py` | 21 | Unit | All mock Gemini |
| `tests/test_diagnosis.py` | 16 | Unit | Mock Gemini |
| `tests/test_memory.py` | 3 | Unit | Mock Gemini |
| `tests/test_evaluation.py` | 30 | Unit | Mock services |
| `tests/integration/test_teaching_flow.py` | 5 | Integration | Mock Gemini |
| `tests/integration/test_memory_extraction.py` | 3 | Integration | Mock Gemini |
| `tests/integration/test_diagnosis_flow.py` | 4 | Integration | Mock Gemini |

**Total AI tests: 82** (all use mock Gemini)

**Missing:**
- No test for `app/ai/router.py` (teach/evaluate HTTP endpoints)
- No test for `app/ai/guardrails/` (zero coverage)
- No real Gemini API integration test
- No test with actual Qdrant connection
