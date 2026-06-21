# Implementation Plan — AI-Native Personalized Schooling Platform (MVP)

## Phase Dependency Map

```
Phase 1: Foundation
  ├──► Phase 2: Auth & Users ──┐
  ├──► Phase 3: Curriculum ────┤
  │                            ▼
  │                  Phase 4: Student Learning
  │                            │
  │                  Phase 5: Teaching Session
  │                            │
  │                  Phase 6: AI Teacher (core)
  │                            │
  └──────────────────► Phase 7: Parent Intelligence
```

Phases 2 and 3 are independent and can be parallelized. Phases 4+ are sequential on the critical path.

**Total estimated duration: 14–19 weeks** (solo developer, full-time)

---

## Phase 1 — Foundation

**Goal:** Establish the project skeleton, infrastructure, database schema, and all tooling. Everything else builds on this.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 1.1 | Project scaffolding | `pyproject.toml` with all dependencies, `Dockerfile`, `.dockerignore`, `.gitignore` |
| 1.2 | Docker Compose environment | `docker-compose.yml` with PostgreSQL 16, Redis 7, Qdrant 1.10 |
| 1.3 | Configuration management | `app/config.py` using `pydantic-settings`, `.env.example`, environment validation |
| 1.4 | Logging infrastructure | `app/infrastructure/logging.py` — structured JSON logging, request-ID middleware, log levels per environment |
| 1.5 | FastAPI app factory | `app/main.py` with lifespan events, CORS, middleware stack (request ID, timing, error handler) |
| 1.6 | SQLAlchemy base + session | `app/infrastructure/database.py` — async engine, `async_sessionmaker`, `Base`, health check |
| 1.7 | All SQLAlchemy models | 23 model files across domain modules (see model list below) |
| 1.8 | Alembic setup + migration | `alembic.ini`, `env.py`, initial migration creating all 9 ENUMs + 23 tables |
| 1.9 | Redis client | `app/infrastructure/redis.py` — `redis.asyncio` client, connection pool, health check |
| 1.10 | Qdrant client | `app/infrastructure/qdrant.py` — `qdrant-client` async, collection bootstrap, health check |
| 1.11 | Test infrastructure | `conftest.py` with async test DB fixture, test client fixture, `pytest.ini`, `tests/factories/` |
| 1.12 | Common utilities | `app/common/` — `base.py` (declarative base + mixins), `types.py` (shared enums), `exceptions.py` (exception hierarchy), `constants.py` |
| 1.13 | Task runner | `Makefile` with `dev`, `test`, `lint`, `migrate`, `seed` commands |
| 1.14 | Seed data script | `scripts/seed_data.py` — admin user creation, demo course scaffold |

### SQLAlchemy Models to Create

```
app/users/models.py          → User, StudentProfile, ParentStudentLink
app/curriculum/models.py     → Course, Module, Lesson, Concept, ConceptContent,
                               LearningObjective, Example, Exercise
app/knowledge_graph/models.py → KnowledgeNode, KnowledgeEdge
app/enrollment/models.py     → StudentCourseEnrollment, CourseSchedule
app/teaching/models.py       → TeachingSession, LessonProgress, Attempt
app/mastery/models.py        → MasteryRecord
app/diagnosis/models.py      → Misconception
app/memory/models.py         → StudentMemory
app/reports/models.py        → Report
app/audit/models.py          → AuditLog
```

### Dependencies

None — this is the root phase.

### Acceptance Criteria

- [ ] `make dev` starts the application on `localhost:8000` with all three backing services
- [ ] `GET /health` returns `{"status": "ok", "db": "connected", "redis": "connected", "qdrant": "connected"}`
- [ ] `make migrate` runs Alembic and all 23 tables + 9 ENUMs exist in PostgreSQL
- [ ] `make test` passes with at least one integration test that writes to and reads from the database
- [ ] Application settings load from environment variables with validation errors on misconfiguration
- [ ] All 23 SQLAlchemy models have correct relationships, foreign keys, and unique constraints matching `DATABASE_SCHEMA.md`
- [ ] Alembic downgrade (`make rollback`) drops all tables cleanly
- [ ] Structured logs output JSON with `timestamp`, `level`, `module`, `request_id`
- [ ] Seed script creates an admin user and one demo course with at least 2 modules, 2 lessons each, with concepts

### Estimated Complexity

**Large (2–3 weeks)**

Rationale: High volume of boilerplate (23 models, infra wiring). Low technical risk but many details to get right. Most time goes to model definitions and Alembic tuning.

### Key Files to Create

```
pyproject.toml
docker-compose.yml
Dockerfile
Makefile
alembic.ini
app/__init__.py
app/main.py
app/config.py
app/common/base.py
app/common/types.py
app/common/exceptions.py
app/common/constants.py
app/infrastructure/__init__.py
app/infrastructure/database.py
app/infrastructure/redis.py
app/infrastructure/qdrant.py
app/infrastructure/logging.py
app/users/models.py
app/curriculum/models.py
app/knowledge_graph/models.py
app/enrollment/models.py
app/teaching/models.py
app/mastery/models.py
app/diagnosis/models.py
app/memory/models.py
app/reports/models.py
app/audit/models.py
tests/conftest.py
tests/factories/__init__.py
scripts/seed_data.py
```

---

## Phase 2 — Authentication & User Management

**Goal:** Implement the identity layer — registration, login, role-based access control, and user management.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 2.1 | JWT service | `app/users/service.py` — token creation, refresh, validation, blacklisting |
| 2.2 | Password hashing | `app/users/service.py` — bcrypt via `passlib`, password policy validation |
| 2.3 | Auth dependencies | `app/api/dependencies.py` — `get_current_user`, `require_role(role)` FastAPI dependencies |
| 2.4 | Registration endpoint | `POST /api/v1/auth/register` |
| 2.5 | Login endpoint | `POST /api/v1/auth/login` |
| 2.6 | Token refresh | `POST /api/v1/auth/refresh` |
| 2.7 | Logout | `POST /api/v1/auth/logout` |
| 2.8 | Password reset flow | `POST /api/v1/auth/forgot-password`, `POST /api/v1/auth/reset-password` |
| 2.9 | RBAC middleware | `app/api/middleware.py` — role check on route level, configurable via `RoleGuard` |
| 2.10 | User CRUD (admin) | `GET /api/v1/admin/users`, `GET /admin/users/{id}`, `PATCH /admin/users/{id}/status` |
| 2.11 | Student profile endpoints | `StudentProfile` read/update for authenticated student |
| 2.12 | Parent-student linking | `POST /api/v1/parent/students` (link), `GET /api/v1/parent/students` (list linked) |
| 2.13 | Admin dashboard | `GET /api/v1/admin/dashboard` — user counts, system stats |
| 2.14 | Auth service tests | Unit tests for token lifecycle, registration validation, RBAC enforcement |
| 2.15 | User API documentation | OpenAPI operation summaries, request/response examples |

### Dependencies

Phase 1 (Foundation) — must have database, models, app factory.

### Acceptance Criteria

- [ ] User can register with email + password, receives 201 with user object (no password in response)
- [ ] Login with valid credentials returns `access_token` and `refresh_token`
- [ ] Login with invalid credentials returns 401
- [ ] JWT expiry returns 401, refresh endpoint returns new tokens
- [ ] `/api/v1/*` endpoints return 401 when no token provided
- [ ] Admin routes return 403 when non-admin token is used
- [ ] Student routes return own data only (cannot access another student's profile)
- [ ] Password reset flow works end-to-end (token generation → email → token validation → new password)
- [ ] Admin can list, filter, and deactivate users
- [ ] Parent can link to a student via student ID and view linked students
- [ ] All auth endpoints return standardized error envelopes
- [ ] `make test` passes with > 80% coverage on auth module
- [ ] Rate limiting on `POST /auth/login` (5 attempts per minute per IP)

### Estimated Complexity

**Medium (1–2 weeks)**

Rationale: Well-understood pattern (JWT + bcrypt + RBAC). Minimal unknowns. Time goes to proper test coverage and edge cases (token refresh race conditions, password policy).

### Key Files to Create/Modify

```
app/users/__init__.py
app/users/service.py
app/users/schemas.py
app/users/router.py
app/api/dependencies.py
app/api/middleware.py
app/infrastructure/redis.py           ← extend for token blacklist
tests/unit/users/test_auth.py
tests/unit/users/test_rbac.py
tests/integration/test_auth_flow.py
```

---

## Phase 3 — Curriculum Engine

**Goal:** Build the complete curriculum content management system — admins upload and structure courses, modules, lessons, concepts, content, exercises, and the knowledge graph.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 3.1 | Course CRUD service | `app/curriculum/service.py` — create, read, update, delete with validation |
| 3.2 | Module CRUD | Nested under course |
| 3.3 | Lesson CRUD | Nested under module |
| 3.4 | Concept CRUD | Nested under lesson |
| 3.5 | ConceptContent CRUD | Nested under concept |
| 3.6 | LearningObjective CRUD | Nested under lesson |
| 3.7 | Example CRUD | Nested under concept |
| 3.8 | Exercise CRUD | Nested under concept |
| 3.9 | Course publish flow | Status toggle with validation (must have ≥1 module, ≥1 lesson per module) |
| 3.10 | Course curriculum tree | `GET /courses/{id}/curriculum` — returns full nested tree |
| 3.11 | Knowledge node CRUD | `app/knowledge_graph/service.py` — create nodes from concepts/objectives |
| 3.12 | Knowledge edge CRUD | `POST /knowledge-graph/edges`, `DELETE /knowledge-graph/edges/{id}` |
| 3.13 | Prerequisite traversal | `GET /knowledge-graph/concepts/{id}/prerequisites` — returns graph walk |
| 3.14 | Order-index management | Automatic re-indexing on insert/delete within parent scope |
| 3.15 | Curriculum validation | Business rules: no circular module references, unique codes, required fields |
| 3.16 | Seed data expansion | Complete demo curriculum with 1 course, 3 modules, 6 lessons, 12 concepts, exercises per concept |
| 3.17 | Curriculum service tests | Unit + integration tests for CRUD, validation, nested resource integrity |

### Curriculum API Endpoints

```
POST   /api/v1/courses
GET    /api/v1/courses
GET    /api/v1/courses/{id}
PUT    /api/v1/courses/{id}
DELETE /api/v1/courses/{id}
PUT    /api/v1/courses/{id}/publish

POST   /api/v1/courses/{id}/modules
GET    /api/v1/courses/{id}/modules
PUT    /api/v1/modules/{id}
DELETE /api/v1/modules/{id}

POST   /api/v1/modules/{id}/lessons
GET    /api/v1/modules/{id}/lessons
PUT    /api/v1/lessons/{id}
DELETE /api/v1/lessons/{id}

POST   /api/v1/lessons/{id}/concepts
GET    /api/v1/lessons/{id}/concepts
PUT    /api/v1/concepts/{id}
DELETE /api/v1/concepts/{id}

POST   /api/v1/concepts/{id}/contents
GET    /api/v1/concepts/{id}/contents
PUT    /api/v1/concept-contents/{id}
DELETE /api/v1/concept-contents/{id}

POST   /api/v1/concepts/{id}/exercises
GET    /api/v1/concepts/{id}/exercises
PUT    /api/v1/exercises/{id}
DELETE /api/v1/exercises/{id}

POST   /api/v1/concepts/{id}/examples
PUT    /api/v1/examples/{id}
DELETE /api/v1/examples/{id}

POST   /api/v1/lessons/{id}/objectives
PUT    /api/v1/objectives/{id}
DELETE /api/v1/objectives/{id}

POST   /api/v1/knowledge-graph/edges
DELETE /api/v1/knowledge-graph/edges/{id}
GET    /api/v1/knowledge-graph/concepts/{id}/prerequisites
```

### Dependencies

Phase 1 (Foundation) — models, database, app skeleton.

Independent of Phase 2. Can run in parallel.

### Acceptance Criteria

- [ ] Admin can create a complete course with modules → lessons → concepts in one editing session
- [ ] Course publish fails validation if it has no modules or modules have no lessons
- [ ] Deleting a parent resource cascades to children (course → modules → lessons → concepts)
- [ ] GET curriculum tree returns full nested structure in a single response
- [ ] Order indices are sequential (1, 2, 3…) and auto-maintain on insert/delete
- [ ] Knowledge graph edges enforce no self-referencing and unique (source, target, relationship) tuples
- [ ] Prerequisite traversal returns the correct graph walk for a concept
- [ ] Course code uniqueness is enforced at the database level
- [ ] All CRUD endpoints return proper 201/200/404/409 responses
- [ ] `make test` passes with > 80% coverage on curriculum module
- [ ] Demo seed script populates a complete, browsable course

### Estimated Complexity

**Large (2–3 weeks)**

Rationale: High endpoint count (~23 endpoints). Nested resource management with order-index maintenance. Knowledge graph traversal adds algorithmic complexity. Most time goes to comprehensive test coverage for all CRUD permutations.

### Key Files to Create/Modify

```
app/curriculum/__init__.py
app/curriculum/service.py
app/curriculum/schemas.py
app/curriculum/router.py
app/knowledge_graph/__init__.py
app/knowledge_graph/service.py
app/knowledge_graph/schemas.py
app/knowledge_graph/router.py
scripts/seed_data.py                ← extend
tests/unit/curriculum/
tests/unit/knowledge_graph/
```

---

## Phase 4 — Student Learning Engine

**Goal:** Enable students to enroll in courses, browse curriculum, track progress, and build mastery records.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 4.1 | Enrollment service | `app/enrollment/service.py` — enroll, pause, resume, drop, duplicate check |
| 4.2 | Course schedule generator | `app/scheduling/service.py` — auto-generate `CourseSchedule` + milestones on enrollment |
| 4.3 | Lesson progress tracker | `app/teaching/service.py` — create/update `LessonProgress` records |
| 4.4 | Attempt recorder | `app/teaching/service.py` — record `Attempt` with validation |
| 4.5 | Mastery calculator | `app/mastery/service.py` — update `MasteryRecord` on each attempt (weighted average of recent N) |
| 4.6 | Curriculum browsing | `GET /courses/{id}/curriculum` — student view with mastery levels |
| 4.7 | Enrollment APIs | `POST /enrollments`, `GET /enrollments`, `GET /enrollments/{id}`, `PATCH /enrollments/{id}` |
| 4.8 | Progress APIs | `GET /lessons/{id}/progress`, `GET /concepts/{id}` (with mastery) |
| 4.9 | Pacing status | `GET /pacing?course_id=...` — deadline-aware pace calculation |
| 4.10 | Enrollment business rules | No duplicate active enrollment, course must be published, deadline validation |
| 4.11 | Service tests | Enrollment lifecycle, progress tracking, mastery calculation accuracy |

### Dependencies

- Phase 2 (Auth) — students must exist and be authenticated
- Phase 3 (Curriculum) — courses, lessons, concepts must exist

### Acceptance Criteria

- [ ] Student can enroll in a published course and receives a `CourseSchedule` with milestones
- [ ] Student cannot enroll in the same course twice while the first enrollment is active
- [ ] Student cannot enroll in an unpublished course
- [ ] Enrollment pause/resume preserves progress state
- [ ] Lesson progress transitions: `not_started` → `in_progress` → `completed`
- [ ] Attempt recording correctly links to student, exercise, and (optionally) session
- [ ] Mastery updates automatically after each attempt using a weighted rolling average
- [ ] Mastery is scoped per student per concept (unique constraint enforced)
- [ ] Curriculum tree view shows student's mastery level per concept when authenticated
- [ ] Pacing endpoint returns correct `on_track` / `behind` / `ahead` based on milestone completion vs current week
- [ ] Pacing recommends catch-up when student falls behind target
- [ ] `make test` passes with > 80% coverage on enrollment + mastery modules

### Estimated Complexity

**Medium (2 weeks)**

Rationale: Straightforward CRUD for enrollment. Moderate algorithmic work for mastery calculation and pacing logic. Main effort is ensuring correctness of the mastery update formula across edge cases (first attempt, reset, etc.).

### Key Files to Create/Modify

```
app/enrollment/__init__.py
app/enrollment/service.py
app/enrollment/schemas.py
app/enrollment/router.py
app/scheduling/__init__.py
app/scheduling/service.py
app/scheduling/schemas.py
app/scheduling/router.py
app/teaching/__init__.py
app/teaching/service.py         ← add lesson progress + attempt logic
app/mastery/__init__.py
app/mastery/service.py
app/mastery/schemas.py
app/mastery/router.py
tests/unit/enrollment/
tests/unit/mastery/
tests/unit/scheduling/
tests/integration/test_enrollment_flow.py
```

---

## Phase 5 — Teaching Session Engine

**Goal:** Build the session lifecycle management — students can start, pause, resume, and end AI-led teaching sessions with full state persistence.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 5.1 | Session service | `app/teaching/service.py` — session CRUD, state machine, auto-resume |
| 5.2 | Session state machine | States: `active` → `paused` → `active` → `completed` / `interrupted` |
| 5.3 | Session resume logic | `POST /sessions` with `resume_last: true` — find and return active session |
| 5.4 | Session context persistence | JSONB context — current concept, action history, teaching state |
| 5.5 | Session activity tracking | `last_activity_at` updates on each interaction |
| 5.6 | Session APIs | `POST /sessions`, `GET /sessions/active`, `GET /sessions/{id}`, `PATCH /sessions/{id}` |
| 5.7 | Attempt → Session linking | All attempts recorded within a session reference `teaching_session_id` |
| 5.8 | Session history | `GET /sessions/{id}/history` — all attempts within session |
| 5.9 | Idle session detection | Stale session recovery — if `last_activity_at` > 30 min, auto-transition to `interrupted` |
| 5.10 | Service tests | Session state transitions, resume correctness, context persistence |

### Dependencies

Phase 4 (Student Learning) — enrollments, progress tracking, mastery records must exist as session will read and write them.

### Acceptance Criteria

- [ ] Student can start a new session with a course → session is created in `active` state
- [ ] Student can resume their last active session → existing session returned
- [ ] Student can pause a session → state changes to `paused`, activity updated
- [ ] Student can end a session → state changes to `completed`, no further actions allowed
- [ ] Session cannot transition from `completed` to `active`
- [ ] Interrupted sessions (30 min inactivity) are detected and auto-closed on next request
- [ ] Session context persists across resume → context JSONB is restored on resume
- [ ] Attempts recorded during a session are linked to the session ID
- [ ] Session history endpoint returns all attempts for the session
- [ ] Concurrent session creation for the same student returns the existing active session (no duplicates)
- [ ] `make test` passes with > 80% coverage on session module

### Estimated Complexity

**Small (1 week)**

Rationale: Focused scope with well-defined state machines. Simple data model. Most time goes to edge cases around concurrent session creation and idle timeout.

### Key Files to Create/Modify

```
app/teaching/router.py             ← new
app/teaching/service.py            ← extend
app/teaching/schemas.py            ← new
tests/unit/teaching/test_sessions.py
tests/integration/test_session_lifecycle.py
```

---

## Phase 6 — AI Teacher MVP

**Goal:** Build the core intelligence — LangGraph state machines, Gemini integration, vector store, misconception detection, and adaptive pacing. This is the heart of the platform.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| **AI Orchestrator** | | |
| 6.1 | LangGraph orchestrator entry point | `app/ai/orchestrator.py` — state machine coordinator |
| 6.2 | Teaching state machine | `app/ai/graphs/teaching_graph.py` — teach → quiz → remediate → revise loop |
| 6.3 | Diagnosis state machine | `app/ai/graphs/diagnosis_graph.py` — detect → categorize → track misconception |
| 6.4 | Pacing state machine | `app/ai/graphs/pacing_graph.py` — deadline-aware next-action decision |
| **LLM Integration** | | |
| 6.5 | Gemini Pro client | `app/ai/llm_client.py` — async HTTP client, retry with exponential backoff, token tracking |
| 6.6 | Embedding client | `app/ai/embedding_client.py` — Gemini embedding generation |
| 6.7 | Prompt template library | `app/ai/prompts/` — `teach.jinja2`, `diagnose.jinja2`, `generate_quiz.jinja2`, `remediate.jinja2`, `report.jinja2` |
| 6.8 | LLM response cache | Redis-based — keyed by prompt hash, TTL per content type |
| **Vector Store** | | |
| 6.9 | Qdrant collection bootstrap | `concept_embeddings`, `memory_embeddings`, `misconception_patterns` |
| 6.10 | Content indexing pipeline | Index all concept contents + examples into Qdrant on create/update |
| 6.11 | Semantic concept retrieval | Retrieve similar concepts for prerequisite teaching |
| 6.12 | Memory retrieval | Semantic search over student memories for AI context |
| **Teaching Actions** | | |
| 6.13 | Teach node | `app/ai/nodes/teach.py` — select best content, explain concept, return teaching payload |
| 6.14 | Quiz node | `app/ai/nodes/quiz.py` — select/generate exercise, check prerequisites |
| 6.15 | Auto-grading node | `app/ai/nodes/grade.py` — grade response (exact match for MCQ, AI for free-text) |
| 6.16 | Diagnose node | `app/ai/nodes/diagnose.py` — detect misconceptions, update `Misconception` table |
| 6.17 | Remediate node | `app/ai/nodes/remediate.py` — fall back to prerequisite concept, generate remedial content |
| 6.18 | Revise node | `app/ai/nodes/revise.py` — spaced repetition trigger, generate review summary |
| 6.19 | Advance node | `app/ai/nodes/advance.py` — check mastery threshold → move to next concept |
| **AI Endpoints** | | |
| 6.20 | Next teaching action | `POST /sessions/{id}/next` — main AI interaction endpoint |
| 6.21 | Submit response | `POST /sessions/{id}/respond` — grade + update mastery + detect misconceptions |
| 6.22 | On-demand quiz | `POST /sessions/{id}/quiz` — AI generates custom quiz |
| 6.23 | AI grading | `POST /exercises/{id}/grade` — standalone AI grading endpoint |
| **Memory & Diagnosis** | | |
| 6.24 | Student memory service | `app/memory/service.py` — read/write/recall, importance scoring |
| 6.25 | Misconception service | `app/diagnosis/service.py` — detect, register, resolve, frequency tracking |
| 6.26 | Knowledge graph service | `app/knowledge_graph/service.py` — prerequisite traversal, shortest remediation path |
| **Pacing** | | |
| 6.27 | Adaptive pacing engine | `app/scheduling/service.py` — adjust `target_lessons_per_week` based on mastery velocity and deadline pressure |
| 6.28 | Revision scheduling | Generate `next_review_at` on `MasteryRecord` based on mastery level |
| **Testing** | | |
| 6.29 | AI orchestrator tests | State machine transitions with mocked LLM, prompt coverage, edge cases |
| 6.30 | Integration tests | Full teaching loop: start session → teach → quiz → respond → grade → next concept |
| 6.31 | LLM prompt tests | Prompt rendering with various inputs, output parsing |

### AI Teaching Loop Flow

```
POST /sessions/{id}/next
  │
  ▼
Orchestrator.load_context()          ← read session state + student memory
  │
  ▼
PacingGraph.run()                    ← check deadlines, revision schedule
  │
  ▼
DiagnosisGraph.run()                 ← check for known misconceptions
  │
  ▼
TeachingGraph.run()                  ← teach / quiz / remediate / revise
  │
  ▼
┌─ Teach:      select content → render → return teaching payload
├─ Quiz:       select/generate exercise → return exercise
├─ Remediate:  find missing prereq → generate remedial content
├─ Revise:     generate review → return summary
└─ Advance:    mark progression → return next concept

POST /sessions/{id}/respond
  │
  ▼
Orchestrator.grade()                 ← auto-grade or AI grade
  │
  ▼
MasteryService.update()              ← update MasteryRecord
  │
  ▼
DiagnosisService.detect()            ← check for misconception patterns
  │
  ▼
MemoryService.observe()              ← store observation
  │
  ▼
SchedulingService.review()           ← update next_review_at
  │
  ▼
Return result + next_action_hint
```

### Dependencies

- Phase 3 (Curriculum) — concepts, content, exercises must exist for the AI to teach
- Phase 4 (Student Learning) — enrollment, progress tracking, mastery records
- Phase 5 (Teaching Session) — session lifecycle management

### Acceptance Criteria

- [ ] `POST /sessions/{id}/next` returns one of: `teach`, `quiz`, `remediate`, `revise`, or `session_complete`
- [ ] Teach action returns concept content from the database, rendered through the LLM
- [ ] Quiz action returns an exercise appropriate to the concept difficulty
- [ ] Remediate action correctly identifies and teaches the weakest prerequisite
- [ ] Revise action triggers when a concept's `next_review_at` is past due
- [ ] `POST /sessions/{id}/respond` correctly grades MCQ responses by exact match
- [ ] `POST /sessions/{id}/respond` correctly grades free-text responses using Gemini
- [ ] Misconception detection creates a `Misconception` record on repeated wrong answers of the same pattern
- [ ] Mastery updates atomically with every attempt (mastery moves up on correct, down on incorrect)
- [ ] Student memory accumulates observations across sessions
- [ ] Pacing decisions account for `target_completion_date` — recommends catch-up when behind
- [ ] LLM cache returns cached responses for identical prompts within TTL
- [ ] Qdrant `concept_embeddings` collection is populated on concept create
- [ ] AI quiz generation creates exercises not in the existing exercise set
- [ ] Full teaching loop (teach → quiz → respond → grade) completes in < 5 seconds
- [ ] Orchestrator handles LLM timeouts gracefully with retry logic
- [ ] `make test` passes with > 80% coverage on AI module (with mocked LLM)
- [ ] Integration test covers a complete lesson: teach 3 concepts → quiz each → respond → complete

### Estimated Complexity

**Extra Large (4–6 weeks)**

Rationale: This phase contains most of the platform's intellectual complexity. Key challenges:
- LangGraph state machine design — getting the teach/quiz/remediate/revise loop right requires iteration
- LLM prompt engineering — prompts must produce structured, parseable output consistently
- Misconception detection — pattern matching across response types is inherently heuristic
- Pacing engine — balancing deadline pressure against mastery quality requires careful design
- Integration testing — the full loop touches every module, making tests complex to write and maintain
- Error handling — LLM failures, timeouts, malformed responses all need graceful degradation

### Key Files to Create/Modify

```
app/ai/__init__.py
app/ai/orchestrator.py
app/ai/llm_client.py
app/ai/embedding_client.py
app/ai/vector_store.py
app/ai/cache.py
app/ai/graphs/__init__.py
app/ai/graphs/teaching_graph.py
app/ai/graphs/diagnosis_graph.py
app/ai/graphs/pacing_graph.py
app/ai/nodes/__init__.py
app/ai/nodes/teach.py
app/ai/nodes/quiz.py
app/ai/nodes/grade.py
app/ai/nodes/diagnose.py
app/ai/nodes/remediate.py
app/ai/nodes/revise.py
app/ai/nodes/advance.py
app/ai/prompts/teach.jinja2
app/ai/prompts/diagnose.jinja2
app/ai/prompts/generate_quiz.jinja2
app/ai/prompts/remediate.jinja2
app/ai/prompts/report.jinja2
app/ai/router.py
app/memory/service.py
app/memory/schemas.py
app/memory/router.py
app/diagnosis/service.py
app/diagnosis/schemas.py
app/diagnosis/router.py
app/scheduling/service.py         ← extend with adaptive pacing
tests/unit/ai/
tests/integration/test_teaching_loop.py
```

---

## Phase 7 — Parent Intelligence

**Goal:** Deliver AI-generated progress reports, recommendations, and a comprehensive parent dashboard.

### Deliverables

| # | Deliverable | Key Artifacts |
|---|---|---|
| 7.1 | Parent dashboard service | `app/reports/service.py` — aggregate data across linked students |
| 7.2 | Student progress view | `GET /parent/students/{id}/progress` — courses, mastery, weekly summary |
| 7.3 | Student mastery view | `GET /parent/students/{id}/mastery` — per-concept breakdown |
| 7.4 | Student misconceptions view | `GET /parent/students/{id}/misconceptions` — active issues |
| 7.5 | Recent session activity | `GET /parent/students/{id}/sessions` — last N sessions with accuracy |
| 7.6 | Report generation service | `app/reports/service.py` — compile report data, invoke AI for narrative |
| 7.7 | AI report content generation | Uses Phase 6 prompts — generates summary, strengths, weaknesses, recommendations |
| 7.8 | Report PDF generation | `app/reports/pdf_generator.py` — HTML → PDF via WeasyPrint |
| 7.9 | Report templates | `app/reports/templates/` — Jinja2 templates for weekly, monthly, milestone reports |
| 7.10 | Report scheduling | Weekly automated report generation via background task |
| 7.11 | Parent dashboard API | `GET /parent/dashboard` — aggregate overview |
| 7.12 | Report APIs | `GET /parent/students/{id}/reports`, `GET /parent/students/{id}/reports/{rid}`, `POST .../generate` |
| 7.13 | Report read tracking | `PATCH /parent/students/{id}/reports/{rid}/read` — mark as read |
| 7.14 | Service tests | Report generation, PDF output, AI content structure |

### Dependencies

- Phase 2 (Auth) — parent-student linking must exist
- Phase 4 (Student Learning) — enrollment, progress, mastery data
- Phase 6 (AI Teacher) — AI prompt infrastructure, LLM client, student memory

### Acceptance Criteria

- [ ] Parent dashboard shows all linked students with overall mastery, active courses, and alerts
- [ ] Parent can view detailed per-student progress across all enrolled courses
- [ ] Parent can see all active misconceptions for each student
- [ ] Parent can view recent session activity with accuracy rates
- [ ] Weekly report generates automatically and includes: summary, strengths, areas for improvement, recommendations
- [ ] On-demand report generation returns a report within 30 seconds
- [ ] Report PDF renders correctly with all sections (summary, metrics, recommendations)
- [ ] Report summary is AI-generated, not a template fill-in
- [ ] Recommendations are specific and actionable (not generic)
- [ ] Unread reports are tracked and displayed on the dashboard
- [ ] `make test` passes with > 80% coverage on reports module

### Estimated Complexity

**Medium (1–2 weeks)**

Rationale: Report generation is well-understood. PDF generation is standard. The AI narrative component leverages Phase 6 prompt infrastructure. Main effort is template design and ensuring report data completeness.

### Key Files to Create/Modify

```
app/reports/__init__.py
app/reports/service.py
app/reports/schemas.py
app/reports/router.py
app/reports/pdf_generator.py
app/reports/templates/weekly_report.jinja2
app/reports/templates/monthly_report.jinja2
app/reports/templates/milestone_report.jinja2
scripts/generate_weekly_reports.py
tests/unit/reports/
tests/integration/test_report_generation.py
```

---

## Summary Timeline

```
Week  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
      ┌─────────────────┐
P1    │   Foundation     │
      └─────────────────┘
            ┌────────────┐
P2          │ Auth/Users  │
            └────────────┘
            ┌──────────────────┐
P3          │   Curriculum     │
            └──────────────────┘
                  ┌──────────────┐
P4                │ Enrollments  │
                  │  + Mastery   │
                  └──────────────┘
                        ┌────────┐
P5                      │Session │
                        └────────┘
                          ┌────────────────────────────┐
P6                        │     AI Teacher MVP         │
                          └────────────────────────────┘
                                    ┌──────────────────┐
P7                                  │ Parent Reports   │
                                    └──────────────────┘

Key:
═══ Critical path (sequential)
─── Parallelizable
```

| Phase | Duration | Dependencies | Parallelizable |
|---|---|---|---|
| P1 — Foundation | 3 weeks | — | — |
| P2 — Auth | 2 weeks | P1 | With P3 |
| P3 — Curriculum | 3 weeks | P1 | With P2 |
| P4 — Student Learning | 2 weeks | P2, P3 | — |
| P5 — Teaching Session | 1 week | P4 | — |
| P6 — AI Teacher | 5 weeks | P5 + P3 + P4 | — |
| P7 — Parent Reports | 2 weeks | P6 + P2 + P4 | — |
| **Total** | **14–19 weeks** | | |

### Staffing Notes

- **Solo developer**: 14–19 weeks full-time
- **Two developers**: Parallelize P2 + P3 → reduces to ~12 weeks
- **With QA support**: Adds 1–2 weeks per phase for regression testing
- **Peak complexity**: Weeks 9–13 (Phase 6 AI development) — highest risk, needs uninterrupted focus

### Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM output quality below threshold for teaching | Medium | Critical | Iterative prompt refinement from week 1 of Phase 6; build evaluation harness early |
| LangGraph state machine complexity causes deadlocks | Medium | High | Unit-test every state transition in isolation; use state diagrams as living docs |
| Database migration conflicts during parallel phases | Low | Medium | All model changes in Phase 1; later phases add columns via separate Alembic revisions |
| Qdrant embedding quality insufficient for misconception detection | Medium | Medium | Fall back to rule-based pattern matching; add embedding fine-tuning as future work |
| Report PDF generation too slow for real-time | Low | Low | Generate asynchronously; return report ID immediately, poll for completion |
| Auth token security review findings | Low | Medium | Use well-vetted libraries (python-jose, passlib); security review before Phase 2 ships |
