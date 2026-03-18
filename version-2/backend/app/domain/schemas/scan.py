from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.panel import PanelMap, ControlGraph, OCRToken


class ScanRequest(BaseModel):
    session_id: str | None = None


class ClassifierResult(BaseModel):
    appliance_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    scan_quality: str = "good"
    scan_quality_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class OCRResult(BaseModel):
    tokens: list[OCRToken] = Field(default_factory=list)
    raw_text: str = ""


class ScanResponse(BaseModel):
    scan_id: str
    session_id: str
    preprocessed_image_ref: str = ""
    classifier_result: ClassifierResult
    ocr_result: OCRResult
    panel_map: PanelMap
    control_graph_summary: dict = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ScanDetailResponse(BaseModel):
    scan_id: str
    session_id: str
    panel_map: PanelMap
    control_graph: ControlGraph
    classifier_result: ClassifierResult
    ocr_result: OCRResult
    preprocessed_image_ref: str = ""
