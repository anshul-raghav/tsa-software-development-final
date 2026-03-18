import uuid

from fastapi import APIRouter, File, UploadFile

from app.core.exceptions import touchmap_exception_to_http, SessionNotFoundError
from app.domain.schemas.guidance import (
    GuidanceStartRequest,
    GuidanceStartResponse,
    GuidanceFrameResponse,
    GuidanceStopRequest,
    GuidanceStopResponse,
)
from app.services.live_guidance.service import LiveGuidanceService
from app.services.session.service import SessionService
from app.core.logging import logger

router = APIRouter(prefix="/guidance", tags=["guidance"])

guidance_service = LiveGuidanceService()
session_service = SessionService()


@router.post("/start", response_model=GuidanceStartResponse)
async def start_guidance(request: GuidanceStartRequest):
    """Start a live guidance session for a specific control."""
    logger.info(f"Guidance start: scan_id={request.scan_id}, target={request.target_control_id}")

    scan_data = await session_service.get_scan(request.scan_id)
    if not scan_data:
        raise touchmap_exception_to_http(SessionNotFoundError(f"Scan {request.scan_id} not found"))

    control = scan_data.control_graph.get_node(request.target_control_id)
    if not control:
        from app.core.exceptions import ControlNotFoundError
        raise touchmap_exception_to_http(
            ControlNotFoundError(request.target_control_id)
        )

    guidance_session_id = str(uuid.uuid4())

    await guidance_service.start_session(
        guidance_session_id=guidance_session_id,
        scan_id=request.scan_id,
        target_control=control,
        panel_map=scan_data.panel_map,
    )

    return GuidanceStartResponse(
        guidance_session_id=guidance_session_id,
        target_label=control.label,
        spoken_reference=control.spoken_description,
    )


@router.post("/frame", response_model=GuidanceFrameResponse)
async def process_guidance_frame(
    guidance_session_id: str = File(...),
    frame: UploadFile = File(...),
):
    """Process a single frame during live guidance."""
    frame_bytes = await frame.read()
    feedback = await guidance_service.process_frame(
        guidance_session_id=guidance_session_id,
        frame_bytes=frame_bytes,
    )
    return GuidanceFrameResponse(feedback=feedback)


@router.post("/stop", response_model=GuidanceStopResponse)
async def stop_guidance(request: GuidanceStopRequest):
    """Stop a live guidance session."""
    await guidance_service.stop_session(request.guidance_session_id)
    return GuidanceStopResponse(stopped=True, message="Guidance session ended.")
