import asyncio
from app.database import AsyncSessionLocal
from app.users.models import User, StudentProfile
from app.common.types import UserRole
from app.curriculum.models import Course, Subject, Lesson
from app.auth.security import get_password_hash

async def seed():
    async with AsyncSessionLocal() as session:
        # Create admin
        admin = User(email="admin@acuity.com", hashed_password=get_password_hash("admin123"), role=UserRole.ADMIN, full_name="Admin User", is_active=True)
        session.add(admin)
        
        # Create teacher
        teacher = User(email="teacher@acuity.com", hashed_password=get_password_hash("teacher123"), role=UserRole.TEACHER, full_name="Jane Teacher", is_active=True)
        session.add(teacher)
        
        # Create student
        student = User(email="student@acuity.com", hashed_password=get_password_hash("student123"), role=UserRole.STUDENT, full_name="John Student", is_active=True)
        session.add(student)
        await session.flush()
        sp = StudentProfile(user_id=student.id)
        session.add(sp)
        
        # Create subject and course
        subject = Subject(name="Mathematics", code="MATH101", description="Basic Math")
        session.add(subject)
        await session.flush()
        course = Course(name="Algebra Basics", subject_id=subject.id, description="Introduction to Algebra", code="ALG101")
        session.add(course)
        await session.flush()
        
        # Create lessons
        for i in range(1, 4):
            lesson = Lesson(course_id=course.id, title=f"Chapter {i}: Algebra Fundamentals", order=i, content_type="text", content=f"Content for chapter {i}")
            session.add(lesson)
        
        await session.commit()
        print("Seed data created successfully!")

asyncio.run(seed())
