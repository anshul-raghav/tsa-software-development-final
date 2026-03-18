from __future__ import annotations

from app.core.logging import logger
from app.domain.models.panel import (
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

        sorted_by_y = sorted(nodes, key=lambda n: n.center_y)
        row_clusters: list[list[ControlNode]] = []
        current_cluster: list[ControlNode] = [sorted_by_y[0]]

        for node in sorted_by_y[1:]:
            if abs(node.center_y - current_cluster[-1].center_y) <= self.ROW_TOLERANCE:
                current_cluster.append(node)
            else:
                row_clusters.append(current_cluster)
                current_cluster = [node]
        row_clusters.append(current_cluster)

        for row_idx, cluster in enumerate(row_clusters):
            sorted_row = sorted(cluster, key=lambda n: n.center_x)
            for col_idx, node in enumerate(sorted_row):
                node.row_index = row_idx
                node.col_index = col_idx

        sorted_by_x = sorted(nodes, key=lambda n: n.center_x)
        col_clusters: list[list[ControlNode]] = []
        current_col: list[ControlNode] = [sorted_by_x[0]]

        for node in sorted_by_x[1:]:
            if abs(node.center_x - current_col[-1].center_x) <= self.COL_TOLERANCE:
                current_col.append(node)
            else:
                col_clusters.append(current_col)
                current_col = [node]
        col_clusters.append(current_col)

        for col_idx, cluster in enumerate(col_clusters):
            for node in cluster:
                node.col_index = col_idx

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

                if a.row_index is not None and a.row_index == b.row_index:
                    if dx > 0.01:
                        edges.append(SpatialEdge(source_id=a.id, target_id=b.id, relation=SpatialRelation.LEFT_OF))
                    elif dx < -0.01:
                        edges.append(SpatialEdge(source_id=a.id, target_id=b.id, relation=SpatialRelation.RIGHT_OF))

                if a.col_index is not None and a.col_index == b.col_index:
                    if dy > 0.01:
                        edges.append(SpatialEdge(source_id=a.id, target_id=b.id, relation=SpatialRelation.ABOVE))
                    elif dy < -0.01:
                        edges.append(SpatialEdge(source_id=a.id, target_id=b.id, relation=SpatialRelation.BELOW))

                if dist <= self.ADJACENCY_THRESHOLD:
                    edges.append(SpatialEdge(source_id=a.id, target_id=b.id, relation=SpatialRelation.ADJACENT_TO))

        for region in regions:
            for cid in region.control_ids:
                edges.append(SpatialEdge(source_id=cid, target_id=region.id, relation=SpatialRelation.INSIDE_REGION))

        return edges

    def _generate_spoken_descriptions(self, nodes: list[ControlNode], regions: list[Region]):
        """Generate human-friendly spatial descriptions for each control."""
        if not nodes:
            return

        max_row = max((n.row_index for n in nodes if n.row_index is not None), default=0)
        max_col = max((n.col_index for n in nodes if n.col_index is not None), default=0)

        for node in nodes:
            parts: list[str] = []

            v_pos = self._vertical_position(node.center_y)
            h_pos = self._horizontal_position(node.center_x)
            parts.append(f"{node.label} is in the {v_pos}-{h_pos}")

            if node.region_id:
                region = next((r for r in regions if r.id == node.region_id), None)
                if region:
                    parts.append(f"of the {region.label}")

            corner = self._corner_description(node.center_x, node.center_y)
            if corner:
                parts = [f"{node.label} is in the {corner}"]
                if node.region_id:
                    region = next((r for r in regions if r.id == node.region_id), None)
                    if region:
                        parts.append(f"of the {region.label}")

            node.spoken_description = " ".join(parts)

    def _vertical_position(self, y: float) -> str:
        if y < 0.33:
            return "top"
        if y < 0.66:
            return "middle"
        return "bottom"

    def _horizontal_position(self, x: float) -> str:
        if x < 0.33:
            return "left"
        if x < 0.66:
            return "center"
        return "right"

    def _corner_description(self, x: float, y: float) -> str | None:
        if x < 0.25 and y < 0.25:
            return "top-left corner"
        if x > 0.75 and y < 0.25:
            return "top-right corner"
        if x < 0.25 and y > 0.75:
            return "bottom-left corner"
        if x > 0.75 and y > 0.75:
            return "bottom-right corner"
        if 0.35 < x < 0.65 and 0.35 < y < 0.65:
            return "center"
        return None
