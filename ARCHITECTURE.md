# AI-Native Personalized Schooling Platform — Backend Architecture (MVP)

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Clients                          │
│  (Admin SPA · Student SPA · Parent SPA)            │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────┐
│                FastAPI Application                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Curriculum│  │ Learning │  │   AI Teacher     │  │
│  │ Module   │  │ Module   │  │   Orchestrator   │  │
│  └─────┬────┘  └────┬─────┘  │  (LangGraph)     │  │
│        │             │        │  ┌────────────┐  │  │
│        │             │        │  │ Teaching   │  │  │
│        │             │        │  │ Graph      │  │  │
│        │             │        │  ├────────────┤  │  │
│        │             │        │  │ Diagnosis  │  │  │
│        │             │        │  │ Graph      │  │  │
│        │             │        │  ├────────────┤  │  │
│        │             │        │  │ Pacing     │  │  │
│        │             │        │  │ Graph      │  │  │
│        │             │        │  └────────────┘  │  │
│        │             │        └──────────────────┘  │
│  ┌─────▼─────────────▼──────────────▼───────────┐  │
│  │           Domain Services                    │  │
│  │  (Knowledge Graph · Session · Memory ·       │  │
│  │   Mastery · Scheduling · Insights)           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                   Services                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │PostgreSQL│  │  Redis   │  │  Qdrant  │          │
│  │(All      │  │ (Session │  │ (Vector  │          │
│  │ State)   │  │  + Cache)│  │  Store)  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                      ┌──────────┐  │
│                                      │ Gemini   │  │
│                                      │ Pro API  │  │
│                                      └──────────┘  │
└─────────────────────────────────────────────────────┘
```

### Data Flow (Concept-Level Teaching)

```
Student Request → Learning Module → AI Teacher Orchestrator
 → Resume or start TeachingSession
 → Load Student Memory (traits, past misconceptions, pace)
 → Query Knowledge Graph for current concept prerequisites
 → Assess prerequisite mastery → Diagnose gaps
 → Select action: teach concept | quiz concept | remediate gap | revise
 → Execute → Update Mastery → Store in Student Memory
 → Check schedule/deadline → Adjust pacing
 → Return response + session state
```

---

## 2. Service Boundaries

| Service                  | Responsibility                                         | Owns Data? |
|---------------------------|--------------------------------------------------------|------------|
| **Curriculum Service**    | CRUD for courses, modules, lessons, concepts, exercises | Yes        |
| **Enrollment Service**    | Student–course registration, deadline tracking          | Yes        |
| **Session Service**       | TeachingSession lifecycle — start, pause, resume, end   | Yes        |
| **Instruction Service**   | Concept delivery, attempt recording, progress tracking  | Yes        |
| **Assessment Service**    | Quiz generation, auto-grading, feedback                 | Yes        |
| **Knowledge Graph Srv.**  | Concept nodes, prerequisite edges, graph traversal      | Yes        |
| **Diagnosis Service**     | Misconception detection and tracking per student        | Yes        |
| **Mastery Service**       | Mastery level tracking per student per concept          | Yes        |
| **Memory Service**        | Long-term student memory — observations, patterns, notes | Yes        |
| **Scheduling Service**    | Course deadlines, pace calculation, revision triggers   | Yes        |
| **Insights Service**      | Parent-facing progress summaries and recommendations    | No (reads) |
| **AI Orchestrator**       | LangGraph state machines coordinating all above services | No (stateless) |

All services communicate **in-process** via Python callables.

---

## 3. Domain-Driven Design Modules

### Bounded Contexts

```
┌─────────────────────────────────────────────────────────┐
│                CURRICULUM & KNOWLEDGE                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Course / │  │ Lesson / │  │   Knowledge Graph    │  │
│  │ Module   │  │ Concept  │  │  (Nodes + Edges)     │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                   LEARNING CORE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │Teaching  │  │ Attempt /│  │     Mastery          │  │
│  │Session   │  │ Exercise │  │  (per concept)       │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                 INTELLIGENCE LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │Diagnosis │  │Student   │  │     Scheduling       │  │
│  │(Miscon-  │  │Memory    │  │  (Deadline-aware     │  │
│  │ceptions) │  │Store     │  │   pacing)            │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    USER & ACCESS                          │
│  ┌──────────┐  ┌──────────┐                             │
│  │ Identity │  │ Parent-  │                             │
│  │ & Roles  │  │ Student  │                             │
│  │          │  │ Link     │                             │
│  └──────────┘  └──────────┘                             │
└─────────────────────────────────────────────────────────┘
```

### Ubiquitous Language (Key Terms)

| Term              | Definition                                                   |
|-------------------|--------------------------------------------------------------|
| Course            | Top-level container of learning                              |
| Module            | Thematic unit within a course                                |
| Lesson            | Structured learning session within a module                  |
| Concept           | Atomic teachable unit — the smallest thing the AI can teach  |
| Knowledge Graph   | Directed graph of concepts with prerequisite edges           |
| Knowledge Node    | A concept represented as a node in the knowledge graph       |
| Knowledge Edge    | Prerequisite relationship from concept A to concept B        |
| TeachingSession   | A live AI–student interaction, persistable and resumable     |
| Mastery           | Demonstrated competence level per concept (0.0–1.0)         |
| Attempt           | Single student response to an exercise or diagnostic probe   |
| Misconception     | Registered incorrect mental model for a student–concept pair |
| Student Memory    | Long-term AI-accessible store of student observations        |
| Schedule          | Course timeline with milestones, deadlines, and pace targets |

---

## 4. Database Entity List

### PostgreSQL (Primary State Store)

```
User
├── id (PK)
├── email (unique)
├── password_hash
├── role (enum: admin | student | parent)
├── full_name
├── is_active
└── created_at

StudentProfile
├── id (PK)
├── user_id (FK → User)
├── grade_level
├── avg_session_duration_minutes
├── current_streak_days
└── metadata (JSONB)

ParentStudentLink
├── parent_id (FK → User)
└── student_id (FK → User)

Course
├── id (PK)
├── code (unique)
├── title
├── description
├── total_duration_hours
├── default_deadline_days          # default duration for completion
├── is_published
├── created_by (FK → User)
└── created_at

Module
├── id (PK)
├── course_id (FK → Course)
├── title
├── description
├── order_index
└── estimated_duration_hours

Lesson
├── id (PK)
├── module_id (FK → Module)
├── title
├── content_url
├── order_index
├── estimated_duration_minutes
├── is_required
└── status (enum: draft | published | archived)

Concept
├── id (PK)
├── lesson_id (FK → Lesson)
├── title
├── description
├── order_index
└── estimated_duration_minutes

LearningObjective
├── id (PK)
├── lesson_id (FK → Lesson)
├── code                      (e.g., "ALG.LIN.01")
├── description
├── success_criterion (JSONB)
└── order_index

KnowledgeNode
├── id (PK)
├── concept_id (FK → Concept, nullable)
├── objective_id (FK → LearningObjective, nullable)
├── node_type (enum: concept | objective)
├── label                     (human-readable name)
└── metadata (JSONB)

KnowledgeEdge
├── id (PK)
├── source_node_id (FK → KnowledgeNode)
├── target_node_id (FK → KnowledgeNode)
├── relationship (enum: requires | reinforces | contains)
└── weight (float, 0.0–1.0)

Example
├── id (PK)
├── concept_id (FK → Concept)
├── content (text)
├── explanation (text)
├── order_index
└── tags (text[])

Exercise
├── id (PK)
├── concept_id (FK → Concept)
├── question_type (enum: mcq | multi_select | short_answer | fill_blank)
├── prompt (text)
├── options (JSONB)
├── correct_answer (text)
├── difficulty (float, 0.0–1.0)
├── order_index
└── tags (text[])

StudentCourseEnrollment
├── id (PK)
├── student_id (FK → StudentProfile)
├── course_id (FK → Course)
├── enrolled_at
├── status (enum: active | paused | completed | dropped)
├── started_at
├── target_completion_date         # deadline for this student
├── completed_at
└── current_concept_id (FK → Concept)

TeachingSession
├── id (PK)
├── student_id (FK → StudentProfile)
├── course_id (FK → Course)
├── current_concept_id (FK → Concept)
├── current_lesson_id (FK → Lesson)
├── state (enum: active | paused | completed | interrupted)
├── context (JSONB)                 # AI session context for resume
├── started_at
├── last_activity_at
└── completed_at

Attempt
├── id (PK)
├── student_id (FK → StudentProfile)
├── exercise_id (FK → Exercise)
├── teaching_session_id (FK → TeachingSession)
├── response (text)
├── is_correct (boolean)
├── score (float, 0.0–1.0)
├── time_taken_seconds
├── attempted_at
├── attempt_number (int)
├── ai_feedback (text)
└── metadata (JSONB)

MasteryRecord
├── id (PK)
├── student_id (FK → StudentProfile)
├── concept_id (FK → Concept)
├── mastery_level (float, 0.0–1.0)
├── last_attempted_at
├── total_attempts
├── consecutive_correct
└── next_review_at

Misconception
├── id (PK)
├── student_id (FK → StudentProfile)
├── concept_id (FK → Concept)
├── category (enum: procedural | conceptual | factual | careless)
├── description (text)
├── detected_at
├── detected_in_session_id (FK → TeachingSession)
├── evidence (JSONB)                # responses that triggered detection
├── frequency (int)
├── is_resolved (boolean)
└── resolved_at

StudentMemory
├── id (PK)
├── student_id (FK → StudentProfile)
├── key (varchar)                   # e.g., "pace_preference", "common_stumble"
├── value (JSONB)                   # the observation payload
├── importance (float, 0.0–1.0)
├── created_at
└── updated_at

CourseSchedule
├── id (PK)
├── enrollment_id (FK → StudentCourseEnrollment)
├── target_lessons_per_week (int)
├── current_week (int)
├── pace_status (enum: on_track | behind | ahead)
├── last_pacing_adjustment_at
└── milestones (JSONB)              # [{week, expected_concept, deadline}]

LessonProgress
├── id (PK)
├── student_id (FK → StudentProfile)
├── lesson_id (FK → Lesson)
├── status (enum: not_started | in_progress | completed | skipped)
├── started_at
├── completed_at
├── time_spent_seconds
└── completion_percentage

Report
├── id (PK)
├── student_id (FK → StudentProfile)
├── parent_id (FK → User, nullable)
├── report_type (enum: weekly | monthly | milestone)
├── generated_at
├── summary (text)
├── recommendations (JSONB)
├── pdf_url
└── is_read (boolean)

AuditLog
├── id (PK)
├── user_id (FK → User)
├── action
├── entity_type
├── entity_id
├── old_value (JSONB)
├── new_value (JSONB)
└── timestamp
```

### Redis (Session & Cache)

| Key Pattern                         | Value                       | TTL         |
|-------------------------------------|-----------------------------|-------------|
| `session:{user_id}`                 | Session data (JSON)         | configurable |
| `session:active:{teaching_session_id}` | Active session lock     | 30 min      |
| `rate_limit:{route}:{ip}`           | Counter                     | sliding     |
| `llm_cache:{prompt_hash}`           | Gemini response cache       | 1 hour      |

### Qdrant (Vector Store)

| Collection                | Use Case                                        | Vector Source            |
|---------------------------|-------------------------------------------------|--------------------------|
| `concept_embeddings`      | Semantic retrieval of concepts for teaching     | Gemini embedding         |
| `memory_embeddings`       | Student memory retrieval by semantic similarity | Gemini embedding         |
| `misconception_patterns`  | Match student errors to known misconception patterns | Gemini embedding    |

---

## 5. Microservice vs. Modular Monolith — Recommendation

**Recommendation: Modular Monolith.**

For an MVP, the modular monolith is the clear choice:

1. **Teaching flow is a single transaction**: a student attempt may update MasteryRecord, Misconception, TeachingSession context, StudentMemory, and CourseSchedule in one atomic unit. Distributed boundaries would force eventual consistency where immediate consistency is pedagogically important.

2. **LangGraph state machines are the backbone**: the AI Orchestrator's graphs (Teaching, Diagnosis, Pacing) call into every domain module. Splitting these across networks adds latency, complexity, and failure modes with zero benefit at MVP scale.

3. **Single developer productivity**: no service discovery, no inter-service auth, no event schemas, no deployment pipelines per service.

4. **Extraction-ready ports**: each service is defined by a Python Protocol/ABC. When any service needs independent scaling (e.g., Insights for PDF generation), extract it behind the same interface.

### Future Extraction Candidates
- **Insights Service**: when parent report generation becomes CPU/LLM-heavy
- **Assessment Service**: when quiz generation needs dedicated workers
- **AI Orchestrator**: when Gemini call concurrency requires independent scaling

---

## 6. Folder Structure

```
Backend/
├── alembic/
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── main.py                     # FastAPI app factory
│   ├── config.py                   # Pydantic settings (env-based)
│   │
│   ├── common/
│   │   ├── base.py                 # SQLAlchemy declarative base
│   │   ├── types.py                # Enums, type aliases
│   │   └── exceptions.py           # Domain exception hierarchy
│   │
│   ├── users/                      # Identity & Access
│   │   ├── models.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── curriculum/                 # Course, Module, Lesson, Concept,
│   │   ├── models.py               #   LearningObjective, Example, Exercise
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── knowledge_graph/            # KnowledgeNode, KnowledgeEdge, traversal
│   │   ├── models.py
│   │   ├── service.py              # Graph operations, prerequisite queries
│   │   └── schemas.py
│   │
│   ├── enrollment/                 # StudentCourseEnrollment, CourseSchedule
│   │   ├── models.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── teaching/                   # TeachingSession, Attempt, LessonProgress
│   │   ├── models.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── assessment/                 # Quiz generation, auto-grading
│   │   ├── service.py
│   │   ├── grader.py
│   │   └── schemas.py
│   │
│   ├── mastery/                    # MasteryRecord per concept
│   │   ├── models.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── diagnosis/                  # Misconception detection and tracking
│   │   ├── models.py
│   │   ├── service.py              # Gap analysis, misconception registration
│   │   └── schemas.py
│   │
│   ├── memory/                     # StudentMemory store
│   │   ├── models.py
│   │   ├── service.py              # Read/write/recall student observations
│   │   └── schemas.py
│   │
│   ├── scheduling/                 # Deadline-aware pacing, revision triggers
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── insights/                   # Parent reports & recommendations
│   │   ├── service.py
│   │   ├── templates/              # Jinja2 report templates
│   │   └── schemas.py
│   │
│   ├── ai/                         # AI Teacher Orchestrator
│   │   ├── orchestrator.py         # LangGraph entry point
│   │   ├── graphs/
│   │   │   ├── teaching_graph.py   # Main teaching state machine
│   │   │   ├── diagnosis_graph.py  # Misconception detection flow
│   │   │   └── pacing_graph.py     # Deadline-aware pacing decisions
│   │   ├── nodes/
│   │   │   ├── teach.py
│   │   │   ├── quiz.py
│   │   │   ├── diagnose.py
│   │   │   ├── remediate.py
│   │   │   ├── revise.py
│   │   │   └── advance.py
│   │   ├── prompts/
│   │   │   ├── teach.jinja2
│   │   │   ├── diagnose.jinja2
│   │   │   ├── generate_quiz.jinja2
│   │   │   ├── remediate.jinja2
│   │   │   └── report.jinja2
│   │   ├── llm_client.py           # Gemini Pro wrapper
│   │   ├── embedding_client.py     # Embedding generation
│   │   └── vector_store.py         # Qdrant abstraction
│   │
│   └── infrastructure/
│       ├── database.py             # SQLAlchemy async engine + session
│       ├── redis.py                # Redis client
│       └── qdrant.py               # Qdrant client
│
├── tests/
│   ├── unit/
│   │   ├── curriculum/
│   │   ├── knowledge_graph/
│   │   ├── teaching/
│   │   ├── diagnosis/
│   │   ├── mastery/
│   │   ├── memory/
│   │   ├── scheduling/
│   │   └── ai/
│   └── conftest.py
│
├── scripts/
│   └── seed_data.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── Makefile
```

---

## Key Architecture Decisions

| Decision              | Choice                              | Rationale for MVP |
|-----------------------|-------------------------------------|-------------------|
| Architecture style    | Modular monolith                    | Atomic mastery updates, single-process LangGraph, small team |
| State machine engine  | LangGraph                           | Built-in checkpointing for session resume, graph-based pedagogy modeling |
| Primary DB            | PostgreSQL (asyncpg)                | Relational integrity for mastery + teaching session state |
| Vector store          | Qdrant                              | Concept similarity search, student memory retrieval, misconception pattern matching |
| Cache / sessions      | Redis                               | Simple, fast; stateless app instances for horizontal scaling |
| LLM                   | Gemini Pro                          | 1M-token context for full-session memory, competitive cost |
| Knowledge graph       | PostgreSQL (adjacency list)         | Sufficient for prerequisite traversal; Qdrant for semantic graph search |
| Student memory        | PostgreSQL + Qdrant                 | Structured observations in PG, semantic recall via embeddings in Qdrant |
| Background tasks      | `asyncio.create_task`               | Avoids infrastructure overhead until needed |
| Knowledge tracing     | Simple threshold-based mastery       | BKT/IRT is premature; mastery = weighted average of recent attempts |
| Report generation     | Sync or background on-demand        | PDF generation triggered by parent request or weekly cron |
