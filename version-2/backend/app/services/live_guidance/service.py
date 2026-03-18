from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from app.core.logging import logger
from app.core.exceptions import GuidanceError
from app.domain.models.panel import PanelMap, ControlNode, BoundingBox
from app.domain.models.guidance import GuidanceFeedback


@dataclass
class GuidanceSession:
    guidance_session_id: str
    scan_id: str
    target_control: ControlNode
    panel_map: PanelMap
    frame_count: int = 0
    reference_features: object = None


class LiveGuidanceService:
    """Provides real-time spoken cues to guide a user toward a target control."""

    def __init__(self):
        self._sessions: dict[str, GuidanceSession] = {}

    async def start_session(
        self,
        guidance_session_id: str,
        scan_id: str,
        target_control: ControlNode,
        panel_map: PanelMap,
    ):
        logger.info(f"Starting guidance session: {guidance_session_id} -> {target_control.label}")
        session = GuidanceSession(
            guidance_session_id=guidance_session_id,
            scan_id=scan_id,
            target_control=target_control,
            panel_map=panel_map,
        )
        self._sessions[guidance_session_id] = session

    async def process_frame(
        self,
        guidance_session_id: str,
        frame_bytes: bytes,
    ) -> GuidanceFeedback:
        session = self._sessions.get(guidance_session_id)
        if not session:
            raise GuidanceError(f"Guidance session {guidance_session_id} not found")

        session.frame_count += 1

        try:
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return GuidanceFeedback(
                    spoken_feedback="I can't see the panel clearly. Try adjusting your camera.",
                    alignment_confidence=0.0,
                )
        except Exception:
            return GuidanceFeedback(
                spoken_feedback="Could not process the camera frame.",
                alignment_confidence=0.0,
            )

        return self._estimate_guidance(frame, session)

    async def stop_session(self, guidance_session_id: str):
        if guidance_session_id in self._sessions:
            del self._sessions[guidance_session_id]
            logger.info(f"Guidance session stopped: {guidance_session_id}")

    def _estimate_guidance(self, frame: np.ndarray, session: GuidanceSession) -> GuidanceFeedback:
        """Estimate where the target control is relative to current camera view.

        Uses the target's known normalized position on the panel to generate
        directional cues. This is approximate guidance — the target bbox from
        the PanelMap tells us where it should be on the panel, and we compare
        that to the center of the current camera frame.
        """
        target = session.target_control
        target_cx = target.center_x
        target_cy = target.center_y

        frame_center_x = 0.5
        frame_center_y = 0.5

        dx = target_cx - frame_center_x
        dy = target_cy - frame_center_y

        distance = (dx**2 + dy**2) ** 0.5
        proximity = max(0.0, 1.0 - distance * 2)

        direction_parts: list[str] = []
        if abs(dy) > 0.08:
            direction_parts.append("down" if dy > 0 else "up")
        if abs(dx) > 0.08:
            direction_parts.append("right" if dx > 0 else "left")

        if distance < 0.1:
            spoken = f"You're very close to {target.label}. Hold still."
            direction_hint = "hold"
        elif distance < 0.2:
            direction = " and ".join(direction_parts) if direction_parts else "closer"
            spoken = f"Almost there. Move slightly {direction}."
            direction_hint = direction_parts[0] if direction_parts else "hold"
        else:
            direction = " and ".join(direction_parts) if direction_parts else "toward the panel"
            spoken = f"Move {direction} to find {target.label}."
            direction_hint = direction_parts[0] if direction_parts else "forward"

        return GuidanceFeedback(
            spoken_feedback=spoken,
            proximity_estimate=round(proximity, 2),
            alignment_confidence=round(max(0.3, proximity), 2),
            direction_hint=direction_hint,
            target_visible=proximity > 0.5,
        )
