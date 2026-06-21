from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.common.types import EdgeRelationship
from app.knowledge_graph.models import KnowledgeEdge, KnowledgeNode
from app.knowledge_graph.service import KnowledgeGraphService


def _make_node(**overrides) -> KnowledgeNode:
    defaults = dict(
        id="node-1",
        concept_id="con-1",
        objective_id=None,
        node_type="concept",
        label="Test Concept",
        node_metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return KnowledgeNode(**defaults)


def _make_edge(**overrides) -> KnowledgeEdge:
    defaults = dict(
        id="edge-1",
        source_node_id="node-1",
        target_node_id="node-2",
        relationship_type=EdgeRelationship.REQUIRES,
        weight=1.0,
        edge_metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return KnowledgeEdge(**defaults)


# ---------------------------------------------------------------------------
# KnowledgeGraphService — Edge CRUD
# ---------------------------------------------------------------------------

class TestKnowledgeGraphEdge:
    @pytest.mark.asyncio
    async def test_create_edge_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = KnowledgeGraphService(mock_session)
        service.node_repo.get = AsyncMock(side_effect=[
            _make_node(id="node-1", concept_id="con-1", label="Concept A"),
            _make_node(id="node-2", concept_id="con-2", label="Concept B"),
        ])
        service.edge_repo.exists = AsyncMock(return_value=False)
        service.edge_repo.create = AsyncMock(return_value=_make_edge())

        edge = await service.create_edge(
            source_node_id="node-1",
            target_node_id="node-2",
            relationship=EdgeRelationship.REQUIRES,
        )
        assert edge.relationship_type == EdgeRelationship.REQUIRES

    @pytest.mark.asyncio
    async def test_create_edge_self_reference(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)

        with pytest.raises(ValidationException) as exc:
            await service.create_edge(
                source_node_id="node-1",
                target_node_id="node-1",
                relationship=EdgeRelationship.REQUIRES,
            )
        assert exc.value.code == "SELF_REFERENCE"

    @pytest.mark.asyncio
    async def test_create_edge_missing_source(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.node_repo.get = AsyncMock(side_effect=[None])

        with pytest.raises(NotFoundException):
            await service.create_edge(
                source_node_id="bad-node",
                target_node_id="node-2",
                relationship=EdgeRelationship.REQUIRES,
            )

    @pytest.mark.asyncio
    async def test_create_edge_missing_target(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.node_repo.get = AsyncMock(side_effect=[
            _make_node(id="node-1"),
            None,
        ])

        with pytest.raises(NotFoundException):
            await service.create_edge(
                source_node_id="node-1",
                target_node_id="bad-node",
                relationship=EdgeRelationship.REQUIRES,
            )

    @pytest.mark.asyncio
    async def test_create_edge_duplicate(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.node_repo.get = AsyncMock(side_effect=[
            _make_node(id="node-1", concept_id="con-1"),
            _make_node(id="node-2", concept_id="con-2"),
        ])
        service.edge_repo.exists = AsyncMock(return_value=True)

        with pytest.raises(ConflictException) as exc:
            await service.create_edge(
                source_node_id="node-1",
                target_node_id="node-2",
                relationship=EdgeRelationship.REQUIRES,
            )
        assert exc.value.code == "EDGE_EXISTS"

    @pytest.mark.asyncio
    async def test_delete_edge_success(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.edge_repo.delete = AsyncMock(return_value=True)

        await service.delete_edge("edge-1")

    @pytest.mark.asyncio
    async def test_delete_edge_not_found(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.edge_repo.delete = AsyncMock(return_value=False)

        with pytest.raises(NotFoundException):
            await service.delete_edge("nonexistent")

    @pytest.mark.asyncio
    async def test_get_prerequisites_success(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)

        concept_node = _make_node(id="node-2", concept_id="con-2", label="Concept B")
        prereq_node = _make_node(id="node-1", concept_id="con-1", label="Concept A")
        edge = _make_edge(
            source_node_id="node-1",
            target_node_id="node-2",
            relationship_type=EdgeRelationship.REQUIRES,
        )

        service.node_repo.find_by_concept_id = AsyncMock(return_value=concept_node)
        service.edge_repo.find_incoming = AsyncMock(return_value=[edge])
        service.node_repo.get = AsyncMock(return_value=prereq_node)

        node, prereqs = await service.get_prerequisites("con-2")
        assert node.id == "node-2"
        assert len(prereqs) == 1
        assert prereqs[0]["label"] == "Concept A"

    @pytest.mark.asyncio
    async def test_get_prerequisites_node_not_found(self) -> None:
        mock_session = MagicMock()
        service = KnowledgeGraphService(mock_session)
        service.node_repo.find_by_concept_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await service.get_prerequisites("nonexistent")
