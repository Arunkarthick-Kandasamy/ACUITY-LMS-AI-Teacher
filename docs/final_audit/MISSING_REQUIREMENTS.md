# MISSING REQUIREMENTS — Acuity LMS AI

**Generated:** 2026-06-25
**Analysis:** Requirements inferred from existing code, frontend pages, API contracts, and standard LMS business logic.

---

## 1. Role: Teacher (Entirely Missing)

The most significant missing role. The system has Student, Parent, and Admin roles but no Teacher role. In an LMS, teachers are the primary content creators and student supervisors.

### Missing Features

| Requirement | Rationale | Complexity |
|-------------|-----------|------------|
| Teacher registration/login with TEACHER role | Cannot onboard teachers | 1 day |
| Teacher dashboard — overview of assigned students | No dashboard | 2 days |
| Student roster management — assign students to teachers | No teacher-student relationship | 3 days |
| Course content creation UI — create/edit modules, lessons, concepts | Content ingestion exists but admin-only | 5 days |
| Student progress monitoring — view all students' mastery, progress, pacing | No teacher view of student data | 3 days |
| Misconception review panel — see all students' misconceptions | Misconception model exists, no teacher UI | 2 days |
| Intervention recommendations — AI suggests which students need help | No intervention system | 3 days |
| Grade/attempt review — see student answers and scores | Attempt model exists, no review UI | 2 days |
| Content draft management — review and approve AI-generated content | Draft workflow exists but admin-only | 2 days |

---

## 2. Core LMS Features Missing

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Email verification** on registration | No email infrastructure at all | HIGH |
| **Password reset email** — actual sending | Service generates token but never sends email | CRITICAL |
| **Rate limiting** on auth endpoints | Constants defined but no middleware | HIGH |
| **Account lockout** after failed login attempts | No failed-attempt tracking | HIGH |
| **Audit logging** — all CRUD operations produce audit records | Model exists, no code writes to it | HIGH |
| **Soft delete** support | Repository does hard deletes only | MEDIUM |
| **Pagination** on list endpoints | No cursor/offset pagination; `find()` has `limit=100` | MEDIUM |
| **Search/filter** on users, courses, enrollments | Admin students page has decorative search | MEDIUM |
| **Data export** (CSV, PDF) for reports | Report model has `pdf_url` but no generation | MEDIUM |
| **Notification system** (in-app, email) | No notification model or service | MEDIUM |
| **Multi-language/internationalization** | All text is hardcoded English | LOW |
| **Dark mode / theme toggle** | Only one theme | LOW |

---

## 3. AI Teacher Missing Features

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Guardrails actually wired into graph** | GuardrailService exists but is never called | CRITICAL |
| **Proper error handling + retry** in all nodes | No try/except anywhere | CRITICAL |
| **Working semantic memory search** | Qdrant embedding generation is broken | HIGH |
| **Expected answer in evaluation prompt** | Prompt doesn't include ground truth | HIGH |
| **Memory context in question generation** | PROMPT_QUESTION only includes teaching_content | MEDIUM |
| **Adaptive teaching** (adjust based on student model) | Only reteach/example/continue; no real adaptation | HIGH |
| **Streaming responses** (SSE/WebSocket) | All responses are blocking HTTP | MEDIUM |
| **Conversation history management** (summarize/prune) | History grows unbounded | MEDIUM |
| **Mastery-based progression** (don't teach concept if mastered) | No check before teaching | MEDIUM |
| **Bayesian Knowledge Tracing / IRT** | Simple threshold-based mastery only | LOW |
| **Personalized question difficulty** | All questions generated fresh; no difficulty levels | MEDIUM |
| **Multi-turn conversation support** | Graph requires separate API call per turn | MEDIUM |

---

## 4. Parent Dashboard Missing Features

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Multi-child support** — student selector for parents with 2+ children | All parent pages show first student only | HIGH |
| **Weekly/daily learning activity timeline** | No activity timeline view | MEDIUM |
| **Comparative analytics** (child vs class/peers) | No comparison data | LOW |
| **Notification preferences** (how often to get reports) | No notification system | LOW |
| **Downloadable PDF reports** | Button exists, no handler | MEDIUM |
| **AI-recommended learning activities** | No recommendations API consumed | MEDIUM |

---

## 5. Admin Dashboard Missing Features

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Time-series analytics** (enrollments over time, active users) | Only static current numbers | HIGH |
| **User management CRUD** (create/edit/disable users) | No user creation/edit endpoints | HIGH |
| **Curriculum editor UI** (drag-and-drop course builder) | No curriculum management page | HIGH |
| **Content upload UI** (file upload, review AI-generated content) | Content ingestion API exists, no frontend | HIGH |
| **System health dashboard** (DB status, AI status, error rates) | Health endpoint only checks DB | MEDIUM |
| **Audit log viewer** (search/filter user actions) | Audit log never written | HIGH |
| **Enrollment management** (manually enroll/unenroll students) | No admin enrollment UI | MEDIUM |
| **System configuration UI** (env vars, feature flags) | No config management | LOW |

---

## 6. Student Experience Missing Features

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Course catalog/browse** with search and filter | No course listing page beyond enrollment | MEDIUM |
| **Goal setting** (weekly lesson targets) | No goal tracking | LOW |
| **Gamification** (badges, streaks, achievements) | No gamification system | LOW |
| **Notes/annotations** on lessons | No note-taking | LOW |
| **Bookmarking/favorites** | No bookmarking | LOW |
| **Mobile responsive design** | Layout breaks below 768px | MEDIUM |

---

## 7. Infrastructure Missing

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **CI/CD pipeline** (GitHub Actions) | No pipeline files | HIGH |
| **Production Docker Compose** (backend + frontend + DB + Redis + Qdrant) | Only PostgreSQL in compose | HIGH |
| **Database backup automation** | No backup script | HIGH |
| **Health check endpoint** for all upstream services | Only DB check | MEDIUM |
| **Rate limiting middleware** | No middleware, no integration | HIGH |
| **Security headers** (CSP, HSTS, X-Frame-Options) | CORS configured, no security headers | MEDIUM |
| **API versioning strategy** | `api_prefix = "/api/v1"` is hardcoded | LOW |
| **Frontend error tracking** (Sentry, etc.) | No error tracking | MEDIUM |

---

## 8. Testing Missing

| Requirement | Evidence | Priority |
|-------------|----------|:--------:|
| **Database-backed tests** | All tests use mocks | CRITICAL |
| **HTTP API tests** for all modules | Only 4 modules have HTTP tests | HIGH |
| **Frontend tests** (unit + component) | No test framework installed | HIGH |
| **E2E tests** (critical student journey) | No E2E tests | MEDIUM |
| **Performance/load tests** | No perf testing | LOW |
| **Security tests** (auth bypass, injection) | No security testing | HIGH |
