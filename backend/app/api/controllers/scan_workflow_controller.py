"""
Scan workflow controller: creates a scan from an uploaded image or returns scan by ID.

Wires image preprocessing, OCR, panelmap extraction/validation, control graph build, and session store
into the ScanPipeline and exposes create_scan_from_image and get_scan_by_id for the scan routes.
"""
import uuid

from fastapi import UploadFile

from app.flows.scan.scan_to_control_graph_pipeline import ScanPipeline
from app.core.exceptions import TouchMapError, SessionNotFoundError, touchmap_exception_to_http
from app.core.logging import logger
from app.domain.schemas.scan_schemas import ScanDetailResponse, ScanResponse
from app.services.graphs.control_graph_builder_service import ControlGraphService
from app.services.ocr.ocr_extraction_service import OCRService
from app.services.panelmap.panelmap_vision_extraction_service import PanelMapExtractionService
from app.services.panelmap.panelmap_normalization_service import PanelMapValidationService
from app.services.scans.image_preprocessing_service import ScanProcessingService
from app.services.sessions.in_memory_session_store import SessionService


class ScanController:
    def __init__(self):
        scan_processor = ScanProcessingService()
        ocr_service = OCRService()
        panelmap_extractor = PanelMapExtractionService()
        panelmap_validator = PanelMapValidationService()
        graph_service = ControlGraphService()
        session_service = SessionService()

        self._session_service = session_service
        self._pipeline = ScanPipeline(
            scan_processor=scan_processor,
            ocr_service=ocr_service,
            panelmap_extractor=panelmap_extractor,
            panelmap_validator=panelmap_validator,
            graph_service=graph_service,
            session_service=session_service,
        )

    async def create_scan_from_image(self, *, image: UploadFile, session_id: str | None) -> ScanResponse:
        if not session_id:
            session_id = str(uuid.uuid4())
        scan_id = str(uuid.uuid4())

        logger.info(f"Starting scan pipeline: scan_id={scan_id}, session_id={session_id}, file={image.filename}")

        try:
            image_bytes = await image.read()
            return await self._pipeline.run(image_bytes=image_bytes, scan_id=scan_id, session_id=session_id)
        except TouchMapError as error:
            raise touchmap_exception_to_http(error)
        except Exception as error:
            logger.error(f"Scan pipeline failed: {error}")
            raise touchmap_exception_to_http(TouchMapError("Scan failed", str(error)))

    async def get_scan_by_id(self, scan_id: str) -> ScanDetailResponse:
        scan_data = await self._session_service.get_scan(scan_id)
        if not scan_data:
            raise touchmap_exception_to_http(SessionNotFoundError(f"Scan {scan_id} not found"))
        return scan_data


scan_controller = ScanController()

