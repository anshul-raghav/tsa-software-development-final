"""
Scan HTTP routes: create scan from uploaded image, get scan by ID.

POST /scan and GET /scan/{scan_id}; controller runs the full pipeline (preprocess → OCR → panelmap → graph → store).
"""
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.api.controllers.scan_workflow_controller import scan_controller
from app.domain.schemas.scan_schemas import ScanResponse, ScanDetailResponse

router = APIRouter(prefix="/scan", tags=["scan"])

@router.post("", response_model=ScanResponse)
async def create_scan(
    image: UploadFile = File(...),
    session_id: str | None = Form(default=None),
):
    """Create a new scan from an uploaded panel image; returns scan_id and summary."""
    return await scan_controller.create_scan_from_image(image=image, session_id=session_id)


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: str):
    """Retrieve full scan results by ID (panel_map, control_graph, ocr_result)."""
    if not (scan_id and scan_id.strip()):
        raise HTTPException(status_code=400, detail="scan_id is required")
    return await scan_controller.get_scan_by_id(scan_id=scan_id.strip())
