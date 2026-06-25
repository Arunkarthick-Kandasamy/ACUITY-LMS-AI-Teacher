# Business Requirements Document — Acuity LMS AI

**Version:** 1.0
**Date:** 2026-06-25
**Status:** Inferred from existing codebase

---

## 1. Product Vision

Acuity LMS AI is an AI-Native Personalized Schooling Platform where students learn through an AI Teacher that behaves like a human tutor. The platform provides personalized learning paths, real-time assessment, adaptive pacing, and detailed analytics for students, parents, teachers, and administrators.

---

## 2. Business Objectives

| Objective | Description | Success Metric |
|-----------|-------------|----------------|
| OBJ-1 | Deliver personalized 1:1 tutoring at scale | Students complete concepts with >=80% mastery |
| OBJ-2 | Reduce teacher workload through AI automation | AI generates 90%+ of curriculum content |
| OBJ-3 | Provide parents with real-time learning visibility | Parents can view progress, mastery, and reports |
| OBJ-4 | Enable rapid curriculum creation and iteration | Admin can create a full course via content ingestion in <1 hour |
| OBJ-5 | Identify and address learning gaps early | Misconceptions detected within 2 sessions |
| OBJ-6 | Provide actionable analytics for administrators | Admin dashboard shows enrollment trends, mastery distribution, system health |

---

## 3. User Roles

| Role | Description | Priority |
|------|-------------|----------|
| Student | Primary learner — consumes content, interacts with AI tutor, takes assessments | P0 |
| Parent | Guardian — monitors learning, receives reports, views progress | P0 |
| Admin | System administrator — manages users, courses, content, analytics | P0 |
| Teacher | Content creator and student supervisor — creates curriculum, reviews AI content, monitors students | P1 (missing — to be built) |

---

## 4. Functional Requirements

### 4.1 Authentication & User Management (FR-AUTH)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-AUTH-01 | Users shall register with email, password, full name, and role | ✅ Implemented |
| FR-AUTH-02 | Users shall log in with email and password | ✅ Implemented |
| FR-AUTH-03 | Users shall receive JWT access tokens (30 min) and refresh tokens (7 days) | ✅ Implemented |
| FR-AUTH-04 | Users shall be able to refresh expired tokens | ✅ Implemented |
| FR-AUTH-05 | Users shall be able to log out (revoke all tokens) | ✅ Implemented |
| FR-AUTH-06 | Users shall be able to reset their password via email | ❌ Broken (email never sent) |
| FR-AUTH-07 | Users shall verify their email on registration | ❌ Missing |
| FR-AUTH-08 | Failed login attempts shall be rate-limited | ❌ Missing |
| FR-AUTH-09 | Accounts shall be locked after N failed login attempts | ❌ Missing |
| FR-AUTH-10 | Users shall be able to update their profile | ❌ Missing |

### 4.2 Curriculum Management (FR-CURR)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-CURR-01 | Admins shall create courses with title, description, subject, grade level, and thumbnail | ✅ Implemented |
| FR-CURR-02 | Courses shall contain modules with ordering | ✅ Implemented |
| FR-CURR-03 | Modules shall contain lessons with ordering | ✅ Implemented |
| FR-CURR-04 | Lessons shall contain concepts with ordering | ✅ Implemented |
| FR-CURR-05 | Concepts shall have content (multiple content items), exercises, and examples | ✅ Implemented |
| FR-CURR-06 | Lessons shall have learning objectives | ✅ Implemented |
| FR-CURR-07 | Courses shall be publishable/unpublishable | ✅ Implemented |
| FR-CURR-08 | Curriculum shall support knowledge graphs (prerequisite relationships) | ✅ Implemented |
| FR-CURR-09 | Teachers shall be able to create and edit curriculum | ❌ Missing (admin-only) |

### 4.3 Enrollment (FR-ENROLL)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-ENROLL-01 | Students shall enroll in published courses | ✅ Implemented |
| FR-ENROLL-02 | Students shall have a schedule generated on enrollment | ✅ Implemented |
| FR-ENROLL-03 | Only students shall be able to enroll in courses | ⚠️ No role guard |
| FR-ENROLL-04 | Students shall be able to view their enrollments | ✅ Implemented |
| FR-ENROLL-05 | Admins shall be able to view all enrollments | ✅ Implemented |

### 4.4 AI Teacher (FR-AI)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-AI-01 | AI shall teach concepts with personalized explanations | ✅ Implemented |
| FR-AI-02 | AI shall generate questions to assess understanding | ✅ Implemented |
| FR-AI-03 | AI shall evaluate student responses with scores and feedback | ✅ Implemented |
| FR-AI-04 | AI shall diagnose misconceptions and knowledge gaps | ✅ Implemented |
| FR-AI-05 | AI shall provide examples when students struggle | ✅ Implemented |
| FR-AI-06 | AI shall recommend prerequisite concepts when needed | ✅ Implemented |
| FR-AI-07 | AI shall track mastery over time | ✅ Implemented |
| FR-AI-08 | AI shall adapt pacing based on student performance | ⚠️ Pacing module exists but dead code |
| FR-AI-09 | AI shall store and retrieve learning memories | ⚠️ Qdrant integration broken |
| FR-AI-10 | AI output shall be validated by guardrails before reaching students | ❌ Guardrails disconnected |
| FR-AI-11 | AI shall handle errors gracefully with retry logic | ❌ Missing |
| FR-AI-12 | AI shall support streaming responses for better UX | ❌ Missing |

### 4.5 Assessment & Progress (FR-PROG)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-PROG-01 | Students shall view their progress per lesson | ✅ Implemented |
| FR-PROG-02 | Students shall record exercise attempts with scores | ✅ Implemented |
| FR-PROG-03 | Student progress shall update correctly | ❌ Broken (wrong ID in update) |
| FR-PROG-04 | Students shall view mastery levels per concept | ✅ Implemented |
| FR-PROG-05 | Mastery shall be calculated from attempt history | ✅ Implemented |
| FR-PROG-06 | Students shall view their learning path | ✅ Implemented |
| FR-PROG-07 | Students shall view adaptive pacing status | ⚠️ Partially implemented |

### 4.6 Parent Dashboard (FR-PARENT)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-PARENT-01 | Parents shall view all linked students | ✅ Implemented |
| FR-PARENT-02 | Parents shall view student progress across courses | ✅ Implemented |
| FR-PARENT-03 | Parents shall view student mastery breakdown | ✅ Implemented |
| FR-PARENT-04 | Parents shall view student misconceptions | ✅ Implemented |
| FR-PARENT-05 | Parents shall view session history with accuracy | ✅ Implemented |
| FR-PARENT-06 | Parents shall generate and view AI reports | ✅ Implemented |
| FR-PARENT-07 | Parents shall view insights and recommendations | ✅ Implemented |
| FR-PARENT-08 | Parents shall manage multiple children | ❌ Only first child shown |

### 4.7 Reports (FR-REPORT)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-REPORT-01 | AI-generated reports shall summarize student progress | ✅ Implemented |
| FR-REPORT-02 | Reports shall include mastery, strengths, weaknesses, and recommendations | ✅ Implemented |
| FR-REPORT-03 | Reports shall be stored and retrievable | ✅ Implemented |
| FR-REPORT-04 | Reports shall be downloadable as PDF | ❌ Not implemented |

### 4.8 Content Ingestion (FR-CONTENT)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-CONTENT-01 | Admins shall upload documents (TXT, PDF, DOCX) | ✅ Implemented |
| FR-CONTENT-02 | AI shall extract structured content from documents | ✅ Implemented |
| FR-CONTENT-03 | AI shall generate full curriculum from extracted content | ✅ Implemented |
| FR-CONTENT-04 | Content shall go through draft → approve → publish workflow | ✅ Implemented |
| FR-CONTENT-05 | Teachers shall upload and manage content | ❌ Missing (admin-only) |

### 4.9 Teacher Module (FR-TEACHER) — New Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TEACHER-01 | Teachers shall register with a TEACHER role | P0 |
| FR-TEACHER-02 | Teachers shall have a dashboard with student overview | P0 |
| FR-TEACHER-03 | Teachers shall be assigned students | P0 |
| FR-TEACHER-04 | Teachers shall create and edit curriculum | P0 |
| FR-TEACHER-05 | Teachers shall review and approve AI-generated content | P0 |
| FR-TEACHER-06 | Teachers shall view student progress and mastery | P1 |
| FR-TEACHER-07 | Teachers shall view student misconceptions | P1 |
| FR-TEACHER-08 | Teachers shall receive AI-generated intervention recommendations | P1 |

### 4.10 Admin Features (FR-ADMIN)

| ID | Requirement | Status |
|----|-------------|--------|
| FR-ADMIN-01 | Admins shall view a dashboard with system statistics | ✅ Implemented |
| FR-ADMIN-02 | Admins shall manage users (list, search, create, edit, disable) | ⚠️ List only; search broken |
| FR-ADMIN-03 | Admins shall manage courses and curriculum | ✅ API only; no frontend |
| FR-ADMIN-04 | Admins shall view analytics (enrollments, activity, mastery) | ⚠️ Static numbers only |
| FR-ADMIN-05 | Admins shall upload content | ✅ API only; no frontend |
| FR-ADMIN-06 | Admins shall view audit logs | ❌ Missing |

---

## 5. Non-Functional Requirements

| ID | Requirement | Status | Priority |
|----|-------------|--------|----------|
| NFR-01 | System shall respond to API requests within 500ms (p95) | ❌ Untested | HIGH |
| NFR-02 | AI responses shall complete within 10 seconds | ❌ No timeout configured | HIGH |
| NFR-03 | System shall support at least 100 concurrent users | ❌ Untested | HIGH |
| NFR-04 | Passwords shall be hashed with bcrypt | ✅ Implemented | CRITICAL |
| NFR-05 | JWT secrets shall not be stored in source code | ❌ Hardcoded default | CRITICAL |
| NFR-06 | All user actions shall be auditable | ❌ Audit log never written | HIGH |
| NFR-07 | AI output shall be validated before reaching users | ❌ Guardrails disconnected | CRITICAL |
| NFR-08 | System shall have 99.9% uptime for API | ❌ No SLA configured | MEDIUM |
| NFR-09 | UI shall be responsive (mobile, tablet, desktop) | ⚠️ Desktop only | MEDIUM |
| NFR-10 | User data shall be backed up daily | ❌ Not configured | HIGH |

---

## 6. System Constraints

| Constraint | Description |
|------------|-------------|
| C-01 | PostgreSQL 16 is the primary database |
| C-02 | Python 3.11+ for backend |
| C-03 | React 19 + TypeScript for frontend |
| C-04 | Google Gemini 1.5 Pro for AI |
| C-05 | LangGraph for AI state machine |
| C-06 | Async-first architecture (FastAPI + async SQLAlchemy) |

---

## 7. Assumptions

| Assumption | Description |
|------------|-------------|
| A-01 | Users have reliable internet connectivity |
| A-02 | Content is in English (no i18n required) |
| A-03 | Primary deployment is cloud-based (AWS/GCP/Azure) |
| A-04 | AI costs are acceptable at projected scale |
| A-05 | Schools provide student email addresses for registration |

---

## 8. Scope & Out of Scope

### In Scope
- Student learning with AI tutor
- Parent monitoring and reporting
- Admin system management
- Teacher content creation and student oversight
- Content ingestion and AI curriculum generation
- Progress tracking and mastery assessment
- Adaptive pacing and learning paths

### Out of Scope (v1.0)
- Real-time video/audio tutoring
- Mobile native apps (responsive web only)
- Third-party LMS integration (LTI)
- Offline mode
- Multi-language support
- Gamification (badges, leaderboards)
- Marketplace for courses
- Payment/subscription management
