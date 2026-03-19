"""
Generates spoken layout descriptions for panel exploration: whole panel, regions, rows, sides, or matching controls.
"""
from __future__ import annotations

import re

from app.core.logging import logger
from app.domain.models.panel_map_models import PanelMap, ControlGraph, ControlNode, Region
from app.domain.schemas.explore_schemas import ExploreResponse


class ExploreService:
    """Generates spoken layout descriptions for panel exploration."""

    def explore(
        self,
        query: str,
        control_graph: ControlGraph,
        panel_map: PanelMap,
    ) -> ExploreResponse:
        logger.info(f"Exploring panel: '{query}'")
        query_lower = query.lower().strip()

        if self._is_whole_panel_query(query_lower):
            return self._describe_whole_panel(control_graph, panel_map)

        region = self._find_region(query_lower, control_graph)
        if region:
            return self._describe_region(region, control_graph)

        row_match = re.search(r"(top|middle|center|bottom)\s*row", query_lower)
        if row_match:
            return self._describe_row(row_match.group(1), control_graph)

        side_match = re.search(r"(left|right)\s*(?:side|column)?", query_lower)
        if side_match:
            return self._describe_side(side_match.group(1), control_graph)

        return self._describe_matching(query_lower, control_graph, panel_map)

    def _is_whole_panel_query(self, query: str) -> bool:
        whole_phrases = ["whole panel", "entire panel", "everything", "full layout", "describe all", "all controls"]
        return any(p in query for p in whole_phrases)

    def _describe_whole_panel(self, graph: ControlGraph, panel_map: PanelMap) -> ExploreResponse:
        parts: list[str] = []

        if panel_map.global_description:
            parts.append(panel_map.global_description)
        else:
            parts.append(f"This is a {panel_map.appliance_type} control panel with {len(graph.nodes)} controls.")

        if graph.regions:
            region_names = [r.label for r in graph.regions]
            parts.append(f"It has {len(graph.regions)} sections: {', '.join(region_names)}.")

        max_row = max((n.row_index for n in graph.nodes if n.row_index is not None), default=-1)
        for row_idx in range(max_row + 1):
            row_controls = graph.controls_in_row(row_idx)
            if row_controls:
                labels = [c.label for c in row_controls]
                row_name = self._row_name(row_idx, max_row)
                parts.append(f"The {row_name} has: {', '.join(labels)}.")

        return ExploreResponse(
            spoken_description=" ".join(parts),
            referenced_controls=[n.id for n in graph.nodes],
        )

    def _describe_region(self, region: Region, graph: ControlGraph) -> ExploreResponse:
        controls = [n for n in graph.nodes if n.id in region.control_ids]
        controls.sort(key=lambda c: (c.row_index or 0, c.col_index or 0))

        parts: list[str] = []
        if region.description:
            parts.append(region.description)
        else:
            parts.append(f"The {region.label} section contains {len(controls)} controls.")

        if controls:
            labels = [c.label for c in controls]
            parts.append(f"From top-left to bottom-right: {', '.join(labels)}.")

        return ExploreResponse(
            spoken_description=" ".join(parts),
            referenced_region=region.id,
            referenced_controls=[c.id for c in controls],
        )

    def _describe_row(self, position: str, graph: ControlGraph) -> ExploreResponse:
        max_row = max((n.row_index for n in graph.nodes if n.row_index is not None), default=0)

        if position in ("top",):
            target_row = 0
        elif position in ("bottom",):
            target_row = max_row
        else:
            target_row = max_row // 2

        controls = graph.controls_in_row(target_row)
        labels = [c.label for c in controls]

        description = f"The {position} row has {len(controls)} controls: {', '.join(labels)}." if labels else f"No controls found in the {position} row."

        return ExploreResponse(
            spoken_description=description,
            referenced_controls=[c.id for c in controls],
        )

    def _describe_side(self, side: str, graph: ControlGraph) -> ExploreResponse:
        threshold = 0.5
        if side == "left":
            controls = [n for n in graph.nodes if n.center_x < threshold]
        else:
            controls = [n for n in graph.nodes if n.center_x >= threshold]

        controls.sort(key=lambda c: (c.center_y, c.center_x))
        labels = [c.label for c in controls]

        description = f"The {side} side has {len(controls)} controls: {', '.join(labels)}." if labels else f"No controls found on the {side} side."

        return ExploreResponse(
            spoken_description=description,
            referenced_controls=[c.id for c in controls],
        )

    def _describe_matching(self, query: str, graph: ControlGraph, panel_map: PanelMap) -> ExploreResponse:
        matching: list[ControlNode] = []
        for node in graph.nodes:
            if query in node.label.lower() or any(query in a.lower() for a in node.aliases):
                matching.append(node)

        for region in graph.regions:
            if query in region.label.lower():
                return self._describe_region(region, graph)

        if matching:
            labels = [f"{c.label} ({c.spoken_description})" for c in matching]
            description = f"Found {len(matching)} matching controls: {'; '.join(labels)}."
        else:
            description = f"I couldn't find any controls or sections matching '{query}'. Try asking about a specific region, row, or the whole panel."

        return ExploreResponse(
            spoken_description=description,
            referenced_controls=[c.id for c in matching],
        )

    def _row_name(self, row_idx: int, max_row: int) -> str:
        if max_row <= 0:
            return "row"
        if row_idx == 0:
            return "top row"
        if row_idx == max_row:
            return "bottom row"
        if max_row >= 3 and row_idx == max_row // 2:
            return "middle row"
        return f"row {row_idx + 1}"

    def _find_region(self, query: str, graph: ControlGraph) -> Region | None:
        for region in graph.regions:
            if region.label.lower() in query or region.id.lower() in query:
                return region
            if query in region.label.lower():
                return region
        return None
