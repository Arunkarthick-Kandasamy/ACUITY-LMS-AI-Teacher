"""Comprehensive seed script that populates all tables with realistic mock data."""

import asyncio
import sys
import os
from datetime import datetime, timedelta, date
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.common.base import Base
from app.common.types import (
    UserRole, LessonStatus, ConceptContentType, QuestionType,
    EnrollmentStatus, SessionState, LessonProgressStatus,
    MisconceptionCategory, EdgeRelationship, AssessmentType,
    PaceStatus, NodeType,
)
from app.auth.security import get_password_hash
from app.config import settings

# Model imports
from app.users.models import User, StudentProfile, ParentStudentLink
from app.auth.models import RefreshToken
from app.institutional.models import School, SchoolDomain
from app.curriculum.models import (
    Course, Module, Lesson, Concept, ConceptContent,
    LearningObjective, Example, Exercise,
)
from app.enrollment.models import StudentCourseEnrollment, CourseSchedule
from app.assessments.models import (
    Assessment, AssessmentQuestion, AssessmentAttempt, AssessmentResponse, QuestionBank,
)
from app.knowledge_graph.models import KnowledgeNode, KnowledgeEdge
from app.moderation.models import ModerationQueue
from app.gamification.models import Badge, UserAchievement, Streak
from app.teacher.models import TeacherStudentAssignment, TeacherCourseAssignment
from app.mastery.models import MasteryRecord
from app.teaching.models import TeachingSession, LessonProgress, Attempt
from app.diagnosis.models import Misconception
from app.memory.models import StudentMemory, MemoryEntry
from app.reports.models import Report
from app.content_ingestion.models import ContentUpload, CurriculumDraft
from app.audit.models import AuditLog
from app.payments.models import PaymentPlan, Subscription
from app.parental_controls.models import ParentalControl
from app.messaging.models import Conversation, Message
from app.evaluation.models import TeacherMetricsSnapshot

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = None
AsyncSessionLocal = None


async def init():
    global engine, AsyncSessionLocal
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def teardown():
    if engine:
        await engine.dispose()


def dt(days_ago=0, hours_ago=0):
    return datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)


async def seed():
    await init()
    async with AsyncSessionLocal() as session:
        # ── USERS ──
        admin = User(
            email="admin@acuity.com",
            password_hash=get_password_hash("Admin123"),
            role=UserRole.ADMIN, full_name="Admin User", is_active=True,
            is_verified=True, country="US", preferred_language="en",
        )
        session.add(admin)

        teachers_data = [
            ("sarah.chen@acuity.com", "Sarah Chen", "US"),
            ("marcus.johnson@acuity.com", "Marcus Johnson", "US"),
            ("priya.sharma@acuity.com", "Priya Sharma", "IN"),
            ("james.wilson@acuity.com", "James Wilson", "UK"),
            ("emma.rodriguez@acuity.com", "Emma Rodriguez", "ES"),
        ]
        teachers = []
        for email, name, country in teachers_data:
            t = User(
                email=email, password_hash=get_password_hash("Teacher123"),
                role=UserRole.TEACHER, full_name=name, is_active=True,
                is_verified=True, country=country, preferred_language="en",
            )
            session.add(t)
            teachers.append(t)
        await session.flush()

        students_data = [
            ("alex.miller@acuity.com", "Alex Miller", "US", 9),
            ("bella.zhang@acuity.com", "Bella Zhang", "CN", 10),
            ("carlos.silva@acuity.com", "Carlos Silva", "BR", 8),
            ("diana.patel@acuity.com", "Diana Patel", "IN", 11),
            ("ethan.brown@acuity.com", "Ethan Brown", "US", 9),
            ("fiona.otoole@acuity.com", "Fiona O'Toole", "IE", 10),
            ("george.kim@acuity.com", "George Kim", "KR", 8),
            ("hannah.lee@acuity.com", "Hannah Lee", "SG", 11),
            ("isabella.rossi@acuity.com", "Isabella Rossi", "IT", 9),
            ("jack.thompson@acuity.com", "Jack Thompson", "AU", 10),
            ("katie.nguyen@acuity.com", "Katie Nguyen", "VN", 8),
            ("liam.o@acuity.com", "Liam O'Brien", "US", 11),
            ("mia.garcia@acuity.com", "Mia Garcia", "MX", 9),
            ("noah.wang@acuity.com", "Noah Wang", "US", 10),
            ("olivia.jones@acuity.com", "Olivia Jones", "UK", 8),
        ]
        students = []
        student_profiles = []
        for email, name, country, grade in students_data:
            u = User(
                email=email, password_hash=get_password_hash("Student123"),
                role=UserRole.STUDENT, full_name=name, is_active=True,
                is_verified=True, country=country, preferred_language="en",
            )
            session.add(u)
            await session.flush()
            sp = StudentProfile(
                user_id=u.id, grade_level=str(grade),
                current_streak_days=__import__('random').randint(0, 15),
                avg_session_duration_minutes=__import__('random').randint(15, 60),
            )
            session.add(sp)
            students.append(u)
            student_profiles.append(sp)
        await session.flush()

        parent_user = User(
            email="parent@acuity.com", password_hash=get_password_hash("Parent123"),
            role=UserRole.PARENT, full_name="Parent User", is_active=True,
            is_verified=True, country="US", preferred_language="en",
        )
        session.add(parent_user)
        await session.flush()

        # Link parent to first 3 students
        for sp in student_profiles[:3]:
            link = ParentStudentLink(
                parent_id=parent_user.id, student_id=sp.id,
                status="approved", parent_email="parent@acuity.com",
                requested_at=dt(30), approved_at=dt(28),
            )
            session.add(link)

        # ── SCHOOLS ──
        schools_data = [
            ("Lincoln High School", "LHS001", "123 Main St, Springfield, IL", "+1-555-0101"),
            ("Washington Academy", "WAS002", "456 Oak Ave, Portland, OR", "+1-555-0102"),
            ("International School of Science", "ISS003", "789 Elm Blvd, Austin, TX", "+1-555-0103"),
        ]
        schools = []
        for name, code, addr, phone in schools_data:
            s = School(name=name, code=code, address=addr, phone=phone, is_active=True)
            session.add(s)
            await session.flush()
            schools.append(s)

        # School domains
        domain_map = [
            (schools[0], "lincoln.edu", True),
            (schools[0], "lhs.school.org", False),
            (schools[1], "washington-academy.org", True),
            (schools[2], "iss.international", True),
        ]
        for school, domain, primary in domain_map:
            sd = SchoolDomain(school_id=school.id, domain=domain, is_primary=primary)
            session.add(sd)
        await session.flush()

        # ── COURSES ──
        courses_data = [
            ("MATH101", "Algebra I", "Foundational algebra including linear equations, inequalities, and functions", 120, 180, teachers[0].id),
            ("SCI101", "Biology Fundamentals", "Introduction to cell biology, genetics, and ecosystems", 140, 200, teachers[1].id),
            ("ENG101", "English Literature", "Analysis of classic and contemporary literature, essay writing", 100, 160, teachers[2].id),
            ("HIS101", "World History", "Survey of major world civilizations and historical events", 130, 190, teachers[3].id),
        ]
        courses = []
        for code, title, desc, hours, deadline, creator_id in courses_data:
            c = Course(
                code=code, title=title, description=desc,
                total_duration_hours=hours, default_deadline_days=deadline,
                is_published=True, created_by=creator_id,
            )
            session.add(c)
            courses.append(c)
        await session.flush()

        # ── MODULES & LESSONS & CONCEPTS ──
        module_templates = {
            "MATH101": [
                ("Foundations", "Basic principles and number systems", [
                    ("Numbers & Operations", "Understanding integers, fractions, and decimals", 45, [
                        ("Integer Operations", "explanation", "Covers addition, subtraction, multiplication, and division of integers"),
                        ("Fractions & Decimals", "explanation", "Converting between fractions and decimals, performing operations"),
                    ]),
                    ("Order of Operations", "Understanding PEMDAS and expression evaluation", 30, [
                        ("PEMDAS Rule", "explanation", "Parentheses, Exponents, Multiplication, Division, Addition, Subtraction"),
                        ("Evaluating Expressions", "explanation", "Substituting values and simplifying expressions"),
                    ]),
                ]),
                ("Linear Equations", "Solving and graphing linear equations", [
                    ("One-Variable Equations", "Solving equations with one variable", 50, [
                        ("Basic Equations", "explanation", "Solving ax + b = c type equations"),
                        ("Equations with Variables on Both Sides", "explanation", "Solving 2x + 5 = x + 10 type equations"),
                    ]),
                    ("Graphing Linear Equations", "Plotting lines on coordinate plane", 40, [
                        ("Slope & Intercept", "explanation", "Understanding y = mx + b form"),
                        ("Plotting Lines", "explanation", "Graphing lines using slope and y-intercept"),
                    ]),
                ]),
                ("Inequalities & Systems", "Advanced algebraic concepts", [
                    ("Linear Inequalities", "Solving and graphing inequalities", 45, [
                        ("Solving Inequalities", "explanation", "Solving and representing inequalities on number lines"),
                        ("Compound Inequalities", "explanation", "And/or compound inequality solutions"),
                    ]),
                ]),
            ],
            "SCI101": [
                ("Cell Biology", "Structure and function of cells", [
                    ("Cell Structure", "Organelles and their functions", 50, [
                        ("Cell Membrane", "explanation", "Structure and function of the phospholipid bilayer"),
                        ("Organelles", "explanation", "Nucleus, mitochondria, ribosomes, ER, Golgi apparatus"),
                    ]),
                    ("Cell Division", "Mitosis and meiosis", 45, [
                        ("Mitosis", "explanation", "Stages of mitotic cell division"),
                        ("Meiosis", "explanation", "Reduction division and gamete formation"),
                    ]),
                ]),
                ("Genetics", "Principles of heredity", [
                    ("Mendelian Genetics", "Laws of inheritance", 50, [
                        ("Punnett Squares", "explanation", "Predicting genotype and phenotype ratios"),
                        ("Dominant & Recessive Traits", "explanation", "Understanding allele interactions"),
                    ]),
                    ("DNA & RNA", "Molecular genetics", 55, [
                        ("DNA Structure", "explanation", "Double helix, base pairing, replication"),
                        ("Transcription & Translation", "explanation", "Protein synthesis from DNA to protein"),
                    ]),
                ]),
                ("Ecosystems", "Interactions in nature", [
                    ("Food Webs", "Energy flow through ecosystems", 40, [
                        ("Trophic Levels", "explanation", "Producers, consumers, and decomposers"),
                        ("Energy Pyramids", "explanation", "Energy transfer efficiency between trophic levels"),
                    ]),
                ]),
            ],
            "ENG101": [
                ("Literary Analysis", "Tools for analyzing literature", [
                    ("Elements of Fiction", "Plot, character, setting, theme", 45, [
                        ("Plot Structure", "explanation", "Exposition, rising action, climax, falling action, resolution"),
                        ("Character Analysis", "explanation", "Protagonist, antagonist, dynamic vs static characters"),
                    ]),
                    ("Poetic Devices", "Understanding poetry techniques", 35, [
                        ("Rhyme & Meter", "explanation", "Types of rhyme schemes and metrical patterns"),
                        ("Figurative Language", "explanation", "Metaphor, simile, personification, imagery"),
                    ]),
                ]),
                ("Essay Writing", "Crafting effective essays", [
                    ("Structure & Thesis", "Building a strong foundation", 40, [
                        ("Thesis Statements", "explanation", "Crafting focused, arguable thesis statements"),
                        ("Essay Organization", "explanation", "Introduction, body paragraphs, conclusion structure"),
                    ]),
                    ("Argumentation", "Persuasive writing techniques", 45, [
                        ("Evidence & Reasoning", "explanation", "Using textual evidence and logical reasoning"),
                        ("Counterarguments", "explanation", "Addressing opposing viewpoints effectively"),
                    ]),
                ]),
            ],
            "HIS101": [
                ("Ancient Civilizations", "Early human societies", [
                    ("Mesopotamia & Egypt", "Cradle of civilization", 50, [
                        ("River Valley Civilizations", "explanation", "Tigris/Euphrates and Nile river valley societies"),
                        ("Ancient Egypt", "explanation", "Pharaohs, pyramids, and Egyptian culture"),
                    ]),
                    ("Classical Greece & Rome", "Foundations of Western civilization", 55, [
                        ("Greek Democracy", "explanation", "Athenian democracy and Greek philosophy"),
                        ("Roman Republic", "explanation", "From republic to empire, Roman law and governance"),
                    ]),
                ]),
                ("Medieval to Modern", "Transformation of the world", [
                    ("The Renaissance", "Rebirth of art and learning", 45, [
                        ("Art & Innovation", "explanation", "Da Vinci, Michelangelo, and Renaissance humanism"),
                        ("Scientific Revolution", "explanation", "Copernicus, Galileo, and the birth of modern science"),
                    ]),
                    ("Age of Exploration", "Global connections", 40, [
                        ("Voyages & Discovery", "explanation", "Columbus, Magellan, and global trade routes"),
                        ("Colonial Encounters", "explanation", "Impact of European colonization on indigenous peoples"),
                    ]),
                ]),
            ],
        }

        exercises_templates = {
            "Integer Operations": [
                ("mcq", "What is -5 + 12?", '{"A": "7", "B": "-7", "C": "17", "D": "-17"}', "A", 0.3, 1),
                ("numeric", "Calculate: 8 × (-3)", None, "-24", 0.4, 1),
            ],
            "PEMDAS Rule": [
                ("mcq", "What is the first step in PEMDAS?", '{"A": "Exponents", "B": "Parentheses", "C": "Multiplication", "D": "Division"}', "B", 0.3, 1),
                ("numeric", "3 + 4 × 2 = ?", None, "11", 0.5, 2),
            ],
            "Cell Membrane": [
                ("mcq", "What is the primary function of the cell membrane?", '{"A": "Protein synthesis", "B": "Regulate passage of materials", "C": "Energy production", "D": "Cell division"}', "B", 0.4, 1),
                ("multi_select", "Which molecules are found in the cell membrane?", '{"A": "Phospholipids", "B": "Proteins", "C": "DNA", "D": "Cholesterol"}', '["A","B","D"]', 0.6, 2),
            ],
            "Plot Structure": [
                ("mcq", "What is the highest point of tension in a story called?", '{"A": "Exposition", "B": "Climax", "C": "Resolution", "D": "Rising action"}', "B", 0.3, 1),
                ("short_answer", "What term describes the main character in a story?", None, "protagonist", 0.4, 1),
            ],
            "River Valley Civilizations": [
                ("mcq", "Which rivers were associated with early Mesopotamian civilization?", '{"A": "Nile and Congo", "B": "Tigris and Euphrates", "C": "Indus and Ganges", "D": "Yellow and Yangtze"}', "B", 0.4, 1),
                ("true_false", "The Egyptian civilization developed along the Nile River.", None, "true", 0.2, 1),
            ],
        }

        all_modules = []
        all_lessons = []
        all_concepts = []
        all_exercises = []

        for course in courses:
            mod_templates = module_templates[course.code]
            for mi, (mod_title, mod_desc, lessons_templates) in enumerate(mod_templates):
                mod = Module(
                    course_id=course.id, title=mod_title,
                    description=mod_desc, order_index=mi + 1,
                    estimated_duration_hours=sum(lt[2] for lt in lessons_templates) // 45 + 1,
                )
                session.add(mod)
                all_modules.append(mod)
                await session.flush()

                for li, (lesson_title, lesson_desc, duration_minutes, concepts_templates) in enumerate(lessons_templates):
                    les = Lesson(
                        module_id=mod.id, title=lesson_title,
                        content_url=f"https://content.acuity.com/lessons/{course.code.lower()}/lesson-{mi + 1}-{li + 1}",
                        order_index=li + 1, estimated_duration_minutes=duration_minutes,
                        is_required=True, status=LessonStatus.PUBLISHED,
                    )
                    session.add(les)
                    all_lessons.append(les)
                    await session.flush()

                    for ci, (concept_title, content_type, content_text) in enumerate(concepts_templates):
                        conc = Concept(
                            lesson_id=les.id, title=concept_title,
                            description=content_text[:200],
                            order_index=ci + 1, estimated_duration_minutes=15,
                        )
                        session.add(conc)
                        all_concepts.append(conc)
                        await session.flush()

                        cc = ConceptContent(
                            concept_id=conc.id, content_type=ConceptContentType(content_type),
                            content=content_text, order_index=0,
                        )
                        session.add(cc)

                        lo_code = f"{course.code}-M{mi+1}L{li+1}C{ci+1}"
                        lo = LearningObjective(
                            lesson_id=les.id, code=lo_code,
                            description=f"Understand {concept_title.lower()}",
                            success_criterion={"min_score": 0.7, "required_exercises": 2},
                            order_index=ci + 1,
                        )
                        session.add(lo)

                        # Learning Objective Example
                        ex = Example(
                            concept_id=conc.id,
                            content=f"Example illustrating {concept_title.lower()}: Consider a practical scenario where this concept applies...",
                            explanation=f"This demonstrates how {concept_title.lower()} works in context.",
                            order_index=0,
                        )
                        session.add(ex)

                        # Exercises
                        key = concept_title
                        if key in exercises_templates:
                            for ei, (qtype, prompt, opts, answer, difficulty, marks) in enumerate(exercises_templates[key]):
                                ex_data = Exercise(
                                    concept_id=conc.id, question_type=QuestionType(qtype),
                                    prompt=prompt, options=__import__('json').loads(opts) if opts else None,
                                    correct_answer=answer, difficulty=difficulty, order_index=ei + 1,
                                )
                                session.add(ex_data)
                                all_exercises.append(ex_data)
                        else:
                            ex_data = Exercise(
                                concept_id=conc.id, question_type=QuestionType.MCQ,
                                prompt=f"Basic question about {concept_title.lower()}?",
                                options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                                correct_answer="A", difficulty=0.5, order_index=1,
                            )
                            session.add(ex_data)
                            all_exercises.append(ex_data)

        await session.flush()

        # ── ENROLLMENTS ──
        enrolled_ids = set()
        for si, sp in enumerate(student_profiles):
            course = courses[si % len(courses)]
            key = (sp.id, course.id)
            if key not in enrolled_ids:
                enrolled_ids.add(key)
                enroll = StudentCourseEnrollment(
                    student_id=sp.id, course_id=course.id,
                    status=EnrollmentStatus.ACTIVE,
                    started_at=dt(__import__('random').randint(1, 60)),
                    target_completion_date=date.today() + timedelta(days=course.default_deadline_days),
                )
                session.add(enroll)
                await session.flush()

                cs = CourseSchedule(
                    enrollment_id=enroll.id, target_lessons_per_week=3,
                    current_week=__import__('random').randint(1, 8),
                    pace_status=list(PaceStatus)[__import__('random').randint(0, 2)],
                    milestones=[{"week": i, "description": f"Week {i} milestone"} for i in range(1, 5)],
                )
                session.add(cs)

        await session.flush()

        # ── TEACHER ASSIGNMENTS ──
        for ti, teacher in enumerate(teachers):
            tca = TeacherCourseAssignment(
                teacher_id=teacher.id, course_id=courses[ti % len(courses)].id,
                role="instructor",
            )
            session.add(tca)
            # Each teacher gets a few students
            for sp in student_profiles[ti * 3:(ti + 1) * 3]:
                tsa = TeacherStudentAssignment(
                    teacher_id=teacher.id, student_id=sp.id,
                )
                session.add(tsa)

        await session.flush()

        # ── ASSESSMENTS ──
        assessment_templates = [
            ("MATH101", AssessmentType.QUIZ, 0.7, 30, 2, "Week 1 Check-in", "Numbers & Operations"),
            ("MATH101", AssessmentType.CHAPTER_TEST, 0.8, 60, 1, "Chapter 1 Test", "Foundations"),
            ("MATH101", AssessmentType.PRACTICE_TEST, 0.6, 45, 3, "Practice: Linear Equations", "Linear Equations"),
            ("SCI101", AssessmentType.QUIZ, 0.7, 30, 2, "Cell Biology Quiz", "Cell Biology"),
            ("SCI101", AssessmentType.CHAPTER_TEST, 0.8, 60, 1, "Biology Chapter 2 Test", "Genetics"),
            ("ENG101", AssessmentType.QUIZ, 0.7, 25, 2, "Literary Terms Quiz", "Literary Analysis"),
            ("HIS101", AssessmentType.QUIZ, 0.7, 30, 2, "Ancient Civilizations Quiz", "Ancient Civilizations"),
        ]

        question_bank_items = []
        all_assessments = []
        assessment_questions_map = {}  # ass.id -> list of questions
        for course_code, atype, pass_score, time_limit, max_at, title, module_title in assessment_templates:
            course = next(c for c in courses if c.code == course_code)
            mod = next((m for m in all_modules if m.course_id == course.id and module_title in m.title), None)
            les = next((l for l in all_lessons if mod and l.module_id == mod.id), None)

            ass = Assessment(
                title=title, description=f"{title} assessment for {course.title}",
                course_id=course.id, module_id=mod.id if mod else None,
                lesson_id=les.id if les else None,
                assessment_type=atype, passing_score=pass_score,
                time_limit=time_limit, max_attempts=max_at,
                is_published=True, created_by=course.created_by,
            )
            session.add(ass)
            all_assessments.append(ass)
            await session.flush()

            # Questions
            q_types = [QuestionType.MCQ, QuestionType.MCQ, QuestionType.TRUE_FALSE, QuestionType.MCQ]
            created_questions = []
            for qi, qt in enumerate(q_types[:4]):
                q = AssessmentQuestion(
                    assessment_id=ass.id, question_type=qt,
                    prompt=f"Question {qi + 1}: Sample {qt.value} question for {title}",
                    options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"} if qt != QuestionType.TRUE_FALSE else None,
                    correct_answer="A" if qt != QuestionType.TRUE_FALSE else "true",
                    difficulty=0.4 + qi * 0.1, marks=1.0,
                    explanation=f"This is the explanation for question {qi + 1}.",
                    order_index=qi + 1,
                )
                session.add(q)
                await session.flush()

                # Add to question bank too
                qb = QuestionBank(
                    course_id=course.id, lesson_id=les.id if les else None,
                    question_type=qt, prompt=q.prompt, options=q.options,
                    correct_answer=q.correct_answer, difficulty=q.difficulty,
                    marks=q.marks, explanation=q.explanation,
                    tags=[course.code.lower(), atype.value],
                )
                session.add(qb)
                question_bank_items.append(qb)
                created_questions.append(q)

            assessment_questions_map[ass.id] = created_questions

        await session.flush()

        # ── ASSESSMENT ATTEMPTS & RESPONSES ──
        for si, sp in enumerate(student_profiles[:8]):
            for ass in all_assessments[:3]:
                n_attempts = __import__('random').randint(1, 2)
                for an in range(1, n_attempts + 1):
                    att = AssessmentAttempt(
                        assessment_id=ass.id, student_id=sp.id,
                        started_at=dt(__import__('random').randint(1, 30)),
                        completed_at=dt(__import__('random').randint(0, 29)),
                        score=__import__('random').uniform(0.3, 1.0),
                        percentage=__import__('random').uniform(30, 100),
                        passed=__import__('random').choices([True, False], weights=[7, 3])[0],
                        attempt_number=an,
                    )
                    session.add(att)
                    await session.flush()

                    for q in assessment_questions_map[ass.id]:
                        resp = AssessmentResponse(
                            attempt_id=att.id, question_id=q.id,
                            response=__import__('random').choice(["A", "B", "C", "D", "true", "false"]),
                            is_correct=__import__('random').choices([True, False], weights=[7, 3])[0],
                            score=__import__('random').uniform(0, 1),
                            time_taken_seconds=__import__('random').randint(10, 120),
                        )
                        session.add(resp)

        await session.flush()

        # ── KNOWLEDGE GRAPH ──
        nodes = []
        for ci, conc in enumerate(all_concepts[:20]):
            kn = KnowledgeNode(
                concept_id=conc.id, node_type=NodeType.CONCEPT,
                label=conc.title,
                node_metadata={"course": "general", "difficulty": "intermediate"},
            )
            session.add(kn)
            nodes.append(kn)
        await session.flush()

        for i in range(len(nodes) - 1):
            ke = KnowledgeEdge(
                source_node_id=nodes[i].id, target_node_id=nodes[i + 1].id,
                relationship_type=EdgeRelationship.REQUIRES, weight=0.8,
            )
            session.add(ke)
        for i in range(0, len(nodes) - 2, 2):
            ke = KnowledgeEdge(
                source_node_id=nodes[i].id, target_node_id=nodes[i + 2].id,
                relationship_type=EdgeRelationship.REINFORCES, weight=0.5,
            )
            session.add(ke)

        await session.flush()

        # ── MODERATION QUEUE ──
        mod_statuses = ["pending", "approved", "rejected"]
        for mi, (content_type, status) in enumerate([
            ("lesson", "pending"), ("exercise", "pending"), ("course", "approved"),
            ("lesson", "pending"), ("assessment", "rejected"), ("course", "pending"),
        ]):
            mq = ModerationQueue(
                content_id=str(uuid4()), content_type=content_type,
                uploader_id=teachers[mi % len(teachers)].id, status=status,
                reviewer_id=admin.id if status != "pending" else None,
                review_notes="Looks good" if status == "approved" else "Needs revision" if status == "rejected" else None,
                reviewed_at=dt(1) if status != "pending" else None,
                flag_reason="Inappropriate content" if status == "rejected" else None,
            )
            session.add(mq)

        await session.flush()

        # ── BADGES & ACHIEVEMENTS ──
        badges_data = [
            ("First Lesson", "Complete your first lesson", "milestone", "Complete one lesson"),
            ("Quick Learner", "Complete 5 lessons in a week", "milestone", "Complete 5 lessons in 7 days"),
            ("Perfect Score", "Get 100% on any assessment", "mastery", "Score 100% on an assessment"),
            ("Streak Master", "Maintain a 7-day streak", "streak", "Study for 7 consecutive days"),
            ("Knowledge Seeker", "Attempt 100 exercises", "milestone", "Complete 100 exercise attempts"),
        ]
        badges = []
        for name, desc, cat, criteria in badges_data:
            b = Badge(name=name, description=desc, category=cat, criteria=criteria)
            session.add(b)
            badges.append(b)
        await session.flush()

        for sp in student_profiles[:5]:
            ua = UserAchievement(user_id=sp.user_id, badge_id=badges[__import__('random').randint(0, len(badges) - 1)].id)
            session.add(ua)

        await session.flush()

        # ── STREAKS ──
        for u in students:
            s = Streak(
                user_id=u.id,
                current_streak=__import__('random').randint(0, 10),
                longest_streak=__import__('random').randint(5, 30),
                last_activity_date=dt(__import__('random').randint(0, 2)),
            )
            session.add(s)

        await session.flush()

        # ── TEACHING SESSIONS ──
        for sp in student_profiles[:5]:
            course = courses[student_profiles.index(sp) % len(courses)]
            concepts_for_course = [c for c in all_concepts if any(l.id == c.lesson_id for l in all_lessons if l.module_id in [m.id for m in all_modules if m.course_id == course.id])]
            if concepts_for_course:
                ts = TeachingSession(
                    student_id=sp.id, course_id=course.id,
                    current_concept_id=concepts_for_course[0].id,
                    current_lesson_id=next((l.id for l in all_lessons if l.id == concepts_for_course[0].lesson_id), None),
                    state=SessionState.COMPLETED,
                    context={"topic": concepts_for_course[0].title, "mode": "tutoring"},
                    started_at=dt(10), last_activity_at=dt(1), completed_at=dt(1),
                )
                session.add(ts)

        await session.flush()

        # ── LESSON PROGRESS ──
        for sp in student_profiles[:5]:
            for les in all_lessons[:5]:
                lp = LessonProgress(
                    student_id=sp.id, lesson_id=les.id,
                    status=list(LessonProgressStatus)[__import__('random').randint(0, 3)],
                    started_at=dt(__import__('random').randint(1, 30)),
                    completed_at=dt(__import__('random').randint(0, 29)) if __import__('random').choices([True, False])[0] else None,
                    time_spent_seconds=__import__('random').randint(120, 3600),
                    completion_percentage=__import__('random').uniform(0, 100),
                )
                session.add(lp)

        await session.flush()

        # ── ATTEMPTS (teaching session exercises) ──
        for sp in student_profiles[:5]:
            for ex in all_exercises[:10]:
                att = Attempt(
                    student_id=sp.id, exercise_id=ex.id,
                    response=str(__import__('random').randint(0, 4)),
                    is_correct=__import__('random').choices([True, False], weights=[7, 3])[0],
                    score=__import__('random').uniform(0, 1),
                    time_taken_seconds=__import__('random').randint(15, 300),
                    attempt_number=1,
                    ai_feedback="Good attempt! Consider reviewing the steps again.",
                )
                session.add(att)

        await session.flush()

        # ── MASTERY RECORDS ──
        for sp in student_profiles[:5]:
            for conc in all_concepts[:10]:
                mr = MasteryRecord(
                    student_id=sp.id, concept_id=conc.id,
                    mastery_level=__import__('random').uniform(0.2, 1.0),
                    last_attempted_at=dt(__import__('random').randint(0, 10)),
                    total_attempts=__import__('random').randint(1, 10),
                    consecutive_correct=__import__('random').randint(0, 5),
                    next_review_at=dt(-__import__('random').randint(1, 7)),
                )
                session.add(mr)

        await session.flush()

        # ── MISCONCEPTIONS ──
        for sp in student_profiles[:5]:
            for conc in all_concepts[:3]:
                mc = Misconception(
                    student_id=sp.id, concept_id=conc.id,
                    category=list(MisconceptionCategory)[__import__('random').randint(0, 3)],
                    description=f"Student struggles with {conc.title.lower()} - common error pattern observed",
                    evidence=[{"exercise": f"Exercise on {conc.title}", "error": "misapplied rule"}],
                    frequency=__import__('random').randint(1, 5),
                    is_resolved=__import__('random').choices([True, False], weights=[4, 6])[0],
                    resolved_at=dt(5) if __import__('random').choices([True, False], weights=[4, 6])[0] else None,
                )
                session.add(mc)

        await session.flush()

        # ── STUDENT MEMORIES ──
        for sp in student_profiles[:5]:
            sm = StudentMemory(
                student_id=sp.id, key="learning_style",
                value={"preferred_mode": "visual", "attention_span": 25},
                importance=0.8,
            )
            session.add(sm)
            me = MemoryEntry(
                student_id=sp.id, memory_key="struggle_area",
                memory_text=f"Student found concept '{all_concepts[0].title}' challenging",
                confidence=0.7, is_active=True,
            )
            session.add(me)

        await session.flush()

        # ── CONTENT UPLOADS & DRAFTS ──
        upload = ContentUpload(
            user_id=teachers[0].id, filename="algebra_lesson_plan.pdf",
            file_type="pdf", file_size=2450000,
            file_path="/uploads/algebra_lesson_plan.pdf",
            status="completed", extracted_text="Sample extracted text from PDF...",
        )
        session.add(upload)
        await session.flush()

        draft = CurriculumDraft(
            upload_id=upload.id, created_by=teachers[0].id,
            title="Algebra Lesson Plan Draft", status="draft",
            generated_data={"sections": ["warmup", "main", "practice"], "duration_minutes": 50},
            course_id=courses[0].id,
        )
        session.add(draft)

        await session.flush()

        # ── REPORTS ──
        user_names_by_profile = {sp.id: students[i].full_name for i, sp in enumerate(student_profiles)}
        for sp in student_profiles[:5]:
            r = Report(
                student_id=sp.id, parent_id=parent_user.id,
                report_type="weekly", title=f"Weekly Report - {user_names_by_profile[sp.id]}",
                summary=f"Good progress this week. Completed 3 lessons and scored 85% on assessments.",
                recommendations=[{"action": "Review cell biology", "priority": "high"}, {"action": "Practice linear equations", "priority": "medium"}],
                report_data={"lessons_completed": 3, "avg_score": 85, "time_spent_minutes": 240},
                is_read=__import__('random').choices([True, False])[0],
            )
            session.add(r)

        await session.flush()

        # ── AUDIT LOGS ──
        actions = ["user.login", "user.create", "course.create", "assessment.publish", "content.upload"]
        for _ in range(20):
            al = AuditLog(
                user_id=__import__('random').choice(students + teachers + [admin]).id,
                action=__import__('random').choice(actions),
                entity_type=__import__('random').choice(["user", "course", "assessment", "lesson", "content"]),
                entity_id=str(uuid4()),
                new_value={"status": "completed", "timestamp": str(datetime.utcnow())},
            )
            session.add(al)

        await session.flush()

        # ── TEACHER METRICS SNAPSHOT ──
        for ti, teacher in enumerate(teachers):
            tms = TeacherMetricsSnapshot(
                snapshot_label=f"{teacher.full_name} - Weekly Metrics",
                period_start=dt(7), period_end=dt(0),
                total_sessions=__import__('random').randint(5, 30),
                concepts_taught=__import__('random').randint(3, 12),
                concept_mastery_rate=__import__('random').uniform(0.5, 0.95),
                remediation_rate=__import__('random').uniform(0.2, 0.6),
                misconception_detection_rate=__import__('random').uniform(0.3, 0.8),
                prerequisite_routing_frequency=__import__('random').uniform(0.1, 0.4),
                session_completion_rate=__import__('random').uniform(0.7, 1.0),
                avg_mastery_gain=__import__('random').uniform(0.1, 0.5),
                avg_execution_duration_ms=__import__('random').uniform(500, 5000),
                total_model_calls=__import__('random').randint(50, 500),
            )
            session.add(tms)

        await session.flush()

        # ── PAYMENT PLANS & SUBSCRIPTIONS ──
        plans_data = [
            ("Free", "Basic access with limited features", 0, 0, "USD", 1, "Basic features"),
            ("Pro", "Full access for individual teachers", 29.99, 299.99, "USD", 5, "All features, priority support"),
            ("School", "Complete platform for schools", 99.99, 999.99, "USD", 100, "All features, dedicated support, analytics"),
        ]
        plans = []
        for name, desc, pm, py, cur, max_s, features in plans_data:
            p = PaymentPlan(
                name=name, description=desc, price_monthly=pm, price_yearly=py,
                currency=cur, max_students=max_s, features=features, is_active=True,
            )
            session.add(p)
            plans.append(p)
        await session.flush()

        sub = Subscription(
            user_id=teachers[0].id, plan_id=plans[1].id, status="active",
            billing_cycle="monthly", current_period_start=dt(30), current_period_end=dt(-30),
        )
        session.add(sub)

        await session.flush()

        # ── PARENTAL CONTROLS ──
        for sp in student_profiles[:3]:
            pc = ParentalControl(
                student_id=sp.id, daily_limit_minutes=120,
                break_interval_minutes=45, break_duration_minutes=10,
                sleep_mode_enabled=True, sleep_start_hour=22, sleep_end_hour=7,
            )
            session.add(pc)

        await session.flush()

        # ── MESSAGING ──
        for si, sp in enumerate(student_profiles[:3]):
            conv = Conversation(
                participant_one=parent_user.id, participant_two=sp.user_id,
                last_message_at=dt(1),
            )
            session.add(conv)
            await session.flush()

            msg = Message(
                conversation_id=conv.id, sender_id=parent_user.id,
                content=f"How is your progress going, {user_names_by_profile[sp.id]}?",
                is_read=__import__('random').choices([True, False])[0],
            )
            session.add(msg)
            reply = Message(
                conversation_id=conv.id, sender_id=sp.user_id,
                content="I'm doing well! Just finished my math homework.",
                is_read=True,
            )
            session.add(reply)

        await session.flush()

        await session.commit()
        print("All seed data created successfully!")
        print(f"   - Users: {2 + len(teachers) + len(students)} (1 admin, {len(teachers)} teachers, {len(students)} students, 1 parent)")
        print(f"   - Schools: {len(schools)}")
        print(f"   - Courses: {len(courses)}")
        print(f"   - Modules: {len(all_modules)}")
        print(f"   - Lessons: {len(all_lessons)}")
        print(f"   - Concepts: {len(all_concepts)}")
        print(f"   - Exercises: {len(all_exercises)}")
        print(f"   - Assessments: {len(all_assessments)}")
        print(f"   - Knowledge Nodes: {len(nodes)}")
        print(f"   - Badges: {len(badges)}")
        print(f"   - Enrollments: {len(enrolled_ids)}")

    await teardown()


asyncio.run(seed())
