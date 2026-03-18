/**
 * Live guidance models for real-time control finding.
 */
import { BoundingBox } from "./panel";

export interface GuidanceTarget {
  target_control_id: string;
  target_label: string;
  target_bbox: BoundingBox;
  target_region: string | null;
  spoken_reference: string;
  confidence: number;
}

export interface GuidanceFeedback {
  spoken_feedback: string;
  proximity_estimate: number;
  alignment_confidence: number;
  direction_hint: string | null;
  target_visible: boolean;
}
