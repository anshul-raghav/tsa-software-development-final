"""
Explore HTTP route: POST /explore to get spoken layout descriptions for panel sections (regions, rows, sides).
"""
from fastapi import APIRouter

from app.core.exceptions import TouchMapError, touchmap_exception_to_http, SessionNotFoundError
from app.domain.schemas.explore_schemas import ExploreRequest, ExploreResponse
from app.services.exploration.panel_layout_description_service import ExploreService
from app.services.sessions.in_memory_session_store import SessionService
from app.core.logging import logger

router = APIRouter(prefix="/explore", tags=["explore"])

explore_service = ExploreService()
session_service = SessionService()


@router.post("", response_model=ExploreResponse)
async def explore_panel(request: ExploreRequest):
    """Describe the layout of a panel section."""
    logger.info(f"Explore request: scan_id={request.scan_id}, query='{request.query}'")

    try:
        scan_data = await session_service.get_scan(request.scan_id)
        if not scan_data:
            raise SessionNotFoundError(f"Scan {request.scan_id} not found")

        result = explore_service.explore(
            query=request.query,
            control_graph=scan_data.control_graph,
            panel_map=scan_data.panel_map,
        )

        return result
    except TouchMapError as error:
        logger.error(f"Explore failed: {error}")
        raise touchmap_exception_to_http(error)
