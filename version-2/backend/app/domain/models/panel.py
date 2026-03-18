from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ControlType(str, Enum):
    ACTION = "action"
    NUMBER = "number"
    MODE = "mode"
    SETTING = "setting"
    DIAL = "dial"
    TOGGLE = "toggle"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    DISPLAY = "display"
    OTHER = "other"


class SpatialRelation(str, Enum):
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    ABOVE = "above"
    BELOW = "below"
    ADJACENT_TO = "adjacent_to"
    INSIDE_REGION = "inside_region"
    NEAR = "near"
    ALIGNED_WITH = "aligned_with"


class BoundingBox(BaseModel):
    """Normalized bounding box with coordinates in [0, 1] relative to panel crop."""

    x1: float = Field(..., ge=0.0, le=1.0)
    y1: float = Field(..., ge=0.0, le=1.0)
    x2: float = Field(..., ge=0.0, le=1.0)
    y2: float = Field(..., ge=0.0, le=1.0)

    @field_validator("x2")
    @classmethod
    def x2_greater_than_x1(cls, v: float, info) -> float:
        if "x1" in info.data and v < info.data["x1"]:
            raise ValueError("x2 must be >= x1")
        return v

    @field_validator("y2")
    @classmethod
    def y2_greater_than_y1(cls, v: float, info) -> float:
        if "y1" in info.data and v < info.data["y1"]:
            raise ValueError("y2 must be >= y1")
        return v

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height

    def iou(self, other: BoundingBox) -> float:
        """Intersection over union with another bounding box."""
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)
        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0
        intersection = (ix2 - ix1) * (iy2 - iy1)
        union = self.area + other.area - intersection
        return intersection / union if union > 0 else 0.0


class OCRToken(BaseModel):
    """A single text token extracted by OCR with its bounding box."""

    text: str
    bbox: BoundingBox
    confidence: float = Field(..., ge=0.0, le=1.0)


class ControlNode(BaseModel):
    """Represents a single control on the panel (button, dial, toggle, etc.)."""

    id: str
    label: str
    aliases: list[str] = Field(default_factory=list)
    type: ControlType = ControlType.OTHER
    bbox: BoundingBox
    region_id: str | None = None
    row_index: int | None = None
    col_index: int | None = None
    is_primary_action: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    spoken_description: str = ""

    @property
    def center_x(self) -> float:
        return self.bbox.center_x

    @property
    def center_y(self) -> float:
        return self.bbox.center_y

    def matches_query(self, query: str) -> bool:
        """Check if this control matches a user query (label or alias)."""
        q = query.strip().lower()
        if q == self.label.lower():
            return True
        return any(a.lower() == q for a in self.aliases)


class Region(BaseModel):
    """A grouped section of the panel (e.g., number_pad, action_column)."""

    id: str
    label: str
    bbox: BoundingBox
    control_ids: list[str] = Field(default_factory=list)
    description: str = ""


class Landmark(BaseModel):
    """A non-interactive visual or spatial anchor on the panel."""

    id: str
    label: str
    bbox: BoundingBox
    description: str = ""


class PanelMap(BaseModel):
    """Complete structured representation of a parsed control panel."""

    panel_id: str
    appliance_type: str = "unknown"
    scan_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    panel_bbox: BoundingBox | None = None
    orientation: str = "portrait"
    regions: list[Region] = Field(default_factory=list)
    controls: list[ControlNode] = Field(default_factory=list)
    landmarks: list[Landmark] = Field(default_factory=list)
    global_description: str = ""
    raw_ocr: list[OCRToken] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    def get_control(self, control_id: str) -> ControlNode | None:
        for c in self.controls:
            if c.id == control_id:
                return c
        return None

    def get_region(self, region_id: str) -> Region | None:
        for r in self.regions:
            if r.id == region_id:
                return r
        return None

    def controls_in_region(self, region_id: str) -> list[ControlNode]:
        region = self.get_region(region_id)
        if not region:
            return []
        return [c for c in self.controls if c.id in region.control_ids]


class SpatialEdge(BaseModel):
    """A directional spatial relationship between two controls."""

    source_id: str
    target_id: str
    relation: SpatialRelation


class ControlGraph(BaseModel):
    """Graph of controls with spatial relationships, derived from PanelMap."""

    nodes: list[ControlNode] = Field(default_factory=list)
    edges: list[SpatialEdge] = Field(default_factory=list)
    regions: list[Region] = Field(default_factory=list)

    def get_node(self, node_id: str) -> ControlNode | None:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def neighbors(self, node_id: str, relation: SpatialRelation | None = None) -> list[ControlNode]:
        """Get all neighbors of a node, optionally filtered by relation type."""
        target_ids: list[str] = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if relation is None or edge.relation == relation:
                    target_ids.append(edge.target_id)
        return [n for n in self.nodes if n.id in target_ids]

    def controls_in_row(self, row_index: int) -> list[ControlNode]:
        return sorted(
            [n for n in self.nodes if n.row_index == row_index],
            key=lambda n: n.center_x,
        )

    def controls_in_column(self, col_index: int) -> list[ControlNode]:
        return sorted(
            [n for n in self.nodes if n.col_index == col_index],
            key=lambda n: n.center_y,
        )

    def find_control(self, query: str) -> ControlNode | None:
        """Fuzzy-find a control by label or alias."""
        q = query.strip().lower()
        for node in self.nodes:
            if node.label.lower() == q:
                return node
        for node in self.nodes:
            if any(a.lower() == q for a in node.aliases):
                return node
        for node in self.nodes:
            if q in node.label.lower() or node.label.lower() in q:
                return node
        return None
