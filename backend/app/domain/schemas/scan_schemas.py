from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.panel_map_models import PanelMap, ControlGraph, OCRToken


class ScanRequest(BaseModel):
    session_id: str | None = None


class OCRResult(BaseModel):
    tokens: list[OCRToken] = Field(default_factory=list)
    raw_text: str = ""


class ScanResponse(BaseModel):
    scan_id: str
    session_id: str
    preprocessed_image_ref: str = ""
    ocr_result: OCRResult
    panel_map: PanelMap
    control_graph_summary: dict = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ScanDetailResponse(BaseModel):
    scan_id: str
    session_id: str
    panel_map: PanelMap
    control_graph: ControlGraph
    ocr_result: OCRResult
    preprocessed_image_ref: str = ""
