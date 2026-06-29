# Business Requirements Document (BRD)
## ACUITY LMS — AI-Powered Learning Management System

**Document Version:** 1.0  
**Status:** Draft  
**Date:** 2026-06-28  
**Based On:** *"The AI-Powered Learning Management System — A Complete User Journey Story"*

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives](#2-business-objectives)
3. [Scope & Boundaries](#3-scope--boundaries)
4. [User Personas](#4-user-personas)
5. [Module-Wise Requirements & Use Cases](#5-module-wise-requirements--use-cases)
   - 5.1 [User Registration & Authentication Module](#51-user-registration--authentication-module)
   - 5.2 [Student Dashboard Module](#52-student-dashboard-module)
   - 5.3 [Course Discovery & Enrollment Module](#53-course-discovery--enrollment-module)
   - 5.4 [Course & Curriculum Management Module](#54-course--curriculum-management-module)
   - 5.5 [AI Tutor Module](#55-ai-tutor-module)
   - 5.6 [Assessment & Mastery Module](#56-assessment--mastery-module)
   - 5.7 [Knowledge Graph & Learning Path Module](#57-knowledge-graph--learning-path-module)
   - 5.8 [Teacher Dashboard Module](#58-teacher-dashboard-module)
   - 5.9 [Parent Dashboard Module](#59-parent-dashboard-module)
   - 5.10 [Administrator Module](#510-administrator-module)
   - 5.11 [Institutional / School District Module](#511-institutional--school-district-module)
   - 5.12 [Gamification & Achievement Module](#512-gamification--achievement-module)
   - 5.13 [Notification & Communication Module](#513-notification--communication-module)
   - 5.14 [Payment & Monetization Module](#514-payment--monetization-module)
   - 5.15 [Content Ingestion & Upload Module](#515-content-ingestion--upload-module)
   - 5.16 [Safety, Privacy & Parental Controls Module](#516-safety-privacy--parental-controls-module)
   - 5.17 [Offline & Accessibility Module](#517-offline--accessibility-module)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Data & Reporting Requirements](#7-data--reporting-requirements)
8. [Assumptions & Dependencies](#8-assumptions--dependencies)
9. [Glossary](#9-glossary)

---

## 1. Executive Summary

The ACUITY LMS is an AI-powered learning management system designed to provide personalized, 24/7 tutoring and learning experiences for students across all age groups. The platform connects students, teachers, parents, and institutions in a unified ecosystem.

**Core Value Proposition:**
- Students get an AI tutor that adapts to their learning style, pace, and knowledge level
- Teachers get powerful analytics and tools to scale their impact beyond the classroom
- Parents get visibility and actionable insights into their child's learning journey
- Institutions get measurable improvements in learning outcomes, retention, and operational efficiency

**Key Outcomes (from story projections):**
- 87% average course completion rate (vs. 20% industry average)
- +15 to +18 percentile points improvement in standardized test scores
- 67% improvement in parent engagement
- 70% reduction in teacher grading time
- Significant cost savings vs. traditional tutoring ($1.8M/year for a 15,000-student district)

---

## 2. Business Objectives

| # | Objective | Success Metric | Priority |
|---|-----------|----------------|----------|
| 1 | Deliver personalized, adaptive AI tutoring at scale | 4.5+/5.0 student satisfaction; 85%+ quiz completion scores | Critical |
| 2 | Enable teachers to create, publish, and monetize courses | 50,000+ courses created in Year 1; $410M paid to teachers | High |
| 3 | Provide parents with real-time visibility into learning | 90%+ parent dashboard monthly active usage | High |
| 4 | Achieve institutional adoption in K-12 districts | 1,200+ schools; 150,000+ institutional students in Year 1 | High |
| 5 | Ensure student safety and wellness | 0 data breaches; < 0.1% harmful content incidents | Critical |
| 6 | Maintain platform reliability at scale | 99.9% uptime; sub-200ms API response times | Critical |
| 7 | Democratize access to quality education | 40%+ users on free tier; support for 10+ languages | Medium |

---

## 3. Scope & Boundaries

### In Scope
- Student registration, profile management, and authentication
- AI-powered conversational tutoring with adaptive learning paths
- Course creation, curriculum management, and content packaging
- Assessment authoring (quizzes, exercises, mastery checks)
- Teacher dashboard with student-level and course-level analytics
- Parent dashboard with progress reports, notifications, and controls
- Parent-student linking and multi-child management
- Institutional / school district management with role-based access
- Gamification (streaks, badges, certificates, achievements)
- Notification engine (email, in-app, push)
- Content ingestion (PDF, DOCX, TXT parsing)
- Knowledge graph for prerequisite mapping and learning paths
- Safety controls (daily usage limits, break reminders, sleep mode)
- COPPA compliance and data privacy enforcement
- Multi-language interface support
- Payment processing for course purchases and teacher payouts
- Audit logging for all critical operations

### Out of Scope (Future Phases)
- Live one-on-one human tutoring marketplace
- Mobile native applications (Phase 2)
- AI-generated video content creation
- VR/AR-based learning experiences
- Blockchain-based credential verification
- Custom white-label solutions for enterprises

---

## 4. User Personas

### Student (e.g., Maya, age 13)
- **Primary Goal:** Learn subjects at own pace with personalized support
- **Pain Points:** Classroom lectures move too fast/slow; embarrassed to ask questions; traditional materials don't adapt
- **Success Criteria:** Understanding concepts, improved grades, restored confidence

### Parent (e.g., Rosa, working mother)
- **Primary Goal:** Stay informed about child's progress without micromanaging
- **Pain Points:** Can't help with homework; feels disconnected from child's education; only hears about problems at parent-teacher conferences
- **Success Criteria:** Regular, actionable reports; ability to set boundaries and controls; confidence child is on track

### Teacher / Course Creator (e.g., Sarah Chen, 7th-grade math teacher)
- **Primary Goal:** Scale teaching impact; earn supplemental income; identify struggling students early
- **Pain Points:** Grading consumes 50%+ of teaching time; 35+ student classes make individual attention impossible; limited tools for personalized instruction
- **Success Criteria:** At-risk student identification; reduced grading workload; course monetization

### Administrator / School Principal (e.g., Mr. Tanaka)
- **Primary Goal:** Improve school-wide learning outcomes and teacher retention
- **Pain Points:** Inconsistent teacher quality; budget constraints for tutoring; difficulty tracking district-wide progress
- **Success Criteria:** Test score improvements; teacher satisfaction; cost savings; equitable access

### System Administrator (Platform Admin)
- **Primary Goal:** Ensure platform reliability, security, and compliance
- **Pain Points:** Scaling infrastructure; content quality moderation; regulatory compliance across jurisdictions
- **Success Criteria:** 99.9% uptime; zero breaches; automated quality enforcement

---

## 5. Module-Wise Requirements & Use Cases

---

### 5.1 User Registration & Authentication Module

**Module Description:** Handles user onboarding, identity verification, role assignment, and secure session management.

#### Use Case UC-01: Student Registration

| Element | Description |
|---------|-------------|
| **Use Case Name** | Register New Student Account |
| **Actor(s)** | Unregistered student |
| **Trigger** | Student clicks "Get Started" or "Sign Up" |
| **Pre-conditions** | 1. Student is not logged in 2. Student is 13 years of age or older (or has parental consent mechanism available) |
| **Post-conditions** | 1. Student account created in `users` table with role = "student" 2. Verification email sent 3. Session created; student redirected to onboarding/dashboard |
| **Main Flow** | 1. System displays registration form with minimal required fields 2. Student enters: email, name, date of birth, country, preferred language, password 3. System validates input format 4. System checks email uniqueness 5. System hashes password (bcrypt) 6. System creates user record 7. System generates verification token 8. System sends verification email 9. System creates authenticated session 10. System redirects to personalized dashboard |
| **Alternative Flows** | **A1: Email already registered** — Prompt for login or password reset. **A2: Under-age without consent** — Block registration; display parent consent flow. **A3: Verification email bounces** — Allow resend; flag account for manual review. **A4: Social SSO** — Future support for Google/Microsoft/Apple OAuth. |
| **Business Rules** | BR-01: Minimum 8 characters password, 1 uppercase, 1 number. BR-02: School email domains may be validated for institutional users. BR-03: Date of birth stored but never displayed publicly. BR-04: Email verification required within 24 hours or account soft-deleted. |
| **Acceptance Criteria** | 1. Registration completes in < 3 seconds 2. Email arrives within 30 seconds 3. 100% of error states have user-friendly messages 4. Password never stored or logged in plaintext |

#### Use Case UC-02: User Login

| Element | Description |
|---------|-------------|
| **Use Case Name** | Authenticate User |
| **Actor(s)** | Registered user (student, teacher, parent, admin) |
| **Trigger** | User navigates to login page |
| **Pre-conditions** | 1. User has verified account 2. Account not locked/disabled |
| **Post-conditions** | 1. JWT access + refresh tokens issued 2. Last login timestamp updated 3. Failed attempt counter reset |
| **Main Flow** | 1. User provides email + password 2. System validates credentials against hashed password 3. System checks email verification status 4. System generates JWT access token (short-lived, 15 min) 5. System generates refresh token (long-lived, 7 days) 6. System returns tokens to client 7. Client stores tokens (httpOnly cookie recommended) 8. User redirected to role-appropriate dashboard |
| **Alternative Flows** | **A1: Invalid credentials** — Increment failed attempt counter; display "Invalid email or password". Lock account after 5 failed attempts for 30 minutes. **A2: Email not verified** — Display resend verification prompt. **A3: Account locked** — Display unlock instructions with cooldown timer. |

#### Use Case UC-03: Password Reset

| Element | Description |
|---------|-------------|
| **Use Case Name** | Reset Forgotten Password |
| **Actor(s)** | Registered user |
| **Trigger** | User clicks "Forgot Password" |
| **Pre-conditions** | User has verified email address |
| **Post-conditions** | 1. Password reset token generated and stored 2. Reset email sent 3. Password updated on confirmation |
| **Main Flow** | 1. User enters email 2. System generates cryptographically secure reset token (valid 1 hour) 3. System sends email with reset link 4. User clicks link 5. System validates token 6. User enters new password 7. System hashes and stores new password 8. System invalidates all existing sessions 9. Confirmation displayed |
| **Business Rules** | BR-05: Reset token single-use only. BR-06: Token expires after 60 minutes. BR-07: Cannot reuse last 3 passwords. |

#### Use Case UC-04: Parent-Student Linking

| Element | Description |
|---------|-------------|
| **Use Case Name** | Link Parent to Student Account |
| **Actor(s)** | Parent, Student |
| **Trigger** | Parent registers and enters child's linking code |
| **Pre-conditions** | 1. Student account exists 2. Parent account exists 3. Student has generated a linking code from their profile settings 4. Student has consented to the link (opt-in) |
| **Post-conditions** | 1. `parent_student_links` record created 2. Parent gains access to student's progress data, reports, and controls 3. Student notified of linked parent |
| **Main Flow** | 1. Student generates linking code from Settings → Parent Access 2. Student shares code with parent 3. Parent enters code in their dashboard 4. System validates code (not expired, correct student) 5. System creates link with "approved" status 6. System notifies both parties 7. Parent redirected to student progress dashboard |
| **Business Rules** | BR-08: Linking code expires in 48 hours. BR-09: Max 2 parents linked per student. BR-10: Parent can unlink at any time. Student must re-consent for re-link. BR-11: One parent account can link to multiple children (up to 10). |

---

### 5.2 Student Dashboard Module

**Module Description:** The primary landing page for students after login, providing a personalized overview of their learning journey.

#### Use Case UC-05: View Personalized Dashboard

| Element | Description |
|---------|-------------|
| **Use Case Name** | View Student Learning Dashboard |
| **Actor(s)** | Student |
| **Trigger** | Student logs in or clicks "Dashboard" |
| **Pre-conditions** | 1. Student logged in 2. Student enrolled in at least one course (or newly registered) |
| **Post-conditions** | Dashboard displayed with personalized data |
| **Main Flow** | 1. System retrieves student's enrolled courses with progress percentages 2. System retrieves current streak count 3. System retrieves recent achievements/unlocked badges 4. System retrieves recommended next actions (continue course, take quiz, review struggling topic) 5. System retrieves any unread notifications 6. System displays: course cards with progress bars, streak counter, achievement badges, "Continue Learning" quick action, recommended courses section, notifications preview 7. System caches dashboard data for 60 seconds |
| **Business Rules** | BR-12: "Recommended for you" uses collaborative filtering + knowledge graph gaps. BR-13: Streak increments when at least one lesson completed per calendar day. BR-14: New users see "Choose your first course" CTA instead of enrolled courses. |

---

### 5.3 Course Discovery & Enrollment Module

**Module Description:** Enables students to search, browse, and enroll in courses across subjects and difficulty levels.

#### Use Case UC-06: Search & Discover Courses

| Element | Description |
|---------|-------------|
| **Use Case Name** | Search and Browse Course Catalog |
| **Actor(s)** | Student (logged in), Guest (limited) |
| **Trigger** | User enters search query or navigates to catalog |
| **Pre-conditions** | (Guest mode) Public catalog accessible without login |
| **Post-conditions** | Search results displayed with relevance ranking |
| **Main Flow** | 1. User enters query in search bar 2. System performs full-text search across course titles, descriptions, topics, and tags 3. System ranks results by: relevance → rating → enrollment count 4. System returns paginated results with: title, thumbnail, teacher name, rating, student count, estimated duration, price (or "Free" badge) 5. System also displays "Popular right now" section and "Recommended for you" section (logged-in users) |
| **Business Rules** | BR-15: Search supports fuzzy matching and typo tolerance. BR-16: "Popular right now" = courses with highest enrollment velocity in last 7 days. BR-17: "Recommended for you" requires at least 3 completed lessons to activate. BR-18: Teachers can mark courses as "featured" (admin-approved). |

#### Use Case UC-07: Enroll in a Course

| Element | Description |
|---------|-------------|
| **Use Case Name** | Enroll Student in Course |
| **Actor(s)** | Student |
| **Trigger** | Student clicks "Start Learning" or "Enroll" on course page |
| **Pre-conditions** | 1. Student logged in 2. Course is published and active 3. Student not already enrolled 4. (If paid) Payment completed |
| **Post-conditions** | 1. `student_course_enrollments` record created 2. Initial learning progress record created 3. Student redirected to lesson 1 or course overview |
| **Main Flow** | 1. System checks enrollment prerequisites (if any required courses not completed, display warning) 2. System creates enrollment record with status = "active" 3. System initializes progress tracker: 0% complete, all lessons "not started" 4. System displays course welcome screen 5. System triggers notification: "Welcome to [Course Name]!" 6. If course is free, immediate enrollment; if paid, redirect to checkout first |
| **Alternative Flows** | **A1: Prerequisites not met** — Display prerequisite course recommendations. Allow override enrollment (student acknowledges). **A2: Course at capacity** — Display waitlist option. **A3: Already enrolled** — Resume from last lesson. **A4: Institutional enrollment blocked** — Enrollment may require teacher/institution approval. |

---

### 5.4 Course & Curriculum Management Module

**Module Description:** Enables teachers to create, structure, and publish courses with a well-defined curriculum hierarchy.

#### Use Case UC-08: Create a Course

| Element | Description |
|---------|-------------|
| **Use Case Name** | Create New Course |
| **Actor(s)** | Teacher, Admin |
| **Trigger** | Teacher clicks "Create New Course" |
| **Pre-conditions** | 1. Teacher has verified account 2. Teacher has completed onboarding/training (optional) |
| **Post-conditions** | 1. Course record created with status = "draft" 2. Teacher redirected to course builder |
| **Main Flow** | 1. Teacher enters: title, short description, full description, subject area, difficulty level (beginner/intermediate/advanced), target age range, estimated duration, course thumbnail, course tags 2. Teacher sets pricing: free, paid (one-time), or subscription 3. Optionally adds: prerequisites, welcome video URL, course syllabus PDF 4. System creates course in draft mode 5. Teacher can then add modules/lessons |
| **Business Rules** | BR-19: Course title must be unique within the platform. BR-20: Description minimum 100 characters. BR-21: At least 1 module with 1 lesson required before publish. BR-22: Admin can mark course as "verified" (trusted creator badge). BR-23: Draft courses saved automatically every 30 seconds. |

#### Use Case UC-09: Structure Curriculum (Modules → Lessons → Concepts)

| Element | Description |
|---------|-------------|
| **Use Case Name** | Create Curriculum Hierarchy |
| **Actor(s)** | Teacher |
| **Trigger** | Teacher opens course builder for an existing draft course |
| **Pre-conditions** | Course exists in draft or published mode |
| **Post-conditions** | Curriculum tree saved |
| **Main Flow** | 1. System displays curriculum tree: Course → Modules → Lessons → Concepts/Content 2. Teacher can: add module (with title, description, ordering), add lesson within module (with title, learning objectives, estimated time), reorder modules/lessons via drag-and-drop, delete modules/lessons (with confirmation) 3. Each lesson can contain: teaching content (text, images, video embeds), exercises, examples, assessment questions, learning objectives 4. Teacher can link concepts to knowledge graph nodes 5. System saves on each action; displays "Unsaved changes" indicator |
| **Business Rules** | BR-24: Max 20 modules per course. BR-25: Max 30 lessons per module. BR-26: Max 10 learning objectives per lesson. BR-27: Curriculum order determines default progression path. |

#### Use Case UC-10: Publish Course

| Element | Description |
|---------|-------------|
| **Use Case Name** | Publish Course for Enrollment |
| **Actor(s)** | Teacher, Admin |
| **Trigger** | Teacher clicks "Publish" from course builder |
| **Pre-conditions** | 1. Course has at least 1 module with 1 lesson 2. Course has title and description 3. (For paid courses) Payment/commission agreement accepted |
| **Post-conditions** | 1. Course status changed to "published" 2. Course visible in search results and catalog 3. Students can enroll |
| **Main Flow** | 1. System validates minimum content requirements 2. System optionally runs automated quality check (content length, no profanity, no empty lessons) 3. System may queue for admin review (if platform policy requires) 4. System sets status = "published" 5. System sends notification to teacher: "Your course is live!" 6. System indexes course for search |
| **Business Rules** | BR-28: Published courses can be unpublished (draft) — existing students retain access. BR-29: Major edits to published courses trigger a "course updated" notification to enrolled students. BR-30: Admin can unlist a course (not searchable but accessible via direct link). |

---

### 5.5 AI Tutor Module

**Module Description:** The core differentiator — an AI-powered conversational tutor that adapts in real-time to each student's knowledge level, learning style, and engagement.

#### Use Case UC-11: Start AI Tutor Session

| Element | Description |
|---------|-------------|
| **Use Case Name** | Initiate AI-Powered Tutoring Session |
| **Actor(s)** | Student |
| **Trigger** | Student clicks "Start Learning with Your AI Tutor" on a lesson |
| **Pre-conditions** | 1. Student enrolled in course 2. Lesson contains teaching content 3. Gemini API key configured (or mock mode for development) 4. Knowledge graph node exists for lesson concepts |
| **Post-conditions** | 1. Teaching session created (`teaching_sessions` record) 2. Lesson progress initialized as "in_progress" 3. Conversational thread started 4. AI adapts initial teaching based on student's knowledge profile |
| **Main Flow** | 1. System creates teaching session with unique ID 2. System loads lesson content (concepts, examples, exercises, objectives) 3. System loads student's knowledge state from mastery records 4. System loads student's learning preferences (visual learner, pace, etc.) 5. AI Tutor (Alex) sends welcome message introducing the lesson 6. AI Tutor begins with diagnostic question to gauge current understanding 7. Student responds 8. AI evaluates response, updates student model 9. AI adapts teaching: if correct → move to next concept / if incorrect → re-explains with visual/alternative approach 10. Each interaction logged for session analytics |
| **Business Rules** | BR-31: Session expires after 60 minutes of inactivity. BR-32: Maximum 3-hour daily AI tutoring time (configurable by parent). BR-33: All session transcripts stored for teacher/parent review. BR-34: AI must identify itself as an AI, never impersonate a human. BR-35: AI must refuse to answer off-topic queries (redirect to lesson content). BR-36: AI must use age-appropriate language (detected from student DOB). BR-37: AI responses must be grounded in the course content + curriculum — not general knowledge only. |

#### Use Case UC-12: AI Adaptive Teaching

| Element | Description |
|---------|-------------|
| **Use Case Name** | Adaptive Content Delivery Based on Student Response |
| **Actor(s)** | AI Tutor System |
| **Trigger** | Student submits answer or question during tutoring session |
| **Pre-conditions** | Active teaching session |
| **Post-conditions** | 1. Student's mastery level updated for the concept 2. AI adjusts next content/topic selection 3. Session transcript updated |
| **Main Flow** | 1. Student submits response to AI question 2. AI evaluates correctness + confidence level 3. AI updates internal student model: concept mastery score, learning style indicators (responds better to visuals/text/analogies), pace preference, misconception detection 4. AI selects next action: if correct & confident → advance to next concept / if correct but hesitant → provide reinforcement + simpler example / if incorrect & major misconception → re-teach with different approach / if incorrect & minor slip → point out error, let student self-correct 5. AI integrates real-world examples, visual representations, and analogies based on student profile 6. AI periodically checks: "Are you following along? Any part that's fuzzy?" |
| **Business Rules** | BR-38: AI must never shame or mock incorrect answers. BR-39: AI should celebrate correct answers with genuine tone. BR-40: After 3 consecutive correct answers, difficulty increases. After 2 consecutive wrong answers, difficulty decreases. BR-41: Learning style profile updated after every 10 interactions. BR-42: Misconception detection uses predefined misconception library + LLM analysis. |

#### Use Case UC-13: End AI Tutor Session

| Element | Description |
|---------|-------------|
| **Use Case Name** | Conclude Tutoring Session with Summary |
| **Actor(s)** | Student |
| **Trigger** | Student clicks "End Session" or session times out |
| **Pre-conditions** | Active teaching session |
| **Post-conditions** | 1. Session marked "completed" 2. Lesson progress updated (percentage, time spent) 3. Mastery records updated for all covered concepts 4. Summary generated and displayed to student |
| **Main Flow** | 1. AI compiles session summary: concepts covered, mastery scores achieved, areas needing review, time spent, quiz results (if any) 2. System updates lesson_progress: mark complete if all objectives met 3. System awards XP/achievements based on performance 4. System triggers parent notification (if enabled) 5. System suggests next lesson / upcoming topic 6. System generates personalized reminder: "See you tomorrow for Lesson 2!" 7. Session transcript saved for analytics |

---

### 5.6 Assessment & Mastery Module

**Module Description:** Handles quizzes, exercises, mastery tracking, and knowledge state management across the learning journey.

#### Use Case UC-14: Take a Lesson Quiz

| Element | Description |
|---------|-------------|
| **Use Case Name** | Complete Lesson Assessment |
| **Actor(s)** | Student |
| **Trigger** | Student clicks "Take Quiz" after or during a lesson |
| **Pre-conditions** | 1. Student has completed minimum 50% of lesson content OR AI recommends readiness 2. Quiz questions exist for the lesson |
| **Post-conditions** | 1. Quiz attempt recorded 2. Score calculated 3. Mastery records updated 4. Wrong answers logged for spaced repetition |
| **Main Flow** | 1. System presents quiz questions (mix of multiple-choice, fill-in-blank, short answer, and visual) 2. Student answers each question 3. For incorrect answers, AI provides explanation after submission 4. System calculates score: percentage correct 5. System updates concept mastery based on question performance 6. System displays results: correct/incorrect breakdown, strengths, areas for review 7. If score >= 80%: lesson marked "mastered" — student advances 8. If score < 80%: system recommends review and retake (different questions) |
| **Business Rules** | BR-43: Questions randomly selected from a pool (minimum 5 questions per lesson, pool of 10+). BR-44: Retake allowed after 24 hours (sooner if teacher override). BR-45: Retake questions differ from first attempt. BR-46: Mastery threshold = 80% for "mastered", 60% for "familiar", below 60% = "needs practice". BR-47: Quiz time limit = 1 minute per question (configurable). |

#### Use Case UC-15: View Mastery Progress

| Element | Description |
|---------|-------------|
| **Use Case Name** | Track Concept-by-Concept Mastery |
| **Actor(s)** | Student, Teacher, Parent |
| **Trigger** | User navigates to progress/mastery section |
| **Pre-conditions** | User has permission to view the student's data |
| **Post-conditions** | Mastery visualization displayed |
| **Main Flow** | 1. System retrieves all knowledge nodes linked to enrolled courses 2. For each node, retrieve latest mastery score (0-100) 3. System displays color-coded map: green (mastered, 80%+), yellow (familiar, 60-79%), red (needs practice, <60%), gray (not attempted) 4. User can click any node to see: detailed score history, last assessment date, recommended next actions |
| **Business Rules** | BR-48: Mastery scores decay at 5% per month without reinforcement. BR-49: Spaced repetition prompts for nodes with decay below 70%. |

---

### 5.7 Knowledge Graph & Learning Path Module

**Module Description:** Maintains a directed graph of concepts (knowledge nodes) and their relationships (prerequisites, related topics) to power adaptive learning paths.

#### Use Case UC-16: Maintain Knowledge Graph

| Element | Description |
|---------|-------------|
| **Use Case Name** | Define Concept Nodes and Relationships |
| **Actor(s)** | Teacher, Admin, Curriculum Designer |
| **Trigger** | User opens curriculum builder and clicks "Knowledge Graph" |
| **Pre-conditions** | Course exists with at least one concept defined |
| **Post-conditions** | Knowledge graph updated |
| **Main Flow** | 1. System displays current concept nodes for the course 2. User can: add new concept node (name, description, domain, difficulty level), link concepts with relationship type (prerequisite, related, extends), set prerequisite depth (must complete before starting target concept) 3. System validates no circular dependencies 4. System saves graph structure |
| **Business Rules** | BR-50: Knowledge graph is a DAG (directed acyclic graph) — no circular prerequisites. BR-51: A concept can have multiple prerequisites. BR-52: Prerequisite chains max depth = 5. |

#### Use Case UC-17: Generate Adaptive Learning Path

| Element | Description |
|---------|-------------|
| **Use Case Name** | Compute Personalized Learning Path |
| **Actor(s)** | AI System |
| **Trigger** | Student enrolls in course OR requests "Optimize My Path" |
| **Pre-conditions** | 1. Knowledge graph exists for the course 2. Student has mastery data for prerequisite nodes |
| **Post-conditions** | Ordered list of next concepts/lessons to study |
| **Main Flow** | 1. System identifies all concepts in the course 2. System filters concepts already mastered 3. System applies topological sort based on prerequisite edges 4. System checks student's mastery of prerequisites for each remaining concept 5. System generates suggested order: unmastered prerequisites first, then current-level concepts, advancing by difficulty 6. System updates student's "learning path" in their dashboard |
| **Business Rules** | BR-53: Path recalculation triggered when: new course enrollment, concept mastered, 7 days idle. BR-54: Student can manually reorder path (advisory, not mandatory). |

---

### 5.8 Teacher Dashboard Module

**Module Description:** Provides teachers with analytics, student management, and intervention tools.

#### Use Case UC-18: View Course Analytics

| Element | Description |
|---------|-------------|
| **Use Case Name** | Monitor Course-Wide Performance |
| **Actor(s)** | Teacher |
| **Trigger** | Teacher opens a specific course from their dashboard |
| **Pre-conditions** | Teacher is the course creator or has been assigned as co-teacher |
| **Post-conditions** | Analytics dashboard displayed |
| **Main Flow** | 1. System retrieves: total enrolled students, active students (last 7 days), completion rate, average quiz score, average time to complete, student satisfaction rating 2. System displays: enrollment trend chart, performance distribution (thriving/development zone/needs support), average score per lesson, week-over-week comparison 3. Teacher can filter by date range, student segment, lesson |
| **Business Rules** | BR-55: Student names anonymized in public views (teacher sees real names). BR-56: Data refresh interval = 5 minutes for real-time dashboard. |

#### Use Case UC-19: Identify & Support At-Risk Students

| Element | Description |
|---------|-------------|
| **Use Case Name** | Identify Struggling Students and Intervene |
| **Actor(s)** | Teacher |
| **Trigger** | Teacher views "Needs Support" section on course dashboard |
| **Pre-conditions** | At least one student has < 70% average quiz score OR declining engagement |
| **Post-conditions** | Teacher intervention recorded (video upload, message, custom exercise) |
| **Main Flow** | 1. System identifies at-risk students: declining quiz scores (3+ consecutive drops), low engagement (< 1 lesson/week), high time-on-lesson (struggling), submitted help requests 2. System ranks students by urgency 3. Teacher clicks on student to view: full profile with detailed performance, session transcripts, AI tutor notes ("struggles with improper fractions"), questions submitted by student 4. Teacher chooses intervention type: record video explanation (uploaded to student's lesson), send personalized encouragement message, assign remedial exercises, schedule live tutoring session (future feature) 5. System delivers intervention to student's dashboard 6. System tracks whether student viewed/engaged with intervention |
| **Business Rules** | BR-57: At-risk flag updated daily. BR-58: Teacher must respond to student help requests within 48 hours (SLA). |

#### Use Case UC-20: Create & Monetize Courses

| Element | Description |
|---------|-------------|
| **Use Case Name** | Course Creation for Revenue |
| **Actor(s)** | Teacher |
| **Trigger** | Teacher clicks "Create Course" with intent to monetize |
| **Pre-conditions** | 1. Teacher account verified 2. Tax/payment information collected 3. Teacher agrees to platform commission terms |
| **Post-conditions** | 1. Course created with pricing 2. Revenue sharing terms recorded |
| **Main Flow** | 1. Teacher creates course content (see UC-08) 2. Teacher sets price: free, $X.XX one-time, or subscription/month 3. Teacher can create coupon codes, discount periods, bundle deals 4. Teacher submits for publication 5. On student purchase: revenue split (e.g., 60% teacher, 40% platform) 6. Teacher earnings tracked in dashboard 7. Payouts processed monthly (min $50 threshold) |
| **Business Rules** | BR-59: Platform commission: 30-40% (tiered by course price). BR-60: Payout threshold: $50 minimum. BR-61: Teacher earnings visible in real-time with transaction history. BR-62: Tax documents required for payout (W-9/W-8BEN equivalent). |

---

### 5.9 Parent Dashboard Module

**Module Description:** Empowers parents to monitor, understand, and support their children's learning journey.

#### Use Case UC-21: View Child's Progress Report

| Element | Description |
|---------|-------------|
| **Use Case Name** | View Comprehensive Student Progress Report |
| **Actor(s)** | Parent |
| **Trigger** | Parent opens their dashboard or clicks a specific child |
| **Pre-conditions** | 1. Parent account exists 2. Parent linked to at least one student 3. Student has learning activity |
| **Post-conditions** | Progress report displayed |
| **Main Flow** | 1. System displays all linked children as cards (for multi-child households) 2. Parent selects a child 3. System displays: courses enrolled with progress %, weekly activity (lessons completed, time spent, quiz scores), strengths identified by AI, challenges/areas needing help, recent achievements/badges, grade-equivalent trend (e.g., C+ → B- improving) 4. System shows AI-generated insight: "Your child learns well with visuals" 5. System shows recommendations: "Try helping them with word problems this week" 6. Parent can view session transcripts and AI tutor conversation history |
| **Business Rules** | BR-63: Reports generated after each lesson completion. BR-64: Weekly digest email sent automatically (opt-out available). BR-65: Parent cannot see other children's data unless they are also linked. BR-66: AI insights are advisory, not diagnostic. |

#### Use Case UC-22: Configure Parental Controls

| Element | Description |
|---------|-------------|
| **Use Case Name** | Manage Student Safety and Usage Settings |
| **Actor(s)** | Parent |
| **Trigger** | Parent opens Settings → Parental Controls |
| **Pre-conditions** | Parent linked to student |
| **Post-conditions** | Control settings saved and enforced |
| **Main Flow** | 1. System displays available controls per child: daily usage time limit (default 3 hours for under-16), learning hours window (default 8 AM - 9 PM), break reminders (every 45 min, 10 min break), notification preferences (real-time, daily digest, weekly only), content filters (age-appropriate level), course enrollment approval (require parent approval) 2. Parent adjusts sliders/toggles 3. System validates settings (e.g., max time per day) 4. System saves and immediately enforces controls 5. Child receives in-app notification of changes |
| **Business Rules** | BR-67: Under-16 students default to 3-hour daily limit. BR-68: Sleep hours (9 PM - 8 AM) enforced globally for under-16. BR-69: Parent can override any default. BR-70: Controls are per-child, not global. |

#### Use Case UC-23: Communicate with Teacher

| Element | Description |
|---------|-------------|
| **Use Case Name** | Message Child's Course Teacher |
| **Actor(s)** | Parent |
| **Trigger** | Parent clicks "Message Teacher" from progress report |
| **Pre-conditions** | 1. Parent linked to student 2. Student enrolled in teacher's course |
| **Post-conditions** | 1. Message sent 2. Teacher notified 3. Response tracked |
| **Main Flow** | 1. Parent composes message 2. System appends context: student name, course name, current lesson, recent performance 3. System sends message to teacher 4. Teacher receives notification (email + in-app) 5. Teacher can reply within dashboard 6. Parent notified of reply |
| **Business Rules** | BR-71: Messages are not real-time chat — async messaging only. BR-72: Teachers expected to respond within 48 hours. BR-73: Message history retained for 1 year. BR-74: Inappropriate messages can be flagged for admin review. |

---

### 5.10 Administrator Module

**Module Description:** Platform-level administration for managing users, courses, content quality, system health, and compliance.

#### Use Case UC-24: Review Platform Analytics

| Element | Description |
|---------|-------------|
| **Use Case Name** | View System-Wide Performance Metrics |
| **Actor(s)** | Admin |
| **Trigger** | Admin opens analytics dashboard |
| **Pre-conditions** | Admin authenticated with admin role |
| **Post-conditions** | Metrics dashboard displayed |
| **Main Flow** | 1. System displays: total users (students, teachers, parents), courses created, lessons completed, active users (DAU/MAU), revenue metrics, platform uptime, average response times, content moderation queue count, teacher payout summary |
| **Business Rules** | BR-75: Real-time metrics may have 5-minute delay. BR-76: Admin can export any report as CSV/PDF. BR-77: Anomaly detection alerts for unusual patterns (spike in errors, drop in engagement). |

#### Use Case UC-25: Moderate Content

| Element | Description |
|---------|-------------|
| **Use Case Name** | Review and Moderate User-Generated Content |
| **Actor(s)** | Admin |
| **Trigger** | Content flagged by automated system or user report |
| **Pre-conditions** | Admin has content moderator permission |
| **Post-conditions** | Content reviewed; action taken (approve, flag, remove, warn user) |
| **Main Flow** | 1. System queues content for review: new courses (if moderation required), reported lessons/questions/comments, AI-detected policy violations 2. Admin reviews content 3. Admin takes action: approve (content published/restored), flag (content marked for revision), remove (content deleted, sent to archive), warn user (warning sent, logged) 4. If removal: system notifies content creator with reason. 5. If user accumulates 3+ violations: account restricted |
| **Business Rules** | BR-78: Automated flagging uses keyword + ML-based detection. BR-79: Response time SLA: 24 hours for reported content. BR-80: Removed content retained in archive for 90 days (appeal window). |

---

### 5.11 Institutional / School District Module

**Module Description:** Supports school/district-wide adoption with bulk enrollment, role management, and institution-level analytics.

#### Use Case UC-26: Onboard School District

| Element | Description |
|---------|-------------|
| **Use Case Name** | Register School District for Institutional Access |
| **Actor(s)** | District Administrator, Superintendent |
| **Trigger** | District admin completes institutional sign-up |
| **Pre-conditions** | 1. Institution verified (tax ID, accreditation) 2. Agreement signed |
| **Post-conditions** | 1. Institution record created 2. Admin accounts provisioned 3. Custom subdomain/portal created |
| **Main Flow** | 1. Institution admin provides: district/school name, address, number of students, number of teachers, grades served, admin contact information 2. System creates institution record with status = "active" 3. System provisions admin accounts (linked to institutional email domain) 4. System creates custom portal (e.g., springfield.learningai.com) 5. System sends welcome materials and onboarding instructions |
| **Business Rules** | BR-81: Institutional users get domain-verified accounts (auto-approve for @schooldomain.edu emails). BR-82: Institution admin can create sub-admins (school-level principals, department heads). BR-83: Bulk student upload via CSV/SSO supported. |

#### Use Case UC-27: Generate Institutional Reports

| Element | Description |
|---------|-------------|
| **Use Case Name** | View Institution-Wide Learning Outcomes |
| **Actor(s)** | District Admin, Principal |
| **Trigger** | Admin opens institution analytics |
| **Pre-conditions** | Institution has active students and teachers |
| **Post-conditions** | Reports displayed/exported |
| **Main Flow** | 1. System displays: total students enrolled, engagement rate (% active last 30 days), average completion rate by course, average quiz scores by grade/subject, student improvement trend (pre/post platform), teacher adoption rate, parent engagement rate 2. System allows drill-down: school → grade → class → student 3. System provides comparison views: vs. other schools in district, vs. district average, vs. national average 4. System allows export to PDF/CSV for board presentations |
| **Business Rules** | BR-84: Student-level data visible only to authorized school staff. BR-85: Aggregate data (no PII) available at district level. BR-86: Reports auto-generated monthly; emailed to designated recipients. |

---

### 5.12 Gamification & Achievement Module

**Module Description:** Drives student motivation and engagement through achievements, streaks, XP, and certificates.

#### Use Case UC-28: Award Achievements & Badges

| Element | Description |
|---------|-------------|
| **Use Case Name** | Unlock Achievement Based on Milestone |
| **Actor(s)** | System (automatic) |
| **Trigger** | Student reaches a predefined milestone |
| **Pre-conditions** | Student logged in and performing actions |
| **Post-conditions** | 1. Achievement record created 2. Badge awarded 3. Notification sent 4. XP applied |
| **Main Flow** | 1. System checks for achievement triggers after each student action: "First Step" — first lesson completed, "Three-Day Streak" 🔥 — 3 consecutive days of learning, "Fractions Master" 🏆 — completed fractions course with 90%+ avg, "21-Day Streak" — 21 consecutive days, "Perfect Quiz" — 100% on any quiz, "Speed Learner" — completed a lesson in under 10 minutes with 100% score, "Course Complete" — finished any course, "Knowledge Seeker" — enrolled in 5+ courses 2. If trigger met: system checks student doesn't already have the achievement 3. System creates achievement record 4. System awards any associated XP/rewards 5. System triggers notification: achievement unlocked animation + shareable badge |
| **Business Rules** | BR-87: Achievements are non-revocable (even if course re-taken). BR-88: Badges are shareable to social media (custom image generated). BR-89: Some achievements have levels (bronze/silver/gold). BR-90: Teachers can create custom achievements for their courses. |

#### Use Case UC-29: Issue Certificate of Completion

| Element | Description |
|---------|-------------|
| **Use Case Name** | Generate Course Completion Certificate |
| **Actor(s)** | System (automatic) |
| **Trigger** | Student achieves >= 80% overall score across all course lessons and quizzes |
| **Pre-conditions** | 1. Student completed all lessons 2. Average quiz score >= 80% |
| **Post-conditions** | 1. Certificate generated 2. Certificate URL shared to student 3. Teacher notified of completion |
| **Main Flow** | 1. System calculates final grade (weighted average of all quizzes, 50% + assignments/exercises 20% + lesson completion 30%) 2. If >= 80%: system generates certificate PDF with: student name, course name, teacher name, completion date, final grade, certificate serial number 3. System makes certificate available in student's profile (shareable link, downloadable PDF) 4. System adds course to "Completed Courses" section on transcript |
| **Business Rules** | BR-91: Certificates have unique, verifiable serial numbers (QR code). BR-92: Certificates hosted at permalink; never deleted. BR-93: Students can earn multiple certificates (one per completed course). |

---

### 5.13 Notification & Communication Module

**Module Description:** Multi-channel notification engine for in-app, email, and push notifications across the platform.

#### Use Case UC-30: Send Progress Notification

| Element | Description |
|---------|-------------|
| **Use Case Name** | Notify Parent of Lesson Completion |
| **Actor(s)** | System (automatic) |
| **Trigger** | Student completes a lesson |
| **Pre-conditions** | 1. Student has linked parent 2. Parent has notification enabled |
| **Post-conditions** | Notification delivered via configured channels |
| **Main Flow** | 1. Lesson completion triggers notification event 2. System compiles notification payload: student name, course name, lesson name, time spent, quiz score, AI assessment summary, "What they learned" bullets, "Where they struggled" bullets, recommended next steps 3. System sends: in-app notification (student and parent dashboards), email (with formatted HTML template), optional push notification (mobile) 4. System logs delivery status |
| **Business Rules** | BR-94: Notifications batched if multiple lessons completed within 15 minutes (digest mode). BR-95: Parents can choose frequency: real-time, daily digest, weekly summary. BR-96: Sleep hours (9 PM - 8 AM) suppress push notifications. BR-97: Notification history retained for 90 days. |

---

### 5.14 Payment & Monetization Module

**Module Description:** Handles course purchases, subscriptions, teacher payouts, and financial reporting.

#### Use Case UC-31: Purchase a Course

| Element | Description |
|---------|-------------|
| **Use Case Name** | Complete Course Purchase |
| **Actor(s)** | Student, Parent |
| **Trigger** | User clicks "Buy" or "Enroll" on a paid course |
| **Pre-conditions** | 1. User account exists 2. Payment method on file or provided 3. Course is priced and available |
| **Post-conditions** | 1. Payment processed 2. Enrollment created 3. Receipt sent 4. Teacher's earnings ledger updated |
| **Main Flow** | 1. System adds course to cart 2. User proceeds to checkout 3. System displays: course name, price, any applicable coupon/promotion, total 4. User enters/selects payment method 5. System processes payment via payment gateway (Stripe/PayPal integration) 6. On success: system creates enrollment, sends receipt, updates teacher's pending earnings 7. On failure: display specific error, retry option |
| **Business Rules** | BR-98: All payments processed via PCI-compliant third-party gateway. BR-99: Platform never stores full credit card numbers. BR-100: Refund policy: 30-day full refund for unused courses. BR-101: Tax handling applies based on student's country. |

#### Use Case UC-32: Process Teacher Payout

| Element | Description |
|---------|-------------|
| **Use Case Name** | Process Monthly Teacher Payout |
| **Actor(s** | System (scheduled) |
| **Trigger** | Monthly payout date (e.g., 1st of each month) |
| **Pre-conditions** | 1. Teacher has pending earnings >= $50 2. Teacher has valid payout information (bank/PayPal) 3. Tax documentation on file |
| **Post-conditions** | 1. Payout initiated 2. Earnings ledger updated 3. Teacher notified |
| **Main Flow** | 1. System calculates teacher's pending earnings for the month 2. System subtracts any platform fees, refunds, chargebacks 3. System submits payout via payment gateway 4. System marks earnings as "paid" 5. System sends payment receipt to teacher 6. System generates monthly financial report |
| **Business Rules** | BR-102: Payouts processed only if balance >= $50; otherwise rolled over. BR-103: Refunds deducted from future earnings. BR-104: Chargeback fee ($15) passed to teacher if excessive chargebacks on their course. BR-105: Payout reports available in teacher dashboard. |

---

### 5.15 Content Ingestion & Upload Module

**Module Description:** Enables teachers to upload existing materials (PDF, DOCX, TXT) and have them automatically parsed into structured lesson content.

#### Use Case UC-33: Upload and Parse Teaching Material

| Element | Description |
|---------|-------------|
| **Use Case Name** | Ingest External Content into Lesson |
| **Actor(s)** | Teacher |
| **Trigger** | Teacher uploads a file in the lesson editor |
| **Pre-conditions** | 1. Teacher editing a lesson 2. File is in allowed format (PDF, DOCX, TXT) 3. File size within limits (max 50MB) |
| **Post-conditions** | 1. File uploaded and stored 2. Content extracted 3. Teacher can review/edit extracted content |
| **Main Flow** | 1. Teacher selects file from local system 2. System validates file type and size 3. System uploads file to secure storage 4. System parses file content: PDF: text extraction (PyMuPDF/pdfplumber) retaining structure, DOCX: extract paragraphs, headings, lists (python-docx), TXT: raw text ingestion 5. System presents extracted content in the lesson editor 6. Teacher can modify, reorganize, and save |
| **Business Rules** | BR-106: Images extracted from DOCX/PDF and stored separately. BR-107: Extracted text limited to 10,000 words per upload (truncation warning). BR-108: Original file retained for reference. BR-109: Scanned PDF (image-based) not supported — OCR may be added in Phase 2. BR-110: Copyright notice displayed: "You confirm you have rights to upload this content." |

---

### 5.16 Safety, Privacy & Parental Controls Module

**Module Description:** Ensures platform safety, regulatory compliance, and student well-being through a multi-layered system of controls and safeguards.

#### Use Case UC-34: Enforce Usage Limits

| Element | Description |
|---------|-------------|
| **Use Case Name** | Apply Time and Access Restrictions |
| **Actor(s)** | System (automatic) |
| **Trigger** | Student attempts to access learning content |
| **Pre-conditions** | Student logged in and under 16 (or parent-configured limits apply) |
| **Post-conditions** | Access granted or denied with clear message |
| **Main Flow** | 1. Student requests to start a lesson or AI session 2. System checks: daily time used vs. daily limit, current time vs. allowed hours, break status (has a break been taken in last 45 min?) 3. Within limits → access granted 4. If limit exceeded: display friendly message: "You've done great today! Time for a break. Come back tomorrow." with a summary of today's achievements 5. If during sleep hours: display "Learning is closed for now. Sleep well and come back in the morning!" 6. If break due: "You've been learning for 45 minutes! Take a 10-minute break. Stretch, drink water, rest your eyes." |
| **Business Rules** | BR-111: Default daily limit for under-16: 3 hours. BR-112: Limit resets at midnight (user's timezone). BR-113: Break timer resets when student stops activity for 10+ minutes. BR-114: Parent can override limits from their dashboard. BR-115: Logged-in student sessions are tracked server-side (client-side enforcement is secondary). |

#### Use Case UC-35: Data Privacy & Compliance

| Element | Description |
|---------|-------------|
| **Use Case Name** | Enforce COPPA and GDPR Compliance |
| **Actor(s)** | System (automatic) |
| **Trigger** | Any operation that processes PII |
| **Pre-conditions** | User data exists in the system |
| **Post-conditions** | Compliance rules enforced |
| **Main Flow** | 1. For students under 13: no behavioral tracking for marketing, data retention capped at course completion + 1 year, parent must have provided verifiable consent, no sharing of PII with third parties (except core service providers) 2. For all users: password hashed (bcrypt), session tokens encrypted in transit (TLS), personal data exportable on request, account deletion available (anonymizes or deletes data within 30 days) 3. Audit logs for all PII access 4. Data breach protocol: detect → isolate → assess → notify (within 72 hours per GDPR) |
| **Business Rules** | BR-116: No advertising or marketing to users under 13. BR-117: Data retention: active accounts = duration of account; inactive > 2 years = anonymized. BR-118: User can request data download in JSON format within 7 days. BR-119: All AI transcripts anonymized after 90 days for model training. |

---

### 5.17 Offline & Accessibility Module

**Module Description:** Extends platform reach to users with limited connectivity or disabilities.

#### Use Case UC-36: Download Lessons for Offline Use

| Element | Description |
|---------|-------------|
| **Use Case Name** | Access Course Content Offline |
| **Actor(s)** | Student |
| **Trigger** | Student clicks "Download for Offline" on a lesson |
| **Pre-conditions** | 1. Student connected to internet 2. Lesson content is downloadable (teacher has not restricted) |
| **Post-conditions** | Lesson content cached locally |
| **Main Flow** | 1. Student selects lesson or module to download 2. System packages content: text, images, exercise descriptions (videos excluded due to size) 3. System downloads to local storage 4. Student can access content from "Offline" tab when not connected 5. When back online, quiz attempts and progress sync automatically |
| **Business Rules** | BR-120: Max 3 courses stored offline at a time. BR-121: Offline content expires after 30 days (must refresh). BR-122: AI tutor requires internet connection. Offline mode is read-only. BR-123: Progress syncs silently when connection restored. |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | API response time (p90) | < 200ms for read endpoints, < 500ms for write |
| NFR-02 | AI Tutor response time | < 3 seconds for first response, < 1 second for follow-ups |
| NFR-03 | Page load time (p90) | < 2 seconds initial load, < 500ms subsequent |
| NFR-04 | Search result latency | < 500ms |
| NFR-05 | Concurrent users supported | 10,000+ simultaneous sessions |
| NFR-06 | Report generation | < 5 seconds for individual, < 30 seconds for institutional |
| NFR-07 | File upload / parsing | < 10 seconds for 10MB file |

### 6.2 Availability & Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-08 | System uptime | 99.9% (excluding planned maintenance) |
| NFR-09 | Planned maintenance window | Max 4 hours/month, communicated 7 days in advance |
| NFR-10 | Disaster recovery | RPO: 5 minutes, RTO: 30 minutes |
| NFR-11 | Backup frequency | Full daily, incremental every 15 minutes |
| NFR-12 | Auto-scaling | Trigger at 70% CPU/memory usage |

### 6.3 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-13 | Authentication | JWT-based; access tokens 15 min TTL, refresh tokens 7 days |
| NFR-14 | Password policy | Min 8 chars, 1 uppercase, 1 number, bcrypt hash |
| NFR-15 | Rate limiting | 100 requests/min per user, 10 login attempts/min per IP |
| NFR-16 | Data in transit | TLS 1.3 minimum |
| NFR-17 | Data at rest | AES-256 encryption |
| NFR-18 | API security | CORS; CSRF protection; security headers (HSTS, X-Frame-Options, X-Content-Type-Options) |
| NFR-19 | Audit logging | All PII access, role changes, financial transactions logged |
| NFR-20 | Penetration testing | Quarterly third-party audits |
| NFR-21 | Vulnerability scanning | Weekly automated scans |

### 6.4 Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-22 | Horizontal scaling | Stateless API layer; database read replicas |
| NFR-23 | Database scaling | Connection pooling; query optimization; indexes on all foreign keys |
| NFR-24 | File storage | CDN-backed for course content/images |
| NFR-25 | Cache strategy | Redis for session cache; API response cache (60s TTL) |

### 6.5 Usability & Accessibility

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-26 | WCAG compliance | WCAG 2.1 AA minimum |
| NFR-27 | Mobile responsiveness | All pages functional on 320px+ width |
| NFR-28 | Multi-language | i18n architecture for 10+ languages (Phase 1: EN, ES, FR, DE) |
| NFR-29 | Screen reader support | Semantic HTML, ARIA labels, keyboard navigation |
| NFR-30 | Color contrast | Minimum 4.5:1 ratio for text |
| NFR-31 | Error messages | User-friendly, actionable, non-technical language |

### 6.6 Data & Analytics

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-32 | Progress tracking accuracy | Real-time within 60 seconds |
| NFR-33 | Dashboard data freshness | Max 5-minute delay for real-time dashboards |
| NFR-34 | Reporting data export | CSV, PDF, JSON formats |
| NFR-35 | Data retention | Active accounts: indefinitely; inactive > 2 years: anonymized |

---

## 7. Data & Reporting Requirements

### 7.1 Core Data Entities

| Entity | Description | Key Relationships |
|--------|-------------|-------------------|
| User | Students, teachers, parents, admins | enrollments, teaching_sessions |
| Course | Published/ draft courses with curriculum | modules, enrollments, teacher |
| Module | Course sub-division | lessons, course |
| Lesson | Atomic teaching unit | concepts, exercises, quizzes, teaching_sessions |
| Concept (Knowledge Node) | Atomic concept in knowledge graph | prerequisites, mastery_records |
| Teaching Session | AI tutoring session transcript | student, lesson, AI messages |
| Mastery Record | Concept-level student mastery | student, concept, score |
| Enrollment | Student-course association | student, course, progress |
| Assessment/Quiz | Lesson-level assessment | questions, attempts, scores |
| Achievement | Gamification milestone | student, badge type, course |

### 7.2 Reports Required

| Report | Audience | Frequency | Description |
|--------|----------|-----------|-------------|
| Lesson Completion Report | Parent, Teacher | Per-lesson | What was learned, quiz score, strengths, areas for review |
| Weekly Progress Summary | Parent, Student | Weekly | Activity summary, trend, recommendations |
| Course Analytics | Teacher | Real-time | Enrollment, completion, scores, at-risk students |
| Student Performance Profile | Teacher, Parent | On-demand | Full historical performance, session transcripts |
| Institutional Report | District Admin | Monthly | District-wide engagement, outcomes, comparison |
| Financial Report | Teacher, Admin | Monthly | Earnings, payouts, refunds, tax documents |
| System Health Report | Admin | Real-time | Uptime, error rates, latency, capacity |
| Content Quality Report | Admin | Weekly | Flagged content, moderation queue, creator warnings |

---

## 8. Assumptions & Dependencies

### Assumptions
1. Students have access to a device with internet connectivity (mobile-responsive web app)
2. Schools will provide institutional email domains for verification
3. Parents have basic digital literacy for dashboard usage
4. Teachers will adopt the platform if it reduces administrative burden
5. Regulatory compliance (COPPA, GDPR, FERPA, etc.) will vary by jurisdiction but platforms must meet the highest standard
6. AI model costs will decrease over time, enabling sustainable free-tier operation
7. Users are comfortable with AI-tutoring (LLM-based) for foundational subjects
8. Third-party payment gateways handle PCI compliance; platform does not store card data

### Dependencies
1. **PostgreSQL** — Primary relational database (async with asyncpg driver)
2. **SQLAlchemy 2.0+** — ORM with async support
3. **FastAPI** — Web framework
4. **LangGraph** — AI agent orchestration for tutoring workflows
5. **Gemini API** — LLM provider for AI tutor (configurable for other providers)
6. **React + Vite** — Frontend framework
7. **Tailwind CSS** — UI styling
8. **Alembic** — Database migrations
9. **Redis** — Session caching, rate limiting, job queues (Phase 2)
10. **Qdrant** — Vector database for AI memory/knowledge retrieval (Phase 2)
11. **Stripe / PayPal** — Payment processing
12. **SMTP provider** — Email delivery (SendGrid, AWS SES, etc.)
13. **CDN** — Content delivery for static assets and course files
14. **Docker** — Containerized deployment

---

## 9. Glossary

| Term | Definition |
|------|------------|
| AI Tutor | LLM-powered conversational agent that delivers personalized instruction |
| Mastery | Quantified understanding level of a specific concept (0-100 scale) |
| Knowledge Graph | Directed graph of concepts and their prerequisite/related relationships |
| Learning Path | Optimized sequence of topics computed from knowledge graph + student state |
| Streak | Consecutive calendar days with at least one lesson completed |
| Session | A single AI tutoring interaction (from start to end) |
| COPPA | Children's Online Privacy Protection Act (US) |
| GDPR | General Data Protection Regulation (EU) |
| FERPA | Family Educational Rights and Privacy Act (US) |
| PII | Personally Identifiable Information |
| JWT | JSON Web Token — stateless authentication mechanism |
| XP | Experience Points — gamification currency |
| RPO | Recovery Point Objective — max data loss in disaster |
| RTO | Recovery Time Objective — time to restore service |
| WCAG | Web Content Accessibility Guidelines |

---

## Appendix A: Use Case Index

| ID | Name | Module | Actor(s) | Priority |
|----|------|--------|----------|----------|
| UC-01 | Register New Student Account | Auth | Student | Critical |
| UC-02 | Authenticate User | Auth | All Users | Critical |
| UC-03 | Reset Forgotten Password | Auth | All Users | High |
| UC-04 | Link Parent to Student Account | Auth | Parent, Student | High |
| UC-05 | View Student Learning Dashboard | Student Dashboard | Student | Critical |
| UC-06 | Search and Browse Course Catalog | Discovery | Student | High |
| UC-07 | Enroll in a Course | Enrollment | Student | Critical |
| UC-08 | Create New Course | Curriculum | Teacher | Critical |
| UC-09 | Create Curriculum Hierarchy | Curriculum | Teacher | Critical |
| UC-10 | Publish Course for Enrollment | Curriculum | Teacher | High |
| UC-11 | Start AI Tutor Session | AI Tutor | Student | Critical |
| UC-12 | Adaptive Teaching by AI | AI Tutor | AI System | Critical |
| UC-13 | End AI Tutor Session with Summary | AI Tutor | Student | Critical |
| UC-14 | Take Lesson Quiz | Assessment | Student | Critical |
| UC-15 | View Mastery Progress | Assessment | Student, Teacher, Parent | High |
| UC-16 | Maintain Knowledge Graph | Knowledge Graph | Teacher | High |
| UC-17 | Generate Adaptive Learning Path | Knowledge Graph | AI System | High |
| UC-18 | View Course Analytics | Teacher Dashboard | Teacher | High |
| UC-19 | Identify & Support At-Risk Students | Teacher Dashboard | Teacher | Critical |
| UC-20 | Create & Monetize Courses | Teacher Dashboard | Teacher | High |
| UC-21 | View Child's Progress Report | Parent Dashboard | Parent | Critical |
| UC-22 | Configure Parental Controls | Parent Dashboard | Parent | High |
| UC-23 | Communicate with Teacher | Parent Dashboard | Parent | Medium |
| UC-24 | View Platform Analytics | Admin | Admin | High |
| UC-25 | Moderate Content | Admin | Admin | High |
| UC-26 | Onboard School District | Institutional | District Admin | High |
| UC-27 | Generate Institutional Reports | Institutional | District Admin | High |
| UC-28 | Award Achievements & Badges | Gamification | System | Medium |
| UC-29 | Issue Certificate of Completion | Gamification | System | High |
| UC-30 | Send Progress Notification | Notifications | System | High |
| UC-31 | Purchase a Course | Payments | Student, Parent | High |
| UC-32 | Process Teacher Payout | Payments | System | High |
| UC-33 | Upload and Parse Teaching Material | Content Ingestion | Teacher | Medium |
| UC-34 | Enforce Usage Limits | Safety | System | Critical |
| UC-35 | Enforce Data Privacy & Compliance | Safety | System | Critical |
| UC-36 | Download Lessons for Offline Use | Offline | Student | Medium |

---

**Document Status:** Initial Draft  
**Next Review:** Based on stakeholder feedback  
**Prepared for:** ACUITY LMS Engineering & Product Teams
