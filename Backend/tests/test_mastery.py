from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import NotFoundException
from app.mastery.models import MasteryRecord
from app.mastery.service import MasteryService


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_student_profile() -> MagicMock:
    profile = MagicMock()
    profile.id = "sp-1"
    profile.user_id = "user-1"
    return profile


def _make_mastery_record(**overrides) -> MasteryRecord:
    defaults = dict(
        id="mr-1",
        student_id="sp-1",
        concept_id="con-1",
        mastery_level=0.85,
        last_attempted_at=datetime.now(timezone.utc),
        total_attempts=10,
        consecutive_correct=8,
        next_review_at=None,
    )
    defaults.update(overrides)
    return MasteryRecord(**defaults)


# ---------------------------------------------------------------------------
# MasteryService
# ---------------------------------------------------------------------------

class TestMasteryService:
    @pytest.mark.asyncio
    async def test_get_overview(self, mock_session, mock_student_profile) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.mastery_repo.find_by_student = AsyncMock(
            return_value=[_make_mastery_record()]
        )

        records = await service.get_overview("user-1")
        assert len(records) == 1
        assert records[0].mastery_level == 0.85

    @pytest.mark.asyncio
    async def test_get_by_concept(self, mock_session, mock_student_profile) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.mastery_repo.find_by_student_and_concept = AsyncMock(
            return_value=_make_mastery_record()
        )

        record = await service.get_by_concept("con-1", "user-1")
        assert record is not None
        assert record.concept_id == "con-1"

    @pytest.mark.asyncio
    async def test_get_by_concept_none(self, mock_session, mock_student_profile) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.mastery_repo.find_by_student_and_concept = AsyncMock(return_value=None)

        record = await service.get_by_concept("con-1", "user-1")
        assert record is None

    @pytest.mark.asyncio
    async def test_get_course_summary(self, mock_session, mock_student_profile) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)
        service.mastery_repo.find_by_student_and_course = AsyncMock(
            return_value=[_make_mastery_record()]
        )

        records = await service.get_course_summary("course-1", "user-1")
        assert len(records) == 1

    @pytest.mark.asyncio
    async def test_recalculate_mastery_new_record(self, mock_session, mock_student_profile) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=mock_student_profile)

        mock_row = MagicMock()
        mock_row[0] = 5
        mock_row[1] = 0.8
        mock_row[2] = 4
        mock_row[3] = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.one = MagicMock(return_value=mock_row)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service.mastery_repo.find_by_student_and_concept = AsyncMock(return_value=None)
        service.mastery_repo.create = AsyncMock(return_value=_make_mastery_record())

        record = await service.recalculate_mastery("sp-1", "con-1")
        assert record.mastery_level == 0.85

    @pytest.mark.asyncio
    async def test_recalculate_mastery_existing_record(self, mock_session) -> None:
        service = MasteryService(mock_session)

        mock_row = MagicMock()
        mock_row[0] = 3
        mock_row[1] = 0.9
        mock_row[2] = 3
        mock_row[3] = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.one = MagicMock(return_value=mock_row)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service.mastery_repo.find_by_student_and_concept = AsyncMock(
            return_value=_make_mastery_record()
        )
        service.mastery_repo.update = AsyncMock(return_value=_make_mastery_record(mastery_level=0.9))

        record = await service.recalculate_mastery("sp-1", "con-1")
        assert record.mastery_level == 0.9

    @pytest.mark.asyncio
    async def test_get_overview_no_profile(self, mock_session) -> None:
        service = MasteryService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_overview("user-1")
