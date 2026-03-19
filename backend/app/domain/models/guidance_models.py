from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.panel_map_models import BoundingBox


class GuidanceTarget(BaseModel):
    """Target control for live guidance mode."""

    target_control_id: str
    target_label: str
    target_bbox: BoundingBox
    target_region: str | None = None
    spoken_reference: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class GuidanceFrame(BaseModel):
    """A single frame submitted during live guidance."""

    guidance_session_id: str
    frame_index: int = 0
    timestamp_ms: int = 0


class GuidanceFeedback(BaseModel):
    """Feedback returned for a single guidance frame."""

    spoken_feedback: str
    proximity_estimate: float = Field(default=0.0, ge=0.0, le=1.0)
    alignment_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    direction_hint: str | None = None
    target_visible: bool = False
