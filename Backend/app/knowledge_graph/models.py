from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base import Base, TimestampMixin, UUIDMixin
from app.common.compat import JSONB
from app.common.types import EdgeRelationship, NodeType


class KnowledgeNode(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_nodes"

    concept_id: Mapped[str | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"), index=True
    )
    objective_id: Mapped[str | None] = mapped_column(
        ForeignKey("learning_objectives.id", ondelete="SET NULL"), index=True
    )
    node_type: Mapped[NodeType] = mapped_column(nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    node_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    __table_args__ = (
        CheckConstraint("concept_id IS NOT NULL OR objective_id IS NOT NULL"),
    )

    concept: Mapped[Concept | None] = relationship(back_populates="knowledge_nodes")
    objective: Mapped[LearningObjective | None] = relationship(back_populates="knowledge_nodes")
    outgoing_edges: Mapped[list[KnowledgeEdge]] = relationship(
        back_populates="from_node",
        foreign_keys="KnowledgeEdge.source_node_id",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list[KnowledgeEdge]] = relationship(
        back_populates="to_node",
        foreign_keys="KnowledgeEdge.target_node_id",
        cascade="all, delete-orphan",
    )


class KnowledgeEdge(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_edges"
    __table_args__ = (
        UniqueConstraint("source_node_id", "target_node_id", "relationship"),
        CheckConstraint("source_node_id <> target_node_id"),
    )

    source_node_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_node_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_type: Mapped[EdgeRelationship] = mapped_column("relationship", nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    edge_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    from_node: Mapped[KnowledgeNode] = relationship(
        back_populates="outgoing_edges", foreign_keys=[source_node_id]
    )
    to_node: Mapped[KnowledgeNode] = relationship(
        back_populates="incoming_edges", foreign_keys=[target_node_id]
    )
