from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.task_models import TaskIntent, TaskPlan


class TaskPlanRequest(BaseModel):
    scan_id: str
    user_request: str


class TaskPlanResponse(BaseModel):
    parsed_intent: TaskIntent
    task_plan: TaskPlan
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    clarification_needed: bool = False


class TaskRepeatRequest(BaseModel):
    scan_id: str
    task_id: str
    current_step: int


class TaskRepeatResponse(BaseModel):
    step_instruction: str
    spoken_hint: str = ""
    step_number: int


class TaskClarifyRequest(BaseModel):
    scan_id: str
    task_id: str
    current_step: int
    question: str


class TaskClarifyResponse(BaseModel):
    clarification: str
    route_to_locate: bool = False
    route_to_guidance: bool = False
    control_id: str | None = None
