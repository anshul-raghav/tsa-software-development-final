/**
 * React hook wrapping the session state machine.
 * Provides current state, context, and a dispatch function.
 */
import { useReducer, useCallback } from "react";
import {
  MachineState,
  SessionEvent,
  createInitialState,
  transition,
} from "../sessionMachine/machine";

export function useSessionMachine() {
  const [state, dispatch] = useReducer(
    (current: MachineState, event: SessionEvent) => transition(current, event),
    createInitialState()
  );

  const send = useCallback(
    (event: SessionEvent) => dispatch(event),
    []
  );

  return {
    currentState: state.current,
    context: state.context,
    send,
  };
}
