"""
Builds a spatial ControlGraph from a validated PanelMap: row/column assignment, region assignment,
edges (left_of, above, adjacent, inside_region), and spoken descriptions for each control.
"""
from __future__ import annotations

from app.core.logging import logger
from app.domain.models.panel_map_models import (
    PanelMap,
    ControlNode,
    ControlGraph,
    SpatialEdge,
    SpatialRelation,
    Region,
)


class ControlGraphService:
    """Builds a deterministic spatial graph from a validated PanelMap."""

    ROW_TOLERANCE = 0.06
    COL_TOLERANCE = 0.08
    ADJACENCY_THRESHOLD = 0.25
    DIRECTIONAL_DELTA_THRESHOLD = 0.01
    TOP_REGION_MAX = 0.33
    MIDDLE_REGION_MAX = 0.66
    LEFT_REGION_MAX = 0.33
    CENTER_REGION_MAX = 0.66
    CORNER_EDGE_THRESHOLD_LOW = 0.25
    CORNER_EDGE_THRESHOLD_HIGH = 0.75
    CENTER_MIN = 0.35
    CENTER_MAX = 0.65

    def build(self, panel_map: PanelMap) -> ControlGraph:
        logger.info(f"Building ControlGraph from {len(panel_map.controls)} controls")

        nodes = list(panel_map.controls)
        regions = list(panel_map.regions)

        self._assign_rows_and_columns(nodes)
        self._assign_regions(nodes, regions)
        edges = self._build_edges(nodes, regions)
        self._generate_spoken_descriptions(nodes, regions)

        graph = ControlGraph(nodes=nodes, edges=edges, regions=regions)
        logger.info(f"ControlGraph built: {len(nodes)} nodes, {len(edges)} edges, {len(regions)} regions")
        return graph

    def _assign_rows_and_columns(self, nodes: list[ControlNode]):
        """Cluster controls into rows (by y) and columns (by x)."""
        if not nodes:
            return

        row_clusters = self._cluster_nodes(
            nodes=nodes,
            sort_key=lambda n: n.center_y,
            tolerance=self.ROW_TOLERANCE,
        )

        for row_idx, cluster in enumerate(row_clusters):
            sorted_row = sorted(cluster, key=lambda n: n.center_x)
            for col_idx, node in enumerate(sorted_row):
                node.row_index = row_idx
                node.col_index = col_idx

        col_clusters = self._cluster_nodes(
            nodes=nodes,
            sort_key=lambda n: n.center_x,
            tolerance=self.COL_TOLERANCE,
        )

        for col_idx, cluster in enumerate(col_clusters):
            for node in cluster:
                node.col_index = col_idx

    def _cluster_nodes(
        self,
        *,
        nodes: list[ControlNode],
        sort_key,
        tolerance: float,
    ) -> list[list[ControlNode]]:
        sorted_nodes = sorted(nodes, key=sort_key)
        clusters: list[list[ControlNode]] = [[sorted_nodes[0]]]

        for node in sorted_nodes[1:]:
            current_cluster = clusters[-1]
            if abs(sort_key(node) - sort_key(current_cluster[-1])) <= tolerance:
                current_cluster.append(node)
            else:
                clusters.append([node])

        return clusters

    def _assign_regions(self, nodes: list[ControlNode], regions: list[Region]):
        """Assign controls to regions based on bbox containment."""
        for node in nodes:
            if node.region_id:
                continue
            for region in regions:
                if self._is_inside(node.bbox, region.bbox):
                    node.region_id = region.id
                    if node.id not in region.control_ids:
                        region.control_ids.append(node.id)
                    break

    def _is_inside(self, inner, outer) -> bool:
        return (
            inner.center_x >= outer.x1
            and inner.center_x <= outer.x2
            and inner.center_y >= outer.y1
            and inner.center_y <= outer.y2
        )

    def _build_edges(self, nodes: list[ControlNode], regions: list[Region]) -> list[SpatialEdge]:
        edges: list[SpatialEdge] = []

        for i, a in enumerate(nodes):
            for j, b in enumerate(nodes):
                if i == j:
                    continue

                dx = b.center_x - a.center_x
                dy = b.center_y - a.center_y
                dist = (dx**2 + dy**2) ** 0.5

                if dist > self.ADJACENCY_THRESHOLD:
                    continue

                self._append_directional_edges(edges=edges, source=a, target=b, dx=dx, dy=dy)
                edges.append(
                    SpatialEdge(
                        source_id=a.id,
                        target_id=b.id,
                        relation=SpatialRelation.ADJACENT_TO,
                    )
                )

        self._append_region_edges(edges=edges, regions=regions)

        return edges

    def _append_directional_edges(
        self,
        *,
        edges: list[SpatialEdge],
        source: ControlNode,
        target: ControlNode,
        dx: float,
        dy: float,
    ) -> None:
        if source.row_index is not None and source.row_index == target.row_index:
            if dx > self.DIRECTIONAL_DELTA_THRESHOLD:
                edges.append(
                    SpatialEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relation=SpatialRelation.LEFT_OF,
                    )
                )
            elif dx < -self.DIRECTIONAL_DELTA_THRESHOLD:
                edges.append(
                    SpatialEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relation=SpatialRelation.RIGHT_OF,
                    )
                )

        if source.col_index is not None and source.col_index == target.col_index:
            if dy > self.DIRECTIONAL_DELTA_THRESHOLD:
                edges.append(
                    SpatialEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relation=SpatialRelation.ABOVE,
                    )
                )
            elif dy < -self.DIRECTIONAL_DELTA_THRESHOLD:
                edges.append(
                    SpatialEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relation=SpatialRelation.BELOW,
                    )
                )

    def _append_region_edges(self, *, edges: list[SpatialEdge], regions: list[Region]) -> None:
        for region in regions:
            for cid in region.control_ids:
                edges.append(
                    SpatialEdge(
                        source_id=cid,
                        target_id=region.id,
                        relation=SpatialRelation.INSIDE_REGION,
                    )
                )

    def _generate_spoken_descriptions(self, nodes: list[ControlNode], regions: list[Region]):
        """Generate human-friendly spatial descriptions for each control."""
        if not nodes:
            return

        regions_by_id = {region.id: region for region in regions}

        for node in nodes:
            node.spoken_description = self._build_spoken_description(
                node=node,
                regions_by_id=regions_by_id,
            )

    def _build_spoken_description(
        self,
        *,
        node: ControlNode,
        regions_by_id: dict[str, Region],
    ) -> str:
        corner = self._corner_description(node.center_x, node.center_y)
        location_text = corner or f"{self._vertical_position(node.center_y)}-{self._horizontal_position(node.center_x)}"
        parts = [f"{node.label} is in the {location_text}"]

        if node.region_id:
            region = regions_by_id.get(node.region_id)
            if region:
                parts.append(f"of the {region.label}")

        return " ".join(parts)

    def _vertical_position(self, y: float) -> str:
        if y < self.TOP_REGION_MAX:
            return "top"
        if y < self.MIDDLE_REGION_MAX:
            return "middle"
        return "bottom"

    def _horizontal_position(self, x: float) -> str:
        if x < self.LEFT_REGION_MAX:
            return "left"
        if x < self.CENTER_REGION_MAX:
            return "center"
        return "right"

    def _corner_description(self, x: float, y: float) -> str | None:
        if x < self.CORNER_EDGE_THRESHOLD_LOW and y < self.CORNER_EDGE_THRESHOLD_LOW:
            return "top-left corner"
        if x > self.CORNER_EDGE_THRESHOLD_HIGH and y < self.CORNER_EDGE_THRESHOLD_LOW:
            return "top-right corner"
        if x < self.CORNER_EDGE_THRESHOLD_LOW and y > self.CORNER_EDGE_THRESHOLD_HIGH:
            return "bottom-left corner"
        if x > self.CORNER_EDGE_THRESHOLD_HIGH and y > self.CORNER_EDGE_THRESHOLD_HIGH:
            return "bottom-right corner"
        if self.CENTER_MIN < x < self.CENTER_MAX and self.CENTER_MIN < y < self.CENTER_MAX:
            return "center"
        return None
