# Missing Features

> Compares planned features from `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `DATABASE_SCHEMA.md`, and `API_CONTRACTS.md` against actual source code. Each row cites evidence files.

---

## Legend

| Status | Meaning |
|--------|---------|
| **IMPLEMENTED** | Feature exists in code matching the spec |
| **PARTIAL** | Feature exists but differs materially from spec |
| **NOT IMPLEMENTED** | Feature does not exist in code |

---

## ARCHITECTURE.md Comparison

> Source: `ARCHITECTURE.md` (531 lines, root level)

### Planned Services

| Service | Claimed (ARCHITECTURE.md) | Actual Code | Status |
|---------|--------------------------|-------------|--------|
| PostgreSQL | Lines 72-76: All state in PostgreSQL | `app/infrastructure/database.py` — async engine, session maker, health check | **IMPLEMENTED** |
| Redis | Lines 72-76: Session + Cache | No `redis.py`, no `redis` dependency in `pyproject.toml`, no config in `docker-compose.yml` | **NOT IMPLEMENTED** |
| Qdrant | Lines 72-76: Vector Store | `app/ai/memory/retrieval.py:151` — Qdrant client exists but is optional; `docker-compose.yml` has no Qdrant service | **NOT IMPLEMENTED** (deployable) |
| Gemini Pro API | Lines 78-80 | `app/ai/services/gemini.py` — Full implementation with mock fallback | **PARTIAL** (no real API testing) |

### Planned Graphs (ARCHITECTURE.md:40-62)

| Artifact | Claimed | Actual | Status |
|----------|---------|--------|--------|
| `Teacher Graph` | Lines 52-55 | `app/ai/graphs/teacher.py` — Single graph with 7 nodes | **IMPLEMENTED** |
| `Diagnosis Graph` | Lines 56-58: Separate graph | No `app/ai/graphs/diagnosis_graph.py` — Diagnosis is a node within teacher graph | **NOT IMPLEMENTED** (merged) |
| `Pacing Graph` | Lines 59-61: Separate graph | No `app/ai/graphs/pacing_graph.py` — Pacing is a standalone service, not a graph | **NOT IMPLEMENTED** (merged) |

### Planned Modules (ARCHITECTURE.md:63-67)

| Module | Claimed | Actual | Status |
|--------|---------|--------|--------|
| Knowledge Graph | Included | `app/knowledge_graph/` — 8 files, 3 endpoints | **IMPLEMENTED** |
| Session | Included | `app/teaching_sessions/` — 4 files | **IMPLEMENTED** |
| Memory | Included | `app/ai/memory/` — retrieval, extraction, persistence | **IMPLEMENTED** |
| Mastery | Included | `app/mastery/` — 4 files | **IMPLEMENTED** |
| Scheduling | Included | No `app/scheduling/` directory | **NOT IMPLEMENTED** |
| Insights | Included | No `app/insights/` directory | **NOT IMPLEMENTED** |
| Assessment | Included in data flow diagram | No `app/assessment/` directory | **NOT IMPLEMENTED** |

### Planned Prompt Template Method (ARCHITECTURE.md: Headings @ prompts section)

| Format | Claimed | Actual | Status |
|--------|---------|--------|--------|
| Jinja2 prompt templates | `teach.jinja2`, `diagnose.jinja2`, etc. | `app/ai/services/prompts.py` — Python f-strings and template variables in source | **NOT IMPLEMENTED** (uses Python strings instead) |

---

## IMPLEMENTATION_PLAN.md Comparison

> Source: `IMPLEMENTATION_PLAN.md` (732 lines, root level)

### Phase 1 — Foundation

| Deliverable | Claimed | Evidence | Status |
|-------------|---------|----------|--------|
| 1.1 Project scaffolding | `pyproject.toml`, `Dockerfile`, `.gitignore` | 3 files exist at root | **IMPLEMENTED** |
| 1.2 Docker Compose environment | PostgreSQL 16, Redis 7, Qdrant 1.10 | `docker-compose.yml` — PostgreSQL only | **PARTIAL** (Redis + Qdrant missing) |
| 1.3 Config management | `app/config.py` pydantic-settings | Exists at `app/config.py:1-85` | **IMPLEMENTED** |
| 1.4 Logging infrastructure | `app/infrastructure/logging.py` | Exists at `app/infrastructure/logging.py` | **IMPLEMENTED** |
| 1.5 FastAPI app factory | `app/main.py` with lifespan, CORS, middleware | Exists at `app/main.py:1-154` | **IMPLEMENTED** |
| 1.6 SQLAlchemy base + session | `app/infrastructure/database.py` | Exists | **IMPLEMENTED** |
| 1.7 All SQLAlchemy models | 23 model files | 30 models across 10+ files | **IMPLEMENTED** (23 → 30, expanded) |
| 1.8 Alembic setup + migration | `alembic.ini`, `env.py`, initial migration | 5 files: `alembic.ini`, `env.py`, 4 migration versions | **IMPLEMENTED** |
| 1.9 Redis client | `app/infrastructure/redis.py` | Does not exist | **NOT IMPLEMENTED** |
| 1.10 Qdrant client | `app/infrastructure/qdrant.py` | Does not exist (Qdrant is in `app/ai/memory/retrieval.py`) | **NOT IMPLEMENTED** |
| 1.11 Test infrastructure | `conftest.py`, `pytest.ini`, `tests/factories/` | `conftest.py` exists; `pytest.ini` exists; `tests/factories/` does NOT exist | **PARTIAL** |
| 1.12 Common utilities | `app/common/base.py`, `types.py`, `exceptions.py`, `constants.py` | All exist | **IMPLEMENTED** |
| 1.13 Task runner | `Makefile` | Exists | **IMPLEMENTED** |
| 1.14 Seed data script | `scripts/seed_data.py` | Exists | **IMPLEMENTED** |

### Phase 4 — Student Learning Engine

| Deliverable | Claimed | Evidence | Status |
|-------------|---------|----------|--------|
| 4.1 Enrollment service | `app/enrollment/service.py` | Exists | **IMPLEMENTED** |
| 4.2 Course schedule generator | `app/scheduling/service.py` | No `app/scheduling/` directory | **NOT IMPLEMENTED** |
| 4.3 Lesson progress tracker | `app/teaching/service.py` | Exists | **IMPLEMENTED** |
| 4.4 Attempt recorder | `app/teaching/service.py` | Exists | **IMPLEMENTED** |
| 4.5 Mastery calculator | `app/mastery/service.py` | Exists | **IMPLEMENTED** |
| 4.6 Curriculum browsing | `GET /courses/{id}/curriculum` | Endpoint exists in `app/curriculum/router.py` | **IMPLEMENTED** |
| 4.7 Enrollment APIs | POST/GET/PATCH enrollments | 3 endpoints in `app/enrollment/router.py` | **IMPLEMENTED** |
| 4.8 Progress APIs | `GET /lessons/{id}/progress`, `GET /concepts/{id}` | Both exist in `app/progress/router.py` | **IMPLEMENTED** |
| 4.9 Pacing status | `GET /pacing` | Exists in `app/pacing/router.py` | **IMPLEMENTED** |
| 4.10 Enrollment business rules | No duplicate, course must be published | Implemented in `app/enrollment/service.py` | **IMPLEMENTED** |

### Phase 5 — Teaching Session Engine

| Deliverable | Claimed | Evidence | Status |
|-------------|---------|----------|--------|
| 5.1 Session service | `app/teaching/service.py` — CRUD, state machine, auto-resume | Exists at `app/teaching_sessions/service.py` | **IMPLEMENTED** (under `teaching_sessions/`) |
| 5.2 Session state machine | `active→paused→active→completed/interrupted` | Implemented in `app/teaching_sessions/service.py` | **IMPLEMENTED** |
| 5.3 Session resume logic | `POST /sessions` with `resume_last: true` | Implemented | **IMPLEMENTED** |
| 5.4 Session context persistence | JSONB context | `app/teaching_sessions/models.py` — `context` field (JSONB) | **IMPLEMENTED** |
| 5.5 Session activity tracking | `last_activity_at` updates | Present | **IMPLEMENTED** |
| 5.6 Session APIs | POST/GET/PATCH sessions | All 4 endpoints exist | **IMPLEMENTED** |
| 5.7 Attempt → Session linking | Foreign key to `teaching_session_id` | `app/teaching/models.py:11` — FK exists | **IMPLEMENTED** |
| 5.8 Session history | `GET /sessions/{id}/history` | Endpoint exists | **IMPLEMENTED** |
| 5.9 Idle session detection | Auto-interrupt after 30 min | No logic found in `app/teaching_sessions/service.py` | **NOT IMPLEMENTED** |
| 5.10 Service tests | Session lifecycle tests | 5 tests in `tests/test_teaching_sessions.py` | **IMPLEMENTED** |

### Phase 6 — AI Teacher MVP

| Deliverable | Claimed | Evidence | Status |
|-------------|---------|----------|--------|
| 6.1 Orchestrator entry point | `app/ai/orchestrator.py` | Does not exist — orchestration is in `app/ai/graphs/teacher.py` | **NOT IMPLEMENTED** (merged) |
| 6.2 Teaching graph | `app/ai/graphs/teaching_graph.py` | Does not exist — single `teacher.py` handles all roles | **NOT IMPLEMENTED** (merged) |
| 6.3 Diagnosis graph | `app/ai/graphs/diagnosis_graph.py` | Does not exist — diagnosis is a node in teacher.py | **NOT IMPLEMENTED** (merged) |
| 6.4 Pacing graph | `app/ai/graphs/pacing_graph.py` | Does not exist — pacing is a standalone service | **NOT IMPLEMENTED** (merged) |
| 6.5 Gemini Pro client | `app/ai/llm_client.py` | Does not exist — Gemini client is in `app/ai/services/gemini.py` | **PARTIAL** (different file) |
| 6.6 Embedding client | `app/ai/embedding_client.py` | Does not exist — embeddings in `app/ai/memory/retrieval.py` | **PARTIAL** (merged) |
| 6.7 Prompt template library | `app/ai/prompts/*.jinja2` | Does not exist — prompts are Python strings in `app/ai/services/prompts.py` | **NOT IMPLEMENTED** (differs) |
| 6.8 LLM response cache | Redis-based | No Redis dependency | **NOT IMPLEMENTED** |
| 6.9 Qdrant collections | 3 collections | Code in `app/ai/memory/retrieval.py` attempts bootstrap but Qdrant not deployed | **PARTIAL** (code only) |
| 6.10 Content indexing pipeline | Index on create/update | Not found in any service | **NOT IMPLEMENTED** |
| 6.11 Semantic concept retrieval | Similar concept search | Not found | **NOT IMPLEMENTED** |
| 6.12 Memory retrieval | Semantic search | `app/ai/memory/retrieval.py` — basic retrieval, not semantic | **PARTIAL** |
| 6.13 Teach node | `app/ai/nodes/teach.py` | Exists | **IMPLEMENTED** |
| 6.14 Quiz node | `app/ai/nodes/quiz.py` | Does not exist — quiz is merged into `ask_question` | **PARTIAL** (merged) |
| 6.15 Auto-grading node | `app/ai/nodes/grade.py` | Does not exist — grading is in `evaluate_response` node | **PARTIAL** (merged) |
| 6.16 Diagnose node | `app/ai/nodes/diagnose.py` | Exists | **IMPLEMENTED** |
| 6.17 Remediate node | `app/ai/nodes/remediate.py` | Does not exist — remediation is in diagnosis node | **PARTIAL** (merged) |
| 6.18 Revise node | `app/ai/nodes/revise.py` | Does not exist — no revision logic found | **NOT IMPLEMENTED** |
| 6.19 Advance node | `app/ai/nodes/advance.py` | Does not exist — progression in `complete_concept` | **PARTIAL** (merged) |
| 6.20 Next teaching action | `POST /sessions/{id}/next` | Does not exist — replaced by `POST /teacher/teach` | **PARTIAL** (different endpoint) |
| 6.21 Submit response | `POST /sessions/{id}/respond` | Does not exist | **NOT IMPLEMENTED** |
| 6.22 On-demand quiz | `POST /sessions/{id}/quiz` | Does not exist | **NOT IMPLEMENTED** |
| 6.23 AI grading | `POST /exercises/{id}/grade` | Does not exist | **NOT IMPLEMENTED** |
| 6.24 Memory service | `app/memory/service.py` | Does not exist — memory logic in `app/ai/memory/` | **PARTIAL** (different structure) |
| 6.25 Misconception service | `app/diagnosis/service.py` | Exists | **IMPLEMENTED** |
| 6.26 Knowledge graph service | Prerequisite traversal, remediation path | `app/knowledge_graph/service.py` — basic traversal only | **PARTIAL** (no shortest path) |
| 6.27 Adaptive pacing | Deadline pressure, mastery velocity | `app/pacing/service.py` — no adaptive logic | **NOT IMPLEMENTED** |
| 6.28 Revision scheduling | `next_review_at` generation | Not implemented in `app/pacing/service.py` | **NOT IMPLEMENTED** |

### Phase 7 — Parent Intelligence

| Deliverable | Claimed | Evidence | Status |
|-------------|---------|----------|--------|
| 7.1 Parent dashboard service | `app/reports/service.py` | Exists | **IMPLEMENTED** |
| 7.2 Student progress view | `GET /parent/students/{id}/progress` | Exists | **IMPLEMENTED** |
| 7.3 Student mastery view | `GET /parent/students/{id}/mastery` | Exists | **IMPLEMENTED** |
| 7.4 Student misconceptions | `GET /parent/students/{id}/misconceptions` | Exists | **IMPLEMENTED** |
| 7.5 Recent session activity | `GET /parent/students/{id}/sessions` | Exists | **IMPLEMENTED** |
| 7.6 Report generation service | Generate report data + AI narrative | Implemented | **IMPLEMENTED** |
| 7.7 AI report content | Via Phase 6 prompts | Implemented | **IMPLEMENTED** |
| 7.8 Report PDF generation | `app/reports/pdf_generator.py` via WeasyPrint | Does not exist | **NOT IMPLEMENTED** |
| 7.9 Report templates | Jinja2 templates for weekly/monthly/milestone | Does not exist | **NOT IMPLEMENTED** |
| 7.10 Report scheduling | Weekly automated background task | No Celery/task queue | **NOT IMPLEMENTED** |
| 7.11 Parent dashboard API | `GET /parent/dashboard` | Exists | **IMPLEMENTED** |
| 7.12 Report APIs | List/get/generate reports | 3 endpoints exist | **IMPLEMENTED** |
| 7.13 Report read tracking | `PATCH .../read` | Exists | **IMPLEMENTED** |

---

## API_CONTRACTS.md Comparison

> Source: `API_CONTRACTS.md` (2924 lines, root level) — claims 80+ endpoint specifications.

### Claimed Endpoints Not Found in Code

| Endpoint (API_CONTRACTS.md) | Section | Evidence |
|-----------------------------|---------|----------|
| `GET /admin/users` | Admin (line 212) | No `app/admin/` router exists |
| `GET /admin/users/{user_id}` | Admin (line 252) | No admin router |
| `PATCH /admin/users/{user_id}/status` | Admin (line 289) | No admin router |
| `GET /admin/dashboard` | Admin (line 321) | No admin router |
| `GET /admin/courses/{course_id}/analytics` | Admin (line 346) | No admin router |
| `GET /exercises/{exercise_id}` | Assessment (line 2110) | No standalone exercise GET endpoint |
| `POST /exercises/{exercise_id}/grade` | Assessment (line 2134) | No AI grading endpoint |
| `GET /attempts/{attempt_id}` | Assessment (line 2172) | No standalone attempt detail endpoint |
| `GET /attempts` | Assessment (line 2201) | No attempt list endpoint |
| `GET /mastery/concepts/{concept_id}` | Mastery (line 2296) | Only `GET /api/v1/mastery` exists |
| `GET /mastery/courses/{course_id}` | Mastery (line 2339) | Only aggregate endpoint |
| `GET /diagnosis` | Diagnosis (line 2382) | No standalone diagnosis list endpoint |
| `GET /diagnosis/concepts/{concept_id}` | Diagnosis (line 2423) | No per-concept diagnosis endpoint |
| `PATCH /diagnosis/{misconception_id}/resolve` | Diagnosis (line 2451) | No diagnosis update endpoint |
| `GET /memory` | Memory (line 2478) | No memory retrieval endpoint |
| `GET /memory/{key}` | Memory (line 2510) | No memory GET endpoint |
| `POST /sessions/{session_id}/quiz` | Assessment (line 2061) | No AI quiz generation endpoint |
| `POST /sessions/{session_id}/next` | Teaching (line 1837) | Does not exist — uses `/teacher/teach` |
| `POST /sessions/{session_id}/respond` | Teaching (line 1954) | Does not exist |
| `PATCH /enrollments/{enrollment_id}` | Learning (line 1472) | Not implemented (pause/resume) |

**Total: 20 endpoints specified in API_CONTRACTS.md that do not exist in code.**

### Response Format Mismatch

| Spec (API_CONTRACTS.md) | Actual Code | Evidence |
|------------------------|-------------|----------|
| `{"status": "success", "data": {...}, "meta": {...}}` | Responses vary — most return data directly | `app/curriculum/router.py` — endpoints return ORM objects, not wrapped in status envelope |
| Error format `{"status": "error", "error": {"code": "...", "message": "..."}}` | HTTPException with standard FastAPI format | `app/common/exceptions.py` — custom exceptions exist but most routes raise plain HTTPException |
| `Authorization: Bearer <JWT>` | Used consistently | `app/auth/dependencies.py` — OAuth2PasswordBearer |

---

## DATABASE_SCHEMA.md Comparison

> Source: `DATABASE_SCHEMA.md` (770 lines, root level) — documents table schemas.

### Tables Specified in DATABASE_SCHEMA.md

**All 23+ tables described in DATABASE_SCHEMA.md are implemented in SQLAlchemy models.** Mismatches found:

| Claim (DATABASE_SCHEMA.md) | Actual | Evidence |
|---------------------------|--------|----------|
| `StudentProfile` table described with specific columns | `app/users/models.py:20` — matches schema | **IMPLEMENTED** |
| `ParentStudentLink` described | `app/users/models.py:43` — matches | **IMPLEMENTED** |
| `RefreshToken` described | `app/auth/models.py:10` — matches | **IMPLEMENTED** |
| `Course`, `Module`, `Lesson`, `Concept` hierarchy described | `app/curriculum/models.py` — all exist | **IMPLEMENTED** |
| `ConceptContent`, `LearningObjective`, `Example`, `Exercise` described | `app/curriculum/models.py` — all exist | **IMPLEMENTED** |
| `KnowledgeNode`, `KnowledgeEdge` described | `app/knowledge_graph/models.py` — both exist | **IMPLEMENTED** |
| `StudentCourseEnrollment`, `CourseSchedule` described | `app/enrollment/models.py` — both exist | **IMPLEMENTED** |
| `TeachingSession`, `LessonProgress`, `Attempt` described | `app/teaching/models.py` — all exist | **IMPLEMENTED** |
| `MasteryRecord` described | `app/mastery/models.py` — exists | **IMPLEMENTED** |
| `Misconception` described | `app/diagnosis/models.py` — exists | **IMPLEMENTED** |
| `StudentMemory` described | `app/memory/models.py` — exists | **IMPLEMENTED** |
| `Report` described | `app/reports/models.py` — exists | **IMPLEMENTED** |
| `AuditLog` described | `app/audit/models.py` — exists | **IMPLEMENTED** |
| `PacingRecord` described | `app/pacing/models.py` — exists | **IMPLEMENTED** |

**Verdict:** All tables in DATABASE_SCHEMA.md are implemented. No discrepancies found in table definitions. The actual model files contain additional models beyond the schema (e.g., evaluation models, content ingestion models).

---

## Other Missing Items (Not in Any Spec Document)

### Frontend

| Feature | Status | Evidence |
|---------|--------|----------|
| Web UI / Client Application | **NOT IMPLEMENTED** | No frontend directory, no `package.json`, no HTML/JS/TS files |
| API Client SDK | **NOT IMPLEMENTED** | No SDK, no OpenAPI client generation |

### Infrastructure

| Feature | Status | Evidence |
|---------|--------|----------|
| CI/CD Pipeline | **NOT IMPLEMENTED** | No `.github/workflows/`, no CI config |
| HTTPS/TLS Termination | **NOT IMPLEMENTED** | No SSL settings in `app/config.py:24`, uvicorn runs without SSL |
| Database Backups | **NOT IMPLEMENTED** | No backup scripts, no pg_dump automation |
| Log Aggregation | **NOT IMPLEMENTED** | `app/infrastructure/logging.py` — stdout only, no log shipping |
| Production Monitoring / Alerting | **NOT IMPLEMENTED** | `app/monitoring/metrics.py` — in-memory only, no Prometheus/Grafana |
| Rate Limiting | **NOT IMPLEMENTED** | No `slowapi` dependency, no rate-limiting middleware |
| Horizontal Scaling Config | **NOT IMPLEMENTED** | No session affinity, no distributed caching |
| Containerized App Service (Docker Compose) | **NOT IMPLEMENTED** | `docker-compose.yml` — only PostgreSQL defined |

### Security

| Feature | Status | Evidence |
|---------|--------|----------|
| Production Secret Management | **NOT IMPLEMENTED** | `app/config.py:37` — hard-coded default JWT secret |
| Email Service | **NOT IMPLEMENTED** | `app/auth/service.py` — creates token but never sends email |
| Refresh Token Reuse Detection | **NOT IMPLEMENTED** | No token family/session tracking |
| Resource-Level Permission Checks | **PARTIAL** | Some ownership checks in enrollment/sessions, missing in curriculum/mastery |
| Audit Logging (write path) | **NOT IMPLEMENTED** | `app/audit/models.py` — table exists but zero callers write to it |

### AI System

| Feature | Status | Evidence |
|---------|--------|----------|
| Guardrail Integration into Production Flow | **NOT IMPLEMENTED** | Guardrails code exists but zero calls from any node or router |
| Real Gemini API Testing | **NOT IMPLEMENTED** | All 21+ AI tests use mock Gemini |
| Async Task Queue for AI Calls | **NOT IMPLEMENTED** | No Celery/Redis Queue; `app/ai/router.py:170` — blocking invoke in HTTP handler |
| Qdrant Vector DB (Production deployment) | **NOT IMPLEMENTED** | Not in `docker-compose.yml`, falls back to mock on connection failure |
| Student Response Streaming | **NOT IMPLEMENTED** | No WebSocket, no SSE; returns single JSON response |

### Testing

| Feature | Status | Evidence |
|---------|--------|----------|
| End-to-End Tests | **NOT IMPLEMENTED** | No tests with real database + real AI API |
| Guardrail Tests | **NOT IMPLEMENTED** | No test file for `app/ai/guardrails/` (5 files, zero coverage) |
| Teach Endpoint HTTP Test | **NOT IMPLEMENTED** | `POST /teacher/teach` has no dedicated HTTP test |
| Forgot/Reset Password HTTP Tests | **SKIPPED** | 5 tests in `tests/test_auth.py:253-311` — all skip with "requires live database" |
| Auth RBAC Integration Tests | **SKIPPED** | 3 tests in `tests/test_rbac.py:121,129,150` — all skip with "requires live database" |
| Test Factories | **NOT IMPLEMENTED** | `tests/factories/` directory does not exist |

### Operational

| Feature | Status | Evidence |
|---------|--------|----------|
| Comprehensive Health Check | **PARTIAL** | `app/api/routes/health.py:13` — only checks DB; no AI/Gemini/Qdrant/disk checks |
| Docker HEALTHCHECK | **NOT IMPLEMENTED** | No `HEALTHCHECK` instruction in `Dockerfile` |
| Non-Root User Proper Setup | **NOT IMPLEMENTED** | `Dockerfile` — non-root user created but `pip install` runs before user switch |
