from fastapi import APIRouter

from app.core.exceptions import touchmap_exception_to_http, SessionNotFoundError
from app.services.session.service import SessionService

router = APIRouter(prefix="/debug", tags=["debug"])

session_service = SessionService()


@router.get("/panel/{scan_id}")
async def debug_panel(scan_id: str):
    """Return raw OCR, PanelMap, ControlGraph, and pipeline metadata for debugging."""
    scan_data = await session_service.get_scan(scan_id)
    if not scan_data:
        raise touchmap_exception_to_http(SessionNotFoundError(f"Scan {scan_id} not found"))

    return {
        "scan_id": scan_id,
        "panel_map": scan_data.panel_map.model_dump(),
        "control_graph": scan_data.control_graph.model_dump(),
        "ocr_result": scan_data.ocr_result.model_dump(),
        "classifier_result": scan_data.classifier_result.model_dump(),
    }
