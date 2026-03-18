"""Shared test fixtures for the TouchMap backend test suite."""
import pytest

from app.domain.models.panel import (
    BoundingBox,
    ControlNode,
    ControlType,
    Region,
    Landmark,
    PanelMap,
    ControlGraph,
    SpatialEdge,
    SpatialRelation,
)
from app.domain.models.task import TaskIntent, TaskPlan, TaskStep, ActionType
from app.services.control_graph.service import ControlGraphService


# ---------------------------------------------------------------------------
# Reusable bounding-box helpers
# ---------------------------------------------------------------------------

def _bbox(x1: float, y1: float, x2: float, y2: float) -> BoundingBox:
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


# ---------------------------------------------------------------------------
# Control fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_controls() -> list[ControlNode]:
    """Five controls resembling a simple microwave panel."""
    return [
        ControlNode(
            id="ctrl_time_cook",
            label="Time Cook",
            aliases=["cook time", "timed cook"],
            type=ControlType.ACTION,
            bbox=_bbox(0.70, 0.05, 0.95, 0.15),
            is_primary_action=False,
            confidence=0.95,
            spoken_description="Time Cook is in the top-right",
        ),
        ControlNode(
            id="ctrl_1",
            label="1",
            aliases=[],
            type=ControlType.NUMBER,
            bbox=_bbox(0.10, 0.30, 0.25, 0.42),
            confidence=0.90,
        ),
        ControlNode(
            id="ctrl_2",
            label="2",
            aliases=[],
            type=ControlType.NUMBER,
            bbox=_bbox(0.30, 0.30, 0.45, 0.42),
            confidence=0.90,
        ),
        ControlNode(
            id="ctrl_3",
            label="3",
            aliases=[],
            type=ControlType.NUMBER,
            bbox=_bbox(0.50, 0.30, 0.65, 0.42),
            confidence=0.90,
        ),
        ControlNode(
            id="ctrl_start",
            label="Start",
            aliases=["begin", "go"],
            type=ControlType.ACTION,
            bbox=_bbox(0.75, 0.80, 0.95, 0.95),
            is_primary_action=True,
            confidence=0.95,
            spoken_description="Start is in the bottom-right corner",
        ),
        ControlNode(
            id="ctrl_stop",
            label="Stop",
            aliases=["cancel", "clear"],
            type=ControlType.ACTION,
            bbox=_bbox(0.75, 0.65, 0.95, 0.78),
            is_primary_action=True,
            confidence=0.93,
            spoken_description="Stop is in the right side, above Start",
        ),
    ]


@pytest.fixture
def sample_regions() -> list[Region]:
    return [
        Region(
            id="number_pad",
            label="Number Pad",
            bbox=_bbox(0.05, 0.25, 0.70, 0.90),
            control_ids=["ctrl_1", "ctrl_2", "ctrl_3"],
            description="A grid of number buttons",
        ),
        Region(
            id="action_column",
            label="Action Buttons",
            bbox=_bbox(0.70, 0.60, 1.0, 1.0),
            control_ids=["ctrl_start", "ctrl_stop"],
            description="Primary action buttons on the right",
        ),
    ]


@pytest.fixture
def sample_panel_map(sample_controls, sample_regions) -> PanelMap:
    return PanelMap(
        panel_id="test_panel_001",
        appliance_type="microwave",
        scan_confidence=0.92,
        orientation="portrait",
        regions=sample_regions,
        controls=sample_controls,
        global_description="A microwave control panel with a number pad on the left and action buttons on the right.",
    )


@pytest.fixture
def sample_control_graph(sample_panel_map) -> ControlGraph:
    service = ControlGraphService()
    return service.build(sample_panel_map)


@pytest.fixture
def heat_60s_intent() -> TaskIntent:
    return TaskIntent(
        appliance_type="microwave",
        intent="heat_for_time",
        parameters={"duration_seconds": 60},
        raw_query="set the microwave for 60 seconds",
        confidence=0.85,
    )
