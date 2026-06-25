# Use Cases — Acuity LMS AI

**Generated:** 2026-06-25
**Legend:** ✅ Complete, ⚠️ Partial/Broken, ❌ Missing, 🔜 Planned

---

## UC-1: Student Registration & Onboarding

**Actors:** Student
**Preconditions:** None
**Postconditions:** Student account exists, enrolled in at least one course

**Flow:**
1. Student navigates to `/login`
2. Student fills registration form (name, email, password, role=STUDENT)
3. System validates and creates account
4. Student is redirected to onboarding
5. Student selects grade, subjects, interests
6. System lists available published courses
7. Student selects a course and enrolls
8. System generates course schedule
9. Student is redirected to dashboard

**Status:** ⚠️ Partial
- Steps 1-3: ✅ Complete
- Step 4-5: ⚠️ Onboarding page exists but preferences are not stored on backend
- Step 6-7: ⚠️ Auto-enrolls in first course; no course selection UI
- Step 8: ✅ Schedule generated
- **Issues:** Errors during enrollment are silently swallowed (step 7)

---

## UC-2: Student Login

**Actors:** Student
**Preconditions:** Student has registered
**Postconditions:** Student has valid JWT tokens

**Flow:**
1. Student navigates to `/login`
2. Student enters email and password
3. System validates credentials
4. System issues access token (30 min) and refresh token (7 days)
5. Student is redirected to their role-based dashboard

**Status:** ✅ Complete
- **Issues:** No rate limiting (brute-force vulnerability). No "forgot password?" link on page.

---

## UC-3: AI Tutor Session — First Interaction

**Actors:** Student
**Preconditions:** Student is enrolled in a course, has an active session
**Postconditions:** Student receives teaching content and a question

**Flow:**
1. Student opens AI Tutor page
2. System creates/loads teaching session
3. System loads current concept to teach
4. System retrieves student's learning memories
5. AI generates teaching explanation
6. AI generates a question
7. Student reads content and sees question
8. System persists conversation to database

**Status:** ⚠️ Partial
- Steps 1-3: ✅ Complete
- Step 4: ⚠️ DB memory retrieval works; Qdrant semantic search broken
- Step 5-6: ⚠️ Generation works but no guardrails, no error handling
- Step 7-8: ✅ Complete
- **Issues:** No retry on AI failure. No error handling. Guardrails not wired. Mock responses without API key.

---

## UC-4: AI Tutor Session — Response Evaluation

**Actors:** Student
**Preconditions:** Student has received a question (UC-3)
**Postconditions:** Student receives evaluation, diagnosis, and next action

**Flow:**
1. Student submits answer to question
2. System loads session and current state
3. AI evaluates response (score + feedback)
4. AI diagnoses understanding (correct / misconception / knowledge gap)
5. System determines next action (reteach / example / continue / prerequisite)
6. If reteach: AI re-explains the concept
7. If example: AI provides an example
8. If continue: AI marks concept as complete
9. System updates mastery score
10. System stores memory entry
11. If misconception detected: persists misconception record

**Status:** ⚠️ Partial
- Steps 1-2: ✅ Complete
- Step 3: ⚠️ Works but expected_answer is hardcoded placeholder
- Step 4: ⚠️ Works but diagnosis prompt lacks actual expected answer
- Step 5: ⚠️ Graph crashes on unrecognized action (no default edge)
- Steps 6-8: ⚠️ Work but no guardrails on any output
- Step 9: ✅ Complete
- Step 10-11: ✅ Complete
- **Issues:** No error handling across all nodes. Guardrails disconnected. Mock-only without API key.

---

## UC-5: Take Assessment

**Actors:** Student
**Preconditions:** Student is enrolled in a course with exercises
**Postconditions:** Attempts recorded, mastery updated

**Flow:**
1. Student navigates to `/student/assessment`
2. System loads exercises for current concept
3. Student answers each question
4. System records each attempt with score
5. System updates mastery after all attempts
6. Student sees assessment results

**Status:** ❌ Broken
- Step 1-2: ⚠️ Loads exercises but only from first concept
- Step 3-4: ❌ **All questions mark first option as correct** (correctIndex: 0)
- Step 4: ⚠️ Sequential submissions (not parallel, slow)
- Step 5: ✅ Mastery updates work
- **Issues:** CRITICAL bug in assessment logic. Sequential submissions are slow.

---

## UC-6: View Progress & Mastery

**Actors:** Student
**Preconditions:** Student has some learning activity
**Postconditions:** Student sees progress data

**Flow:**
1. Student navigates to `/student/progress`
2. System loads mastery overview
3. System loads course curriculum with mastery levels
4. Student sees overall mastery, weak concepts, strong concepts
5. Student sees detailed concept breakdown

**Status:** ⚠️ Partial
- Step 1-3: ✅ Complete
- Step 4-5: ⚠️ Progress updates are broken (404 on PATCH)
- **Issues:** CRITICAL: progress update endpoint always returns 404

---

## UC-7: Parent Dashboard — Monitor Student

**Actors:** Parent
**Preconditions:** Parent is linked to at least one student
**Postconditions:** Parent sees student data

**Flow:**
1. Parent logs in
2. System loads parent dashboard with linked students
3. Parent sees overview cards (progress, mastery, sessions)
4. Parent clicks on a student for detail
5. Parent sees courses, mastery breakdown, misconceptions, session history
6. Parent can generate AI reports
7. Parent can view insights and recommendations

**Status:** ⚠️ Partial
- Step 1: ✅ Complete
- Step 2-7: ⚠️ All parent pages show first student only
- Step 4: ⚠️ Non-functional buttons (Download Report)
- **Issues:** No multi-child support. Several buttons lack onClick handlers.

---

## UC-8: Admin — Content Ingestion

**Actors:** Admin
**Preconditions:** Admin is logged in
**Postconditions:** New curriculum is published

**Flow:**
1. Admin uploads a document (TXT, PDF, DOCX)
2. System validates and stores file
3. AI extracts structured content from document
4. Admin reviews extraction results
5. AI generates full curriculum (Course → Modules → Lessons → Concepts)
6. Admin reviews generated curriculum in draft state
7. Admin approves draft
8. Admin publishes course (visible to students)

**Status:** ⚠️ API Only
- All steps: ✅ Backend API exists for all steps
- Frontend: ❌ No frontend UI for any step
- **Issues:** No admin content management interface in the frontend

---

## UC-9: Password Reset

**Actors:** Any user
**Preconditions:** User has registered with an email
**Postconditions:** User can log in with new password

**Flow:**
1. User clicks "Forgot Password" on login page
2. User enters email
3. System generates reset token and sends email with reset link
4. User clicks link (carries token)
5. User enters new password
6. System validates token and updates password
7. System revokes all existing sessions

**Status:** ❌ Broken
- Step 1: ❌ No "Forgot Password" link on login page
- Step 2-3: ❌ API generates token but never sends email (no SMTP infrastructure)
- Step 4-7: ✅ Reset logic works (if token could be delivered)
- **Issues:** CRITICAL: password reset is non-functional end-to-end

---

## UC-10: Teacher — Curriculum Creation (New)

**Actors:** Teacher
**Preconditions:** Teacher is logged in
**Postconditions:** New curriculum is ready for students

**Flow:**
1. Teacher navigates to curriculum management
2. Teacher creates a new course (title, description, subject, grade)
3. Teacher adds modules with ordering
4. Teacher adds lessons to modules
5. Teacher adds concepts to lessons
6. Teacher adds content, exercises, examples to concepts
7. Teacher adds learning objectives to lessons
8. Teacher sets prerequisite relationships
9. Teacher publishes course

**Status:** ❌ Missing (entire role)
- No TEACHER role in auth system
- No teacher frontend pages
- No teacher-specific API endpoints
- Curriculum CRUD is admin-only

---

## UC-11: Teacher — Student Monitoring (New)

**Actors:** Teacher
**Preconditions:** Teacher is assigned students
**Postconditions:** Teacher has visibility into student performance

**Flow:**
1. Teacher navigates to student roster
2. Teacher sees list of assigned students
3. Teacher clicks on a student
4. Teacher sees student's courses, progress, mastery, misconceptions
5. Teacher sees AI-generated intervention recommendations
6. Teacher can take action (message, assign extra practice)

**Status:** ❌ Missing (entire role)

---

## UC-12: Admin — Analytics Dashboard

**Actors:** Admin
**Preconditions:** System has users and activity
**Postconditions:** Admin understands platform usage

**Flow:**
1. Admin navigates to `/admin/analytics`
2. System loads dashboard statistics
3. Admin sees:
   - Total users by role
   - Active sessions
   - Course counts
   - Enrollment numbers
   - Mastery distribution
   - Time-series trends (enrollments over time, activity over time)
4. Admin can filter by date range

**Status:** ⚠️ Partial
- Steps 1-2: ✅ Numbers are loaded
- Step 3: ⚠️ Only static numbers shown; no time-series, no charts
- Step 4: ❌ No filtering
- **Issues:** No visualization. Arbitrary metric mappings (courses→percentage).

---

## UC-13: User Logout

**Actors:** Any authenticated user
**Preconditions:** User is logged in
**Postconditions:** User is logged out, tokens revoked

**Flow:**
1. User clicks logout button
2. System calls logout API
3. System revokes all user's refresh tokens
4. System clears local tokens
5. User is redirected to landing page

**Status:** ✅ Complete
- No confirmation dialog (instant logout)
- Topbar may not update reactively after logout

---

## UC-14: Knowledge Graph — Prerequisite Navigation

**Actors:** Student, AI System
**Preconditions:** Knowledge graph has prerequisite edges
**Postconditions:** System can recommend prerequisite concepts

**Flow:**
1. Teacher/Admin creates prerequisite edges between concepts
2. AI system detects student struggling with concept
3. AI looks up prerequisites via knowledge graph
4. AI recommends learning prerequisites first
5. Student is guided to prerequisite concept

**Status:** ⚠️ Partial
- Step 1: ✅ API exists
- Step 2-3: ⚠️ Works but N+1 query in get_prerequisites
- Step 4-5: ⚠️ AI can recommend prerequisites but has only basic adaptation

---

## Summary

| Use Case | Status | Priority |
|----------|--------|----------|
| UC-1: Student Registration & Onboarding | ⚠️ Partial | P0 |
| UC-2: Student Login | ✅ Complete | P0 |
| UC-3: AI Tutor First Interaction | ⚠️ Partial | P0 |
| UC-4: AI Tutor Response Evaluation | ⚠️ Partial | P0 |
| UC-5: Take Assessment | ❌ Broken | P0 |
| UC-6: View Progress & Mastery | ⚠️ Partial | P0 |
| UC-7: Parent Dashboard | ⚠️ Partial | P0 |
| UC-8: Admin Content Ingestion | ⚠️ API only | P0 |
| UC-9: Password Reset | ❌ Broken | P0 |
| UC-10: Teacher Curriculum Creation | ❌ Missing | P1 |
| UC-11: Teacher Student Monitoring | ❌ Missing | P1 |
| UC-12: Admin Analytics Dashboard | ⚠️ Partial | P0 |
| UC-13: User Logout | ✅ Complete | P0 |
| UC-14: Knowledge Graph Prerequisite | ⚠️ Partial | P1 |
