"""Unit tests for ControlGraphService — row/column assignment, edges, spoken descriptions."""
import pytest

from app.domain.models.panel import (
    BoundingBox,
    ControlNode,
    ControlType,
    PanelMap,
    Region,
    SpatialRelation,
)
from app.services.control_graph.service import ControlGraphService


@pytest.fixture
def graph_service():
    return ControlGraphService()


def _bbox(x1, y1, x2, y2):
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def _grid_panel() -> PanelMap:
    """Create a 3x3 grid of number controls plus Start/Stop."""
    controls = []
    for row in range(3):
        for col in range(3):
            num = row * 3 + col + 1
            x1 = 0.1 + col * 0.2
            y1 = 0.2 + row * 0.2
            controls.append(ControlNode(
                id=f"ctrl_{num}",
                label=str(num),
                type=ControlType.NUMBER,
                bbox=_bbox(x1, y1, x1 + 0.12, y1 + 0.12),
            ))

    controls.append(ControlNode(
        id="ctrl_start",
        label="Start",
        type=ControlType.ACTION,
        bbox=_bbox(0.80, 0.85, 0.95, 0.95),
        is_primary_action=True,
    ))

    regions = [
        Region(
            id="number_pad",
            label="Number Pad",
            bbox=_bbox(0.05, 0.15, 0.75, 0.85),
            control_ids=[f"ctrl_{i}" for i in range(1, 10)],
        ),
    ]

    return PanelMap(
        panel_id="grid_test",
        appliance_type="microwave",
        controls=controls,
        regions=regions,
    )


class TestRowAssignment:
    def test_same_row_for_aligned_controls(self, graph_service):
        graph = graph_service.build(_grid_panel())
        ctrl_1 = graph.get_node("ctrl_1")
        ctrl_2 = graph.get_node("ctrl_2")
        ctrl_3 = graph.get_node("ctrl_3")
        assert ctrl_1.row_index == ctrl_2.row_index == ctrl_3.row_index

    def test_different_rows_for_stacked_controls(self, graph_service):
        graph = graph_service.build(_grid_panel())
        ctrl_1 = graph.get_node("ctrl_1")
        ctrl_4 = graph.get_node("ctrl_4")
        assert ctrl_1.row_index != ctrl_4.row_index


class TestColumnAssignment:
    def test_same_column_for_vertically_aligned(self, graph_service):
        graph = graph_service.build(_grid_panel())
        ctrl_1 = graph.get_node("ctrl_1")
        ctrl_4 = graph.get_node("ctrl_4")
        ctrl_7 = graph.get_node("ctrl_7")
        assert ctrl_1.col_index == ctrl_4.col_index == ctrl_7.col_index


class TestEdgeGeneration:
    def test_left_of_edge_exists(self, graph_service):
        graph = graph_service.build(_grid_panel())
        left_of_edges = [
            e for e in graph.edges
            if e.source_id == "ctrl_1" and e.relation == SpatialRelation.LEFT_OF
        ]
        target_ids = {e.target_id for e in left_of_edges}
        assert "ctrl_2" in target_ids

    def test_above_edge_exists(self, graph_service):
        graph = graph_service.build(_grid_panel())
        above_edges = [
            e for e in graph.edges
            if e.source_id == "ctrl_1" and e.relation == SpatialRelation.ABOVE
        ]
        target_ids = {e.target_id for e in above_edges}
        assert "ctrl_4" in target_ids

    def test_adjacency_edges_created(self, graph_service):
        graph = graph_service.build(_grid_panel())
        adj_edges = [
            e for e in graph.edges
            if e.source_id == "ctrl_5" and e.relation == SpatialRelation.ADJACENT_TO
        ]
        assert len(adj_edges) >= 4  # center should be adjacent to at least 4 neighbors


class TestRegionAssignment:
    def test_controls_assigned_to_region(self, graph_service):
        graph = graph_service.build(_grid_panel())
        inside_edges = [
            e for e in graph.edges if e.relation == SpatialRelation.INSIDE_REGION
        ]
        inside_ids = {e.source_id for e in inside_edges}
        for i in range(1, 10):
            assert f"ctrl_{i}" in inside_ids


class TestSpokenDescriptions:
    def test_corner_control_gets_corner_description(self, graph_service):
        graph = graph_service.build(_grid_panel())
        start = graph.get_node("ctrl_start")
        assert start.spoken_description
        assert "bottom" in start.spoken_description.lower() or "right" in start.spoken_description.lower()

    def test_every_control_has_description(self, graph_service):
        graph = graph_service.build(_grid_panel())
        for node in graph.nodes:
            assert node.spoken_description, f"Missing description for {node.label}"


class TestFullBuildPipeline:
    def test_graph_has_correct_node_count(self, graph_service):
        graph = graph_service.build(_grid_panel())
        assert len(graph.nodes) == 10  # 9 numbers + Start

    def test_graph_has_edges(self, graph_service):
        graph = graph_service.build(_grid_panel())
        assert len(graph.edges) > 0

    def test_graph_has_regions(self, graph_service):
        graph = graph_service.build(_grid_panel())
        assert len(graph.regions) == 1
        assert graph.regions[0].id == "number_pad"
