# Feature Roadmap — Acuity LMS AI

**Generated:** 2026-06-25
**Based on:** Phase 0 Full Audit, Phase 1 Requirements Reconstruction

---

## 1. Prioritization Framework

| Priority | Definition | Timeline |
|----------|------------|----------|
| **P0** | Blocking bug, security vulnerability, or missing feature that prevents demo/production use | Immediate |
| **P1** | Core feature required for MVP; significant user-facing value | This phase |
| **P2** | Important feature that enhances the product but not blocking | Next phase |
| **P3** | Nice-to-have; can be deferred | Future |

---

## 2. Execution Phases

### Phase 2: End-to-End Flow Validation (Estimated: 3-4 days)

**Goal:** Fix all critical bugs and blocking issues so that core user journeys work

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| FIX-01 | Fix progress update wrong ID (`lesson.id` → `existing.id`) | P0 | 5 min | None |
| FIX-02 | Fix Attempt model `teaching_session_id` nullable | P0 | 5 min | Migration needed |
| FIX-03 | Fix assessment `correctIndex: 0` — use actual exercise data | P0 | 1 hour | None |
| FIX-04 | Add frontend route guards (auth check + role check) | P0 | 3 hours | None |
| FIX-05 | Persist authStore across page reloads (hydrate from localStorage) | P0 | 1 hour | None |
| FIX-06 | Make Topbar reactive to auth state changes | P1 | 1 hour | None |
| FIX-07 | Fix onboarding silent error catch | P1 | 30 min | None |
| FIX-08 | Add forgot-password link to login page | P1 | 15 min | None |
| FIX-09 | Fix enrollment role guard (require STUDENT role) | P1 | 30 min | None |
| FIX-10 | Fix pacing endpoint hardcoded empty course_id | P1 | 15 min | None |
| FIX-11 | Add default edge handler to LangGraph (prevent crash on unknown action) | P1 | 30 min | None |
| FIX-12 | Fix Dockerfile build order | P1 | 15 min | None |
| FIX-13 | Hide/remove fake parameter scores from student dashboard | P1 | 15 min | None |
| FIX-14 | Add minimal empty states to LearningPathPage | P1 | 30 min | None |
| FIX-15 | Add `endSession` call on AITutorPage unmount | P1 | 30 min | None |

### Phase 3: AI Teacher Completion (Estimated: 5-7 days)

**Goal:** Make the AI teacher reliable, safe, and production-quality

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| AI-01 | Wire GuardrailService into all graph nodes (teach, question, evaluate, diagnose, example) | P0 | 1 day | None |
| AI-02 | Add try/except error handling to all 7 graph nodes | P0 | 1 day | None |
| AI-03 | Add retry logic to GeminiService (3 retries with exponential backoff) | P0 | 1 day | None |
| AI-04 | Add fallback response content when all retries fail | P1 | 4 hours | AI-03 |
| AI-05 | Fix `_generate_embedding()` — use proper embedding API (Gemini embedding or sentence-transformers) | P1 | 1 day | None |
| AI-06 | Fix Qdrant point ID generation (use stable hash, not `hash()`) | P1 | 2 hours | None |
| AI-07 | Call `ensure_collection()` before Qdrant operations | P1 | 30 min | None |
| AI-08 | Add `expected_answer` to evaluation prompt (from concept content) | P1 | 1 hour | None |
| AI-09 | Add memory context to question generation prompt | P1 | 1 hour | None |
| AI-10 | Add conversation history summarization/pruning to prevent unbounded growth | P2 | 4 hours | None |
| AI-11 | Fix Gemini `contents` format for correct SDK interface | P1 | 2 hours | None |
| AI-12 | Add timeout to GeminiService HTTP calls | P1 | 30 min | None |
| AI-13 | Fix evaluation harness double-invocation bug | P1 | 1 hour | None |
| AI-14 | Fix evaluation harness `model_calls` counting | P1 | 30 min | AI-13 |
| AI-15 | Detect and alert when Gemini mock fallback is active | P1 | 1 hour | None |

### Phase 4: Content System & Teacher Role (Estimated: 5-7 days)

**Goal:** Complete content workflows and implement the missing Teacher role

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| TCH-01 | Add TEACHER role to UserRole enum and registration | P1 | 1 hour | None |
| TCH-02 | Create teacher-student assignment table + API | P1 | 4 hours | None |
| TCH-03 | Create teacher-course assignment table + API | P1 | 4 hours | TCH-02 |
| TCH-04 | Create teacher dashboard page (assigned students, recent activity) | P1 | 1 day | TCH-02 |
| TCH-05 | Create teacher student roster page | P1 | 1 day | TCH-04 |
| TCH-06 | Create teacher student detail page (progress, mastery, misconceptions) | P1 | 1 day | TCH-05 |
| TCH-07 | Create teacher curriculum editor (course builder UI) | P2 | 3 days | None |
| TCH-08 | Create teacher content upload UI | P2 | 1 day | None |
| TCH-09 | Create teacher AI content review/approval UI | P2 | 2 days | TCH-08 |
| TCH-10 | Create teacher misconception review panel | P2 | 1 day | None |
| TCH-11 | Add AI intervention recommendation endpoint + frontend display | P2 | 2 days | AI-01, AI-02 |

### Phase 5: Frontend Completion (Estimated: 5-7 days)

**Goal:** All frontend pages are complete with proper states, error handling, and UX

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| FE-01 | Add NotFound (404) route | P1 | 15 min | None |
| FE-02 | Add ErrorBoundary to app root | P1 | 30 min | None |
| FE-03 | Add request timeout to apiRequest (30s default) | P1 | 30 min | None |
| FE-04 | Fix Topbar notification/settings to be functional or hidden | P1 | 1 hour | None |
| FE-05 | Implement parent student selector (multi-child support) | P2 | 1 day | None |
| FE-06 | Make layout responsive (mobile support) | P2 | 2 days | None |
| FE-07 | Implement assessment parallel submission with Promise.all | P2 | 1 hour | FIX-03 |
| FE-08 | Implement admin students page search filtering | P2 | 2 hours | None |
| FE-09 | Add admin curriculum editor UI (basic CRUD) | P2 | 3 days | None |
| FE-10 | Add admin content upload UI | P2 | 1 day | None |
| FE-11 | Add pagination to admin students page | P2 | 2 hours | None |
| FE-12 | Add functional Download Report buttons | P2 | 4 hours | None |
| FE-13 | Fix admin dashboard metric mappings to use real percentages | P2 | 2 hours | None |
| FE-14 | Implement admin analytics page with charts (Recharts) | P2 | 2 days | None |
| FE-15 | Replace fake dashboard parameter scores with real data or remove | P2 | 1 day | None |
| FE-16 | Add loading states to all pages that are missing them | P1 | 1 day | None |

### Phase 6: Security Hardening (Estimated: 3-5 days)

**Goal:** Eliminate all security vulnerabilities

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| SEC-01 | Add startup assertion: fail if SECRET_KEY is default in production | P0 | 30 min | None |
| SEC-02 | Change `debug` default to `False` | P0 | 5 min | None |
| SEC-03 | Add rate limiting middleware on auth endpoints (slowapi or custom) | P0 | 1 day | None |
| SEC-04 | Remove email from JWT access token payload | P1 | 15 min | None |
| SEC-05 | Implement audit logging middleware for all CRUD operations | P1 | 2 days | None |
| SEC-06 | Add security headers middleware (helmet-style) | P1 | 1 hour | None |
| SEC-07 | Add validators to LoginRequest, RefreshRequest, UserCreate schemas | P1 | 1 hour | None |
| SEC-08 | Strengthen password policy (add special character requirement) | P2 | 15 min | None |
| SEC-09 | Implement account lockout after N failed login attempts | P2 | 1 day | None |
| SEC-10 | Add `revoked_at` to PasswordResetToken model | P2 | 30 min | Migration needed |
| SEC-11 | Restrict CORS in production (explicit origins, methods, headers) | P1 | 30 min | None |
| SEC-12 | Add `ENABLE_DOCS` env var (default false) | P2 | 15 min | None |
| SEC-13 | Add SMTP/email sending infrastructure | P1 | 2 days | None |
| SEC-14 | Wire email sending into forgot-password flow | P1 | 1 day | SEC-13 |

### Phase 7: DevOps (Estimated: 2-3 days)

**Goal:** One-command local development and deployable system

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| DEV-01 | Fix Dockerfile (reorder COPY before pip install) | P1 | 15 min | None |
| DEV-02 | Add backend service to docker-compose.yml | P1 | 1 hour | DEV-01 |
| DEV-03 | Add frontend service to docker-compose.yml | P2 | 1 hour | None |
| DEV-04 | Add Redis to docker-compose.yml (optional) | P2 | 30 min | None |
| DEV-05 | Add health checks to all Docker services | P2 | 1 hour | DEV-02 |
| DEV-06 | Add .env.example with all required variables including SECRET_KEY | P1 | 30 min | None |
| DEV-07 | Create Makefile / startup script for one-command setup | P2 | 1 hour | DEV-02, DEV-03 |
| DEV-08 | Setup basic GitHub Actions CI (lint + test) | P2 | 1 day | None |
| DEV-09 | Add docker-compose.prod.yml for production deployment | P2 | 2 days | DEV-02, DEV-03 |

### Phase 8: Testing (Estimated: 5-7 days)

**Goal:** Comprehensive test coverage with real database and HTTP-level tests

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| TST-01 | Add pytest-asyncio test database fixture (create/drop tables per session) | P1 | 1 day | None |
| TST-02 | Add HTTP API tests for auth module (register, login, refresh, logout) | P1 | 1 day | TST-01 |
| TST-03 | Add HTTP API tests for curriculum module | P1 | 1 day | TST-01 |
| TST-04 | Add HTTP API tests for enrollment module | P1 | 4 hours | TST-01 |
| TST-05 | Add HTTP API tests for progress module | P1 | 4 hours | TST-01 |
| TST-06 | Add HTTP API tests for teaching sessions module | P1 | 4 hours | TST-01 |
| TST-07 | Add HTTP API tests for AI teacher endpoint | P1 | 4 hours | TST-01 |
| TST-08 | Add HTTP API tests for parent dashboard (remaining 8 routes) | P1 | 4 hours | TST-01 |
| TST-09 | Unskip auth HTTP tests (make them work with test DB) | P1 | 4 hours | TST-01 |
| TST-10 | Add vitest + React Testing Library to frontend | P2 | 1 day | None |
| TST-11 | Add frontend component tests for critical pages (Login, Dashboard, AI Tutor) | P2 | 2 days | TST-10 |
| TST-12 | Add mock AI integration tests with real Gemini API key | P2 | 2 days | None |

### Phase 9: Demo Mode (Estimated: 2-3 days)

**Goal:** System is demonstrable to clients with minimal manual setup

| ID | Task | Priority | Effort | Dependencies |
|----|------|----------|--------|-------------|
| DEMO-01 | Create `scripts/demo_seed.py` with comprehensive seed data | P1 | 1 day | None |
| DEMO-02 | Demo seed: admin account (admin@acuity.demo / password) | P1 | - | DEMO-01 |
| DEMO-03 | Demo seed: parent account (parent@acuity.demo / password) | P1 | - | DEMO-01 |
| DEMO-04 | Demo seed: teacher account (teacher@acuity.demo / password) | P1 | - | DEMO-01 |
| DEMO-05 | Demo seed: 3 student accounts with varying progress | P1 | - | DEMO-01 |
| DEMO-06 | Demo seed: full demo course (3 modules, 9 lessons, 27 concepts, exercises) | P1 | - | DEMO-01 |
| DEMO-07 | Demo seed: parent-student linkages | P1 | - | DEMO-01 |
| DEMO-08 | Demo seed: sample enrollments, progress, mastery records | P1 | - | DEMO-01 |
| DEMO-09 | Demo seed: sample AI reports for demo students | P1 | - | DEMO-01 |
| DEMO-10 | Demo seed: sample misconceptions and memory entries | P1 | - | DEMO-01 |
| DEMO-11 | Create demo startup script (seed DB, start services) | P2 | 4 hours | DEMO-01, DEV-02 |
| DEMO-12 | Return reset token in forgot-password response when in demo mode | P2 | 30 min | None |

---

## 3. Phase Dependency Graph

```
Phase 2 (Flow Fixes)
  ├── Phase 3 (AI Teacher)
  │     └── Phase 4 (Content + Teacher)
  ├── Phase 5 (Frontend)
  ├── Phase 6 (Security)
  ├── Phase 7 (DevOps)
  │     └── Phase 8 (Testing)
  └── Phase 9 (Demo)
```

- Phase 2 has NO dependencies and should be executed first
- Phases 3, 5, 6, 7 can run in parallel after Phase 2
- Phase 4 depends on Phase 3 (AI reliability)
- Phase 8 can start after Phase 2 and run alongside other phases
- Phase 9 can start after Phases 2-4 are stable

---

## 4. Estimated Total Effort

| Phase | Effort | Can Parallelize? |
|-------|--------|:----------------:|
| Phase 2: Flow Validation | 3-4 days | No |
| Phase 3: AI Teacher | 5-7 days | With Phase 5, 6, 7 |
| Phase 4: Content + Teacher | 5-7 days | After Phase 3 |
| Phase 5: Frontend | 5-7 days | With Phase 3, 6, 7 |
| Phase 6: Security | 3-5 days | With Phase 3, 5, 7 |
| Phase 7: DevOps | 2-3 days | With Phase 3, 5, 6 |
| Phase 8: Testing | 5-7 days | After Phase 2 |
| Phase 9: Demo | 2-3 days | After Phase 2-4 |
| **Total** | **~6-8 weeks** | With 2-3 engineers: **~4-5 weeks** |

---

## 5. Demo Readiness Milestone

With Phase 2 complete and Phase 9 partial (seed data), the system can reach **"Controlled Demo"** state in approximately **1 week**.

Required for controlled demo:
- [x] Core auth (register, login, refresh, logout)
- [x] AI teacher (basic teaching, questions, evaluation)
- [ ] Fix assessment scoring (Phase 2 task)
- [ ] Add route guards (Phase 2 task)
- [ ] Fix progress updates (Phase 2 task)
- [ ] Create demo seed data (Phase 9 task)
- [ ] Fix authStore persistence (Phase 2 task)
- [ ] Hide fake metrics (Phase 2 task)
- [ ] Add basic error handling to AI nodes (Phase 3 task)
