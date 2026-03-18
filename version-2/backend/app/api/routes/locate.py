from fastapi import APIRouter

from app.core.exceptions import touchmap_exception_to_http, SessionNotFoundError
from app.domain.schemas.locate import LocateRequest, LocateResponse
from app.services.locate.service import LocateService
from app.services.session.service import SessionService
from app.core.logging import logger

router = APIRouter(prefix="/locate", tags=["locate"])

locate_service = LocateService()
session_service = SessionService()


@router.post("", response_model=LocateResponse)
async def locate_control(request: LocateRequest):
    """Find a specific control on the scanned panel."""
    logger.info(f"Locate request: scan_id={request.scan_id}, query='{request.query}'")

    try:
        scan_data = await session_service.get_scan(request.scan_id)
        if not scan_data:
            raise SessionNotFoundError(f"Scan {request.scan_id} not found")

        result = locate_service.locate(
            query=request.query,
            control_graph=scan_data.control_graph,
            panel_map=scan_data.panel_map,
        )

        return result
    except Exception as e:
        logger.error(f"Locate failed: {e}")
        raise touchmap_exception_to_http(e) if hasattr(e, "message") else e
