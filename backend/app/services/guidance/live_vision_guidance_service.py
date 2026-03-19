"""
Live vision guidance: compares user camera frames to the scan reference and returns spoken directional feedback.

Start session with target control and reference image; process_frame returns GuidanceFeedback (direction, proximity, spoken).
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field

import cv2
import numpy as np
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import GuidanceError
from app.domain.models.panel_map_models import PanelMap, ControlNode, ControlGraph, BoundingBox
from app.domain.models.guidance_models import GuidanceFeedback

_GUIDANCE_SYSTEM_PROMPT = """\
You are a vision-based guidance system helping a blind user find a specific \
control on a physical panel (e.g. a microwave, oven, or appliance).

You will receive:
1. A REFERENCE image of the full panel (taken during the initial scan).
2. A LIVE camera frame showing what the user's camera currently sees.
3. Information about the TARGET control the user is trying to reach.

Your job: compare the live frame to the reference image and determine where \
the user's camera (or finger) is relative to the target control.

Respond with ONLY a JSON object:
{
  "direction": "<one of: left, right, up, down, up-left, up-right, down-left, down-right, hold>",
  "proximity": <float 0.0 to 1.0, where 1.0 means directly on target>,
  "feedback": "<short spoken instruction, 1-2 sentences max>"
}

Rules:
- "hold" means the target is visible and centered in the live frame.
- Directions are from the user's perspective (left means move camera/finger left).
- If you cannot see the panel at all in the live frame, set proximity to 0.0 \
  and give a general instruction like "Point your camera at the panel."
- If the target control is visible in the live frame, set proximity >= 0.7.
- Keep feedback concise — it will be spoken aloud.
"""


@dataclass
class GuidanceSession:
    guidance_session_id: str
    scan_id: str
    target_control: ControlNode
    panel_map: PanelMap
    control_graph: ControlGraph | None = None
    reference_image_b64: str = ""
    frame_count: int = 0


class LiveGuidanceService:
    """Provides real-time spoken cues to guide a user toward a target control.

    Uses OpenAI Vision to compare live camera frames against the original
    scan reference image, producing accurate directional feedback.
    """

    def __init__(self):
        self._sessions: dict[str, GuidanceSession] = {}
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def start_session(
        self,
        guidance_session_id: str,
        scan_id: str,
        target_control: ControlNode,
        panel_map: PanelMap,
        control_graph: ControlGraph | None = None,
        reference_image_b64: str = "",
    ):
        logger.info(f"Starting guidance session: {guidance_session_id} -> {target_control.label}")
        session = GuidanceSession(
            guidance_session_id=guidance_session_id,
            scan_id=scan_id,
            target_control=target_control,
            panel_map=panel_map,
            control_graph=control_graph,
            reference_image_b64=reference_image_b64,
        )
        self._sessions[guidance_session_id] = session

    async def process_frame(
        self,
        guidance_session_id: str,
        frame_bytes: bytes,
    ) -> GuidanceFeedback:
        session = self._sessions.get(guidance_session_id)
        if not session:
            logger.error("Guidance session not found: %s", guidance_session_id)
            raise GuidanceError(f"Guidance session {guidance_session_id} not found")

        session.frame_count += 1

        try:
            frame_b64 = base64.b64encode(frame_bytes).decode("utf-8")
        except Exception:
            return GuidanceFeedback(
                spoken_feedback="Could not process the camera frame.",
                alignment_confidence=0.0,
            )

        return await self._estimate_guidance(frame_b64, session)

    async def stop_session(self, guidance_session_id: str):
        if guidance_session_id in self._sessions:
            del self._sessions[guidance_session_id]
            logger.info(f"Guidance session stopped: {guidance_session_id}")

    def _build_target_context(self, session: GuidanceSession) -> str:
        target = session.target_control
        parts = [
            f"TARGET CONTROL: \"{target.label}\"",
            f"  Type: {target.type}",
            f"  Position on panel: center_x={target.center_x:.2f}, center_y={target.center_y:.2f}",
            f"  Bounding box: ({target.bbox.x1:.2f}, {target.bbox.y1:.2f}) to ({target.bbox.x2:.2f}, {target.bbox.y2:.2f})",
        ]

        if session.control_graph:
            neighbors = session.control_graph.neighbors(target.id)
            if neighbors:
                neighbor_labels = [n.label for n in neighbors[:6]]
                parts.append(f"  Nearby controls: {', '.join(neighbor_labels)}")

        return "\n".join(parts)

    async def _estimate_guidance(self, frame_b64: str, session: GuidanceSession) -> GuidanceFeedback:
        """Analyze the live camera frame using OpenAI Vision to produce directional cues."""
        target_context = self._build_target_context(session)

        content_parts: list[dict] = []

        if session.reference_image_b64:
            content_parts.append({
                "type": "text",
                "text": "REFERENCE IMAGE (the full panel from the initial scan):",
            })
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{session.reference_image_b64}", "detail": "low"},
            })

        content_parts.append({
            "type": "text",
            "text": f"LIVE CAMERA FRAME (what the user's camera currently sees):",
        })
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}", "detail": "low"},
        })

        content_parts.append({
            "type": "text",
            "text": target_context,
        })

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": _GUIDANCE_SYSTEM_PROMPT},
                    {"role": "user", "content": content_parts},
                ],
                max_tokens=256,
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            if not raw:
                raise ValueError("Empty response from OpenAI")

            data = json.loads(raw)
            direction = data.get("direction", "hold")
            proximity = float(data.get("proximity", 0.5))
            feedback = data.get("feedback", f"Move toward {session.target_control.label}.")

            proximity = max(0.0, min(1.0, proximity))

            return GuidanceFeedback(
                spoken_feedback=feedback,
                proximity_estimate=round(proximity, 2),
                alignment_confidence=round(max(0.2, proximity), 2),
                direction_hint=direction,
                target_visible=proximity >= 0.7,
            )
        except Exception as error:
            logger.warning(f"Guidance Vision API call failed: {error}")
            return self._fallback_guidance(session)

    def _fallback_guidance(self, session: GuidanceSession) -> GuidanceFeedback:
        """Static fallback when the Vision API is unavailable."""
        return GuidanceFeedback(
            spoken_feedback=(
                f"I couldn't analyze the frame. "
                f"Try pointing your camera at the panel and look for {session.target_control.label}."
            ),
            proximity_estimate=0.0,
            alignment_confidence=0.0,
            direction_hint="forward",
            target_visible=False,
        )
