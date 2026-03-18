"""Unit tests for TaskPlanningService — deterministic plan generation from intents."""
import pytest

from app.domain.models.panel import (
    BoundingBox,
    ControlNode,
    ControlType,
    ControlGraph,
    PanelMap,
    Region,
)
from app.domain.models.task import TaskIntent, ActionType
from app.services.task_planning.service import TaskPlanningService


@pytest.fixture
def planner():
    return TaskPlanningService()


class TestDurationToDigits:
    """Verifies correct conversion of seconds into digit sequences."""

    def test_60_seconds(self, planner):
        assert planner._duration_to_digits(60) == [1, 0, 0]

    def test_30_seconds(self, planner):
        assert planner._duration_to_digits(30) == [3, 0]

    def test_90_seconds(self, planner):
        assert planner._duration_to_digits(90) == [1, 3, 0]

    def test_5_seconds(self, planner):
        assert planner._duration_to_digits(5) == [5]

    def test_120_seconds(self, planner):
        assert planner._duration_to_digits(120) == [2, 0, 0]


class TestMicrowaveHeatForTime:
    @pytest.mark.asyncio
    async def test_produces_correct_sequence(self, planner, sample_control_graph, sample_panel_map):
        intent = TaskIntent(
            appliance_type="microwave",
            intent="heat_for_time",
            parameters={"duration_seconds": 60},
            raw_query="set the microwave for 60 seconds",
        )
        plan = await planner.plan(intent, sample_control_graph, sample_panel_map)

        assert plan.confidence > 0.5
        assert len(plan.steps) >= 2

        instructions = [s.instruction for s in plan.steps]
        assert any("Time Cook" in i for i in instructions)
        assert any("Start" in i for i in instructions)

    @pytest.mark.asyncio
    async def test_all_steps_are_press_actions(self, planner, sample_control_graph, sample_panel_map):
        intent = TaskIntent(
            appliance_type="microwave",
            intent="heat_for_time",
            parameters={"duration_seconds": 30},
            raw_query="heat for 30 seconds",
        )
        plan = await planner.plan(intent, sample_control_graph, sample_panel_map)

        for step in plan.steps:
            assert step.action_type == ActionType.PRESS


class TestMicrowaveStop:
    @pytest.mark.asyncio
    async def test_stop_finds_stop_button(self, planner, sample_control_graph, sample_panel_map):
        intent = TaskIntent(
            appliance_type="microwave",
            intent="stop",
            raw_query="stop the microwave",
        )
        plan = await planner.plan(intent, sample_control_graph, sample_panel_map)

        assert len(plan.steps) == 1
        assert "Stop" in plan.steps[0].instruction


class TestMissingControls:
    @pytest.mark.asyncio
    async def test_empty_graph_produces_fallback(self, planner):
        empty_graph = ControlGraph(nodes=[], edges=[], regions=[])
        empty_map = PanelMap(panel_id="empty", controls=[])
        intent = TaskIntent(
            appliance_type="microwave",
            intent="heat_for_time",
            parameters={"duration_seconds": 60},
            raw_query="heat for 60 seconds",
        )
        plan = await planner.plan(intent, empty_graph, empty_map)

        assert plan.confidence < 0.5
        assert plan.fallback_message != ""
        assert plan.clarification_needed is True


class TestGenericAppliance:
    @pytest.mark.asyncio
    async def test_generic_start(self, planner, sample_control_graph, sample_panel_map):
        intent = TaskIntent(
            appliance_type="unknown",
            intent="start",
            raw_query="start it",
        )
        plan = await planner.plan(intent, sample_control_graph, sample_panel_map)
        assert len(plan.steps) >= 1

    @pytest.mark.asyncio
    async def test_generic_stop(self, planner, sample_control_graph, sample_panel_map):
        intent = TaskIntent(
            appliance_type="unknown",
            intent="stop",
            raw_query="stop",
        )
        plan = await planner.plan(intent, sample_control_graph, sample_panel_map)
        assert len(plan.steps) >= 1
