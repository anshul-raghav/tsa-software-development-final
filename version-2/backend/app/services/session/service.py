from __future__ import annotations

from dataclasses import dataclass, field

from app.core.logging import logger
from app.domain.models.panel import PanelMap, ControlGraph
from app.domain.models.task import TaskPlan
from app.domain.schemas.scan import ClassifierResult, OCRResult, ScanDetailResponse


@dataclass
class ScanRecord:
    scan_id: str
    session_id: str
    panel_map: PanelMap
    control_graph: ControlGraph
    classifier_result: ClassifierResult
    ocr_result: OCRResult
    preprocessed_image_ref: str = ""
    task_plans: dict[str, TaskPlan] = field(default_factory=dict)


class SessionService:
    """In-memory session store for scans and task plans.

    In production, this would use SQLAlchemy + SQLite/PostgreSQL.
    The in-memory store is sufficient for demo and testing.
    """

    _scans: dict[str, ScanRecord] = {}

    async def store_scan(
        self,
        scan_id: str,
        session_id: str,
        panel_map: PanelMap,
        control_graph: ControlGraph,
        classifier_result: ClassifierResult,
        ocr_result: OCRResult,
        preprocessed_image_ref: str = "",
    ):
        record = ScanRecord(
            scan_id=scan_id,
            session_id=session_id,
            panel_map=panel_map,
            control_graph=control_graph,
            classifier_result=classifier_result,
            ocr_result=ocr_result,
            preprocessed_image_ref=preprocessed_image_ref,
        )
        self._scans[scan_id] = record
        logger.info(f"Stored scan: {scan_id} (session={session_id})")

    async def get_scan(self, scan_id: str) -> ScanDetailResponse | None:
        record = self._scans.get(scan_id)
        if not record:
            return None
        return ScanDetailResponse(
            scan_id=record.scan_id,
            session_id=record.session_id,
            panel_map=record.panel_map,
            control_graph=record.control_graph,
            classifier_result=record.classifier_result,
            ocr_result=record.ocr_result,
            preprocessed_image_ref=record.preprocessed_image_ref,
        )

    async def store_task_plan(self, scan_id: str, plan: TaskPlan):
        record = self._scans.get(scan_id)
        if record:
            record.task_plans[plan.task_id] = plan
            logger.info(f"Stored task plan: {plan.task_id} for scan={scan_id}")

    async def get_task_plan(self, scan_id: str, task_id: str) -> TaskPlan | None:
        record = self._scans.get(scan_id)
        if not record:
            return None
        return record.task_plans.get(task_id)

    async def list_sessions(self) -> list[dict]:
        return [
            {
                "scan_id": r.scan_id,
                "session_id": r.session_id,
                "appliance_type": r.panel_map.appliance_type,
                "control_count": len(r.panel_map.controls),
            }
            for r in self._scans.values()
        ]
