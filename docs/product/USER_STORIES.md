# User Stories — Acuity LMS AI

**Generated:** 2026-06-25
**Legend:** ✅ Implemented, ⚠️ Partially Implemented, ❌ Missing

---

## 1. Student Stories

### Registration & Onboarding

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-S-01 | As a student, I want to register with my email and password so that I can create an account. | ✅ | Registration works |
| US-S-02 | As a student, I want to select my grade level and subjects during onboarding so that the system can personalize my learning. | ⚠️ | No API storage for preferences |
| US-S-03 | As a student, I want to enroll in courses so that I can start learning. | ⚠️ | Auto-enrolls in first course; no course selection |
| US-S-04 | As a student, I want to verify my email address so that my account is secure. | ❌ | Not implemented |

### Learning

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-S-05 | As a student, I want to see my learning path so that I know what to study next. | ⚠️ | No empty state; assumes enrollment exists |
| US-S-06 | As a student, I want the AI to teach me concepts so that I can learn new material. | ⚠️ | Works but no error handling; mock-only without API key |
| US-S-07 | As a student, I want the AI to ask me questions so that I can test my understanding. | ⚠️ | Works but prompt is sparse |
| US-S-08 | As a student, I want the AI to evaluate my answers so that I get feedback. | ⚠️ | Works but no expected_answer in prompt |
| US-S-09 | As a student, I want the AI to explain concepts differently if I'm struggling. | ⚠️ | Reteach path exists but limited adaptation |
| US-S-10 | As a student, I want the AI to show me examples so that I can understand better. | ⚠️ | Works but no guardrails |
| US-S-11 | As a student, I want the AI to detect when I have misconceptions so that I can correct them. | ⚠️ | Works but mocked |
| US-S-12 | As a student, I want the AI to remember what I've learned so that sessions build on each other. | ⚠️ | Works via DB; Qdrant broken |
| US-S-13 | As a student, I want streaming AI responses so that I don't wait for the full response. | ❌ | Not implemented |

### Assessment & Progress

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-S-14 | As a student, I want to take assessments so that I can test my knowledge. | ❌ | **Broken — correctIndex: 0** |
| US-S-15 | As a student, I want to see my progress on each lesson so that I know how far I've come. | ⚠️ | Broken update (404) |
| US-S-16 | As a student, I want to see my mastery levels so that I know which concepts I've mastered. | ⚠️ | Works but no historical trend |
| US-S-17 | As a student, I want to see my weak areas so that I know what to focus on. | ⚠️ | Weak concepts shown; no recommendations |
| US-S-18 | As a student, I want to see my learning pace so that I know if I'm on track. | ❌ | Not exposed in frontend |
| US-S-19 | As a student, I want to see my dashboard with real metrics so that I can track my performance. | ❌ | Shows fake parameter scores |

### Sessions

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-S-20 | As a student, I want to start a teaching session so that I can learn with the AI. | ✅ | Works |
| US-S-21 | As a student, I want to pause and resume sessions so that I can learn at my own pace. | ✅ | Works |
| US-S-22 | As a student, I want to view my session history so that I can review past learning. | ✅ | Works |

### Profile

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-S-23 | As a student, I want to view my profile so that I can see my account details. | ✅ | Read-only |
| US-S-24 | As a student, I want to edit my profile so that I can update my information. | ❌ | Not implemented |

---

## 2. Parent Stories

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-P-01 | As a parent, I want to register so that I can monitor my children's learning. | ✅ | Registration works |
| US-P-02 | As a parent, I want to link to my children so that I can see their data. | ✅ | ParentStudentLink model exists |
| US-P-03 | As a parent, I want to see an overview of all my children's learning so that I can quickly check their status. | ⚠️ | First child only |
| US-P-04 | As a parent, I want to see each child's course progress so that I know what they're learning. | ⚠️ | First child only |
| US-P-05 | As a parent, I want to see each child's mastery breakdown so that I know their strengths and weaknesses. | ⚠️ | First child only |
| US-P-06 | As a parent, I want to see any misconceptions my child has so that I can help them. | ⚠️ | First child only |
| US-P-07 | As a parent, I want to see my child's recent sessions with accuracy so that I know how they're performing. | ⚠️ | First child only |
| US-P-08 | As a parent, I want to generate and view AI reports so that I get detailed analysis. | ⚠️ | First child only; download non-functional |
| US-P-09 | As a parent, I want to see insights about my child's learning habits so that I can support them better. | ⚠️ | First child only; static recommendations |
| US-P-10 | As a parent, I want to select which child I'm viewing so that I can manage multiple children. | ❌ | No student selector |

---

## 3. Admin Stories

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-A-01 | As an admin, I want to register so that I can manage the system. | ✅ | Registration works (admin role) |
| US-A-02 | As an admin, I want to see a dashboard with system statistics so that I can monitor the platform. | ⚠️ | Static numbers; arbitrary metric mappings |
| US-A-03 | As an admin, I want to view all users so that I can manage accounts. | ⚠️ | List works; search is decorative |
| US-A-04 | As an admin, I want to create and edit users so that I can manage accounts manually. | ❌ | No user creation/editing API |
| US-A-05 | As an admin, I want to disable users so that I can block access. | ❌ | Not implemented |
| US-A-06 | As an admin, I want to create and manage courses so that I can build the curriculum. | ⚠️ | API exists; no frontend UI |
| US-A-07 | As an admin, I want to create and manage the curriculum hierarchy so that content is well-organized. | ⚠️ | API exists; no frontend UI |
| US-A-08 | As an admin, I want to upload documents and generate courses with AI so that I can create content quickly. | ⚠️ | API exists; no frontend UI |
| US-A-09 | As an admin, I want to approve or reject AI-generated content so that quality is controlled. | ⚠️ | API exists; no frontend UI |
| US-A-10 | As an admin, I want to view analytics with charts and trends so that I can understand usage patterns. | ❌ | Static numbers only; no charts |
| US-A-11 | As an admin, I want to view enrollment data so that I can track adoption. | ⚠️ | Numbers shown; no trends |
| US-A-12 | As an admin, I want to view audit logs so that I can investigate incidents. | ❌ | Audit logging not implemented |
| US-A-13 | As an admin, I want to manage enrollments so that I can manually enroll/unenroll students. | ❌ | Not implemented |

---

## 4. Teacher Stories (New — Not Implemented)

| ID | Story | Priority |
|----|-------|----------|
| US-T-01 | As a teacher, I want to register with a TEACHER role so that I can access teacher features. | P0 |
| US-T-02 | As a teacher, I want to log in and see a teacher dashboard with my assigned students. | P0 |
| US-T-03 | As a teacher, I want to create courses and lessons so that I can build curriculum. | P0 |
| US-T-04 | As a teacher, I want to upload content documents and have AI generate curriculum from them. | P0 |
| US-T-05 | As a teacher, I want to review AI-generated content and make edits before publishing. | P0 |
| US-T-06 | As a teacher, I want to see a list of my students so that I know who I'm teaching. | P0 |
| US-T-07 | As a teacher, I want to view each student's progress, mastery, and weak areas. | P1 |
| US-T-08 | As a teacher, I want to see misconceptions detected by the AI so that I can intervene. | P1 |
| US-T-09 | As a teacher, I want the AI to recommend interventions for struggling students. | P1 |
| US-T-10 | As a teacher, I want to see student session history and attempt details. | P1 |
| US-T-11 | As a teacher, I want to create exercises and assessments for specific concepts. | P1 |

---

## 5. AI-Specific Stories

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-AI-01 | As a student, I want the AI to generate personalized explanations so that I can understand concepts in my own way. | ⚠️ | Generates content but no personalization |
| US-AI-02 | As a student, I want the AI to adapt its teaching based on my performance so that I learn at the right level. | ❌ | No real adaptation beyond reteach/example |
| US-AI-03 | As a system, I want the AI's output validated before reaching students so that no harmful content is shown. | ❌ | Guardrails disconnected |
| US-AI-04 | As a system, I want the AI to retry on failure so that transient errors don't disrupt learning. | ❌ | No retry logic |
| US-AI-05 | As a system, I want to monitor AI performance so that we can detect degradation. | ❌ | In-memory only |
| US-AI-06 | As a parent, I want the AI to generate progress reports so that I have detailed insights. | ✅ | Works |

---

## 6. Security Stories

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-SEC-01 | As a system, I want to use a secure JWT secret so that tokens can't be forged. | ❌ | Default secret in source |
| US-SEC-02 | As a system, I want to rate-limit login attempts so that brute-force attacks are prevented. | ❌ | Not implemented |
| US-SEC-03 | As a system, I want to log all sensitive operations so that we have an audit trail. | ❌ | Audit log never written |
| US-SEC-04 | As a system, I want to lock accounts after too many failed logins so that attackers are blocked. | ❌ | Not implemented |
| US-SEC-05 | As a system, I want to validate all user inputs so that injection attacks are prevented. | ⚠️ | Some schemas lack validation |
| US-SEC-06 | As a system, I want to use HTTPS so that data is encrypted in transit. | ❌ | Not configured |
| US-SEC-07 | As a system, I want security headers on all responses so that XSS and clickjacking are prevented. | ❌ | Not implemented |

---

## 7. Infrastructure Stories

| ID | Story | Status | Notes |
|----|-------|--------|-------|
| US-INF-01 | As a developer, I want `docker compose up` to start the entire system so that I can develop locally. | ❌ | Only PostgreSQL; app missing |
| US-INF-02 | As a developer, I want the Dockerfile to build successfully so that I can deploy the backend. | ❌ | Build order broken |
| US-INF-03 | As a developer, I want a CI/CD pipeline so that tests run automatically. | ❌ | Not configured |
| US-INF-04 | As an operator, I want database backups so that data is not lost. | ❌ | Not configured |
| US-INF-05 | As an operator, I want health checks on all services so that I can monitor uptime. | ⚠️ | DB only |
| US-INF-06 | As an operator, I want production-grade logging and monitoring so that I can debug issues. | ⚠️ | Structured logs; no aggregation |
