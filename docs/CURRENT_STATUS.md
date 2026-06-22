# Current Status — Acuity LMS AI

> Living document describing the project as it actually exists. Generated from source code, not plans.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Name** | Acuity LMS AI |
| **Version** | 0.1.0 (pre-alpha) |
| **Type** | Backend API only (no frontend) |
| **Language** | Python 3.11+ |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 16 via asyncpg |
| **AI Framework** | LangGraph + Google Gemini 1.5 Pro |
| **API Base** | `/api/v1` |
| **Auth** | JWT (access + refresh tokens) |

---

## 2. High-Level Architecture (As Built)

```
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Application                     │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Auth    │  │Curriculum│  │Enrollment│  │ Progress │ │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Mastery  │  │  Pacing  │  │Teaching  │  │Knowledge │ │
│  │  Module  │  │  Module  │  │ Sessions │  │  Graph   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                            │
│  ┌──────────────────────┐  ┌──────────┐  ┌──────────┐    │
│  │   AI Teacher         │  │  Parent  │  │ Content  │    │
│  │   (LangGraph)        │  │Dashboard │  │Ingestion │    │
│  │   ┌────────────────┐ │  │          │  │          │    │
│  │   │  teacher.py    │ │  └──────────┘  └──────────┘    │
│  │   │  (7 nodes)     │ │                                 │
│  │   └────────────────┘ │  ┌──────────┐  ┌──────────┐    │
│  └──────────────────────┘  │ Reports  │  │Evaluation│    │
│                            │  Module  │  │ Harness  │    │
│                            └──────────┘  └──────────┘    │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│                   PostgreSQL 16                           │
│                   30 tables, 14 enums                     │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│              Google Gemini 1.5 Pro API                    │
│            (mock fallback when no API key)                │
└──────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions (from code)

- **Modular monolith** — all code in `app/` with clear domain boundaries (auth/, curriculum/, ai/, etc.)
- **Repository pattern** — each module has `repository.py` for database queries
- **Service layer** — business logic in `service.py` files, routers are thin
- **Unit of Work** — sessions managed by `get_session()` dependency, `db.flush()` for partial writes
- **async everywhere** — all endpoints, services, repositories, and ORM queries are async
- **pydantic-settings** — configuration via `.env` file with `BaseSettings`
- **LangGraph** — single state machine for AI teacher, not multiple graphs
- **No caching layer** — Redis not present; no in-memory cache either
- **No task queue** — AI calls block the HTTP handler

---

## 3. Directory Structure (As Built)

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app: middleware, lifespan, routers
│   ├── config.py                # pydantic-settings, 85 lines
│   ├── api/routes/
│   │   └── health.py            # GET /health endpoint
│   ├── common/
│   │   ├── base.py              # UUIDMixin (UUID PK, created_at, updated_at)
│   │   ├── types.py             # 13 shared enums
│   │   ├── exceptions.py        # AppException hierarchy
│   │   ├── constants.py         # shared constants
│   │   ├── context.py           # request_id context var
│   │   └── response.py          # success_response() helper
│   ├── users/
│   │   ├── models.py            # User, StudentProfile, ParentStudentLink
│   │   └── repository.py        # UserRepository, StudentProfileRepository
│   ├── auth/
│   │   ├── router.py            # 6 auth endpoints
│   │   ├── service.py           # register, login, refresh, logout, forgot, reset
│   │   ├── schemas.py           # request/response schemas
│   │   ├── models.py            # RefreshToken, PasswordResetToken
│   │   ├── repository.py        # RefreshTokenRepository
│   │   └── dependencies.py      # get_current_user, require_role, get_current_active_user
│   ├── security/
│   │   ├── jwt.py               # create/decode tokens
│   │   ├── password.py          # hash, verify, validate_strength
│   │   └── rbac.py              # RoleChecker class
│   ├── curriculum/
│   │   ├── router.py            # 36 CRUD endpoints
│   │   ├── service.py           # CourseService (CRUD for all entities)
│   │   ├── schemas.py           # request/response schemas
│   │   ├── models.py            # Course, Module, Lesson, Concept, ConceptContent, Exercise, Example, LearningObjective
│   │   └── repository.py        # CourseRepository, ModuleRepository, LessonRepository, ConceptRepository
│   ├── knowledge_graph/
│   │   ├── router.py            # 3 endpoints (edges CRUD, prerequisites)
│   │   ├── service.py           # KnowledgeGraphService
│   │   ├── models.py            # KnowledgeNode, KnowledgeEdge
│   │   └── repository.py        # KnowledgeNodeRepository, KnowledgeEdgeRepository
│   ├── enrollment/
│   │   ├── router.py            # 3 endpoints (enroll, list, get)
│   │   ├── service.py           # EnrollmentService
│   │   ├── schemas.py
│   │   ├── models.py            # StudentCourseEnrollment, CourseSchedule
│   │   └── repository.py        # EnrollmentRepository
│   ├── progress/
│   │   ├── router.py            # progress endpoints
│   │   ├── service.py           # ProgressService
│   │   ├── schemas.py
│   │   └── repository.py        # LessonProgressRepository
│   ├── mastery/
│   │   ├── router.py            # 1 endpoint
│   │   ├── service.py           # MasteryService
│   │   ├── schemas.py
│   │   ├── models.py            # MasteryRecord
│   │   └── repository.py        # MasteryRecordRepository
│   ├── pacing/
│   │   ├── router.py            # 1 endpoint
│   │   ├── service.py           # PacingService
│   │   ├── schemas.py
│   │   ├── models.py            # PacingRecord
│   │   └── repository.py        # PacingRecordRepository
│   ├── teaching_sessions/
│   │   ├── router.py            # 5 endpoints
│   │   ├── service.py           # TeachingSessionService (session lifecycle)
│   │   ├── schemas.py
│   │   └── repository.py        # TeachingSessionRepository, AttemptRepository
│   ├── teaching/
│   │   └── models.py            # TeachingSession, LessonProgress, Attempt (shared models)
│   ├── ai/
│   │   ├── router.py            # POST /teacher/teach, POST /teacher/evaluate
│   │   ├── state.py             # TeacherState (TypedDict), TeacherAction (enum)
│   │   ├── graphs/
│   │   │   └── teacher.py       # LangGraph with 7 nodes
│   │   ├── nodes/
│   │   │   ├── teach.py         # teach, ask_question, provide_example, complete_concept
│   │   │   ├── diagnose.py      # diagnose node
│   │   │   ├── evaluate_response.py  # evaluate node
│   │   │   └── retrieve_memories.py # memory retrieval node
│   │   ├── services/
│   │   │   ├── gemini.py        # GeminiService (text + JSON generation)
│   │   │   └── prompts.py       # Prompt templates (Python f-strings)
│   │   ├── memory/
│   │   │   ├── retrieval.py     # DB memory retrieval + Qdrant (optional)
│   │   │   └── service.py       # MemoryService (extract + store)
│   │   ├── diagnosis/
│   │   │   └── service.py       # DiagnosisService (persist misconception)
│   │   ├── guardrails/
│   │   │   └── service.py       # GuardrailService (NOT integrated into flow)
│   │   └── evaluation/          # AI evaluation harness (6 endpoints, internal tool)
│   ├── parent_dashboard/
│   │   ├── router.py            # 12 read-only endpoints
│   │   └── service.py           # ParentDashboardService
│   ├── reports/
│   │   ├── router.py            # 6 endpoints
│   │   ├── service.py           # ReportService (AI-generated reports)
│   │   ├── schemas.py
│   │   └── models.py            # Report
│   ├── content_ingestion/
│   │   ├── router.py            # 9 endpoints
│   │   ├── service.py           # ContentIngestionService
│   │   ├── schemas.py
│   │   ├── models.py            # ContentUpload, CurriculumDraft
│   │   └── parsers/             # TXT, PDF, DOCX parsers
│   ├── diagnosis/
│   │   ├── models.py            # Misconception
│   │   └── service.py           # DiagnosisService (standalone)
│   ├── memory/
│   │   └── models.py            # StudentMemory
│   ├── audit/
│   │   └── models.py            # AuditLog (never written to)
│   ├── monitoring/
│   │   └── metrics.py           # In-memory metrics (lost on restart)
│   └── infrastructure/
│       ├── database.py          # async engine, session factory, init/close
│       └── logging.py           # JSON structured logging
├── tests/                       # 22 test files, 331 tests
├── alembic/                     # 4 migration versions
├── scripts/seed_data.py         # Admin user + demo course
├── docker-compose.yml           # PostgreSQL 16 only
├── Dockerfile                   # App container
├── pyproject.toml               # Dependencies + config
├── Makefile                     # dev, test, lint, migrate, seed
├── .env.example                 # Environment template
├── ARCHITECTURE.md              # Planned architecture (not current)
├── IMPLEMENTATION_PLAN.md       # Original implementation plan
├── DATABASE_SCHEMA.md           # Database schema documentation
├── API_CONTRACTS.md             # API contract specifications
└── docs/
    ├── audit/                   # First audit (12 files, may have discrepancies)
    └── audit_v2/                # Current audit (10 files, evidence-based)
```

---

## 4. Data Flow

### 4a. Authentication Flow

```
User → POST /auth/register → AuthService.register()
                                ├── hash password (bcrypt)
                                ├── create User record
                                ├── generate JWT access token (30 min)
                                └── generate refresh token (7 days)

User → POST /auth/login → AuthService.login()
                           ├── verify password
                           ├── create RefreshToken record
                           └── return access + refresh tokens

User → POST /auth/refresh → AuthService.refresh()
                             ├── hash provided refresh token
                             ├── match against stored hash
                             ├── revoke old token
                             └── issue new token pair

User → POST /auth/logout → AuthService.logout()
                            └── revoke all user's refresh tokens

User → POST /auth/forgot-password → AuthService.forgot_password()
                                      ├── create PasswordResetToken
                                      └── [STOPS HERE — email not sent]

User → POST /auth/reset-password → AuthService.reset_password()
                                    ├── verify token hash + expiry
                                    └── update password_hash
```

### 4b. Curriculum Management Flow

```
Admin → POST /courses → Course → POST /courses/{id}/modules → Module
                                 → POST /modules/{id}/lessons → Lesson
                                 → POST /lessons/{id}/concepts → Concept
                                         → POST /concepts/{id}/contents → ConceptContent
                                         → POST /concepts/{id}/exercises → Exercise
                                         → POST /concepts/{id}/examples → Example
                                         → POST /lessons/{id}/objectives → LearningObjective
                                 → PUT /courses/{id}/publish → is_published = true

Student → GET /courses → list published courses
        → GET /courses/{id} → course + module tree
        → GET /courses/{id}/curriculum → full tree with mastery levels
        → GET /lessons/{id} → lesson + concept list
        → GET /concepts/{id} → concept + content + examples + mastery
```

### 4c. Enrollment + Progress Flow

```
Student → POST /enrollments → EnrollmentService.enroll()
                               ├── check course is published
                               ├── check no duplicate active enrollment
                               └── create StudentCourseEnrollment (status: active)

Student → GET /lessons/{id}/progress → ProgressService.get_lesson_progress()
                                        └── return LessonProgress (status, time_spent, completion %)

Systems → MasteryService.update_mastery()  ← called by AI graph after evaluation
           ├── update mastery_level (weighted average)
           ├── increment total_attempts
           ├── update consecutive_correct
           └── calculate next_review_at

Systems → PacingService.get_pacing_status()
           ├── compare actual_lessons_per_week vs target
           └── return on_track / behind / ahead
```

### 4d. Teaching Session Lifecycle

```
Student → POST /sessions → TeachingSessionService.create_session()
                            ├── if resume_last and active session exists → return it
                            ├── validate enrollment is active
                            └── create TeachingSession (state: active)

Student → GET /sessions/active → return active session or null
        → GET /sessions/{id} → return session details + context
        → PATCH /sessions/{id} → update state (paused / completed)

Student → GET /sessions/{id}/history → list all attempts in session
```

### 4e. AI Teaching Flow (The Core Loop)

```
                    ┌─────────────────────────────────────┐
                    │  POST /teacher/teach                 │
                    │  body: { session_id, student_response? } │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │  _load_session_data()               │
                    │  ├── fetch TeachingSession          │
                    │  ├── fetch Concept (current)        │
                    │  ├── fetch ConceptContent           │
                    │  ├── fetch Examples                 │
                    │  ├── fetch KnowledgeEdge → prereqs  │
                    │  └── build TeacherState             │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │  teacher_graph.ainvoke(initial_state)│
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │  decide_entry()             │    │
                    │  │  ├── has student_response?  │    │
                    │  │  │   YES → evaluate_response│    │
                    │  │  │   NO  → retrieve_memories│    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  [retrieve_memories]         │    │
                    │  │  Load student memory from DB │    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  [teach]                     │    │
                    │  │  Gemini generates:           │    │
                    │  │  - teaching_content (explanation)│ │
                    │  │  - question (exercise)       │    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  [ask_question]              │    │
                    │  │  (passes question to state)  │    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │             ▼                        │
                    │           END                        │
                    │             │                        │
                    │  (on next call with response)        │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  [evaluate_response]         │    │
                    │  │  Gemini grades response     │    │
                    │  │  returns {score, feedback}   │    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  [diagnose]                  │    │
                    │  │  Detects:                   │    │
                    │  │  - misconception             │    │
                    │  │  - knowledge_gap             │    │
                    │  │  - correct                   │    │
                    │  └──────────┬──────────────────┘    │
                    │             │                        │
                    │  ┌──────────▼──────────────────┐    │
                    │  │  decide_after_diagnosis()   │    │
                    │  │  ├── reteach → retrieve_memories │
                    │  │  ├── prerequisite → retrieve_mem │
                    │  │  ├── example → provide_example  │
                    │  │  └── continue → complete_concept │
                    │  └────────────────────────────────┘    │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │  Persist results                    │
                    │  ├── update session context (JSONB) │
                    │  ├── if misconception → persist it  │
                    │  ├── extract + store memory entry   │
                    │  └── db.flush()                     │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │  Return response                    │
                    │  {                                  │
                    │    session_id,                      │
                    │    action: teach|ask_question|eval..│
                    │    mastery_estimate,                │
                    │    teaching_content?,               │
                    │    question?,                       │
                    │    evaluation?,                     │
                    │    example_content?,                │
                    │    diagnosis?                       │
                    │  }                                  │
                    └─────────────────────────────────────┘
```

### 4f. Content Ingestion Flow

```
Admin → POST /content/upload → parser (TXT/PDF/DOCX) → ContentUpload (status: pending)
      → POST /content/extract → Gemini extracts structured content
      → POST /content/generate → Gemini generates curriculum (Course→Module→Lesson→Concept)
      → PUT /content/submissions/{id}/approve → status: approved → CurriculumDraft → published
      → PUT /content/submissions/{id}/reject → status: rejected
```

### 4g. Parent Dashboard Flow

```
Parent → GET /parent/students → list linked students
       → GET /parent/students/{id}/progress → courses, mastery, weekly summary
       → GET /parent/students/{id}/mastery → per-concept breakdown by course
       → GET /parent/students/{id}/misconceptions → active issues
       → GET /parent/students/{id}/sessions → last N sessions with accuracy
       → GET /parent/students/{id}/reports → generated AI reports
       → GET /parent/students/{id}/reports/{rid} → full report detail
       → POST /parent/students/{id}/reports/generate → on-demand report
       → PATCH /parent/students/{id}/reports/{rid}/read → mark as read
       → GET /parent/dashboard → aggregate overview of all linked students
```

---

## 5. API Endpoint Summary

| Module | Prefix | Endpoints | Auth |
|--------|--------|:---------:|------|
| Health | `/health` | 1 | Public |
| Auth | `/auth` | 6 | Public (except logout) |
| Curriculum | `/courses`, `/modules`, `/lessons`, `/concepts`, etc. | 36 | Admin for writes, Authenticated for reads |
| Knowledge Graph | `/knowledge-graph` | 3 | Admin for writes |
| Enrollment | `/enrollments` | 3 | Student |
| Progress | `/lessons/{id}/progress`, `/courses/{id}/curriculum` | 2 | Student |
| Mastery | `/mastery` | 1 | Student |
| Pacing | `/pacing` | 1 | Student |
| Teaching Sessions | `/sessions` | 5 | Student |
| AI Teacher | `/teacher` | 2 | Student |
| AI Evaluation | `/ai/evaluation` | 6 | Internal |
| Parent Dashboard | `/parent` | 12 | Parent |
| Reports | `/reports` | 6 | Authenticated |
| Content Ingestion | `/content` | 9 | Admin |
| **Total** | | **91** | |

---

## 6. Database Model Summary

| Module | Tables | Key Models |
|--------|--------|------------|
| users | 3 | User, StudentProfile, ParentStudentLink |
| auth | 2 | RefreshToken, PasswordResetToken |
| curriculum | 8 | Course, Module, Lesson, Concept, ConceptContent, Exercise, Example, LearningObjective |
| knowledge_graph | 2 | KnowledgeNode, KnowledgeEdge |
| enrollment | 2 | StudentCourseEnrollment, CourseSchedule |
| teaching | 3 | TeachingSession, LessonProgress, Attempt |
| mastery | 1 | MasteryRecord |
| pacing | 1 | PacingRecord |
| diagnosis | 1 | Misconception |
| memory | 1 | StudentMemory |
| reports | 1 | Report |
| audit | 1 | AuditLog |
| content_ingestion | 2 | ContentUpload, CurriculumDraft |
| ai/evaluation | 2 | EvaluationDataset, EvaluationResult |
| **Total** | **30** | |

14 enum types in `app/common/types.py` and `app/content_ingestion/models.py`.

---

## 7. AI Teacher Detail

### State Type (`app/ai/state.py`)

```python
class TeacherAction(Enum):
    TEACH = "teach"
    ASK_QUESTION = "ask_question"
    EVALUATE_RESPONSE = "evaluate_response"
    DIAGNOSE = "diagnose"
    PROVIDE_EXAMPLE = "provide_example"
    COMPLETE_CONCEPT = "complete_concept"

class TeacherState(TypedDict):
    session_id: str
    student_id: str
    concept_id: str
    lesson_id: str
    course_id: str
    current_action: TeacherAction | str
    conversation_history: list[dict]      # [{role, content}]
    student_response: str | None
    teaching_content: str | None
    question: str | None
    evaluation: dict | None               # {score, feedback, understanding}
    example_content: str | None
    diagnosis_result: dict | None         # {diagnosis_type, recommended_action, ...}
    recommended_action: str | None
    concept_title: str
    concept_description: str
    concept_content: list[dict]           # [{content, content_type}]
    expected_answer: str | None
    prerequisite_concepts: list[dict]     # [{title, relationship}]
    examples: list[dict]                  # [{content, explanation}]
    mastery_estimate: float
    errors: list[str]
```

### Graph Structure

```
ENTRY → decide_entry()
          │
          ├── NO student_response ──► retrieve_memories → teach → ask_question → END
          │
          └── HAS student_response ──► evaluate_response → diagnose → decide_after_diagnosis
                                                                             │
                                    ┌────────────────────────────────────────┼─────────────────┐
                                    ▼                                        ▼                 ▼
                              reteach / prerequisite                    example          continue
                                    │                                        │                 │
                                    ▼                                        ▼                 ▼
                          retrieve_memories (loop)                    provide_example  complete_concept
                                                                           │                 │
                                                                           ▼                 ▼
                                                                     ask_question          END
                                                                           │
                                                                           ▼
                                                                         END
```

### Gemini Service

- **File:** `app/ai/services/gemini.py`
- **Class:** `GeminiService`
- **Methods:** `generate(prompt, type)`, `generate_json(prompt)`
- **Model:** `gemini-1.5-pro` (configurable via `GEMINI_MODEL` env var)
- **Mock fallback:** Returns hard-coded sample data if `GEMINI_API_KEY` is empty
- **No guardrails:** GuardrailService exists but is never called after generation

### Memory System

- **DB storage:** `StudentMemory` table (student_id, key, value JSONB, importance)
- **Qdrant:** Optional — `app/ai/memory/retrieval.py` attempts connection to `localhost:6333`, falls back to mock
- **Extraction:** `MemoryService.extract_and_store()` called after each teach response

### Guardrails (NOT Integrated)

- `GuardrailService.validate_json_output()` — check LLM response is valid JSON
- `GuardrailService.detect_empty_response()` — catch empty responses
- `GuardrailService.detect_hallucination()` — check against known context
- `GuardrailService.sanitize_output()` — strip harmful content
- **Zero calls** from any node or router — code exists but is disconnected

---

## 8. Testing Status

| Metric | Value |
|--------|:-----:|
| Test files | 22 |
| Total tests | 331 |
| Active tests | 323 |
| Skipped tests | 8 |
| AI tests (all mock Gemini) | 82 |
| Integration tests (mock AI) | 19 |

### Skipped Tests (All Require Live Database)

- 5 auth HTTP tests (`tests/test_auth.py`)
- 3 RBAC HTTP tests (`tests/test_rbac.py`)

### Missing Test Coverage

- `app/ai/guardrails/` — 5 files, zero tests
- `app/ai/router.py` — no HTTP test for `/teacher/teach`
- No end-to-end test with real database + real AI

---

## 9. Infrastructure (As Deployed)

| Component | Status | Details |
|-----------|--------|---------|
| PostgreSQL 16 | ✅ Running | Via `docker-compose.yml` |
| Redis | ❌ Not present | No service, no client, no config |
| Qdrant | ⚠️ Optional | Code exists, not in docker-compose, falls back to mock |
| Docker Compose | ⚠️ Partial | Only PostgreSQL defined, app runs manually |
| Dockerfile | ✅ Defined | Python 3.11-slim, uvicorn entrypoint |
| CI/CD | ❌ Not present | No GitHub Actions, no automation |
| Monitoring | ❌ In-memory only | Metrics lost on restart |
| HTTPS/TLS | ❌ Not configured | Uvicorn runs without SSL |
| Rate Limiting | ❌ Not implemented | No slowapi or middleware |
| Database Backups | ❌ Not configured | No pg_dump automation |
| Log Aggregation | ❌ Stdout only | No log shipping |

---

## 10. Key Design Patterns (From Code)

| Pattern | Implementation | Example |
|---------|---------------|---------|
| Repository | Each module has `*Repository` class | `app/users/repository.py::UserRepository` |
| Service | Each module has `*Service` class | `app/curriculum/service.py::CourseService` |
| Dependency Injection | FastAPI `Depends()` | `get_session()`, `get_current_active_user()` |
| State Machine (Session) | TeachingSession has explicit state transitions | `active→paused→completed` |
| State Machine (AI) | LangGraph StateGraph | `teacher.py` with conditional edges |
| UUID Primary Keys | SQLAlchemy `UUIDMixin` | `app/common/base.py:10` |
| Async Everything | async/await in all layers | `async def`, `await db.execute()` |
| JSONB for flexible data | PostgreSQL JSONB columns | `session.context`, `milestones`, `evidence` |
| Enum for closed values | Python `Enum` → PostgreSQL ENUM | `UserRole`, `SessionState`, etc. |

---

## 11. Current Limitations (From Code)

| Limitation | Impact | Evidence |
|------------|--------|----------|
| No frontend exists | Cannot be used by end users | No `package.json`, HTML, or JS files |
| Gemini defaults to mock | AI system untested with real LLM | `app/config.py:46` — `gemini_api_key: str = ""` |
| Default JWT secret in source | Critical security vulnerability | `app/config.py:37` — `"change-me-in-production-use-a-real-secret"` |
| AI calls block HTTP handler | Poor throughput under load | `app/ai/router.py:170` — direct `await` in handler |
| Password reset email never sent | Feature is broken | `app/auth/service.py:forgot_password()` — no SMTP call |
| AuditLog never written to | No audit trail | `app/audit/models.py` — zero callers across codebase |
| No rate limiting | No abuse protection | No `slowapi` dependency, no middleware |
| Guardrails not wired | Unvalidated AI output reaches users | Zero calls to `GuardrailService` in nodes or routers |
| Qdrant not deployable | Semantic search non-functional | Not in `docker-compose`, optional dependency, mock fallback |
| 8 tests skipped | Auth + RBAC untested at HTTP layer | All skip with "requires live database" |
| No persistent monitoring | Metrics lost on restart | `app/monitoring/metrics.py` — in-memory only |

---

## 12. Quick Reference: Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app — middleware, lifespan, 14 routers |
| `app/config.py` | Configuration via env vars with pydantic-settings |
| `app/infrastructure/database.py` | Async SQLAlchemy engine + session |
| `app/infrastructure/logging.py` | Structured JSON logging |
| `app/auth/service.py` | Auth service — register, login, refresh, logout, forgot, reset |
| `app/auth/dependencies.py` | Auth dependencies — JWT validation, role checks |
| `app/security/jwt.py` | JWT creation and decoding |
| `app/security/password.py` | Password hashing and strength validation |
| `app/common/base.py` | UUIDMixin — base for all models |
| `app/common/types.py` | Shared enum types (13 enums) |
| `app/curriculum/service.py` | CourseService — full CRUD for all curriculum entities |
| `app/curriculum/router.py` | 36 curriculum CRUD endpoints |
| `app/enrollment/service.py` | EnrollmentService — enroll, list, get |
| `app/progress/service.py` | ProgressService — lesson progress tracking |
| `app/mastery/service.py` | MasteryService — mastery scoring and updates |
| `app/pacing/service.py` | PacingService — pace status calculation |
| `app/teaching_sessions/service.py` | TeachingSessionService — session lifecycle |
| `app/teaching/models.py` | TeachingSession, LessonProgress, Attempt models |
| `app/ai/graphs/teacher.py` | LangGraph state machine — the AI teacher |
| `app/ai/state.py` | TeacherState TypedDict and TeacherAction enum |
| `app/ai/services/gemini.py` | GeminiService — LLM integration with mock fallback |
| `app/ai/services/prompts.py` | Prompt templates (Python f-strings) |
| `app/ai/nodes/teach.py` | Teach, ask_question, provide_example, complete_concept nodes |
| `app/ai/nodes/evaluate_response.py` | Evaluate response node |
| `app/ai/nodes/diagnose.py` | Diagnose node |
| `app/ai/nodes/retrieve_memories.py` | Memory retrieval node |
| `app/ai/memory/retrieval.py` | Memory storage + Qdrant (optional) |
| `app/ai/guardrails/service.py` | GuardrailService (NOT integrated) |
| `app/ai/router.py` | POST /teacher/teach — main AI endpoint |
| `app/parent_dashboard/service.py` | ParentDashboardService — 12 read-only methods |
| `app/reports/service.py` | ReportService — AI-generated reports |
| `app/content_ingestion/service.py` | ContentIngestionService — upload, extract, generate |
| `app/diagnosis/service.py` | DiagnosisService — misconception persistence |
| `app/monitoring/metrics.py` | In-memory metrics (lost on restart) |
| `tests/conftest.py` | Async test fixtures |
| `docker-compose.yml` | PostgreSQL 16 only |
| `Dockerfile` | Python 3.11-slim with uvicorn |
| `scripts/seed_data.py` | Admin user + demo course seeder |
