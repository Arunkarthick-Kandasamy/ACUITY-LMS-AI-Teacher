# Current Status — Acuity LMS AI

> Living document describing the project as it actually exists. Generated from source code, not plans.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Name** | Acuity LMS AI (Acuity Learning Hub) |
| **Version** | 0.1.0 (pre-alpha) |
| **Type** | AI-Native Personalized Schooling Platform |
| **Status** | Active development; backend largely implemented with frontend scaffolding in place |

---

## 2. Technology Stack

### Backend
| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ (3.12 in Docker) |
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async with asyncpg) |
| Database | PostgreSQL 16 (aiosqlite for dev/testing) |
| Migrations | Alembic (4 migration versions) |
| AI Framework | LangGraph (state machine) |
| LLM | Google Gemini 1.5 Pro (mock fallback when no API key) |
| Auth | JWT (access + refresh tokens) with bcrypt |
| Linting | Ruff (line-length 120) |
| Testing | pytest, pytest-asyncio, httpx |
| Container | Docker (multi-stage, python:3.12-slim) |

### Frontend
| Component | Technology |
|-----------|------------|
| Language | TypeScript 6.0 |
| Framework | React 19.2 |
| Build Tool | Vite 8.0 |
| Routing | react-router-dom v7 |
| Styling | Tailwind CSS 3.4 (navy/gold/electric palette) |
| Animations | Framer Motion 12, GSAP 3.15 |
| Charts | Recharts 2.15 |
| UI Components | Radix UI primitives (avatar, dialog, dropdown, progress, tabs, tooltip) |
| Icons | Lucide React |
| Linting | ESLint 10 with TypeScript-ESLint |
| State Management | Simple observer pattern store (no Redux/Zustand) |

---

## 3. High-Level Architecture (As Built)

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

┌──────────────────────────────────────────────────────────┐
│                React Frontend (Vite + TS)                  │
│                                                            │
│   Landing  │  Auth  │  Student  │  Parent  │  Admin       │
│   (1 pg)   │ (2 pg) │  (6 pgs)  │  (4 pgs) │  (3 pgs)    │
│                                                            │
│   API Service Layer (13 modules) ←→ Backend API            │
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

## 4. Directory Structure (As Built)

```
Root/
├── acuity-frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── main.tsx               # Entry point
│   │   ├── App.tsx                # RouterProvider root
│   │   ├── assets/
│   │   ├── styles/globals.css     # Tailwind directives
│   │   ├── lib/                   # api.ts (Axios client), utils.ts
│   │   ├── services/              # 13 API service modules
│   │   │   ├── api.ts             # Token storage (localStorage)
│   │   │   ├── auth.ts            # Login/register/logout
│   │   │   ├── admin.ts           # Admin API calls
│   │   │   ├── curriculum.ts      # Curriculum browsing
│   │   │   ├── enrollment.ts      # Enrollment API
│   │   │   ├── mastery.ts         # Mastery API
│   │   │   ├── pacing.ts          # Pacing API
│   │   │   ├── parent.ts          # Parent dashboard API
│   │   │   ├── progress.ts        # Progress API
│   │   │   ├── reports.ts         # Reports API
│   │   │   ├── sessions.ts        # Teaching session API
│   │   │   ├── index.ts           # Barrel export
│   │   │   └── types.ts           # Shared TypeScript interfaces
│   │   ├── store/authStore.ts     # Auth state (observer pattern)
│   │   ├── hooks/                 # 5 custom hooks
│   │   ├── router/index.tsx       # All routes
│   │   ├── layouts/               # AppLayout, Sidebar, Topbar
│   │   ├── components/ui/         # Button, index
│   │   └── pages/
│   │       ├── landing/LandingPage.tsx
│   │       ├── auth/LoginPage.tsx, StudentOnboarding.tsx
│   │       ├── student/           # 6 pages
│   │       ├── parent/            # 4 pages
│   │       └── admin/             # 3 pages
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── eslint.config.js
│   └── postcss.config.js
│
├── Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app: middleware, lifespan, routers
│   │   ├── config.py              # pydantic-settings, 87 lines
│   │   ├── api/routes/
│   │   │   └── health.py          # GET /health endpoint
│   │   ├── common/
│   │   │   ├── base.py            # UUIDMixin (UUID PK, created_at, updated_at)
│   │   │   ├── types.py           # 13 shared enums
│   │   │   ├── exceptions.py      # AppException hierarchy
│   │   │   ├── constants.py       # shared constants
│   │   │   ├── context.py         # request_id context var
│   │   │   ├── compat.py          # SQLite dev support
│   │   │   ├── response.py        # success_response() helper
│   │   │   └── repository.py      # Base repository pattern
│   │   ├── users/
│   │   │   ├── models.py          # User, StudentProfile, ParentStudentLink
│   │   │   └── repository.py      # UserRepository, StudentProfileRepository
│   │   ├── auth/
│   │   │   ├── router.py          # 6 auth endpoints
│   │   │   ├── service.py         # register, login, refresh, logout, forgot, reset
│   │   │   ├── schemas.py         # request/response schemas
│   │   │   ├── models.py          # RefreshToken, PasswordResetToken
│   │   │   ├── repository.py      # RefreshTokenRepository
│   │   │   └── dependencies.py    # get_current_user, require_role
│   │   ├── security/
│   │   │   ├── jwt.py             # create/decode tokens
│   │   │   ├── password.py        # hash, verify, validate_strength
│   │   │   └── rbac.py            # RoleChecker class
│   │   ├── curriculum/
│   │   │   ├── router.py          # 36 CRUD endpoints
│   │   │   ├── service.py         # CourseService (CRUD for all entities)
│   │   │   ├── schemas.py
│   │   │   ├── models.py          # Course, Module, Lesson, Concept, ConceptContent, Exercise, Example, LearningObjective
│   │   │   └── repository.py      # CourseRepository, ModuleRepository, LessonRepository, ConceptRepository
│   │   ├── knowledge_graph/
│   │   │   ├── router.py          # 3 endpoints (edges CRUD, prerequisites)
│   │   │   ├── service.py         # KnowledgeGraphService
│   │   │   ├── models.py          # KnowledgeNode, KnowledgeEdge
│   │   │   └── repository.py      # KnowledgeNodeRepository, KnowledgeEdgeRepository
│   │   ├── enrollment/
│   │   │   ├── router.py          # 3 endpoints (enroll, list, get)
│   │   │   ├── service.py         # EnrollmentService
│   │   │   ├── schemas.py
│   │   │   ├── models.py          # StudentCourseEnrollment, CourseSchedule
│   │   │   └── repository.py      # EnrollmentRepository
│   │   ├── progress/
│   │   │   ├── router.py          # progress endpoints
│   │   │   ├── service.py         # ProgressService
│   │   │   ├── schemas.py
│   │   │   └── repository.py      # LessonProgressRepository
│   │   ├── mastery/
│   │   │   ├── router.py          # 1 endpoint
│   │   │   ├── service.py         # MasteryService
│   │   │   ├── schemas.py
│   │   │   ├── models.py          # MasteryRecord
│   │   │   └── repository.py      # MasteryRecordRepository
│   │   ├── pacing/
│   │   │   ├── router.py          # 1 endpoint
│   │   │   ├── service.py         # PacingService
│   │   │   ├── schemas.py
│   │   │   ├── models.py          # PacingRecord
│   │   │   └── repository.py      # PacingRecordRepository
│   │   ├── teaching_sessions/
│   │   │   ├── router.py          # 5 endpoints
│   │   │   ├── service.py         # TeachingSessionService (session lifecycle)
│   │   │   ├── schemas.py
│   │   │   └── repository.py      # TeachingSessionRepository, AttemptRepository
│   │   ├── teaching/
│   │   │   └── models.py          # TeachingSession, LessonProgress, Attempt (shared models)
│   │   ├── ai/
│   │   │   ├── router.py          # POST /teacher/teach, POST /teacher/evaluate
│   │   │   ├── state.py           # TeacherState (TypedDict), TeacherAction (enum)
│   │   │   ├── graphs/
│   │   │   │   └── teacher.py     # LangGraph with 7 nodes
│   │   │   ├── nodes/
│   │   │   │   ├── teach.py       # teach, ask_question, provide_example, complete_concept
│   │   │   │   ├── diagnose.py    # diagnose node
│   │   │   │   ├── evaluate_response.py  # evaluate node
│   │   │   │   └── retrieve_memories.py # memory retrieval node
│   │   │   ├── services/
│   │   │   │   ├── gemini.py      # GeminiService (text + JSON generation)
│   │   │   │   └── prompts.py     # Prompt templates (Python f-strings)
│   │   │   ├── memory/
│   │   │   │   ├── retrieval.py   # DB memory retrieval + Qdrant (optional)
│   │   │   │   └── service.py     # MemoryService (extract + store)
│   │   │   ├── diagnosis/
│   │   │   │   └── service.py     # DiagnosisService (persist misconception)
│   │   │   ├── guardrails/
│   │   │   │   └── service.py     # GuardrailService (NOT integrated into flow)
│   │   │   └── evaluation/        # AI evaluation harness (6 endpoints, internal tool)
│   │   ├── parent_dashboard/
│   │   │   ├── router.py          # 12 read-only endpoints
│   │   │   └── service.py         # ParentDashboardService
│   │   ├── reports/
│   │   │   ├── router.py          # 6 endpoints
│   │   │   ├── service.py         # ReportService (AI-generated reports)
│   │   │   ├── schemas.py
│   │   │   └── models.py          # Report
│   │   ├── content_ingestion/
│   │   │   ├── router.py          # 9 endpoints
│   │   │   ├── service.py         # ContentIngestionService
│   │   │   ├── schemas.py
│   │   │   ├── models.py          # ContentUpload, CurriculumDraft
│   │   │   └── parsers/           # TXT, PDF, DOCX parsers
│   │   ├── diagnosis/
│   │   │   ├── models.py          # Misconception
│   │   │   └── service.py         # DiagnosisService (standalone)
│   │   ├── memory/
│   │   │   └── models.py          # StudentMemory
│   │   ├── audit/
│   │   │   └── models.py          # AuditLog (never written to)
│   │   ├── monitoring/
│   │   │   └── metrics.py         # In-memory metrics (lost on restart)
│   │   └── infrastructure/
│   │       ├── database.py        # async engine, session factory, init/close
│   │       └── logging.py         # JSON structured logging
│   ├── tests/                     # 22 test files, 331 tests
│   ├── alembic/                   # 4 migration versions
│   ├── scripts/seed_data.py       # Admin user + demo course
│   ├── docker-compose.yml         # PostgreSQL 16 only
│   ├── Dockerfile                 # Python 3.12-slim multi-stage build
│   ├── pyproject.toml             # Dependencies + config
│   ├── Makefile                   # dev, test, lint, migrate, seed
│   ├── .env / .env.example        # Environment config
│   │
│   ├── ARCHITECTURE.md            # Planned architecture (not current)
│   ├── IMPLEMENTATION_PLAN.md     # Original implementation plan
│   ├── DATABASE_SCHEMA.md         # Database schema documentation
│   └── API_CONTRACTS.md           # API contract specifications
│
└── docs/
    └── audit_v2/                  # 11 audit documents (evidence-based)
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

## 6. Frontend Routes

| Route | Page | Role |
|-------|------|------|
| `/` | LandingPage | Public |
| `/login` | LoginPage | Public |
| `/onboarding` | StudentOnboarding | Student |
| `/student/dashboard` | StudentDashboard | Student |
| `/student/learning` | LearningPathPage | Student |
| `/student/ai-tutor` | AITutorPage | Student |
| `/student/assessment` | AssessmentPage | Student |
| `/student/progress` | ProgressPage | Student |
| `/student/profile` | ProfilePage | Student |
| `/parent/dashboard` | ParentDashboard | Parent |
| `/parent/student` | ParentStudentDetail | Parent |
| `/parent/reports` | ReportsPage | Parent |
| `/parent/insights` | InsightsPage | Parent |
| `/admin/dashboard` | AdminDashboard | Admin |
| `/admin/students` | StudentsPage | Admin |
| `/admin/analytics` | AnalyticsPage | Admin |

---

## 7. Database Model Summary

| Module | Tables | Key Models |
|--------|:------:|------------|
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

## 8. AI Teacher Detail

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
    conversation_history: list[dict]
    student_response: str | None
    teaching_content: str | None
    question: str | None
    evaluation: dict | None
    example_content: str | None
    diagnosis_result: dict | None
    recommended_action: str | None
    concept_title: str
    concept_description: str
    concept_content: list[dict]
    expected_answer: str | None
    prerequisite_concepts: list[dict]
    examples: list[dict]
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
                                    ┌───────────────────────────────────────┼──────────────┐
                                    ▼                                       ▼              ▼
                              reteach / prerequisite                   example       continue
                                    │                                       │              │
                                    ▼                                       ▼              ▼
                          retrieve_memories (loop)                   provide_example  complete_concept
                                                                           │              │
                                                                           ▼              ▼
                                                                     ask_question       END
                                                                           │
                                                                           ▼
                                                                         END
```

### Memory System

- **DB storage:** `StudentMemory` table (student_id, key, value JSONB, importance)
- **Qdrant:** Optional — `retrieval.py` attempts connection to localhost:6333, falls back to mock
- **Extraction:** `MemoryService.extract_and_store()` called after each teach response

### Guardrails (NOT Integrated)

- `GuardrailService.validate_json_output()` — check LLM response is valid JSON
- `GuardrailService.detect_empty_response()` — catch empty responses
- `GuardrailService.detect_hallucination()` — check against known context
- `GuardrailService.sanitize_output()` — strip harmful content
- **Zero calls** from any node or router — code exists but is disconnected

---

## 9. Testing Status

| Metric | Value |
|--------|:-----:|
| Test files | 22 |
| Total tests | 331 |
| Active tests | 323 |
| Skipped tests | 8 |
| AI tests (all mock Gemini) | 82 |
| Integration tests (mock AI) | 19 |
| Frontend tests | 0 |

### Skipped Tests (All Require Live Database)
- 5 auth HTTP tests (`tests/test_auth.py`)
- 3 RBAC HTTP tests (`tests/test_rbac.py`)

### Missing Test Coverage
- `app/ai/guardrails/` — zero tests
- `app/ai/router.py` — no HTTP test for `/teacher/teach`
- No end-to-end test with real database + real AI
- No frontend tests

---

## 10. Infrastructure (As Deployed)

| Component | Status | Details |
|-----------|--------|---------|
| PostgreSQL 16 | ✅ Running | Via `docker-compose.yml` |
| Backend Dockerfile | ✅ Defined | Python 3.12-slim multi-stage, uvicorn entrypoint |
| Docker Compose | ⚠️ Partial | Only PostgreSQL defined; app runs manually |
| Frontend | ⚠️ Dev only | Vite dev server, no production build config |
| Redis | ❌ Not present | No service, no client, no config |
| Qdrant | ⚠️ Optional | Code exists, not in docker-compose, falls back to mock |
| CI/CD | ❌ Not present | No GitHub Actions or automation |
| Monitoring | ❌ In-memory only | Metrics lost on restart |
| HTTPS/TLS | ❌ Not configured | Uvicorn runs without SSL |
| Rate Limiting | ❌ Not implemented | No slowapi or middleware |
| Database Backups | ❌ Not configured | No pg_dump automation |
| Log Aggregation | ❌ Stdout only | No log shipping |

---

## 11. Known Limitations & Gaps

| Issue | Impact | Evidence |
|-------|--------|----------|
| Gemini defaults to mock | AI system untested with real LLM | `config.py` — `gemini_api_key: str = ""` |
| Default JWT secret in source | **Security vulnerability** | `config.py` — `"change-me-in-production-use-a-real-secret"` |
| AI calls block HTTP handler | Poor throughput under load | `ai/router.py` — direct `await` in handler |
| Password reset email never sent | Feature is broken | `auth/service.py` — no SMTP call |
| AuditLog never written to | No audit trail | Zero callers across codebase |
| No rate limiting | No abuse protection | No dependency or middleware |
| Guardrails not wired | Unvalidated AI output reaches users | Zero calls in nodes or routers |
| Qdrant not deployable | Semantic search non-functional | Not in docker-compose, mock fallback |
| 8 tests skipped | Auth + RBAC untested at HTTP layer | All skip: "requires live database" |
| No persistent monitoring | Metrics lost on restart | In-memory only |
| No CI/CD | No automated testing/deployment | No pipeline config |
| No frontend tests | UI untested | No test files in frontend |

---

## 12. Recent Git History

| Commit | Description |
|--------|-------------|
| `6abc380` | Add SQLite development support: compat module, updated models, DB init script |
| `bb722eb` | Integrate frontend with backend API: add service layer, update auth store, connect all pages |
| `df6e3e5` | Add acuity-frontend (Vite + React) |
| `1442b7d` | Clean up audit docs, add project .gitignore, add audit_v2 docs |
| `16f884e` | Add AI teacher system, content ingestion, reports, evaluation, monitoring, parent dashboard, integration tests |
| `6faa2d2` | version 1 initial commit |
| `8ecc55a` | first commit |

---

## 13. Configuration Files

| File | Purpose |
|------|---------|
| `Backend/pyproject.toml` | Python dependencies, Ruff config, pytest config |
| `Backend/.env` / `.env.example` | Environment variables |
| `Backend/Dockerfile` | Multi-stage build for Python 3.12 app |
| `Backend/docker-compose.yml` | PostgreSQL 16 service |
| `Backend/Makefile` | dev, test, lint, format, docker-up, docker-down |
| `Backend/alembic.ini` | DB migration configuration |
| `acuity-frontend/package.json` | NPM dependencies and scripts |
| `acuity-frontend/vite.config.ts` | Vite build config with `@` path alias |
| `acuity-frontend/tailwind.config.js` | Custom design system (navy/gold/electric) |
| `acuity-frontend/eslint.config.js` | ESLint flat config |
| `.gitignore` | Git ignore rules |

No CI/CD configuration files present.

---

## 14. Key Design Patterns (From Code)

| Pattern | Implementation | Example |
|---------|---------------|---------|
| Repository | Each module has `*Repository` class | `app/users/repository.py::UserRepository` |
| Service | Each module has `*Service` class | `app/curriculum/service.py::CourseService` |
| Dependency Injection | FastAPI `Depends()` | `get_session()`, `get_current_active_user()` |
| State Machine (Session) | TeachingSession has explicit state transitions | `active→paused→completed` |
| State Machine (AI) | LangGraph StateGraph | `teacher.py` with conditional edges |
| UUID Primary Keys | SQLAlchemy `UUIDMixin` | `app/common/base.py` |
| Async Everything | async/await in all layers | `async def`, `await db.execute()` |
| JSONB for flexible data | PostgreSQL JSONB columns | `session.context`, `milestones`, `evidence` |
| Enum for closed values | Python `Enum` → PostgreSQL ENUM | `UserRole`, `SessionState`, etc. |

---

## 15. Quick Reference: Key Files

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
| `app/common/compat.py` | SQLite development support |
| `app/curriculum/service.py` | CourseService — full CRUD for all curriculum entities |
| `app/ai/graphs/teacher.py` | LangGraph state machine — the AI teacher |
| `app/ai/state.py` | TeacherState TypedDict and TeacherAction enum |
| `app/ai/services/gemini.py` | GeminiService — LLM integration with mock fallback |
| `app/ai/nodes/teach.py` | Teach, ask_question, provide_example, complete_concept nodes |
| `app/ai/guardrails/service.py` | GuardrailService (NOT integrated) |
| `acuity-frontend/src/services/` | 13 API service modules connecting frontend to backend |
| `acuity-frontend/src/pages/` | 15 page components across 4 roles |
