from fastapi import APIRouter

from app.core.exceptions import touchmap_exception_to_http
from app.domain.schemas.task import (
    TaskPlanRequest,
    TaskPlanResponse,
    TaskRepeatRequest,
    TaskRepeatResponse,
    TaskClarifyRequest,
    TaskClarifyResponse,
)
from app.services.intent_parsing.service import IntentParsingService
from app.services.task_planning.service import TaskPlanningService
from app.services.session.service import SessionService
from app.core.logging import logger

router = APIRouter(prefix="/task", tags=["task"])

intent_parser = IntentParsingService()
task_planner = TaskPlanningService()
session_service = SessionService()


@router.post("/plan", response_model=TaskPlanResponse)
async def plan_task(request: TaskPlanRequest):
    """Parse user intent and generate a step-by-step task plan."""
    logger.info(f"Task plan request: scan_id={request.scan_id}, query='{request.user_request}'")

    try:
        scan_data = await session_service.get_scan(request.scan_id)
        if not scan_data:
            from app.core.exceptions import SessionNotFoundError
            raise SessionNotFoundError(f"Scan {request.scan_id} not found")

        intent = await intent_parser.parse(
            user_request=request.user_request,
            appliance_type=scan_data.panel_map.appliance_type,
        )

        plan = await task_planner.plan(
            intent=intent,
            control_graph=scan_data.control_graph,
            panel_map=scan_data.panel_map,
        )

        await session_service.store_task_plan(request.scan_id, plan)

        return TaskPlanResponse(
            parsed_intent=intent,
            task_plan=plan,
            confidence=plan.confidence,
            clarification_needed=plan.clarification_needed,
        )
    except Exception as e:
        logger.error(f"Task planning failed: {e}")
        raise touchmap_exception_to_http(e) if hasattr(e, "message") else e


@router.post("/repeat", response_model=TaskRepeatResponse)
async def repeat_step(request: TaskRepeatRequest):
    """Repeat the current task step."""
    plan = await session_service.get_task_plan(request.scan_id, request.task_id)
    if not plan:
        from app.core.exceptions import SessionNotFoundError
        raise touchmap_exception_to_http(
            SessionNotFoundError(f"Task plan {request.task_id} not found")
        )

    step = plan.get_step(request.current_step)
    if not step:
        step = plan.steps[-1] if plan.steps else None

    if not step:
        return TaskRepeatResponse(
            step_instruction="No steps available.",
            step_number=0,
        )

    return TaskRepeatResponse(
        step_instruction=step.instruction,
        spoken_hint=step.spoken_hint,
        step_number=step.step_number,
    )


@router.post("/clarify", response_model=TaskClarifyResponse)
async def clarify_step(request: TaskClarifyRequest):
    """Provide clarification for a task step."""
    logger.info(f"Clarify request: step={request.current_step}, question='{request.question}'")

    scan_data = await session_service.get_scan(request.scan_id)
    plan = await session_service.get_task_plan(request.scan_id, request.task_id)

    if not scan_data or not plan:
        from app.core.exceptions import SessionNotFoundError
        raise touchmap_exception_to_http(SessionNotFoundError("Scan or task plan not found"))

    step = plan.get_step(request.current_step)
    if not step:
        return TaskClarifyResponse(clarification="Step not found. Try asking again.")

    control = scan_data.control_graph.get_node(step.control_id)
    if control and ("where" in request.question.lower() or "find" in request.question.lower()):
        return TaskClarifyResponse(
            clarification=control.spoken_description or f"{control.label} is on the panel.",
            route_to_locate=True,
            control_id=control.id,
        )

    return TaskClarifyResponse(
        clarification=step.spoken_hint or step.instruction,
    )
