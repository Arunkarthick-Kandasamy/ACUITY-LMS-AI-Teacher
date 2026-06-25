# FEATURE MATRIX — Acuity LMS AI

**Generated:** 2026-06-25
**Legend:** ✅ Complete, ⚠️ Partial/Buggy, ❌ Missing, 🔜 Planned

---

## 1. Authentication & User Management

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| User Registration | ✅ | ✅ | ✅ (unit) | Tokens not issued on registration (by design) |
| User Login | ✅ | ✅ | ✅ (unit) | No rate limiting; missing validators on schema |
| Token Refresh | ✅ | ✅ | ✅ (unit) | Rotation implemented correctly |
| Logout | ✅ | ✅ | ✅ (unit) | Revokes all tokens |
| Forgot Password | ⚠️ | ❌ | ⚠️ | **Email never sent**; no forgot-password page |
| Reset Password | ✅ | ❌ | ✅ (unit) | Token validation + session revocation works |
| Email Verification | ❌ | ❌ | ❌ | No verification flow for new registrations |
| Account Lockout | ❌ | ❌ | ❌ | No failed-attempt tracking |
| Role-Based Access (RBAC) | ✅ | ❌ | ✅ (unit) | Backend enforces; frontend does not |
| User Profile View | ✅ | ✅ | ❌ | Read-only |
| User Profile Edit | ❌ | ❌ | ❌ | No update endpoint exposed |

---

## 2. Student Features

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| Dashboard Overview | ✅ | ⚠️ | ⚠️ | Fake parameter scores; first-course only |
| Course Enrollment | ✅ | ✅ | ✅ (unit) | No role guard (any user can enroll) |
| Learning Path View | ✅ | ⚠️ | ❌ | No empty state |
| AI Tutor (Teach) | ⚠️ | ⚠️ | ⚠️ | No error handling; no guardrails; mock-only AI |
| AI Tutor (Evaluate) | ⚠️ | ⚠️ | ⚠️ | Same issues |
| AI Tutor (Diagnose) | ⚠️ | ⚠️ | ⚠️ | Same issues |
| AI Tutor (Examples) | ⚠️ | ⚠️ | ⚠️ | Same issues |
| Session Management | ✅ | ⚠️ | ✅ (unit) | No endSession on unmount |
| Assessment/Exercises | ✅ | ❌ | ⚠️ | **correctIndex: 0 bug**; sequential submissions |
| Progress Tracking | ⚠️ | ⚠️ | ❌ | **CRITICAL: update uses wrong ID** |
| Mastery Tracking | ✅ | ⚠️ | ✅ (unit) | Empty response for no-data; frontend assumes 0-1 range |
| Adaptive Pacing | ⚠️ | ❌ | ✅ (unit) | Generate endpoint dead code |
| Learning Memory | ⚠️ | ❌ | ✅ (unit) | Qdrant broken; hash IDs unstable |
| Misconception Tracking | ⚠️ | ❌ | ✅ (unit) | No business-layer CRUD service |
| Personalized Reports | ✅ | ❌ | ✅ (unit + HTTP) | No frontend report viewer |
| Student Profile | ✅ | ✅ | ❌ | Read-only |

---

## 3. Parent Features

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| Linked Students Overview | ✅ | ⚠️ | ✅ (unit + 2 HTTP) | First student only; no student selector |
| Student Progress View | ✅ | ⚠️ | ✅ (unit) | First student only |
| Student Mastery View | ✅ | ❌ | ✅ (unit) | Not displayed separately |
| Student Misconceptions | ✅ | ❌ | ✅ (unit) | Not displayed |
| Student Sessions History | ✅ | ❌ | ✅ (unit) | Not displayed |
| Student Reports | ✅ | ⚠️ | ✅ (unit + HTTP) | First student only; download button non-functional |
| Report Generation | ✅ | ❌ | ✅ (unit + HTTP) | No frontend trigger |
| Insights Dashboard | ✅ | ⚠️ | ❌ | First student only; static recommendations |
| Pace/Ahead Tracking | ✅ | ❌ | ✅ (unit) | Not displayed |
| Notifications | ❌ | ❌ | ❌ | No notification system |

---

## 4. Admin Features

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| Dashboard Overview | ✅ | ⚠️ | ❌ | Arbitrary metric mappings to percentages |
| User Management (List) | ✅ | ⚠️ | ❌ | Search is decorative; no pagination |
| User Management (Create/Edit) | ❌ | ❌ | ❌ | No user CRUD endpoints |
| Course Management (CRUD) | ✅ | ❌ | ✅ (unit) | No admin course editor UI |
| Module/Lesson/Concept Management | ✅ | ❌ | ✅ (unit) | No admin curriculum editor UI |
| Content Upload | ✅ | ❌ | ✅ (unit) | No frontend upload UI |
| Content Approval Workflow | ✅ | ❌ | ✅ (unit) | No frontend review UI |
| Enrollment Management | ✅ | ❌ | ✅ (unit) | No admin enrollment UI |
| Analytics (charts, trends) | ⚠️ | ❌ | ❌ | Only static numbers; no time-series |
| System Configuration | ❌ | ❌ | ❌ | No settings UI |
| Audit Log Viewer | ❌ | ❌ | ❌ | Audit log never written |

---

## 5. Teacher Features (NEW — Entirely Missing)

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| Teacher Login/Auth | ❌ | ❌ | ❌ | No TEACHER role in registration |
| Teacher Dashboard | ❌ | ❌ | ❌ | No teacher pages |
| Course Creation | ✅ (as admin) | ❌ | ❌ | Not exposed to teacher role |
| Lesson/Content Creation | ✅ (as admin) | ❌ | ❌ | Not exposed to teacher role |
| Student Roster | ❌ | ❌ | ❌ | No teacher-student assignment |
| Student Progress Monitoring | ❌ | ❌ | ❌ | No teacher view of student data |
| Misconception Review | ❌ | ❌ | ❌ | No teacher-facing misconception list |
| Intervention Recommendations | ❌ | ❌ | ❌ | No AI-recommended interventions for teachers |
| Content Draft Management | ❌ | ❌ | ❌ | Partially exists in content ingestion |
| Grade/Attempt Review | ❌ | ❌ | ❌ | No teacher-gradebook |

---

## 6. AI Teacher Features

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| Teach Concept | ⚠️ | ⚠️ | ✅ (unit) | No error handling; no guardrails |
| Generate Question | ⚠️ | ⚠️ | ✅ (unit) | Sparse prompt without memory context |
| Evaluate Response | ⚠️ | ⚠️ | ✅ (unit) | No expected_answer in prompt |
| Diagnose Understanding | ⚠️ | ❌ | ✅ (unit) | Hardcoded expected_answer |
| Detect Misconceptions | ⚠️ | ❌ | ✅ (unit) | Works; no business-layer service |
| Recommend Prerequisites | ⚠️ | ❌ | ✅ (unit) | Depends on KN graph |
| Generate Examples | ⚠️ | ❌ | ✅ (unit) | No guardrails |
| Complete Concept | ✅ | ❌ | ✅ (unit) | Hardcoded "Great job!" message |
| Adapt Explanation | ❌ | ❌ | ❌ | No adaptation logic beyond reteach/example |
| Store Learning Memory | ⚠️ | ❌ | ✅ (unit) | Qdrant broken; DB-only works |
| Semantic Memory Search | ❌ | ❌ | ❌ | Qdrant embeddings broken |
| Track Mastery | ⚠️ | ❌ | ✅ (unit) | Simple threshold; no Bayesian/IRT |
| Generate Reports | ✅ | ❌ | ✅ (unit + HTTP) | No frontend consumption |
| Guardrail Validation | ❌ | ❌ | ❌ | Service exists but disconnected |
| Retry Logic | ❌ | ❌ | ❌ | No transient-failure handling |
| Streaming Responses | ❌ | ❌ | ❌ | All responses are blocking |

---

## 7. Content System Features

| Feature | Backend | Frontend | Tests | Notes |
|---------|---------|----------|-------|-------|
| File Upload (TXT, PDF, DOCX) | ✅ | ❌ | ✅ (unit) | Robust parser with error handling |
| AI Content Extraction | ✅ | ❌ | ✅ (unit) | Uses Gemini |
| AI Curriculum Generation | ✅ | ❌ | ❌ | Generates course→module→lesson→concept |
| Draft Workflow | ✅ | ❌ | ✅ (unit) | Approve/reject/publish |
| Curriculum CRUD | ✅ | ❌ | ✅ (unit) | No admin UI |
| Knowledge Graph CRUD | ✅ | ❌ | ✅ (unit) | No admin UI |
| Learning Objectives | ✅ | ❌ | ✅ (unit) | Defined but not used by AI teacher |

---

## 8. Infrastructure Features

| Feature | Status | Notes |
|---------|--------|-------|
| PostgreSQL Database | ✅ | Docker compose + 4 migrations |
| Backend Docker Image | ⚠️ | Dockerfile has build bug |
| Frontend Docker Image | ❌ | Not built |
| Docker Compose (all services) | ❌ | Only PostgreSQL |
| Redis | ❌ | No service, no client |
| Qdrant | ❌ | Not in compose; integration broken |
| CI/CD Pipeline | ❌ | No GitHub Actions |
| Health Checks | ⚠️ | DB only; no upstream check |
| Monitoring | ⚠️ | In-memory only |
| Logging | ✅ | Structured JSON |
| Rate Limiting | ❌ | Constants defined but unused |
| HTTPS/TLS | ❌ | Not configured |
| Database Backups | ❌ | Not configured |

---

## 9. Testing Feature Matrix

| Area | Unit | Integration | HTTP/API | E2E |
|------|:----:|:-----------:|:--------:|:---:|
| Health | ❌ | ❌ | ✅ (1) | ❌ |
| Auth | ✅ (17) | ❌ | ❌ (8 skipped) | ❌ |
| RBAC | ✅ (5) | ❌ | ❌ (3 skipped) | ❌ |
| Curriculum | ✅ (15) | ❌ | ❌ | ❌ |
| Enrollment | ✅ (9) | ❌ | ❌ | ❌ |
| Progress | ✅ (9) | ❌ | ❌ | ❌ |
| Mastery | ✅ (10) | ❌ | ❌ | ❌ |
| Pacing | ✅ (9) | ❌ | ❌ | ❌ |
| Teaching Sessions | ✅ (16) | ❌ | ❌ | ❌ |
| AI Graph | ✅ (22) | ✅ (all mocked) | ❌ | ❌ |
| AI Memory | ✅ (21) | ✅ (all mocked) | ❌ | ❌ |
| AI Diagnosis | ✅ (15) | ✅ (all mocked) | ❌ | ❌ |
| AI Evaluation | ✅ (15) | ❌ | ✅ (1) | ❌ |
| Knowledge Graph | ✅ (11) | ❌ | ❌ | ❌ |
| Parent Dashboard | ✅ (26) | ❌ | ✅ (2) | ❌ |
| Reports | ✅ (20) | ✅ (all mocked) | ✅ (3) | ❌ |
| Content Ingestion | ✅ (22) | ✅ (all mocked) | ❌ | ❌ |
| Frontend | ❌ | ❌ | ❌ | ❌ |

---

## 10. Missing High-Priority Features Summary

| Feature | Priority | Reason |
|---------|----------|--------|
| Teacher role + module | HIGH | Critical missing role in an LMS |
| Route guards + role-based access | CRITICAL | Security |
| Email sending (password reset, notifications) | HIGH | Required for real use |
| Report viewer (frontend) | HIGH | Parent requirement |
| Admin curriculum editor UI | HIGH | Admin requirement |
| Content upload UI | HIGH | Admin requirement |
| Student dashboard real metrics | HIGH | Currently shows fake data |
| Streaming AI responses | MEDIUM | UX improvement |
| Time-series analytics | MEDIUM | Admin requirement |
| Audit log viewer | MEDIUM | Compliance |
| Account lockout / rate limiting | HIGH | Security |
| User profile edit | LOW | Nice-to-have |
