from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.knowledge_graph.models import KnowledgeEdge, KnowledgeNode
from app.knowledge_graph.repository import KnowledgeEdgeRepository, KnowledgeNodeRepository


class KnowledgeGraphService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.node_repo = KnowledgeNodeRepository(session)
        self.edge_repo = KnowledgeEdgeRepository(session)

    async def create_edge(self, **kwargs) -> KnowledgeEdge:
        source_id = kwargs["source_node_id"]
        target_id = kwargs["target_node_id"]

        if source_id == target_id:
            raise ValidationException(
                message="Source and target nodes must be different", code="SELF_REFERENCE"
            )

        source_node = await self.node_repo.get(source_id)
        if source_node is None:
            raise NotFoundException(message=f"Source node {source_id} not found")

        target_node = await self.node_repo.get(target_id)
        if target_node is None:
            raise NotFoundException(message=f"Target node {target_id} not found")

        exists = await self.edge_repo.exists(
            KnowledgeEdge.source_node_id == source_id,
            KnowledgeEdge.target_node_id == target_id,
            KnowledgeEdge.relationship_type == kwargs["relationship"],
        )
        if exists:
            raise ConflictException(
                message="An edge with the same source, target, and relationship already exists",
                code="EDGE_EXISTS",
            )

        kwargs["relationship_type"] = kwargs.pop("relationship")
        return await self.edge_repo.create(**kwargs)

    async def delete_edge(self, edge_id: str) -> None:
        deleted = await self.edge_repo.delete(edge_id)
        if not deleted:
            raise NotFoundException(message="Edge not found")

    async def get_prerequisites(self, concept_id: str) -> tuple[KnowledgeNode | None, list[dict]]:
        node = await self.node_repo.find_by_concept_id(concept_id)
        if node is None:
            raise NotFoundException(message="Knowledge node not found for this concept")

        incoming = await self.edge_repo.find_incoming(node.id)
        prerequisites = []
        for edge in incoming:
            prereq_node = await self.node_repo.get(edge.source_node_id)
            if prereq_node is not None:
                prerequisites.append({
                    "node_id": prereq_node.id,
                    "label": prereq_node.label,
                    "relationship": edge.relationship_type,
                    "weight": edge.weight,
                })
        return node, prerequisites
