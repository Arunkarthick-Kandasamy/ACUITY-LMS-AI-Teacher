from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    status: str
    review_notes: str | None = None


class ModerationItemResponse(BaseModel):
    id: str
    content_id: str
    content_type: str
    uploader_id: str
    status: str
    reviewer_id: str | None = None
    review_notes: str | None = None
    reviewed_at: datetime | None = None
    flag_reason: str | None = None
    created_at: datetime
    uploader_name: str = ""

    model_config = {"from_attributes": True}
