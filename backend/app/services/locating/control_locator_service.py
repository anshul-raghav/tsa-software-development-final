"""
Resolves a user query to a specific control and returns spatial instructions and a GuidanceTarget for live guidance.
"""
from __future__ import annotations

from app.core.logging import logger
from app.core.exceptions import ControlNotFoundError
from app.domain.models.panel_map_models import PanelMap, ControlGraph, ControlNode
from app.domain.models.guidance_models import GuidanceTarget
from app.domain.schemas.locate_schemas import LocateResponse


class LocateService:
    """Resolves a user query to a specific control and generates spatial instructions."""

    def locate(
        self,
        query: str,
        control_graph: ControlGraph,
        panel_map: PanelMap,
    ) -> LocateResponse:
        logger.info(f"Locating control: '{query}'")

        control = control_graph.find_control(query)

        if not control:
            suggestions = self._suggest_similar(query, control_graph)
            if suggestions:
                spoken = (
                    f"I couldn't find '{query}'. "
                    f"Did you mean: {', '.join(suggestions[:3])}?"
                )
            else:
                spoken = f"I couldn't find a control matching '{query}' on this panel."

            return LocateResponse(
                spoken_instruction=spoken,
                confidence=0.0,
            )

        instruction = self._build_instruction(control, control_graph)
        guidance_target = GuidanceTarget(
            target_control_id=control.id,
            target_label=control.label,
            target_bbox=control.bbox,
            target_region=control.region_id,
            spoken_reference=control.spoken_description,
        )

        return LocateResponse(
            resolved_control_id=control.id,
            resolved_label=control.label,
            spoken_instruction=instruction,
            guidance_target=guidance_target,
            confidence=1.0,
        )

    def _build_instruction(self, control: ControlNode, graph: ControlGraph) -> str:
        parts: list[str] = []

        if control.spoken_description:
            parts.append(control.spoken_description)
        else:
            parts.append(f"{control.label} is on the panel")

        neighbors_above = graph.neighbors(control.id, relation=None)
        nearby = [
            n for n in neighbors_above
            if n.id != control.id
        ]

        if nearby:
            closest = min(nearby, key=lambda n: (
                (n.center_x - control.center_x) ** 2 + (n.center_y - control.center_y) ** 2
            ))
            dx = closest.center_x - control.center_x
            dy = closest.center_y - control.center_y

            if abs(dx) > abs(dy):
                direction = "left of" if dx > 0 else "right of"
            else:
                direction = "above" if dy > 0 else "below"

            parts.append(f"It is {direction} {closest.label}.")

        return " ".join(parts)

    def _suggest_similar(self, query: str, graph: ControlGraph) -> list[str]:
        q_lower = query.lower()
        suggestions: list[str] = []

        for node in graph.nodes:
            label_lower = node.label.lower()
            if q_lower in label_lower or label_lower in q_lower:
                suggestions.append(node.label)
                continue
            for alias in node.aliases:
                if q_lower in alias.lower() or alias.lower() in q_lower:
                    suggestions.append(node.label)
                    break

        return suggestions
