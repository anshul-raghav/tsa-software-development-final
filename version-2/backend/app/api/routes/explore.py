from fastapi import APIRouter

from app.core.exceptions import touchmap_exception_to_http, SessionNotFoundError
from app.domain.schemas.explore import ExploreRequest, ExploreResponse
from app.services.explore.service import ExploreService
from app.services.session.service import SessionService
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
    except Exception as e:
        logger.error(f"Explore failed: {e}")
        raise touchmap_exception_to_http(e) if hasattr(e, "message") else e
