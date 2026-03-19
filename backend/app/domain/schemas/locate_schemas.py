from __future__ import annotations

from pydantic import BaseModel

from app.domain.models.guidance_models import GuidanceTarget


class LocateRequest(BaseModel):
    scan_id: str
    query: str


class LocateResponse(BaseModel):
    resolved_control_id: str | None = None
    resolved_label: str = ""
    spoken_instruction: str
    guidance_target: GuidanceTarget | None = None
    confidence: float = 1.0
