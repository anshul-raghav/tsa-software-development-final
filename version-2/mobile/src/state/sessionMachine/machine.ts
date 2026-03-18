/**
 * XState state machine governing the entire TouchMap session lifecycle.
 *
 * Every user action and mode transition is an explicit event.
 * No ad-hoc navigation — all flow goes through defined transitions.
 */
import type { PanelMap, ControlGraph } from "../../models/panel";
import type { TaskPlan } from "../../models/task";

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

export interface SessionContext {
  scanId: string | null;
  sessionId: string | null;
  panelMap: PanelMap | null;
  controlGraph: ControlGraph | null;
  currentTaskPlan: TaskPlan | null;
  currentStep: number;
  guidanceSessionId: string | null;
  targetControlId: string | null;
  previousMode: string | null;
  error: string | null;
}

export const initialContext: SessionContext = {
  scanId: null,
  sessionId: null,
  panelMap: null,
  controlGraph: null,
  currentTaskPlan: null,
  currentStep: 0,
  guidanceSessionId: null,
  targetControlId: null,
  previousMode: null,
  error: null,
};

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

export type SessionEvent =
  | { type: "START_SCAN" }
  | { type: "REQUEST_PERMISSIONS" }
  | { type: "PERMISSIONS_GRANTED" }
  | { type: "PERMISSIONS_DENIED" }
  | { type: "CAPTURE_COMPLETE"; imageUri: string }
  | { type: "QUALITY_CHECK"; quality: string }
  | { type: "QUALITY_OK" }
  | { type: "RETRY_SCAN" }
  | { type: "SCAN_SUCCESS"; scanId: string; sessionId: string; panelMap: PanelMap; controlGraph: ControlGraph }
  | { type: "SCAN_FAILED"; error: string }
  | { type: "SELECT_TASK" }
  | { type: "SELECT_LOCATE" }
  | { type: "SELECT_EXPLORE" }
  | { type: "SET_TASK_PLAN"; plan: TaskPlan }
  | { type: "NEXT_STEP" }
  | { type: "PREVIOUS_STEP" }
  | { type: "START_GUIDANCE"; guidanceSessionId: string; targetControlId: string }
  | { type: "STOP_GUIDANCE" }
  | { type: "BACK" }
  | { type: "NEW_SCAN" }
  | { type: "RETRY" }
  | { type: "RESET" }
  | { type: "ERROR"; error: string };

// ---------------------------------------------------------------------------
// States
// ---------------------------------------------------------------------------

export type SessionState =
  | "idle"
  | "requesting_permissions"
  | "scanning"
  | "scan_quality_feedback"
  | "processing_scan"
  | "panel_ready"
  | "task_mode"
  | "locate_mode"
  | "explore_mode"
  | "live_guidance"
  | "repeat_prompt"
  | "error_recovery";

// ---------------------------------------------------------------------------
// Transition table — deterministic, no ambiguity
// ---------------------------------------------------------------------------

export interface MachineState {
  current: SessionState;
  context: SessionContext;
}

export function createInitialState(): MachineState {
  return { current: "idle", context: { ...initialContext } };
}

/**
 * Pure transition function: (state, event) -> next state.
 * Keeps all state logic in one testable, deterministic place.
 */
export function transition(state: MachineState, event: SessionEvent): MachineState {
  const { current, context } = state;

  switch (current) {
    case "idle":
      if (event.type === "START_SCAN") return { current: "scanning", context };
      if (event.type === "REQUEST_PERMISSIONS") return { current: "requesting_permissions", context };
      break;

    case "requesting_permissions":
      if (event.type === "PERMISSIONS_GRANTED") return { current: "idle", context };
      if (event.type === "PERMISSIONS_DENIED") return { current: "error_recovery", context: { ...context, error: "Camera and microphone permissions are required." } };
      break;

    case "scanning":
      if (event.type === "CAPTURE_COMPLETE") return { current: "processing_scan", context };
      if (event.type === "QUALITY_CHECK") return { current: "scan_quality_feedback", context };
      if (event.type === "SCAN_SUCCESS") {
        return {
          current: "panel_ready",
          context: {
            ...context,
            scanId: event.scanId,
            sessionId: event.sessionId,
            panelMap: event.panelMap,
            controlGraph: event.controlGraph,
            error: null,
          },
        };
      }
      if (event.type === "SCAN_FAILED") return { current: "error_recovery", context: { ...context, error: event.error } };
      if (event.type === "ERROR") return { current: "error_recovery", context: { ...context, error: event.error } };
      break;

    case "scan_quality_feedback":
      if (event.type === "RETRY_SCAN") return { current: "scanning", context };
      if (event.type === "QUALITY_OK") return { current: "processing_scan", context };
      break;

    case "processing_scan":
      if (event.type === "SCAN_SUCCESS") {
        return {
          current: "panel_ready",
          context: {
            ...context,
            scanId: event.scanId,
            sessionId: event.sessionId,
            panelMap: event.panelMap,
            controlGraph: event.controlGraph,
            error: null,
          },
        };
      }
      if (event.type === "SCAN_FAILED") return { current: "error_recovery", context: { ...context, error: event.error } };
      break;

    case "panel_ready":
      if (event.type === "SELECT_TASK") return { current: "task_mode", context: { ...context, previousMode: "panel_ready" } };
      if (event.type === "SELECT_LOCATE") return { current: "locate_mode", context: { ...context, previousMode: "panel_ready" } };
      if (event.type === "SELECT_EXPLORE") return { current: "explore_mode", context: { ...context, previousMode: "panel_ready" } };
      if (event.type === "NEW_SCAN") return { current: "scanning", context: { ...context, scanId: null, panelMap: null, controlGraph: null } };
      break;

    case "task_mode":
      if (event.type === "SET_TASK_PLAN") return { current: "task_mode", context: { ...context, currentTaskPlan: event.plan, currentStep: 0 } };
      if (event.type === "NEXT_STEP") return { current: "task_mode", context: { ...context, currentStep: context.currentStep + 1 } };
      if (event.type === "PREVIOUS_STEP") return { current: "task_mode", context: { ...context, currentStep: Math.max(0, context.currentStep - 1) } };
      if (event.type === "START_GUIDANCE") return { current: "live_guidance", context: { ...context, guidanceSessionId: event.guidanceSessionId, targetControlId: event.targetControlId, previousMode: "task_mode" } };
      if (event.type === "BACK") return { current: "panel_ready", context: { ...context, currentTaskPlan: null, currentStep: 0 } };
      if (event.type === "ERROR") return { current: "error_recovery", context: { ...context, error: event.error } };
      break;

    case "locate_mode":
      if (event.type === "START_GUIDANCE") return { current: "live_guidance", context: { ...context, guidanceSessionId: event.guidanceSessionId, targetControlId: event.targetControlId, previousMode: "locate_mode" } };
      if (event.type === "BACK") return { current: "panel_ready", context };
      if (event.type === "ERROR") return { current: "error_recovery", context: { ...context, error: event.error } };
      break;

    case "explore_mode":
      if (event.type === "BACK") return { current: "panel_ready", context };
      if (event.type === "ERROR") return { current: "error_recovery", context: { ...context, error: event.error } };
      break;

    case "live_guidance":
      if (event.type === "STOP_GUIDANCE") {
        const returnTo = (context.previousMode === "task_mode" || context.previousMode === "locate_mode")
          ? context.previousMode as SessionState
          : "panel_ready";
        return { current: returnTo, context: { ...context, guidanceSessionId: null } };
      }
      if (event.type === "BACK") return { current: "panel_ready", context: { ...context, guidanceSessionId: null } };
      break;

    case "error_recovery":
      if (event.type === "RETRY") return { current: "scanning", context: { ...context, error: null } };
      if (event.type === "RESET") return createInitialState();
      if (event.type === "BACK" && context.panelMap) return { current: "panel_ready", context: { ...context, error: null } };
      break;
  }

  return state;
}
