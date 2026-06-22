# System Architecture

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
│  │ Public  │  │  Auth     │  │ Curriculum│  │ AI Teacher │  │
│  │ Health  │  │ Module   │  │ Module    │  │ Module     │  │
│  └─────────┘  └──────────┘  └───────────┘  └────────────┘  │
│                                                              │
│  ┌────────────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Knowledge  │  │Enrollment│  │ Mastery   │  │ Progress │  │
│  │ Graph      │  │ Module  │  │ Module    │  │ Module   │  │
│  └────────────┘  └─────────┘  └───────────┘  └──────────┘  │
│                                                              │
│  ┌──────────┐  ┌────────────────┐  ┌────────────┐          │
│  │ Pacing   │  │ Parent Dashboard│  │ Reports   │          │
│  │ Module   │  │ Module         │  │ Module    │          │
│  └──────────┘  └────────────────┘  └────────────┘          │
│                                                              │
│  ┌──────────────┐  ┌───────────┐  ┌─────────────┐          │
│  │ Content      │  │ Teaching  │  │ Evaluation  │          │
│  │ Ingestion    │  │ Sessions  │  │ Module      │          │
│  └──────────────┘  └───────────┘  └─────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Common Infrastructure                    │   │
│  │  ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │Security│ │Database │ │Logging   │ │Monitoring│   │   │
│  │  │ (JWT)  │ │(SQLAlch)│ │(JSON)    │ │(Metrics) │   │   │
│  │  └────────┘ └─────────┘ └──────────┘ └──────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   PostgreSQL 16     │
              │   (Asyncpg Driver)  │
              └─────────────────────┘
                         │
              ┌─────────────────────┐
              │   Gemini AI API     │
              │   (google-genai)    │
              └─────────────────────┘
                         │
              ┌─────────────────────┐
              │   Qdrant (Optional) │
              │   Vector DB         │
              └─────────────────────┘
```

## Module Breakdown

### Tech Stack
- **Python 3.10+** with **FastAPI** (async web framework)
- **PostgreSQL 16** via **SQLAlchemy 2.0** (async) + **asyncpg**
- **LangGraph** for AI state machine orchestration
- **Google Gemini** via `google-genai` SDK
- **Qdrant** (optional) for vector-based memory retrieval
- **JWT** via `python-jose` for authentication
- **bcrypt/passlib** for password hashing

### Module Descriptions

| Module | Location | Purpose | Lines of Code |
|--------|----------|---------|:------------:|
| `api` | `app/api/` | Health endpoint | ~30 |
| `auth` | `app/auth/` | Registration, login, JWT, password reset | ~350 |
| `security` | `app/security/` | JWT encode/decode, password hashing | ~75 |
| `users` | `app/users/` | User, StudentProfile, ParentStudentLink models | ~120 |
| `curriculum` | `app/curriculum/` | Course/Module/Lesson/Concept CRUD | ~1,500 |
| `knowledge_graph` | `app/knowledge_graph/` | Knowledge nodes and edges | ~400 |
| `enrollment` | `app/enrollment/` | Student course enrollment | ~300 |
| `progress` | `app/progress/` | Lesson progress, attempt recording | ~350 |
| `mastery` | `app/mastery/` | Concept mastery scoring | ~250 |
| `pacing` | `app/pacing/` | Course scheduling, pace tracking | ~200 |
| `teaching` | `app/teaching/` | Session, progress, attempt models | ~150 |
| `teaching_sessions` | `app/teaching_sessions/` | Session CRUD service | ~400 |
| `ai` | `app/ai/` | LangGraph teacher, diagnosis, memory, guardrails, evaluation | ~2,500 |
| `reports` | `app/reports/` | AI-generated parent reports | ~600 |
| `parent_dashboard` | `app/parent_dashboard/` | Parent view of student data | ~500 |
| `content_ingestion` | `app/content_ingestion/` | File upload, parsing, AI curriculum generation | ~900 |
| `monitoring` | `app/monitoring/` | In-memory metrics collection | ~200 |
| `audit` | `app/audit/` | Audit log model | ~30 |
| `common` | `app/common/` | Base model, types, exceptions, repository, response | ~300 |
| `infrastructure` | `app/infrastructure/` | Database session, logging setup | ~130 |

## Service Interactions

```
┌──────────────┐     HTTP      ┌──────────────┐     SQL      ┌──────────┐
│   Clients    │ ──────────►   │   Routers    │ ──────────►  │   Repos  │
│  (No UI yet) │ ◄───────────  │  (FastAPI)   │ ◄──────────  │ (CRUD)   │
└──────────────┘               └──────┬───────┘              └────┬─────┘
                                      │                           │
                                      │                     ┌─────┴─────┐
                                      │                     │  Models   │
                                      │                     │ (SQLAlch) │
                                      │                     └─────┬─────┘
                                      │                           │
                                      ▼                           ▼
                              ┌───────────────┐          ┌──────────────┐
                              │   Services    │          │  PostgreSQL  │
                              │  (Business    │          │              │
                              │   Logic)      │          └──────────────┘
                              └───────┬───────┘
                                      │
                    ┌─────────────────┼────────────────────┐
                    │                 │                     │
                    ▼                 ▼                     ▼
            ┌────────────┐   ┌───────────────┐   ┌─────────────────┐
            │  Gemini    │   │   Qdrant      │   │  Curriculum     │
            │  AI API    │   │  Vector DB    │   │  Generator      │
            └────────────┘   └───────────────┘   └─────────────────┘
```

## Request Lifecycle

```
Client Request
     │
     ▼
CORS Middleware ────► Request ID Middleware ────► Exception Handlers
     │                        │                          │
     ▼                        ▼                          ▼
Router (path matching) ──► Auth Dependency ──► Service Method
     │                        │                       │
     │                        ▼                       ▼
     │                  decode_token()           Repository calls
     │                  load_user()              Business logic
     │                  check_role()             AI calls (if applicable)
     │                                             │
     ▼                                             ▼
Response ◄────────────── JSON Serialization ◄──────┘
```

## Teaching Lifecycle (LangGraph)

```
                    ┌──────────────┐
                    │   ENTRY      │
                    │ (decide_entry)│
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │                     │
          (has response?)       (no response)
                │                     │
                ▼                     ▼
        ┌───────────────┐   ┌──────────────────┐
        │ Evaluate      │   │ Retrieve Memories │
        │ Response      │   │                  │
        └───────┬───────┘   └────────┬─────────┘
                │                     │
                ▼                     ▼
        ┌───────────────┐   ┌──────────────────┐
        │   Diagnose    │   │     Teach        │
        │ (recommended  │   │                  │
        │  action)      │   └────────┬─────────┘
        └───────┬───────┘            │
                │                    ▼
    ┌───────────┼───────────┐ ┌──────────────┐
    │           │           │ │ Ask Question │
    ▼           ▼           ▼ └──────┬───────┘
┌────────┐ ┌────────┐ ┌──────────┐   │
│Reteach │ │Prereq  │ │ Example │   END
│        │ │        │ │          │
└───┬────┘ └───┬────┘ └────┬─────┘
    │          │           │
    └────┬─────┘           │
         │ (loop back)     │
         ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │ Retrieve Mem │  │ Provide      │
  │ ──► Teach    │  │ Example      │
  │ ──► Ask Q    │  │ ──► Ask Q    │
  └──────────────┘  └──────────────┘

Diagnose "continue" ──► Complete Concept ──► END
```

## Parent Reporting Lifecycle

```
Parent Request: POST /reports/generate/{student_id}
     │
     ▼
Verify Parent Access (is admin? is linked to student?)
     │
     ▼
Collect Student Data:
  ├── Enrollments & Pace Status
  ├── Lesson Progress (completed/in-progress)
  ├── Concept Mastery (per-concept scores)
  ├── Misconceptions (unresolved, by frequency)
  ├── Knowledge Gaps
  ├── Recent Session Activity
  └── Attempt History (correct/incorrect rates)
     │
     ▼
Build AI Prompt Context:
  └── Format all collected data into structured text
     │
     ▼
Call Gemini generate_json() for report generation
     │
     ├── Success? → Parse structured report (strengths, challenges, recommendations, risk indicators)
     └── Failure? → Use fallback template with default data
     │
     ▼
Validate & Store Report in database
     │
     ▼
Return ReportResponse to parent
```

## AI Lifecycle (Inside Teaching Session)

```
1. Start Session
   └── Load concept, teaching content, examples from DB
       └── Check prerequisites via knowledge graph
           └── Build initial TeacherState

2. Retrieve Memories (MemoryService)
   ├── DB query: unresolved misconceptions for student+concept
   ├── DB query: active memory entries (ordered by confidence)
   └── Qdrant (optional): semantic similarity search
       └── Format: "Student previously struggled with X. Try using examples."

3. Teach (Gemini generate)
   ├── Prompt: concept content + memory context + conversation history
   └── System: act as supportive 1:1 tutor

4. Ask Question (Gemini generate)
   ├── Prompt: just-taught content
   └── Returns: comprehension question

5. Evaluate Response (Gemini generate_json)
   ├── Prompt: concept + teaching + question + student answer
   └── Returns: {score, feedback, understanding}

6. Diagnose (DiagnosisService via Gemini generate_json)
   ├── Prompt: full context + evaluation result
   └── Returns: {diagnosis_type, recommended_action, misconception, evidence}
       └── Persists: Misconception record in DB (if applicable)

7. Memory Extraction (MemoryExtractor → persist)
   ├── Extract: struggles, excels, misconception patterns, learning preferences, pacing
   └── Persist: MemoryEntry records in DB + Qdrant embeddings

8. Route based on recommended_action:
   ├── reteach/prerequisite → loop to step 2
   ├── example → provide example → ask question → END
   └── continue → complete concept → END
```

## Directory Structure

```
Backend/
├── alembic/               # DB migrations
│   └── versions/
│       ├── 0001_create_all_tables.py
│       ├── 0002_create_auth_tables.py
│       ├── 0003_add_report_title_and_data.py
│       └── 0004_add_content_ingestion_tables.py
├── app/
│   ├── config.py          # Pydantic Settings
│   ├── main.py            # FastAPI app factory
│   ├── ai/                # AI Teacher Orchestrator
│   │   ├── graphs/        # LangGraph definition
│   │   ├── nodes/         # 7 graph node functions
│   │   ├── diagnosis/     # Misconception detection
│   │   ├── memory/        # Extraction & retrieval
│   │   ├── guardrails/    # Safety checks
│   │   ├── evaluation/    # Harness, metrics, datasets
│   │   └── services/      # Gemini wrapper
│   ├── api/               # Health endpoint
│   ├── auth/              # Auth + RBAC
│   ├── common/            # Shared base classes & types
│   ├── content_ingestion/ # File upload → AI curriculum
│   ├── curriculum/        # Course/Module/Lesson/Concept CRUD
│   ├── enrollment/        # Student enrollment
│   ├── knowledge_graph/   # Knowledge nodes & edges
│   ├── mastery/           # Concept mastery scoring
│   ├── monitoring/        # In-memory metrics
│   ├── pacing/            # Course scheduling
│   ├── parent_dashboard/  # Parent views
│   ├── progress/          # Lesson progress tracking
│   ├── reports/           # AI-generated reports
│   ├── security/          # JWT, password hashing
│   ├── teaching/          # Session/progress/attempt models
│   └── teaching_sessions/ # Session CRUD
├── tests/                 # 323 tests (unit + integration)
└── docker-compose.yml     # PostgreSQL only
```
