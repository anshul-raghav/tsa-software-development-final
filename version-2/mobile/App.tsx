/**
 * TouchMap — root application component.
 * Routes screens via the session state machine. No ad-hoc navigation.
 */
import React from "react";
import { StatusBar } from "react-native";
import { useSessionMachine } from "./src/state/hooks/useSessionMachine";
import HomeScreen from "./src/screens/HomeScreen";
import ScanScreen from "./src/screens/ScanScreen";
import PanelReadyScreen from "./src/screens/PanelReadyScreen";
import TaskModeScreen from "./src/screens/TaskModeScreen";
import LocateModeScreen from "./src/screens/LocateModeScreen";
import ExploreModeScreen from "./src/screens/ExploreModeScreen";
import LiveGuidanceScreen from "./src/screens/LiveGuidanceScreen";
import type { ScanResponse } from "./src/models/api";
import type { ControlGraph } from "./src/models/panel";

export default function App() {
  const { currentState, context, send } = useSessionMachine();

  const handleScanComplete = (result: ScanResponse) => {
    send({
      type: "SCAN_SUCCESS",
      scanId: result.scan_id,
      sessionId: result.session_id,
      panelMap: result.panel_map,
      controlGraph: result.panel_map as unknown as ControlGraph,
    });
  };

  const handleStartGuidance = async (controlId: string) => {
    send({
      type: "START_GUIDANCE",
      guidanceSessionId: `guidance_${Date.now()}`,
      targetControlId: controlId,
    });
  };

  const renderScreen = () => {
    switch (currentState) {
      case "idle":
      case "requesting_permissions":
        return (
          <HomeScreen
            onStartScan={() => send({ type: "START_SCAN" })}
          />
        );

      case "scanning":
      case "processing_scan":
        return (
          <ScanScreen
            onScanComplete={handleScanComplete}
            onBack={() => send({ type: "RESET" })}
          />
        );

      case "panel_ready":
        return context.panelMap ? (
          <PanelReadyScreen
            panelMap={context.panelMap}
            onSelectTask={() => send({ type: "SELECT_TASK" })}
            onSelectLocate={() => send({ type: "SELECT_LOCATE" })}
            onSelectExplore={() => send({ type: "SELECT_EXPLORE" })}
            onNewScan={() => send({ type: "NEW_SCAN" })}
            onBack={() => send({ type: "RESET" })}
          />
        ) : (
          <HomeScreen onStartScan={() => send({ type: "START_SCAN" })} />
        );

      case "task_mode":
        return context.scanId ? (
          <TaskModeScreen
            scanId={context.scanId}
            onStartGuidance={handleStartGuidance}
            onBack={() => send({ type: "BACK" })}
          />
        ) : null;

      case "locate_mode":
        return context.scanId ? (
          <LocateModeScreen
            scanId={context.scanId}
            onStartGuidance={handleStartGuidance}
            onBack={() => send({ type: "BACK" })}
          />
        ) : null;

      case "explore_mode":
        return context.scanId ? (
          <ExploreModeScreen
            scanId={context.scanId}
            onBack={() => send({ type: "BACK" })}
          />
        ) : null;

      case "live_guidance":
        return context.scanId && context.targetControlId ? (
          <LiveGuidanceScreen
            scanId={context.scanId}
            targetControlId={context.targetControlId}
            onStop={() => send({ type: "STOP_GUIDANCE" })}
          />
        ) : null;

      case "error_recovery":
        return (
          <HomeScreen
            onStartScan={() => send({ type: "RETRY" })}
          />
        );

      default:
        return (
          <HomeScreen onStartScan={() => send({ type: "START_SCAN" })} />
        );
    }
  };

  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#0A0A0A" />
      {renderScreen()}
    </>
  );
}
