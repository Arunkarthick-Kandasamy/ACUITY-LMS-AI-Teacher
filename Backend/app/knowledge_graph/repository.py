from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.knowledge_graph.models import KnowledgeEdge, KnowledgeNode


class KnowledgeNodeRepository(Repository[KnowledgeNode]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(KnowledgeNode, session)

    async def find_by_concept_id(self, concept_id: str) -> KnowledgeNode | None:
        stmt = select(KnowledgeNode).where(KnowledgeNode.concept_id == concept_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_objective_id(self, objective_id: str) -> KnowledgeNode | None:
        stmt = select(KnowledgeNode).where(KnowledgeNode.objective_id == objective_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class KnowledgeEdgeRepository(Repository[KnowledgeEdge]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(KnowledgeEdge, session)

    async def find_outgoing(self, node_id: str) -> list[KnowledgeEdge]:
        stmt = select(KnowledgeEdge).where(KnowledgeEdge.source_node_id == node_id)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_incoming(self, node_id: str) -> list[KnowledgeEdge]:
        stmt = select(KnowledgeEdge).where(KnowledgeEdge.target_node_id == node_id)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
