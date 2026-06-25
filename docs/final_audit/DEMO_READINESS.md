# DEMO READINESS — Acuity LMS AI

**Generated:** 2026-06-25
**Assessment:** NOT DEMO READY — 7 CRITICAL issues would cause demo failures or embarrassment

---

## 1. Demo Readiness Score: 3 / 10

| Criterion | Score | Notes |
|-----------|:-----:|-------|
| Can a new user register and login? | ✅ Yes | Registration and login work |
| Can a student take a lesson? | ⚠️ Partially | AI tutor works but has issues |
| Can a student take an assessment? | ❌ No | All answers marked first-option correct |
| Can a parent view student progress? | ⚠️ Partially | First student only; fake dashboard metrics |
| Can an admin view analytics? | ⚠️ Partially | Static numbers; no charts |
| Can all pages load without errors? | ❌ No | No route guards cause blank data |
| Does the UI look professional? | ✅ Yes | Tailwind design system is polished |
| Can the AI teacher hold a conversation? | ⚠️ Partially | Works but mock-only; no real Gemini |
| Can a user reset their password? | ❌ No | Email never sent |
| Does the demo survive a page refresh? | ❌ No | authStore not persisted |
| Are error states handled gracefully? | ❌ No | Silent catches, 500 errors propagate |
| Are loading states shown? | ✅ Mostly | Spinners present on most pages |

---

## 2. Demo Killers (Issues That Would Ruin a Demo)

### K1: Assessment Always Shows Wrong Results

**File:** `acuity-frontend/src/pages/student/AssessmentPage.tsx:35`
**What happens:** Every question marks the first option as correct. If a student selects any non-first answer, it's marked wrong. If they select the first answer, it's marked correct regardless of actual content.

**Demo impact:** **Catastrophic.** Client would immediately notice all questions have the same correct answer. Undermines all credibility.

**Fix:** Map exercise data's correct answer to the options array and use `correctIndex` from the actual response (5 min fix).

---

### K2: Page Refresh Logs the User Out

**File:** `acuity-frontend/src/store/authStore.ts:8-13`
**What happens:** `currentUser` is initialized to `null`. On browser refresh, the app loses the user's identity. The token exists in localStorage but the store doesn't hydrate from it.

**Demo impact:** **Very bad.** If you refresh the page to show something, the UI reverts to logged-out state. Must log in again.

**Fix:** On store initialization, check `localStorage` for a stored user object or call a `/users/me` endpoint with the existing token.

---

### K3: Any User Can Access Any Page

**File:** `acuity-frontend/src/router/index.tsx:32-63`
**What happens:** No route guards. Someone can navigate to `/admin/dashboard` without being logged in. Parts of pages may load with empty data; others may show error states.

**Demo impact:** **Confusing.** If the client navigates to the wrong URL, they see broken pages. If they notice they can access restricted data, they'll question security.

**Fix:** Add route guards that redirect to `/login` or appropriate dashboard based on auth/role.

---

### K4: AI Tutor Uses Mock Responses

**File:** `Backend/app/ai/services/gemini.py:39-40`
**What happens:** If `GEMINI_API_KEY` is not configured, the AI teacher silently returns hardcoded mock responses. The teaching content is generic ("Let's learn about variables..."), evaluations always give score 0.5.

**Demo impact:** **Moderate to severe.** The demo will function but the AI won't seem intelligent. Responses won't relate to actual student input. The client will see canned, generic answers.

**Fix:** Configure a real Gemini API key for the demo. Or improve mock responses to be more contextual.

---

### K5: Student Dashboard Shows Fake Metrics

**File:** `acuity-frontend/src/pages/student/StudentDashboard.tsx:77-82`
**What happens:** "Parameter scores" (correctness, response time, retries, skips) are not from the API. They're invented: `Math.round(overallMastery * 0.9/0.8/0.85/0.9)`.

**Demo impact:** **Moderate.** If a client asks "what are these scores based on?", the answer would be "nothing." If they enter a demo with no data, the dashboard looks empty.

**Fix:** Either implement real parameter tracking on the backend or hide these metrics from the dashboard.

---

### K6: Password Reset Fails Silently

**File:** `Backend/app/auth/service.py:136-158`
**What happens:** If a client tries to reset their password, the API returns "If the email exists, a reset link has been sent" — but no email is actually sent. The token is logged to console only.

**Demo impact:** **Moderate.** Client tries forgot-password flow, never receives email, feature appears broken. The API response is deceptive.

**Fix:** For demo purposes, return the reset token in the API response (with a clear "DEMO MODE" indicator) so the flow can be completed manually.

---

### K7: No Seed Data — Demo System Is Empty

**File:** `Backend/scripts/` (no seed script exists)
**What happens:** Fresh startup has no admin user, no courses, no enrollments, no reports. The entire system is empty.

**Demo impact:** **Severe.** Client registers, logs in, and sees a blank dashboard. No courses to enroll in. No AI to interact with. Nothing to demo.

**Fix:** Create `scripts/demo_seed.py` that populates the system with demo data.

---

## 3. Demo Experience by Role

### Student Demo Flow

| Step | Status | Issues |
|------|--------|--------|
| 1. Register as student | ✅ Works | — |
| 2. Log in | ✅ Works | — |
| 3. Complete onboarding | ⚠️ Partially | Only enrolls in first course; errors silently swallowed |
| 4. View dashboard | ⚠️ Partially | Fake parameter scores; only first course shown |
| 5. View learning path | ⚠️ Partially | No empty state if no courses |
| 6. Open AI Tutor | ⚠️ Partially | Mock responses if no API key; no endSession on unmount |
| 7. Take assessment | ❌ Broken | All answers marked first-option correct |
| 8. View progress | ⚠️ Partially | Broken update (404 on progress patch) |
| 9. View profile | ✅ Works | Read-only |

### Parent Demo Flow

| Step | Status | Issues |
|------|--------|--------|
| 1. Register as parent | ✅ Works | — |
| 2. Log in | ✅ Works | — |
| 3. View parent dashboard | ⚠️ Partially | First child only; non-functional buttons |
| 4. View student detail | ⚠️ Partially | Arbitrary metrics; non-functional download |
| 5. View reports | ⚠️ Partially | First child only; non-functional download |
| 6. View insights | ⚠️ Partially | Static recommendations |

### Admin Demo Flow

| Step | Status | Issues |
|------|--------|--------|
| 1. Register as admin | ✅ Works | — |
| 2. Log in | ✅ Works | — |
| 3. View admin dashboard | ⚠️ Partially | Arbitrary metric mappings |
| 4. Manage students | ⚠️ Partially | Search non-functional; no pagination; no create/edit |
| 5. View analytics | ⚠️ Partially | Static numbers only; no charts |

---

## 4. Quick Fixes for Demo Readiness (1-2 Days)

These fixes would make the system presentable enough for a controlled demo:

| Fix | Effort | Impact |
|-----|--------|--------|
| Create demo seed script | 4 hours | Populates system with test data |
| Set real Gemini API key | 15 min | AI teacher works intelligently |
| Fix assessment correctIndex bug | 5 min | Assessments produce correct results |
| Add basic route guards | 2 hours | Prevents broken page access |
| Persist authStore across refresh | 1 hour | Survives page reload |
| Hide fake parameter scores | 15 min | Removes misleading dashboard metrics |
| Return reset token in API response (demo mode) | 30 min | Password reset demo-able |
| **Total** | **~8 hours** | |

---

## 5. Verdict

**Acuity LMS AI is NOT demo ready.**

While the UI looks professional and the architecture is sound, at least 4 issues (K1, K2, K4, K7) would cause visible failures or confusion in any uncontrolled demo. With approximately **8 hours of targeted fixes**, the system could reach a "controlled demo" state where a presenter guides the client through pre-scripted scenarios.

**For an unattended/take-home demo, significantly more work is required** (primarily proper error handling, loading states, and seeded data across all pages).

---

## 6. Demo Preparation Checklist

- [ ] Create demo seed script with admin, parent, student, teacher accounts
- [ ] Create demo course with modules, lessons, concepts, exercises, examples
- [ ] Configure real Gemini API key
- [ ] Fix assessment `correctIndex: 0`
- [ ] Add basic route guards to prevent blank pages
- [ ] Persist authStore across refresh
- [ ] Hide or fix fake parameter scores on student dashboard
- [ ] Return reset token in forgot-password response
- [ ] Add minimal empty states to learning path page
- [ ] Test the full student journey end-to-end
- [ ] Test the full parent journey end-to-end
- [ ] Test the full admin journey end-to-end
- [ ] Prepare demo script with key talking points
