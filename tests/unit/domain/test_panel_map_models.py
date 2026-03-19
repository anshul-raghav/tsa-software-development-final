"""Unit tests for panel map domain models — validation, computed properties, and query methods."""
import pytest
from pydantic import ValidationError

from app.domain.models.panel_map_models import (
    BoundingBox,
    ControlNode,
    ControlType,
    ControlGraph,
    PanelMap,
    Region,
    SpatialEdge,
    SpatialRelation,
)


class TestBoundingBox:
    def test_center_calculation(self):
        bbox = BoundingBox(x1=0.2, y1=0.3, x2=0.8, y2=0.9)
        assert bbox.center_x == pytest.approx(0.5)
        assert bbox.center_y == pytest.approx(0.6)

    def test_dimensions(self):
        bbox = BoundingBox(x1=0.1, y1=0.2, x2=0.5, y2=0.6)
        assert bbox.width == pytest.approx(0.4)
        assert bbox.height == pytest.approx(0.4)
        assert bbox.area == pytest.approx(0.16)

    def test_iou_identical_boxes(self):
        bbox = BoundingBox(x1=0.0, y1=0.0, x2=0.5, y2=0.5)
        assert bbox.iou(bbox) == pytest.approx(1.0)

    def test_iou_no_overlap(self):
        a = BoundingBox(x1=0.0, y1=0.0, x2=0.3, y2=0.3)
        b = BoundingBox(x1=0.5, y1=0.5, x2=0.8, y2=0.8)
        assert a.iou(b) == pytest.approx(0.0)

    def test_iou_partial_overlap(self):
        a = BoundingBox(x1=0.0, y1=0.0, x2=0.5, y2=0.5)
        b = BoundingBox(x1=0.25, y1=0.25, x2=0.75, y2=0.75)
        iou = a.iou(b)
        assert 0.0 < iou < 1.0

    def test_rejects_inverted_coordinates(self):
        with pytest.raises(ValidationError):
            BoundingBox(x1=0.8, y1=0.0, x2=0.2, y2=1.0)

    def test_rejects_out_of_range(self):
        with pytest.raises(ValidationError):
            BoundingBox(x1=-0.1, y1=0.0, x2=0.5, y2=0.5)


class TestControlNode:
    def test_matches_exact_label(self):
        node = ControlNode(
            id="ctrl_start", label="Start", type=ControlType.ACTION,
            bbox=BoundingBox(x1=0.7, y1=0.8, x2=0.9, y2=1.0),
        )
        assert node.matches_query("Start") is True
        assert node.matches_query("start") is True

    def test_matches_alias(self):
        node = ControlNode(
            id="ctrl_start", label="Start", aliases=["begin", "go"],
            type=ControlType.ACTION,
            bbox=BoundingBox(x1=0.7, y1=0.8, x2=0.9, y2=1.0),
        )
        assert node.matches_query("begin") is True
        assert node.matches_query("Go") is True

    def test_no_match_for_unrelated_query(self):
        node = ControlNode(
            id="ctrl_start", label="Start",
            type=ControlType.ACTION,
            bbox=BoundingBox(x1=0.7, y1=0.8, x2=0.9, y2=1.0),
        )
        assert node.matches_query("Defrost") is False


class TestControlGraph:
    def test_find_control_exact(self, sample_control_graph):
        ctrl = sample_control_graph.find_control("Start")
        assert ctrl is not None
        assert ctrl.id == "ctrl_start"

    def test_find_control_alias(self, sample_control_graph):
        ctrl = sample_control_graph.find_control("begin")
        assert ctrl is not None
        assert ctrl.id == "ctrl_start"

    def test_find_control_partial(self, sample_control_graph):
        ctrl = sample_control_graph.find_control("Time")
        assert ctrl is not None
        assert ctrl.id == "ctrl_time_cook"

    def test_find_control_missing(self, sample_control_graph):
        assert sample_control_graph.find_control("Pizza") is None

    def test_neighbors_returns_adjacent(self, sample_control_graph):
        neighbors = sample_control_graph.neighbors("ctrl_1")
        neighbor_ids = {n.id for n in neighbors}
        assert "ctrl_2" in neighbor_ids

    def test_controls_in_row(self, sample_control_graph):
        row_0_controls = sample_control_graph.controls_in_row(0)
        assert len(row_0_controls) >= 1


class TestPanelMap:
    def test_get_control(self, sample_panel_map):
        ctrl = sample_panel_map.get_control("ctrl_start")
        assert ctrl is not None
        assert ctrl.label == "Start"

    def test_get_control_missing(self, sample_panel_map):
        assert sample_panel_map.get_control("nonexistent") is None

    def test_controls_in_region(self, sample_panel_map):
        controls = sample_panel_map.controls_in_region("number_pad")
        labels = {c.label for c in controls}
        assert "1" in labels
        assert "2" in labels
        assert "3" in labels

    def test_get_region(self, sample_panel_map):
        region = sample_panel_map.get_region("number_pad")
        assert region is not None
        assert region.label == "Number Pad"
