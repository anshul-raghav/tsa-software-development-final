"""Unit tests for task domain models."""
import pytest

from app.domain.models.task_models import TaskPlan, TaskStep, ActionType


class TestTaskPlan:
    def test_get_step_by_number(self):
        plan = TaskPlan(
            task_id="t1", user_goal="test", appliance_type="microwave",
            intent="heat_for_time",
            steps=[
                TaskStep(step_number=1, control_id="c1", instruction="Press A"),
                TaskStep(step_number=2, control_id="c2", instruction="Press B"),
            ],
        )
        step = plan.get_step(1)
        assert step is not None
        assert step.instruction == "Press A"

    def test_get_step_missing(self):
        plan = TaskPlan(
            task_id="t1", user_goal="test", appliance_type="microwave",
            intent="stop", steps=[],
        )
        assert plan.get_step(99) is None

    def test_step_count(self):
        plan = TaskPlan(
            task_id="t1", user_goal="test", appliance_type="microwave",
            intent="heat_for_time",
            steps=[
                TaskStep(step_number=1, control_id="c1", instruction="A"),
                TaskStep(step_number=2, control_id="c2", instruction="B"),
                TaskStep(step_number=3, control_id="c3", instruction="C"),
            ],
        )
        assert plan.step_count == 3
