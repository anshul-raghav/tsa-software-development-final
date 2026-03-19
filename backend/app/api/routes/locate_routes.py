"""
Locate HTTP route: POST /locate to resolve a control by name and return spatial instructions and guidance target.
"""
from fastapi import APIRouter

from app.core.exceptions import TouchMapError, touchmap_exception_to_http, SessionNotFoundError
from app.domain.schemas.locate_schemas import LocateRequest, LocateResponse
from app.services.locating.control_locator_service import LocateService
from app.services.sessions.in_memory_session_store import SessionService
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
    except TouchMapError as error:
        logger.error(f"Locate failed: {error}")
        raise touchmap_exception_to_http(error)
