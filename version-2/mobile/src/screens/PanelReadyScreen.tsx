/**
 * Panel Ready screen — shows scan results and three mode selection cards.
 * Speaks a confirmation and prompts the user to choose a mode.
 */
import React, { useEffect } from "react";
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import { Colors, FontSize, Spacing } from "../constants/theme";
import StatusBanner from "../components/StatusBanner";
import ModeCard from "../components/ModeCard";
import VoiceButton from "../components/VoiceButton";
import { speechService } from "../services/speech";
import type { PanelMap } from "../models/panel";

interface PanelReadyScreenProps {
  panelMap: PanelMap;
  onSelectTask: () => void;
  onSelectLocate: () => void;
  onSelectExplore: () => void;
  onNewScan: () => void;
  onBack: () => void;
}

export default function PanelReadyScreen({
  panelMap,
  onSelectTask,
  onSelectLocate,
  onSelectExplore,
  onNewScan,
  onBack,
}: PanelReadyScreenProps) {
  useEffect(() => {
    const controlCount = panelMap.controls.length;
    const applianceType = panelMap.appliance_type;
    speechService.speak(
      `Panel scanned successfully. This appears to be a ${applianceType} with ${controlCount} controls. ` +
      "Choose a mode: Complete a Task, Find a Control, or Explore the Layout."
    );
  }, [panelMap]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBanner title="Panel Ready" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        <View style={styles.summary}>
          <Text style={styles.applianceType}>
            {panelMap.appliance_type.toUpperCase()}
          </Text>
          <Text style={styles.controlCount}>
            {panelMap.controls.length} controls detected
          </Text>
          <Text style={styles.confidence}>
            Confidence: {Math.round(panelMap.scan_confidence * 100)}%
          </Text>
        </View>

        <Text style={styles.sectionTitle} accessibilityRole="header">
          Choose a Mode
        </Text>

        <ModeCard
          title="Complete a Task"
          description="Tell me what you want to do and I'll guide you step by step."
          iconLabel="T"
          onPress={onSelectTask}
          accessibilityHint="Opens task mode where you describe what you want to accomplish"
        />

        <ModeCard
          title="Find a Control"
          description="Ask me where a specific button or control is located."
          iconLabel="L"
          onPress={onSelectLocate}
          accessibilityHint="Opens locate mode to find a specific control on the panel"
        />

        <ModeCard
          title="Explore Layout"
          description="Ask me to describe sections of the panel to build a mental map."
          iconLabel="E"
          onPress={onSelectExplore}
          accessibilityHint="Opens explore mode to understand the panel layout"
        />

        <View style={styles.newScanContainer}>
          <VoiceButton
            label="Scan New Panel"
            onPress={onNewScan}
            variant="outline"
            accessibilityHint="Starts a new scan with the camera"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    flex: 1,
  },
  contentInner: {
    padding: Spacing.lg,
    paddingBottom: Spacing.xxl,
  },
  summary: {
    backgroundColor: Colors.surface,
    borderRadius: 16,
    padding: Spacing.lg,
    alignItems: "center",
    marginBottom: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  applianceType: {
    color: Colors.primary,
    fontSize: FontSize.xl,
    fontWeight: "800",
    letterSpacing: 2,
  },
  controlCount: {
    color: Colors.text,
    fontSize: FontSize.lg,
    marginTop: Spacing.sm,
  },
  confidence: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    marginTop: Spacing.xs,
  },
  sectionTitle: {
    color: Colors.text,
    fontSize: FontSize.lg,
    fontWeight: "700",
    marginBottom: Spacing.md,
  },
  newScanContainer: {
    marginTop: Spacing.xl,
  },
});
