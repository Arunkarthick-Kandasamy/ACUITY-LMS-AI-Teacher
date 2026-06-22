# Technical Debt

## Priority Key

| Level | Color | Action Required |
|-------|-------|-----------------|
| **High** | 🔴 | Fix before next milestone |
| **Medium** | 🟡 | Fix within 2 milestones |
| **Low** | 🟢 | Fix when convenient |

---

## 🔴 High Priority

### H1. Gemini Mock Fallback by Default
- **File:** `app/ai/services/gemini.py` lines 24-31
- **Issue:** When `GEMINI_API_KEY` is empty, `GeminiService` silently returns mock responses — no warning is logged, making it appear the AI is working when it's not
- **Impact:** Development and testing are disconnected from real AI behavior
- **Fix:** Log a warning when using mock, or raise an error in non-development environments

### H2. Default Secret Key in Source Code
- **File:** `app/config.py` line 37
- **Issue:** `secret_key` defaults to `"change-me-in-production-use-a-real-secret"`
- **Impact:** Anyone with the source code can forge JWT tokens in production if the key isn't changed
- **Fix:** Remove default; fail at startup if not configured in production

### H3. No Rate Limiting
- **Issue:** All 90 API endpoints are unprotected against abuse
- **Impact:** Brute force auth attacks, DoS on AI endpoint (expensive Gemini calls)
- **Fix:** Implement `slowapi` or custom middleware

### H4. Guardrails Not Used in Production Teaching Flow
- **Files:** `app/ai/guardrails/` vs `app/ai/nodes/*.py`
- **Issue:** Guardrails service exists but is only used in the evaluation harness, not in the actual teaching graph nodes
- **Impact:** AI-generated teaching content, questions, evaluations, and diagnoses are not validated for quality or safety before reaching students
- **Fix:** Wrap Gemini calls in graph nodes with GuardrailService checks

### H5. Asymmetric Draft Endpoint
- **File:** `app/content_ingestion/router.py` line 103-109
- **Issue:** The `generate_draft` endpoint is at `POST /drafts/{draft_id}/generate` but accepts `upload_id` in the path, not `draft_id`. The route parameter name is misleading — the function uses `draft_id` as the parameter name but passes it as `upload_id` to the service
- **Impact:** API contract confusion; API docs will be wrong
- **Fix:** Rename route to `POST /uploads/{upload_id}/generate` or fix the service to accept a draft_id

---

## 🟡 Medium Priority

### M1. Auth API Tests Skipped
- **Files:** `tests/test_auth.py`, `tests/test_rbac.py`
- **Issue:** 8 integration tests skipped with `reason="requires live database"`
- **Impact:** HTTP request/response validation for auth endpoints is untested
- **Fix:** Add Docker-based test database to CI pipeline

### M2. No Audit Trail Usage
- **Files:** `app/audit/models.py`
- **Issue:** `AuditLog` table exists with full schema (user_id, action, entity_type, old_value, new_value, timestamp) but no service layer writes to it
- **Impact:** No traceability for who changed what in the curriculum
- **Fix:** Add audit logging to CurriculumService and AuthService

### M3. Inconsistent Resource Ownership Checks
- **Files:** Various service files
- **Issue:** Some services verify resource ownership (e.g., `ContentIngestionService._verify_access`), others only check RBAC role
- **Impact:** Students may access each other's progress/session data
- **Fix:** Standardize ownership verification as a reusable dependency

### M4. In-Memory Metrics Lost on Restart
- **File:** `app/monitoring/metrics.py`
- **Issue:** `MetricsCollector` stores all metrics in Python lists
- **Impact:** All latency, token usage, and error rate data is lost on application restart
- **Fix:** Persist metrics to database or use Prometheus pushgateway

### M5. Password Reset Without Email Delivery
- **File:** `app/auth/service.py`
- **Issue:** Reset tokens are generated and stored but never sent to the user
- **Impact:** Feature is non-functional
- **Fix:** Integrate email service (SendGrid, SMTP) or document limitation

### M6. B008 Ruff Warnings (FastAPI Pattern)
- **Files:** `app/content_ingestion/router.py`, `app/ai/evaluation/router.py` (13 instances)
- **Issue:** `Depends(get_session)` and `File(...)` in argument defaults trigger ruff B008
- **Impact:** Noise in lint output; can mask real issues
- **Fix:** Add `# noqa: B008` or configure ruff to ignore this rule for FastAPI files

### M7. V1 Prompt Registry Duplication
- **Files:** `app/ai/prompts.py` vs `app/ai/prompts/v1/`
- **Issue:** Two copies of similar prompts exist — inline in `app/ai/prompts.py` and structured in `app/ai/prompts/v1/`. The inline versions are used by graph nodes; the V1 versions are unused
- **Impact:** Maintenance burden; prompt updates must be made in two places or will diverge
- **Fix:** Remove inline prompts, use V1 registry exclusively

---

## 🟢 Low Priority

### L1. Ambiguous Variable Name `l`
- **File:** `app/content_ingestion/ai/extractor.py` line 108 (already fixed)
- **Issue:** E741 lint warning for variable name `l`
- **Impact:** Lint warning only
- **Status:** Fixed in current working tree

### L2. Long Lines in Test Files
- **Files:** Multiple test files
- **Issue:** Several lines exceed 120-character limit (E501) in test data dictionaries
- **Impact:** Lint warnings only; test readability may suffer if split

### L3. Empty `app/ai/prompts/` Directory
- **File:** `app/ai/prompts/` (root-level, not Backend/)
- **Issue:** An empty directory exists at project root with no `__init__.py`
- **Impact:** Confusing to developers; no functional impact

### L4. Unused Imports
- **Files:** `app/content_ingestion/service.py`, `app/content_ingestion/schemas.py`, `app/content_ingestion/ai/curriculum_generator.py`
- **Issue:** Several modules import unused symbols (`os`, `Any`, `select`, `KnowledgeNode`, `Field`)
- **Impact:** Minor code cleanliness; some caught by ruff --fix

### L5. No Special Character Requirement in Password Policy
- **File:** `app/security/password.py` line 11
- **Issue:** Password regex only checks for uppercase, lowercase, and digit
- **Impact:** Weaker passwords than industry standard
- **Fix:** Add `(?=.*[!@#$%^&*])` to regex

### L6. Re-export Models Instead of Direct Import
- **Files:** `app/progress/models.py`, `app/pacing/models.py`
- **Issue:** These files re-export models from other modules (`LessonProgress` from teaching, `CourseSchedule` from enrollment)
- **Impact:** Circular import risk; confusing namespace

### L7. Copyright/License Missing
- **Issue:** No LICENSE file or copyright headers in source files
- **Impact:** Legal ambiguity for open-source or commercial use

---

## Summary

| Priority | Count | Key Items |
|----------|:-----:|-----------|
| **High** | 5 | Mock fallback, secret key, rate limiting, guardrails, asymmetric endpoint |
| **Medium** | 7 | Skipped tests, audit trail, ownership checks, metrics persistence, email delivery, B008 lint, prompt duplication |
| **Low** | 7 | Variable naming, long lines, empty directory, unused imports, password policy, re-exports, license |
| **TOTAL** | **19** | |
