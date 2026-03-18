import uuid

from fastapi import APIRouter, File, Form, UploadFile

from app.core.exceptions import SessionNotFoundError, touchmap_exception_to_http
from app.domain.schemas.scan import ScanResponse, ScanDetailResponse
from app.services.scan_processing.service import ScanProcessingService
from app.services.ocr.service import OCRService
from app.services.panelmap_extraction.service import PanelMapExtractionService
from app.services.panelmap_validation.service import PanelMapValidationService
from app.services.control_graph.service import ControlGraphService
from app.services.session.service import SessionService
from app.core.logging import logger

router = APIRouter(prefix="/scan", tags=["scan"])

scan_processor = ScanProcessingService()
ocr_service = OCRService()
panelmap_extractor = PanelMapExtractionService()
panelmap_validator = PanelMapValidationService()
graph_service = ControlGraphService()
session_service = SessionService()


@router.post("", response_model=ScanResponse)
async def scan_panel(
    image: UploadFile = File(...),
    session_id: str | None = Form(default=None),
):
    """Full scan pipeline: preprocess -> OCR -> PanelMap -> validate -> Graph."""
    if not session_id:
        session_id = str(uuid.uuid4())
    scan_id = str(uuid.uuid4())

    logger.info(f"Starting scan pipeline: scan_id={scan_id}, session_id={session_id}, file={image.filename}")

    try:
        image_bytes = await image.read()

        preprocessed = await scan_processor.process(image_bytes, scan_id)

        ocr_result = await ocr_service.extract(preprocessed.cleaned_image)

        raw_panel_map = await panelmap_extractor.extract(
            cleaned_image=preprocessed.cleaned_image,
            ocr_tokens=ocr_result.tokens,
            scan_id=scan_id,
        )

        panel_map = await panelmap_validator.validate_and_normalize(raw_panel_map)

        control_graph = graph_service.build(panel_map)

        await session_service.store_scan(
            scan_id=scan_id,
            session_id=session_id,
            panel_map=panel_map,
            control_graph=control_graph,
            ocr_result=ocr_result,
            preprocessed_image_ref=preprocessed.image_ref,
        )

        logger.info(f"Scan complete: {len(panel_map.controls)} controls, {len(control_graph.edges)} edges")

        return ScanResponse(
            scan_id=scan_id,
            session_id=session_id,
            preprocessed_image_ref=preprocessed.image_ref,
            ocr_result=ocr_result,
            panel_map=panel_map,
            control_graph_summary={
                "node_count": len(control_graph.nodes),
                "edge_count": len(control_graph.edges),
                "region_count": len(control_graph.regions),
            },
            confidence=panel_map.scan_confidence,
        )
    except Exception as e:
        logger.error(f"Scan pipeline failed: {e}")
        raise touchmap_exception_to_http(e) if hasattr(e, "message") else e


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: str):
    """Retrieve full scan results by ID."""
    scan_data = await session_service.get_scan(scan_id)
    if not scan_data:
        raise touchmap_exception_to_http(SessionNotFoundError(f"Scan {scan_id} not found"))
    return scan_data
