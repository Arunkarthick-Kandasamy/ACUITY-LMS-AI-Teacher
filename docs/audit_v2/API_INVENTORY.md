# API Inventory

> Routes extracted directly from FastAPI router registrations in `app/main.py` and individual router files. Cross-referenced against `API_CONTRACTS.md` (2924-line spec at project root) for completeness.

**API Prefix:** `/api/v1` (from `app/config.py:24`)

---

## Health

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/health` | `app/api/routes/health.py:8` | `health_check()` | Yes |

---

## Authentication

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/auth/register` | `app/auth/router.py:22` | `register()` | Yes |
| POST | `/api/v1/auth/login` | `app/auth/router.py:22` | `login()` | Yes |
| POST | `/api/v1/auth/refresh` | `app/auth/router.py:22` | `refresh()` | Yes |
| POST | `/api/v1/auth/logout` | `app/auth/router.py:22` | `logout()` | Yes |
| POST | `/api/v1/auth/forgot-password` | `app/auth/router.py:22` | `forgot_password()` | Yes |
| POST | `/api/v1/auth/reset-password` | `app/auth/router.py:22` | `reset_password()` | Yes |

**6/6 auth endpoints match API_CONTRACTS.md.**

---

## Curriculum (Courses / Modules / Lessons / Concepts)

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/courses` | `app/curriculum/router.py:54` | `create_course()` | Yes |
| GET | `/api/v1/courses` | `app/curriculum/router.py:54` | `list_courses()` | Yes |
| GET | `/api/v1/courses/{course_id}` | `app/curriculum/router.py:54` | `get_course()` | Yes |
| PUT | `/api/v1/courses/{course_id}` | `app/curriculum/router.py:54` | `update_course()` | Yes |
| DELETE | `/api/v1/courses/{course_id}` | `app/curriculum/router.py:54` | `delete_course()` | Yes |
| PUT | `/api/v1/courses/{course_id}/publish` | `app/curriculum/router.py:54` | `publish_course()` | Yes |
| POST | `/api/v1/courses/{course_id}/modules` | `app/curriculum/router.py:54` | `create_module()` | Yes |
| GET | `/api/v1/courses/{course_id}/modules` | `app/curriculum/router.py:54` | `list_modules()` | Yes |
| PUT | `/api/v1/modules/{module_id}` | `app/curriculum/router.py:54` | `update_module()` | Yes |
| DELETE | `/api/v1/modules/{module_id}` | `app/curriculum/router.py:54` | `delete_module()` | Yes |
| POST | `/api/v1/modules/{module_id}/lessons` | `app/curriculum/router.py:54` | `create_lesson()` | Yes |
| GET | `/api/v1/modules/{module_id}/lessons` | `app/curriculum/router.py:54` | `list_lessons()` | Yes |
| GET | `/api/v1/lessons/{lesson_id}` | `app/curriculum/router.py:54` | `get_lesson()` | Yes |
| PUT | `/api/v1/lessons/{lesson_id}` | `app/curriculum/router.py:54` | `update_lesson()` | Yes |
| DELETE | `/api/v1/lessons/{lesson_id}` | `app/curriculum/router.py:54` | `delete_lesson()` | Yes |
| POST | `/api/v1/lessons/{lesson_id}/concepts` | `app/curriculum/router.py:54` | `create_concept()` | Yes |
| GET | `/api/v1/lessons/{lesson_id}/concepts` | `app/curriculum/router.py:54` | `list_concepts()` | Yes |
| GET | `/api/v1/concepts/{concept_id}` | `app/curriculum/router.py:54` | `get_concept()` | Yes |
| PUT | `/api/v1/concepts/{concept_id}` | `app/curriculum/router.py:54` | `update_concept()` | Yes |
| DELETE | `/api/v1/concepts/{concept_id}` | `app/curriculum/router.py:54` | `delete_concept()` | Yes |
| POST | `/api/v1/concepts/{concept_id}/contents` | `app/curriculum/router.py:54` | `create_content()` | Yes |
| GET | `/api/v1/concepts/{concept_id}/contents` | `app/curriculum/router.py:54` | `list_contents()` | Yes |
| PUT | `/api/v1/concept-contents/{content_id}` | `app/curriculum/router.py:54` | `update_content()` | Yes |
| DELETE | `/api/v1/concept-contents/{content_id}` | `app/curriculum/router.py:54` | `delete_content()` | Yes |
| POST | `/api/v1/concepts/{concept_id}/exercises` | `app/curriculum/router.py:54` | `create_exercise()` | Yes |
| GET | `/api/v1/concepts/{concept_id}/exercises` | `app/curriculum/router.py:54` | `list_exercises()` | Yes |
| PUT | `/api/v1/exercises/{exercise_id}` | `app/curriculum/router.py:54` | `update_exercise()` | Yes |
| DELETE | `/api/v1/exercises/{exercise_id}` | `app/curriculum/router.py:54` | `delete_exercise()` | Yes |
| POST | `/api/v1/concepts/{concept_id}/examples` | `app/curriculum/router.py:54` | `create_example()` | Yes |
| GET | `/api/v1/concepts/{concept_id}/examples` | `app/curriculum/router.py:54` | `list_examples()` | Yes |
| PUT | `/api/v1/examples/{example_id}` | `app/curriculum/router.py:54` | `update_example()` | Yes |
| DELETE | `/api/v1/examples/{example_id}` | `app/curriculum/router.py:54` | `delete_example()` | Yes |
| POST | `/api/v1/lessons/{lesson_id}/objectives` | `app/curriculum/router.py:54` | `create_objective()` | Yes |
| GET | `/api/v1/lessons/{lesson_id}/objectives` | `app/curriculum/router.py:54` | `list_objectives()` | Yes |
| PUT | `/api/v1/objectives/{objective_id}` | `app/curriculum/router.py:54` | `update_objective()` | Yes |
| DELETE | `/api/v1/objectives/{objective_id}` | `app/curriculum/router.py:54` | `delete_objective()` | Yes |

**36/36 curriculum endpoints match API_CONTRACTS.md.**

---

## Knowledge Graph

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/knowledge-graph/edges` | `app/knowledge_graph/router.py:21` | `create_edge()` | Yes |
| DELETE | `/api/v1/knowledge-graph/edges/{edge_id}` | `app/knowledge_graph/router.py:21` | `delete_edge()` | Yes |
| GET | `/api/v1/knowledge-graph/concepts/{concept_id}/prerequisites` | `app/knowledge_graph/router.py:21` | `get_prerequisites()` | Yes |

**3/3 knowledge graph endpoints match API_CONTRACTS.md.**

---

## Enrollment

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/enrollments` | `app/enrollment/router.py:15` | `enroll()` | Yes |
| GET | `/api/v1/enrollments` | `app/enrollment/router.py:15` | `list_enrollments()` | Yes |
| GET | `/api/v1/enrollments/{enrollment_id}` | `app/enrollment/router.py:15` | `get_enrollment()` | Yes |

**3/3 enrollment endpoints match API_CONTRACTS.md.**

**Missing (specified in API_CONTRACTS.md but not in code):**
- `PATCH /enrollments/{enrollment_id}` — enrollment pause/resume

---

## Progress

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/lessons/{lesson_id}/progress` | `app/progress/router.py:15` | `get_progress()` | Yes |
| GET | `/api/v1/concepts/{concept_id}` | `app/curriculum/router.py:54` | `get_concept()` | Yes (with mastery) |
| GET | `/api/v1/courses/{course_id}/curriculum` | `app/curriculum/router.py:54` | `get_curriculum_tree()` | Yes |

**3/3 progress endpoints match API_CONTRACTS.md.**

---

## Mastery

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/mastery` | `app/mastery/router.py:15` | `get_mastery()` | Yes |

**1/1 mastery endpoint matches API_CONTRACTS.md.**

**Missing (specified in API_CONTRACTS.md but not in code):**
- `GET /mastery/concepts/{concept_id}` — per-concept mastery detail
- `GET /mastery/courses/{course_id}` — course-level mastery aggregate

---

## Pacing

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/pacing` | `app/pacing/router.py:15` | `get_pacing()` | Yes |

**1/1 pacing endpoint matches API_CONTRACTS.md.**

---

## Teaching Sessions

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/sessions` | `app/teaching_sessions/router.py:21` | `create_session()` | Yes |
| GET | `/api/v1/sessions/active` | `app/teaching_sessions/router.py:21` | `get_active_session()` | Yes |
| GET | `/api/v1/sessions/{session_id}` | `app/teaching_sessions/router.py:21` | `get_session()` | Yes |
| PATCH | `/api/v1/sessions/{session_id}` | `app/teaching_sessions/router.py:21` | `update_session()` | Yes |
| GET | `/api/v1/sessions/{session_id}/history` | `app/teaching_sessions/router.py:21` | `get_session_history()` | Yes |

**5/5 session endpoints match API_CONTRACTS.md.**

**Missing (specified in API_CONTRACTS.md but not in code):**
- `POST /sessions/{session_id}/next` — replaced by `/teacher/teach` (different pathway)
- `POST /sessions/{session_id}/respond` — not implemented
- `POST /sessions/{session_id}/quiz` — AI quiz generation not implemented

---

## AI Teacher

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/teacher/teach` | `app/ai/router.py:15` | `teach()` | No (replaces `POST /sessions/{id}/next`) |
| POST | `/api/v1/teacher/evaluate` | `app/ai/router.py:15` | `evaluate()` | No (replaces `POST /exercises/{id}/grade`) |

**2/2 AI endpoints are NOT in API_CONTRACTS.md.** The spec describes `/sessions/{id}/next` and `/sessions/{id}/respond` instead.

---

## Parent Dashboard

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/parent/students` | `app/parent_dashboard/router.py:20` | `list_students()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/progress` | `app/parent_dashboard/router.py:20` | `get_student_progress()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/mastery` | `app/parent_dashboard/router.py:20` | `get_student_mastery()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/misconceptions` | `app/parent_dashboard/router.py:20` | `get_student_misconceptions()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/sessions` | `app/parent_dashboard/router.py:20` | `get_student_sessions()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/reports` | `app/parent_dashboard/router.py:20` | `list_reports()` | Yes |
| GET | `/api/v1/parent/students/{student_id}/reports/{report_id}` | `app/parent_dashboard/router.py:20` | `get_report()` | Yes |
| POST | `/api/v1/parent/students/{student_id}/reports/generate` | `app/parent_dashboard/router.py:20` | `generate_report()` | Yes |
| PATCH | `/api/v1/parent/students/{student_id}/reports/{report_id}/read` | `app/parent_dashboard/router.py:20` | `mark_report_read()` | Yes |
| GET | `/api/v1/parent/dashboard` | `app/parent_dashboard/router.py:20` | `get_dashboard()` | Yes |

**10/10 parent dashboard endpoints match API_CONTRACTS.md.**

---

## Reports

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| GET | `/api/v1/reports` | `app/reports/router.py:15` | `list_reports()` | Yes |
| GET | `/api/v1/reports/{report_id}` | `app/reports/router.py:15` | `get_report()` | Yes |
| POST | `/api/v1/reports/generate` | `app/reports/router.py:15` | `generate_report()` | Yes |

**3/6 report endpoints match API_CONTRACTS.md.**

**Extra endpoints in code not in API_CONTRACTS.md:**
- `POST /api/v1/reports/generate-ai` (AI-powered generation separate)
- `POST /api/v1/reports/generate-pdf` (PDF generation endpoint)
- `GET /api/v1/reports/templates` (template listing)

---

## AI Evaluation

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/ai/evaluation/datasets` | `app/ai/evaluation/router.py:15` | `create_dataset()` | No |
| GET | `/api/v1/ai/evaluation/datasets` | `app/ai/evaluation/router.py:15` | `list_datasets()` | No |
| GET | `/api/v1/ai/evaluation/datasets/{id}` | `app/ai/evaluation/router.py:15` | `get_dataset()` | No |
| POST | `/api/v1/ai/evaluation/datasets/{id}/run` | `app/ai/evaluation/router.py:15` | `run_evaluation()` | No |
| GET | `/api/v1/ai/evaluation/results` | `app/ai/evaluation/router.py:15` | `list_results()` | No |
| GET | `/api/v1/ai/evaluation/results/{id}` | `app/ai/evaluation/router.py:15` | `get_result()` | No |

**6/6 evaluation endpoints are NOT in API_CONTRACTS.md.** This is an internal tooling module.

---

## Content Ingestion

| Method | Path | Router File | Handler | In API_CONTRACTS.md? |
|--------|------|-------------|---------|---------------------|
| POST | `/api/v1/content/upload` | `app/content_ingestion/router.py:20` | `upload_file()` | No |
| GET | `/api/v1/content/submissions` | `app/content_ingestion/router.py:20` | `list_submissions()` | No |
| GET | `/api/v1/content/submissions/{id}` | `app/content_ingestion/router.py:20` | `get_submission()` | No |
| PUT | `/api/v1/content/submissions/{id}/approve` | `app/content_ingestion/router.py:20` | `approve_submission()` | No |
| PUT | `/api/v1/content/submissions/{id}/reject` | `app/content_ingestion/router.py:20` | `reject_submission()` | No |
| POST | `/api/v1/content/extract` | `app/content_ingestion/router.py:20` | `extract_content()` | No |
| POST | `/api/v1/content/generate` | `app/content_ingestion/router.py:20` | `generate_curriculum()` | No |
| GET | `/api/v1/content/pending` | `app/content_ingestion/router.py:20` | `list_pending()` | No |
| DELETE | `/api/v1/content/submissions/{id}` | `app/content_ingestion/router.py:20` | `delete_submission()` | No |

**9/9 content ingestion endpoints are NOT in API_CONTRACTS.md.** This module is not documented in the API spec.

---

## Summary

| Router Module | Endpoints in Code | In API_CONTRACTS.md | Missing from Code | Not in Spec |
|---------------|:-----------------:|:-------------------:|:-----------------:|:-----------:|
| Health | 1 | 1 | 0 | 0 |
| Auth | 6 | 6 | 0 | 0 |
| Curriculum | 36 | 36 | 0 | 0 |
| Knowledge Graph | 3 | 3 | 0 | 0 |
| Enrollment | 3 | 4 | 1 (PATCH) | 0 |
| Progress | 3 | 3 | 0 | 0 |
| Mastery | 1 | 3 | 2 | 0 |
| Pacing | 1 | 1 | 0 | 0 |
| Teaching Sessions | 5 | 8 | 3 | 0 |
| AI Teacher | 2 | 0 | 0 | 2 |
| Parent Dashboard | 10 | 10 | 0 | 0 |
| Reports | 6 | 3 | 0 | 3 |
| AI Evaluation | 6 | 0 | 0 | 6 |
| Content Ingestion | 9 | 0 | 0 | 9 |
| **Total** | **91** | **78** | **6** | **20** |

**6 endpoints specified in API_CONTRACTS.md are missing from the code. 20 endpoints in code are not documented in API_CONTRACTS.md.**
