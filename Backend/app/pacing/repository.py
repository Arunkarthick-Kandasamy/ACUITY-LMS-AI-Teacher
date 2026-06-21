from __future__ import annotations

from app.common.repository import Repository
from app.enrollment.models import CourseSchedule


class CourseScheduleRepository(Repository[CourseSchedule]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(CourseSchedule, session)
