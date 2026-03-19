/**
 * TouchMap — root application component.
 * Routes screens via the session state machine. No ad-hoc navigation.
 */
import React from "react";
import { StatusBar } from "react-native";
import { Gradient } from "./touchmap/constants/design-tokens";
import { useSessionMachine } from "./touchmap/state/hooks/use-touchmap-session-state-machine";
import HomeScreen from "./touchmap/screens/landing-start-scan-screen";
import ScanScreen from "./touchmap/screens/panel-scan-capture-screen";
import PanelReadyScreen from "./touchmap/screens/panel-ready-mode-selection-screen";
import TaskModeScreen from "./touchmap/screens/task-planning-mode-screen";
import LocateModeScreen from "./touchmap/screens/locate-control-mode-screen";
import ExploreModeScreen from "./touchmap/screens/explore-panel-layout-screen";
import LiveGuidanceScreen from "./touchmap/screens/live-vision-guidance-screen";
import type { ScanResponse } from "./touchmap/models/touchmap-backend-api-types";
import type { ControlGraph } from "./touchmap/models/panel-map-types";

export default function App() {
  const { currentState, sessionContext, sendSessionEvent } = useSessionMachine();

  const handleScanComplete = (result: ScanResponse) => {
    // Backend returns panel_map; we use it as both panel map and control-graph summary for the session.
    sendSessionEvent({
      type: "SCAN_SUCCESS",
      scanId: result.scan_id,
      sessionId: result.session_id,
      panelMap: result.panel_map,
      controlGraph: result.panel_map as unknown as ControlGraph,
    });
  };

  const handleStartGuidance = async (controlId: string) => {
    sendSessionEvent({
      type: "START_GUIDANCE",
      guidanceSessionId: `guidance_${Date.now()}`,
      targetControlId: controlId,
    });
  };

  // Map session state to the active screen; all transitions go through the state machine.
  const renderScreenForState = () => {
    switch (currentState) {
      case "idle":
      case "requesting_permissions":
        return (
          <HomeScreen
            onStartScan={() => sendSessionEvent({ type: "START_SCAN" })}
          />
        );

      case "scanning":
      case "processing_scan":
        return (
          <ScanScreen
            onScanComplete={handleScanComplete}
            onBack={() => sendSessionEvent({ type: "RESET" })}
          />
        );

      case "panel_ready":
        return sessionContext.panelMap ? (
          <PanelReadyScreen
            panelMap={sessionContext.panelMap}
            onSelectTask={() => sendSessionEvent({ type: "SELECT_TASK" })}
            onSelectLocate={() => sendSessionEvent({ type: "SELECT_LOCATE" })}
            onSelectExplore={() => sendSessionEvent({ type: "SELECT_EXPLORE" })}
            onNewScan={() => sendSessionEvent({ type: "NEW_SCAN" })}
            onBack={() => sendSessionEvent({ type: "RESET" })}
          />
        ) : (
          <HomeScreen onStartScan={() => sendSessionEvent({ type: "START_SCAN" })} />
        );

      case "task_mode":
        return sessionContext.scanId ? (
          <TaskModeScreen
            scanId={sessionContext.scanId}
            onStartGuidance={handleStartGuidance}
            onBack={() => sendSessionEvent({ type: "BACK" })}
          />
        ) : null;

      case "locate_mode":
        return sessionContext.scanId ? (
          <LocateModeScreen
            scanId={sessionContext.scanId}
            onStartGuidance={handleStartGuidance}
            onBack={() => sendSessionEvent({ type: "BACK" })}
          />
        ) : null;

      case "explore_mode":
        return sessionContext.scanId ? (
          <ExploreModeScreen
            scanId={sessionContext.scanId}
            onBack={() => sendSessionEvent({ type: "BACK" })}
          />
        ) : null;

      case "live_guidance":
        return sessionContext.scanId && sessionContext.targetControlId ? (
          <LiveGuidanceScreen
            scanId={sessionContext.scanId}
            targetControlId={sessionContext.targetControlId}
            onStop={() => sendSessionEvent({ type: "STOP_GUIDANCE" })}
          />
        ) : null;

      case "error_recovery":
        return (
          <HomeScreen
            onStartScan={() => sendSessionEvent({ type: "RETRY" })}
          />
        );

      default:
        return (
          <HomeScreen onStartScan={() => sendSessionEvent({ type: "START_SCAN" })} />
        );
    }
  };

  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor={Gradient.top} />
      {renderScreenForState()}
    </>
  );
}
