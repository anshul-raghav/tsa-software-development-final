/**
 * Core domain models for panel representation.
 * Mirrors the backend PanelMap, ControlNode, and ControlGraph schemas.
 */

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface OCRToken {
  text: string;
  bbox: BoundingBox;
  confidence: number;
}

export type ControlType =
  | "action"
  | "number"
  | "mode"
  | "setting"
  | "dial"
  | "toggle"
  | "confirm"
  | "cancel"
  | "display"
  | "other";

export interface ControlNode {
  id: string;
  label: string;
  aliases: string[];
  type: ControlType;
  bbox: BoundingBox;
  region_id: string | null;
  row_index: number | null;
  col_index: number | null;
  is_primary_action: boolean;
  confidence: number;
  spoken_description: string;
}

export interface Region {
  id: string;
  label: string;
  bbox: BoundingBox;
  control_ids: string[];
  description: string;
}

export interface Landmark {
  id: string;
  label: string;
  bbox: BoundingBox;
  description: string;
}

export interface PanelMap {
  panel_id: string;
  appliance_type: string;
  scan_confidence: number;
  panel_bbox: BoundingBox | null;
  orientation: string;
  regions: Region[];
  controls: ControlNode[];
  landmarks: Landmark[];
  global_description: string;
  raw_ocr: OCRToken[];
  metadata: Record<string, unknown>;
}

export type SpatialRelation =
  | "left_of"
  | "right_of"
  | "above"
  | "below"
  | "adjacent_to"
  | "inside_region"
  | "near"
  | "aligned_with";

export interface SpatialEdge {
  source_id: string;
  target_id: string;
  relation: SpatialRelation;
}

export interface ControlGraph {
  nodes: ControlNode[];
  edges: SpatialEdge[];
  regions: Region[];
}
