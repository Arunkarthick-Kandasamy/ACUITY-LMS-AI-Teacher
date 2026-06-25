# Role Matrix — Acuity LMS AI

**Generated:** 2026-06-25
**Legend:** ✅ Full, ⚠️ Partial, ❌ Missing, N/A Not applicable

---

## 1. Feature Access by Role

| Feature | Student | Parent | Admin | Teacher | Teacher Status |
|---------|:-------:|:------:|:-----:|:-------:|:--------------:|
| Register | ✅ | ✅ | ✅ | ❌ | Missing |
| Login | ✅ | ✅ | ✅ | ❌ | Missing |
| View own profile | ✅ | ✅ | ✅ | ❌ | Missing |
| Edit profile | ❌ | ❌ | ❌ | ❌ | Missing |
| Forgot/reset password | ❌ | ❌ | ❌ | ❌ | Broken for all |
| Course catalog / browse | ⚠️ | ❌ | ✅ | ❌ | Missing |
| Enroll in courses | ⚠️ | ❌ | ❌ | ❌ | Missing role guard |
| View learning path | ⚠️ | ❌ | ❌ | ❌ | Missing |
| AI Tutor sessions | ⚠️ | ❌ | ❌ | ❌ | Missing |
| Assessments | ❌ | ❌ | ❌ | ❌ | Broken for all |
| View progress | ⚠️ | ❌ | ❌ | ❌ | Missing |
| View mastery | ⚠️ | ❌ | ❌ | ❌ | Missing |
| View weak concepts | ⚠️ | ❌ | ❌ | ❌ | Missing |
| View learning pace | ❌ | ❌ | ❌ | ❌ | Missing |
| View session history | ✅ | ❌ | ✅ | ❌ | Missing |
| Link parent account | ❌ | ✅ | ✅ | ❌ | Missing |
| Manage linked students | N/A | ⚠️ | N/A | ❌ | Missing |
| View student progress | N/A | ⚠️ | ✅ | ❌ | Missing |
| View student mastery | N/A | ⚠️ | ✅ | ❌ | Missing |
| View student misconceptions | N/A | ⚠️ | ❌ | ❌ | Missing |
| View student sessions | N/A | ⚠️ | ❌ | ❌ | Missing |
| View student reports | N/A | ⚠️ | ✅ | ❌ | Missing |
| Generate reports | N/A | ⚠️ | ✅ | ❌ | Missing |
| Insights & recommendations | N/A | ⚠️ | ❌ | ❌ | Missing |
| Manage courses (CRUD) | ❌ | ❌ | ✅ | ❌ | Missing |
| Manage curriculum (modules/lessons/concepts) | ❌ | ❌ | ✅ | ❌ | Missing |
| Manage knowledge graph | ❌ | ❌ | ✅ | ❌ | Missing |
| Upload content | ❌ | ❌ | ✅ | ❌ | Missing |
| Review AI-generated content | ❌ | ❌ | ✅ | ❌ | Missing |
| Approve/publish content | ❌ | ❌ | ✅ | ❌ | Missing |
| View all users | ❌ | ❌ | ⚠️ | ❌ | Missing |
| Create/edit users | ❌ | ❌ | ❌ | ❌ | Missing |
| Disable users | ❌ | ❌ | ❌ | ❌ | Missing |
| View analytics | ❌ | ❌ | ⚠️ | ❌ | Missing |
| View audit logs | ❌ | ❌ | ❌ | ❌ | Missing |
| View student roster | N/A | N/A | ❌ | ❌ | Missing |
| Assign students to teachers | N/A | N/A | ❌ | ❌ | Missing |
| Create assessments/exercises | ❌ | ❌ | ✅ | ❌ | Missing |
| View AI intervention recommendations | N/A | ❌ | ❌ | ❌ | Missing |

---

## 2. API Endpoint Access by Role

| Module | Public | Student | Parent | Admin | Teacher |
|--------|:------:|:-------:|:------:|:-----:|:-------:|
| Health | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auth: Register | ✅ | ✅ | ✅ | ✅ | ❌ |
| Auth: Login | ✅ | ✅ | ✅ | ✅ | ❌ |
| Auth: Refresh | ✅ | ✅ | ✅ | ✅ | ❌ |
| Auth: Logout | ❌ | ✅ | ✅ | ✅ | ❌ |
| Auth: Forgot Password | ✅ | ✅ | ✅ | ✅ | ❌ |
| Auth: Reset Password | ✅ | ✅ | ✅ | ✅ | ❌ |
| Curriculum: Read | ❌ | ✅ | ❌ | ✅ | ❌ |
| Curriculum: Write | ❌ | ❌ | ❌ | ✅ | ❌ |
| Knowledge Graph: Read | ❌ | ✅ | ❌ | ✅ | ❌ |
| Knowledge Graph: Write | ❌ | ❌ | ❌ | ✅ | ❌ |
| Enrollment: Own | ❌ | ✅ | ❌ | ✅ | ❌ |
| Progress: Own | ❌ | ✅ | ❌ | ✅ | ❌ |
| Mastery: Own | ❌ | ✅ | ❌ | ✅ | ❌ |
| Pacing: Own | ❌ | ✅ | ❌ | ✅ | ❌ |
| Teaching Sessions: Own | ❌ | ✅ | ❌ | ✅ | ❌ |
| AI Teacher | ❌ | ✅ | ❌ | ❌ | ❌ |
| Parent Dashboard | ❌ | ❌ | ✅ | ✅ | ❌ |
| Reports: Own | ❌ | ✅ | ✅ | ✅ | ❌ |
| Content Ingestion | ❌ | ❌ | ❌ | ✅ | ❌ |
| Admin: All users | ❌ | ❌ | ❌ | ✅ | ❌ |
| AI Evaluation | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## 3. Frontend Page Access by Role

| Route | Page | Public | Student | Parent | Admin | Teacher |
|-------|------|:------:|:-------:|:------:|:-----:|:-------:|
| `/` | Landing | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/login` | Login | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/onboarding` | Student Onboarding | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/dashboard` | Student Dashboard | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/learning` | Learning Path | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/ai-tutor` | AI Tutor | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/assessment` | Assessment | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/progress` | Progress | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/student/profile` | Profile | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/parent/dashboard` | Parent Dashboard | ❌ | ❌ | ✅ | ✅ | ❌ |
| `/parent/student` | Student Detail | ❌ | ❌ | ✅ | ✅ | ❌ |
| `/parent/reports` | Reports | ❌ | ❌ | ✅ | ✅ | ❌ |
| `/parent/insights` | Insights | ❌ | ❌ | ✅ | ✅ | ❌ |
| `/admin/dashboard` | Admin Dashboard | ❌ | ❌ | ❌ | ✅ | ❌ |
| `/admin/students` | Students | ❌ | ❌ | ❌ | ✅ | ❌ |
| `/admin/analytics` | Analytics | ❌ | ❌ | ❌ | ✅ | ❌ |

**Note:** Currently, NO route guards are implemented. Any user can access any route.

---

## 4. Teacher Role Design (Proposed)

### 4.1 New Teacher Pages

| Route | Page | Description |
|-------|------|-------------|
| `/teacher/dashboard` | Teacher Dashboard | Overview of assigned students, recent activity |
| `/teacher/students` | Student Roster | List of assigned students with key metrics |
| `/teacher/students/{id}` | Student Detail | Detailed view of a specific student |
| `/teacher/courses` | My Courses | List of courses the teacher manages |
| `/teacher/courses/{id}/edit` | Course Editor | Create/edit course structure |
| `/teacher/content` | Content Management | Upload, review, approve AI-generated content |
| `/teacher/misconceptions` | Misconception Review | View all student misconceptions |
| `/teacher/reports` | Reports & Interventions | Generate and view reports |

### 4.2 New Teacher API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teacher/students` | List assigned students |
| GET | `/api/v1/teacher/students/{id}/progress` | Get student progress |
| GET | `/api/v1/teacher/students/{id}/mastery` | Get student mastery |
| GET | `/api/v1/teacher/students/{id}/misconceptions` | Get student misconceptions |
| GET | `/api/v1/teacher/students/{id}/sessions` | Get student session history |
| GET | `/api/v1/teacher/students/{id}/attempts` | Get student attempt details |
| GET | `/api/v1/teacher/students/{id}/interventions` | Get AI intervention recommendations |
| POST | `/api/v1/teacher/courses` | Create course (teacher-specific) |
| PUT | `/api/v1/teacher/courses/{id}` | Update course |
| DELETE | `/api/v1/teacher/courses/{id}` | Delete course (if no enrollments) |
| POST | `/api/v1/teacher/content/upload` | Upload content document |
| GET | `/api/v1/teacher/misconceptions` | All misconceptions across students |
| GET | `/api/v1/teacher/reports/generate/{student_id}` | Generate report |

### 4.3 Teacher-Student Assignment Table

```sql
CREATE TABLE teacher_student_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID NOT NULL REFERENCES users(id),
    student_id UUID NOT NULL REFERENCES users(id),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(teacher_id, student_id)
);
```

### 4.4 Teacher-Course Assignment Table

```sql
CREATE TABLE teacher_course_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID NOT NULL REFERENCES users(id),
    course_id UUID NOT NULL REFERENCES courses(id),
    role VARCHAR(20) NOT NULL DEFAULT 'instructor',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(teacher_id, course_id)
);
```

---

## 5. Role Hierarchy & Permissions

```
PUBLIC
  └── Health check
  └── Auth: Register, Login, Refresh
  └── Auth: Forgot/Reset Password
  └── Landing page

AUTHENTICATED (any logged-in user)
  └── View own profile
  └── Auth: Logout
  └── Reports: Own

STUDENT (extends Authenticated)
  └── Enroll in courses
  └── View learning path
  └── AI Tutor sessions
  └── Assessments
  └── View own progress, mastery, pacing
  └── View own session history

PARENT (extends Authenticated)
  └── View linked students' data
  └── Generate and view reports
  └── View insights

TEACHER (extends Authenticated) [NEW]
  └── Create/edit curriculum
  └── Upload content
  └── Review/approve AI content
  └── View assigned students' progress
  └── View student misconceptions
  └── View intervention recommendations
  └── Generate reports for assigned students

ADMIN (extends Authenticated)
  └── All Teacher permissions
  └── Manage all users
  └── Manage all courses
  └── Manage all enrollments
  └── View system analytics
  └── View audit logs
  └── Access evaluation tools
```
