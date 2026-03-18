from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.guidance import GuidanceFeedback


class GuidanceStartRequest(BaseModel):
    scan_id: str
    target_control_id: str


class GuidanceStartResponse(BaseModel):
    guidance_session_id: str
    target_label: str
    spoken_reference: str = ""


class GuidanceFrameRequest(BaseModel):
    guidance_session_id: str


class GuidanceFrameResponse(BaseModel):
    feedback: GuidanceFeedback


class GuidanceStopRequest(BaseModel):
    guidance_session_id: str


class GuidanceStopResponse(BaseModel):
    stopped: bool = True
    message: str = "Guidance session ended."
