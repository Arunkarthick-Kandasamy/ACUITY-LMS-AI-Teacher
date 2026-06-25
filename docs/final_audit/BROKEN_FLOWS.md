# BROKEN FLOWS — Acuity LMS AI

**Generated:** 2026-06-25
**Severity:** CRITICAL = breaks core functionality, HIGH = significant data/UX issue

---

## CRITICAL BROKEN FLOWS

### B1: Progress Update Always Fails (404)

**File:** `Backend/app/progress/service.py:97`
**Issue:** `await self.progress_repo.update(lesson.id, **update_data)` uses `lesson.id` (Lesson PK) instead of `existing.id` (LessonProgress PK). The `Repository.update()` method looks up by primary key, so it always gets `None` and raises `NotFoundException`.

**Impact:** Any PATCH to lesson progress after the initial create will fail with 404. Students cannot update their progress, mark lessons complete, or track time spent.

**Severity:** CRITICAL

**Fix:** Change `lesson.id` to `existing.id`.

---

### B2: Attempt Model Constraint Mismatch

**Files:** `Backend/app/teaching/models.py:80-82`, `Backend/app/progress/service.py:117`
**Issue:** `Attempt.teaching_session_id` is defined as NOT NULL (`Mapped[str]`), but `progress/service.py:117` pops `teaching_session_id` with a default of `None`. Recording an attempt without a session causes an `IntegrityError`.

**Impact:** Attempts recorded outside a teaching session (e.g., standalone exercises) crash with a database error.

**Severity:** CRITICAL

**Fix:** Make `teaching_session_id` nullable in the model or ensure all attempt recording passes a session ID.

---

### B3: Frontend Route Guards Missing

**File:** `acuity-frontend/src/router/index.tsx:32-63`
**Issue:** No authentication or role-based route guards. Any user can navigate to `/student/dashboard`, `/parent/dashboard`, `/admin/dashboard` without logging in.

**Impact:** Unauthenticated users can access all pages. Students can access admin pages and vice versa.

**Severity:** CRITICAL

**Fix:** Wrap role routes with an `AuthGuard` component.

---

### B4: Assessment Correct Answer Always Index 0

**File:** `acuity-frontend/src/pages/student/AssessmentPage.tsx:35`
**Issue:** `const correctIndex = 0` — every question marks the first option as correct, regardless of exercise data.

**Impact:** All assessments produce wrong scores. The student gets incorrect feedback. Mastery data is corrupted.

**Severity:** CRITICAL

**Fix:** Use the actual correct answer from the exercise API response.

---

### B5: AI Teacher Graph Has No Default Conditional Edge

**File:** `Backend/app/ai/graphs/teacher.py:70-74`
**Issue:** `RETURN_ACTION_MAP` only maps 4 actions (`reteach`, `prerequisite`, `example`, `continue`). If diagnosis returns an unrecognized action, LangGraph raises `ValueError` with no fallback.

**Impact:** Graph crashes on unexpected diagnosis output. No error recovery path.

**Severity:** CRITICAL

**Fix:** Add a default edge handler or validate `recommended_action` before routing.

---

### B6: GuardrailService Never Called

**File:** `Backend/app/ai/guardrails/service.py` (entire file)
**Issue:** `GuardrailService.check_json_response()` and `check_text_response()` are well-implemented but never invoked from any graph node or router. All LLM output flows to the user unchecked.

**Impact:** Empty, hallucinated, or harmful AI output reaches the student. No validation, no fallback.

**Severity:** CRITICAL

**Fix:** Wire guardrail calls into every node that produces LLM output.

---

### B7: Qdrant Embedding Generation Broken

**File:** `Backend/app/ai/memory/retrieval.py:195-211`
**Issue:** `_generate_embedding()` asks Gemini to generate a string representation of a 768-dimensional vector and parses it as JSON. This is unreliable, expensive, and produces fake vectors. Mock fallback generates random noise.

**Impact:** Semantic memory search is completely non-functional. Qdrant integration provides no value.

**Severity:** CRITICAL

**Fix:** Use a proper embedding model (e.g., Gemini embedding API, sentence-transformers).

---

### B8: No Error Handling in Any Graph Node

**Files:** All files in `Backend/app/ai/nodes/`
**Issue:** None of the 7 graph nodes have try/except blocks. Any exception from GeminiService, DB, or Qdrant propagates and crashes the entire graph.

**Impact:** Any transient failure loses the entire session context. Student gets a 500 error.

**Severity:** CRITICAL

**Fix:** Add try/except with graceful degradation to all nodes.

---

### B9: Password Reset Email Never Sent

**File:** `Backend/app/auth/service.py:136-158`
**Issue:** `forgot_password()` generates a token, logs it to console, returns it — but the router discards the return value. No SMTP/email infrastructure exists anywhere in the codebase.

**Impact:** Users cannot reset their passwords. The feature is completely non-functional.

**Severity:** CRITICAL

**Fix:** Implement email service and send actual reset emails.

---

### B10: Dockerfile Build Order Broken

**File:** `Backend/Dockerfile`
**Issue:** `pip install .` is run before `COPY . .` in the builder stage. The pyproject.toml exists at that point but the package source code does not, so `pip install .` fails.

**Impact:** Docker image cannot be built.

**Severity:** HIGH (blocking deployment)

**Fix:** Reorder: `COPY . .` before `pip install .`

---

## HIGH SEVERITY BROKEN FLOWS

### B11: Progress Endpoint Uses Wrong Schema for Update

**File:** `Backend/app/curriculum/router.py:491-501`
**Issue:** `PUT /concept-contents/{content_id}` uses `ConceptContentCreate` (all required) instead of `ConceptContentUpdate`. Partial updates are impossible.

**Impact:** Clients must send all fields, negating the purpose of an update endpoint.

---

### B12: Pacing Generate Endpoint Dead Code

**File:** `Backend/app/pacing/service.py:36-63`
**Issue:** `generate_schedule()` duplicates enrollment schedule creation. Since enrollment already creates a `CourseSchedule`, calling generate raises "Schedule already exists." The endpoint is unusable.

**Impact:** The pacing generate API endpoint always returns an error.

---

### B13: Pacing Response Returns Empty Course ID

**File:** `Backend/app/pacing/router.py:34-35`
**Issue:** `course_id=""` is hardcoded in the response. Clients receive a pacing status with no course association.

**Impact:** Clients cannot match pacing data to courses.

---

### B14: Enrollment Missing Role Guard

**File:** `Backend/app/enrollment/router.py:33-41`
**Issue:** Any authenticated user (admin, parent) can enroll in a course. Admin users without a student profile will get a 404 from `_get_student_profile`, but parent users with student profiles can enroll in courses.

**Impact:** Unauthorized enrollment possible.

---

### B15: AI Evaluation Harness Invokes Graph Twice

**File:** `Backend/app/ai/evaluation/harness.py:69, 91`
**Issue:** `_execute_with_tracing()` calls `teacher_graph.astream()` (tracing) AND `teacher_graph.ainvoke()` (final state). This runs the entire graph twice.

**Impact:** Doubles LLM cost and latency during evaluation. Model call counts are inflated.

---

### B16: authStore Not Persisted Across Reloads

**File:** `acuity-frontend/src/store/authStore.ts:8-13`
**Issue:** `currentUser` is initialized to `null`. On hard refresh, the user must re-login even if a valid token exists in localStorage.

**Impact:** Poor UX; every browser refresh logs the user out.

---

### B17: Topbar Not Reactive to Auth Changes

**File:** `acuity-frontend/src/layouts/Topbar.tsx:7`
**Issue:** `authStore.user` is read directly from the module-level object. The component won't re-render when auth state changes because there's no React state or subscription binding.

**Impact:** Topbar shows stale user info (or 'User') after login/logout.

---

### B18: Assessment Submissions Sequential Instead of Parallel

**File:** `acuity-frontend/src/pages/student/AssessmentPage.tsx:43-55`
**Issue:** Uses `for...of` with `await` inside — each `recordAttempt` waits for completion before starting the next. For 20 questions, this is 20 sequential HTTP requests.

**Impact:** Slow assessment submission; poor UX.

---

### B19: Onboarding Silently Swallows Errors

**File:** `acuity-frontend/src/pages/student/StudentOnboarding.tsx:34`
**Issue:** `catch {}` — all errors during course enrollment are silently swallowed. The user is redirected to the dashboard regardless of success or failure.

**Impact:** Users may land on an empty dashboard with no indication that enrollment failed.

---

### B20: Student Dashboard Uses Fake Parameter Scores

**File:** `acuity-frontend/src/pages/student/StudentDashboard.tsx:77-82`
**Issue:** `Math.round(overallMastery * 0.9)` etc. — correctness, response time, retries, and skips are invented multipliers of overall mastery, not real API data.

**Impact:** Students see fabricated learning metrics that are misleading.

---

### B21: Admin Students Page Search Non-Functional

**File:** `acuity-frontend/src/pages/admin/StudentsPage.tsx:29-31`
**Issue:** Search input has an empty `onChange` handler. Users can type but nothing filters.

**Impact:** Broken search feature in admin panel.

---

### B22: AuditLog Model Never Written To

**File:** `Backend/app/audit/models.py` (entire file)
**Issue:** `AuditLog` model is well-designed but no code in the entire backend creates audit records. CRUD operations, auth events, and AI interactions leave no trace.

**Impact:** No audit trail for compliance, debugging, or security investigations.

---

### B23: Diagnosis Module Has No Business Service

**File:** `Backend/app/diagnosis/` (entire directory)
**Issue:** `Misconception` model exists but there is no business-layer service for CRUD operations. The only service is in the AI layer (`app/ai/diagnosis/`).

**Impact:** No API for querying, resolving, or managing misconceptions outside the AI flow.

---

## SUMMARY TABLE

| ID | Flow | Severity | Type |
|----|------|:--------:|------|
| B1 | Progress update | CRITICAL | Bug |
| B2 | Attempt recording | CRITICAL | Bug |
| B3 | Frontend route access | CRITICAL | Missing |
| B4 | Assessment scoring | CRITICAL | Bug |
| B5 | AI graph routing | CRITICAL | Bug |
| B6 | AI output validation | CRITICAL | Missing |
| B7 | Semantic memory search | CRITICAL | Bug |
| B8 | AI node error handling | CRITICAL | Missing |
| B9 | Password reset | CRITICAL | Missing |
| B10 | Docker build | HIGH | Bug |
| B11 | Concept content update | HIGH | Bug |
| B12 | Pacing generate | HIGH | Dead code |
| B13 | Pacing response | HIGH | Bug |
| B14 | Enrollment access | HIGH | Missing |
| B15 | Evaluation harness | HIGH | Bug |
| B16 | Auth store persistence | HIGH | Missing |
| B17 | Topbar reactivity | HIGH | Bug |
| B18 | Assessment performance | HIGH | Bug |
| B19 | Onboarding error handling | HIGH | Missing |
| B20 | Dashboard fake metrics | HIGH | Bug |
| B21 | Search functionality | HIGH | Missing |
| B22 | Audit trail | HIGH | Missing |
| B23 | Diagnosis business service | HIGH | Missing |
