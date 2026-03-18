from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    PRESS = "press"
    HOLD = "hold"
    TURN = "turn"
    SLIDE = "slide"
    WAIT = "wait"
    VERIFY = "verify"


class TaskIntent(BaseModel):
    """Structured representation of a user's parsed task intent."""

    appliance_type: str
    intent: str
    parameters: dict = Field(default_factory=dict)
    raw_query: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TaskStep(BaseModel):
    """A single step in a task execution plan."""

    step_number: int
    action_type: ActionType = ActionType.PRESS
    control_id: str
    instruction: str
    spoken_hint: str = ""
    verification_hint: str = ""


class TaskPlan(BaseModel):
    """Complete execution plan for a user task."""

    task_id: str
    user_goal: str
    appliance_type: str
    intent: str
    parameters: dict = Field(default_factory=dict)
    steps: list[TaskStep] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    fallback_message: str = ""
    clarification_needed: bool = False

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def get_step(self, step_number: int) -> TaskStep | None:
        for s in self.steps:
            if s.step_number == step_number:
                return s
        return None
