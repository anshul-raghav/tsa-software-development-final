/**
 * API request/response types matching every backend endpoint.
 */
import { PanelMap, ControlGraph, OCRToken } from "./panel";
import { TaskIntent, TaskPlan } from "./task";
import { GuidanceTarget, GuidanceFeedback } from "./guidance";

// --- Scan ---

export interface OCRResult {
  tokens: OCRToken[];
  raw_text: string;
}

export interface ScanResponse {
  scan_id: string;
  session_id: string;
  preprocessed_image_ref: string;
  ocr_result: OCRResult;
  panel_map: PanelMap;
  control_graph_summary: {
    node_count: number;
    edge_count: number;
    region_count: number;
  };
  confidence: number;
}

export interface ScanDetailResponse {
  scan_id: string;
  session_id: string;
  panel_map: PanelMap;
  control_graph: ControlGraph;
  ocr_result: OCRResult;
  preprocessed_image_ref: string;
}

// --- Task ---

export interface TaskPlanRequest {
  scan_id: string;
  user_request: string;
}

export interface TaskPlanResponse {
  parsed_intent: TaskIntent;
  task_plan: TaskPlan;
  confidence: number;
  clarification_needed: boolean;
}

export interface TaskRepeatRequest {
  scan_id: string;
  task_id: string;
  current_step: number;
}

export interface TaskRepeatResponse {
  step_instruction: string;
  spoken_hint: string;
  step_number: number;
}

export interface TaskClarifyRequest {
  scan_id: string;
  task_id: string;
  current_step: number;
  question: string;
}

export interface TaskClarifyResponse {
  clarification: string;
  route_to_locate: boolean;
  route_to_guidance: boolean;
  control_id: string | null;
}

// --- Locate ---

export interface LocateRequest {
  scan_id: string;
  query: string;
}

export interface LocateResponse {
  resolved_control_id: string | null;
  resolved_label: string;
  spoken_instruction: string;
  guidance_target: GuidanceTarget | null;
  confidence: number;
}

// --- Explore ---

export interface ExploreRequest {
  scan_id: string;
  query: string;
}

export interface ExploreResponse {
  spoken_description: string;
  referenced_region: string | null;
  referenced_controls: string[];
}

// --- Guidance ---

export interface GuidanceStartRequest {
  scan_id: string;
  target_control_id: string;
}

export interface GuidanceStartResponse {
  guidance_session_id: string;
  target_label: string;
  spoken_reference: string;
}

export interface GuidanceFrameResponse {
  feedback: GuidanceFeedback;
}

export interface GuidanceStopResponse {
  stopped: boolean;
  message: string;
}
