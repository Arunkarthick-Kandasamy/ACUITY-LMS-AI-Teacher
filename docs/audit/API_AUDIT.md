# API Audit

## Overview

- **Prefix:** `/api/v1`
- **Total Endpoints:** 90
- **Modules:** 14
- **Auth:** JWT Bearer tokens via `Authorization` header

---

## Endpoint Count Per Module

| Module | Route Prefix | GET | POST | PUT | PATCH | DELETE | Total |
|--------|-------------|:---:|:---:|:---:|:----:|:-----:|:-----:|
| Curriculum | _(mixed prefixes)_ | 13 | 9 | 8 | 0 | 6 | **36** |
| Parent Dashboard | `/parents` | 12 | 0 | 0 | 0 | 0 | **12** |
| Auth | `/auth` | 0 | 6 | 0 | 0 | 0 | **6** |
| Content Ingestion | `/content` | 2 | 4 | 0 | 0 | 0 | **6** |
| Teaching Sessions | _(mixed)_ | 2 | 1 | 0 | 2 | 0 | **5** |
| Progress | _(mixed)_ | 2 | 1 | 0 | 1 | 0 | **5** |
| Enrollment | _(mixed)_ | 2 | 1 | 0 | 0 | 0 | **3** |
| Mastery | `/mastery` | 3 | 0 | 0 | 0 | 0 | **3** |
| Pacing | `/pacing` | 1 | 1 | 0 | 1 | 0 | **3** |
| Reports | `/reports` | 2 | 1 | 0 | 0 | 0 | **3** |
| Knowledge Graph | `/knowledge-graph` | 1 | 1 | 0 | 0 | 1 | **3** |
| AI Evaluation | `/ai/evaluation` | 3 | 0 | 0 | 0 | 0 | **3** |
| AI Teacher (teach) | _(mixed)_ | 0 | 1 | 0 | 0 | 0 | **1** |
| Health | `/health` | 1 | 0 | 0 | 0 | 0 | **1** |
| **TOTAL** | | **43** | **26** | **8** | **4** | **7** | **90** |

## Endpoint Summary by HTTP Method
- **GET:** 43 — Read operations
- **POST:** 26 — Create operations
- **PUT:** 8 — Full updates
- **PATCH:** 4 — Partial updates
- **DELETE:** 7 — Delete operations

## Authorization Summary
- **Authenticated (any active user):** 55 endpoints
- **Admin-only:** 28 endpoints
- **Public (no auth):** 7 endpoints

---

## Endpoint Detail

### 1. Health — `/api/v1/health`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| GET | `/` | Public | `health_check` | — | `{status, version, database}` |

**Router:** `app/api/routes/health.py`

---

### 2. Auth — `/api/v1/auth`

| Method | Path | Auth | Function | Request Body | Response |
|--------|------|:----:|----------|-------------|----------|
| POST | `/register` | Public | `register` | `RegisterRequest {email, password, full_name, role}` | `UserResponse` |
| POST | `/login` | Public | `login` | `LoginRequest {email, password}` | `TokenResponse {access_token, refresh_token, user}` |
| POST | `/refresh` | Public | `refresh` | `RefreshRequest {refresh_token}` | `TokenResponse` |
| POST | `/logout` | Auth | `logout` | — | `MessageResponse` |
| POST | `/forgot-password` | Public | `forgot_password` | `ForgotPasswordRequest {email}` | `MessageResponse` |
| POST | `/reset-password` | Public | `reset_password` | `ResetPasswordRequest {token, new_password}` | `MessageResponse` |

**Router:** `app/auth/router.py`

---

### 3. Curriculum — `/api/v1` (mixed prefixes)

#### Courses

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/courses` | Admin | `create_course` | `CourseCreate` | `CourseResponse` |
| GET | `/courses` | Auth | `list_courses` | Query: `is_published, search, page, per_page` | Paginated `CourseListResponse` |
| GET | `/courses/{id}` | Auth | `get_course` | — | `CourseDetailResponse` |
| PUT | `/courses/{id}` | Admin | `update_course` | `CourseUpdate` | `CourseResponse` |
| DELETE | `/courses/{id}` | Admin | `delete_course` | — | `DeleteMessage` |
| PUT | `/courses/{id}/publish` | Admin | `publish_course` | `CoursePublishRequest` | `CoursePublishResponse` |

#### Modules

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/courses/{id}/modules` | Admin | `create_module` | `ModuleCreate` | `ModuleResponse` |
| GET | `/courses/{id}/modules` | Auth | `list_modules` | — | `[ModuleListResponse]` |
| PUT | `/modules/{id}` | Admin | `update_module` | `ModuleUpdate` | `ModuleResponse` |
| DELETE | `/modules/{id}` | Admin | `delete_module` | — | `DeleteMessage` |

#### Lessons

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/modules/{id}/lessons` | Admin | `create_lesson` | `LessonCreate` | `LessonResponse` |
| GET | `/modules/{id}/lessons` | Auth | `list_lessons` | — | `[LessonListResponse]` |
| GET | `/lessons/{id}` | Auth | `get_lesson` | — | `LessonDetailResponse` |
| PUT | `/lessons/{id}` | Admin | `update_lesson` | `LessonUpdate` | `LessonResponse` |
| DELETE | `/lessons/{id}` | Admin | `delete_lesson` | — | `DeleteMessage` |

#### Concepts

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/lessons/{id}/concepts` | Admin | `create_concept` | `ConceptCreate` | `ConceptResponse` |
| GET | `/lessons/{id}/concepts` | Auth | `list_concepts` | — | `[ConceptListResponse]` |
| GET | `/concepts/{id}` | Auth | `get_concept` | — | `ConceptDetailResponse` |
| PUT | `/concepts/{id}` | Admin | `update_concept` | `ConceptUpdate` | `ConceptResponse` |
| DELETE | `/concepts/{id}` | Admin | `delete_concept` | — | `DeleteMessage` |

#### Concept Contents

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/concepts/{id}/contents` | Admin | `create_content` | `ConceptContentCreate` | `ConceptContentResponse` |
| GET | `/concepts/{id}/contents` | Auth | `list_contents` | — | `[ConceptContentResponse]` |
| PUT | `/concept-contents/{id}` | Admin | `update_content` | `ConceptContentCreate` | `ConceptContentResponse` |
| DELETE | `/concept-contents/{id}` | Admin | `delete_content` | — | `DeleteMessage` |

#### Exercises

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/concepts/{id}/exercises` | Admin | `create_exercise` | `ExerciseCreate` | `ExerciseResponse` |
| GET | `/concepts/{id}/exercises` | Auth | `list_exercises` | — | `[ExerciseListResponse]` |
| PUT | `/exercises/{id}` | Admin | `update_exercise` | `ExerciseUpdate` | `ExerciseResponse` |
| DELETE | `/exercises/{id}` | Admin | `delete_exercise` | — | `DeleteMessage` |

#### Examples

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/concepts/{id}/examples` | Admin | `create_example` | `ExampleCreate` | `ExampleResponse` |
| GET | `/concepts/{id}/examples` | Auth | `list_examples` | — | `[ExampleBrief]` |
| PUT | `/examples/{id}` | Admin | `update_example` | `ExampleUpdate` | `ExampleResponse` |
| DELETE | `/examples/{id}` | Admin | `delete_example` | — | `DeleteMessage` |

#### Learning Objectives

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/lessons/{id}/objectives` | Admin | `create_objective` | `LearningObjectiveCreate` | `LearningObjectiveResponse` |
| GET | `/lessons/{id}/objectives` | Auth | `list_objectives` | — | `[LearningObjectiveResponse]` |
| PUT | `/objectives/{id}` | Admin | `update_objective` | `LearningObjectiveUpdate` | `LearningObjectiveResponse` |
| DELETE | `/objectives/{id}` | Admin | `delete_objective` | — | `DeleteMessage` |

**Router:** `app/curriculum/router.py` (36 endpoints — the largest module)

---

### 4. Knowledge Graph — `/api/v1/knowledge-graph`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/edges` | Admin | `create_edge` | `KnowledgeEdgeCreate` | `KnowledgeEdgeResponse` |
| DELETE | `/edges/{id}` | Admin | `delete_edge` | — | `DeleteMessage` |
| GET | `/concepts/{id}/prerequisites` | Auth | `get_prerequisites` | — | `PrerequisiteResponse` |

**Router:** `app/knowledge_graph/router.py`

---

### 5. Enrollment — `/api/v1`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/enrollments` | Auth | `enroll` | `EnrollmentCreate` | `EnrollmentResponse` |
| GET | `/enrollments` | Auth | `list_enrollments` | Query: `student_id` | `[EnrollmentListResponse]` |
| GET | `/enrollments/{id}` | Auth | `get_enrollment` | — | `EnrollmentResponse` |

**Router:** `app/enrollment/router.py`

---

### 6. Progress — `/api/v1`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| GET | `/courses/{id}/curriculum` | Auth | `get_curriculum_tree` | — | `CurriculumTreeResponse` |
| GET | `/lessons/{id}/progress` | Auth | `get_lesson_progress` | — | `LessonProgressResponse` |
| PATCH | `/lessons/{id}/progress` | Auth | `update_lesson_progress` | `LessonProgressUpdate` | `LessonProgressResponse` |
| POST | `/exercises/{id}/attempts` | Auth | `record_attempt` | `AttemptCreate` | `AttemptResponse` |
| GET | `/attempts` | Auth | `get_attempt_history` | Query: `page, per_page` | Paginated `[AttemptHistoryItem]` |

**Router:** `app/progress/router.py`

---

### 7. Mastery — `/api/v1/mastery`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| GET | `/` | Auth | `get_mastery_overview` | — | `[MasteryResponse]` |
| GET | `/concepts/{id}` | Auth | `get_mastery_by_concept` | — | `MasteryResponse` |
| GET | `/courses/{id}` | Auth | `get_course_mastery_summary` | — | `MasterySummaryResponse` |

**Router:** `app/mastery/router.py`

---

### 8. Pacing — `/api/v1/pacing`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/generate` | Auth | `generate_schedule` | `GenerateScheduleRequest` | `PacingStatusResponse` |
| GET | `/` | Auth | `get_pacing_status` | — | `[PacingStatusResponse]` |
| PATCH | `/` | Auth | `update_pacing_status` | `PacingUpdateRequest` | `PacingUpdateResponse` |

**Router:** `app/pacing/router.py`

---

### 9. Teaching Sessions — `/api/v1`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/sessions` | Auth | `start_session` | `StartSessionRequest` | `SessionResponse` |
| GET | `/sessions/current` | Auth | `resume_session` | — | `SessionResponse` |
| PATCH | `/sessions/{id}/pause` | Auth | `pause_session` | — | `SessionResponse` |
| PATCH | `/sessions/{id}/end` | Auth | `end_session` | `EndSessionRequest` (opt) | `SessionResponse` |
| GET | `/sessions/history` | Auth | `get_session_history` | Query: `page, per_page, student_id` | Paginated `[SessionHistoryItem]` |

**Router:** `app/teaching_sessions/router.py`

---

### 10. Parent Dashboard — `/api/v1/parents`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| GET | `/students` | Parent/Admin | `list_students` | — | `[ParentStudentResponse]` |
| GET | `/students/{id}` | Parent/Admin | `get_student` | — | `StudentProfileResponse` |
| GET | `/students/{id}/progress` | Parent/Admin | `get_student_progress` | — | `ProgressSummaryResponse` |
| GET | `/students/{id}/curriculum` | Parent/Admin | `get_student_curriculum` | Query: `course_id` | `CurriculumTreeResponse` |
| GET | `/students/{id}/mastery` | Parent/Admin | `get_student_mastery` | — | `MasterySummaryResponse` |
| GET | `/students/{id}/mastery/concepts` | Parent/Admin | `get_student_mastery_concepts` | — | `[MasteryConceptResponse]` |
| GET | `/students/{id}/pacing` | Parent/Admin | `get_student_pacing` | — | `[PacingStatusResponse]` |
| GET | `/students/{id}/misconceptions` | Parent/Admin | `get_student_misconceptions` | — | `[MisconceptionResponse]` |
| GET | `/students/{id}/knowledge-gaps` | Parent/Admin | `get_student_knowledge_gaps` | — | `[KnowledgeGapResponse]` |
| GET | `/students/{id}/sessions` | Parent/Admin | `get_student_sessions` | Query: `page, per_page` | Paginated `[TeachingSessionResponse]` |
| GET | `/students/{id}/recent-activity` | Parent/Admin | `get_student_recent_activity` | Query: `days` | `[RecentActivityItem]` |
| GET | `/students/{id}/dashboard` | Parent/Admin | `get_student_dashboard` | — | `DashboardResponse` |

**Router:** `app/parent_dashboard/router.py`

---

### 11. Reports — `/api/v1/reports`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/generate/{student_id}` | Parent/Admin | `generate_report` | Query: `report_type` | `ReportResponse` |
| GET | `/{id}` | Parent/Admin | `get_report` | — | `ReportResponse` |
| GET | `/student/{student_id}` | Parent/Admin | `list_student_reports` | Query: `page, per_page` | Paginated `[ReportResponse]` |

**Router:** `app/reports/router.py`

---

### 12. Content Ingestion — `/api/v1/content`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/upload` | Admin | `upload_content` | Multipart `UploadFile` | `UploadResponse` |
| GET | `/jobs/{upload_id}` | Auth | `get_job_status` | — | `JobStatusResponse` |
| GET | `/drafts/{draft_id}` | Auth | `get_draft` | — | `DraftResponse` |
| POST | `/drafts/{draft_id}/generate` | Admin | `generate_draft` | — | `DraftResponse` |
| POST | `/drafts/{draft_id}/approve` | Admin | `approve_draft` | — | `ApproveResponse` |
| POST | `/drafts/{draft_id}/publish` | Admin | `publish_draft` | — | `PublishResponse` |

**Note:** The `generate` endpoint accepts `draft_id` in the path but internally uses `upload_id` (naming asymmetry).

**Router:** `app/content_ingestion/router.py`

---

### 13. AI Teacher — `/api/v1`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| POST | `/teacher/teach` | Auth | `teach` | `{session_id, student_response?}` | `{action, mastery_estimate, content...}` |

**Router:** `app/ai/router.py`  
**Note:** This is the single entry point into the entire LangGraph teaching state machine.

---

### 14. AI Evaluation — `/api/v1/ai/evaluation`

| Method | Path | Auth | Function | Request | Response |
|--------|------|:----:|----------|---------|----------|
| GET | `/metrics` | Auth | `get_evaluation_metrics` | — | Metrics summary |
| GET | `/traces` | Auth | `get_evaluation_traces` | Query: `limit, offset, scenario` | Paginated traces |
| GET | `/scenarios` | Auth | `list_scenarios` | — | `[scenario_labels]` |

**Router:** `app/ai/evaluation/router.py`

---

## Response Format

All endpoint responses follow a consistent envelope:

```json
{
  "status": "success",
  "data": { ... }
}
```

Error responses:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": []
  }
}
```

## Missing Endpoints (by common REST patterns)

The following standard CRUD operations are not implemented:

- **Auth:** No `PUT /auth/profile` for updating user profile
- **Auth:** No `GET /auth/me` for current user profile
- **Enrollment:** No `DELETE /enrollments/{id}` (drop enrollment via status only)
- **Knowledge Graph:** No `PUT /edges/{id}` for updating edges
- **Mastery:** No recalculation endpoint (done implicitly through service calls)
- **Monitoring:** No metrics retrieval endpoint (in-memory only, no router)
