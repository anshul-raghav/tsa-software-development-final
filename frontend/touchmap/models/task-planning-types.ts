/**
 * Task planning models for goal-oriented interaction.
 */

export interface TaskIntent {
  appliance_type: string;
  intent: string;
  parameters: Record<string, unknown>;
  raw_query: string;
  confidence: number;
}

export type ActionType = "press" | "hold" | "turn" | "slide" | "wait" | "verify";

export interface TaskStep {
  step_number: number;
  action_type: ActionType;
  control_id: string;
  instruction: string;
  spoken_hint: string;
  verification_hint: string;
}

export interface TaskPlan {
  task_id: string;
  user_goal: string;
  appliance_type: string;
  intent: string;
  parameters: Record<string, unknown>;
  steps: TaskStep[];
  confidence: number;
  fallback_message: string;
  clarification_needed: boolean;
}
