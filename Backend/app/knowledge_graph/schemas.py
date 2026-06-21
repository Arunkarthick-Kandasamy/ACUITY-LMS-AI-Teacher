from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.common.types import EdgeRelationship


class KnowledgeEdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship: EdgeRelationship
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class KnowledgeEdgeResponse(BaseModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship: EdgeRelationship
    weight: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DeleteMessage(BaseModel):
    message: str


class PrerequisiteNode(BaseModel):
    node_id: str
    label: str
    relationship: EdgeRelationship
    weight: float

    model_config = {"from_attributes": True}


class PrerequisiteResponse(BaseModel):
    concept_id: str
    concept_title: str
    prerequisites: list[PrerequisiteNode]
