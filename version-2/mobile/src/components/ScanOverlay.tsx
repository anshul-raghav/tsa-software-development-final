/**
 * Camera overlay for scan guidance — frame guide, status text, quality indicator.
 */
import React from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";
import { Colors, FontSize, Spacing } from "../constants/theme";

interface ScanOverlayProps {
  statusText: string;
  qualityLabel?: string;
  isProcessing?: boolean;
}

const { width: SCREEN_WIDTH } = Dimensions.get("window");
const GUIDE_SIZE = SCREEN_WIDTH * 0.8;

export default function ScanOverlay({
  statusText,
  qualityLabel,
  isProcessing = false,
}: ScanOverlayProps) {
  return (
    <View style={styles.overlay} pointerEvents="none">
      <View style={styles.guideFrame}>
        <View style={[styles.corner, styles.topLeft]} />
        <View style={[styles.corner, styles.topRight]} />
        <View style={[styles.corner, styles.bottomLeft]} />
        <View style={[styles.corner, styles.bottomRight]} />
      </View>

      <View style={styles.statusContainer}>
        <Text
          style={styles.statusText}
          accessibilityRole="text"
          accessibilityLabel={statusText}
          accessibilityLiveRegion="polite"
        >
          {isProcessing ? "Processing..." : statusText}
        </Text>

        {qualityLabel && (
          <Text style={styles.qualityLabel}>
            Quality: {qualityLabel}
          </Text>
        )}
      </View>
    </View>
  );
}

const CORNER_SIZE = 40;
const CORNER_WIDTH = 4;

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
  },
  guideFrame: {
    width: GUIDE_SIZE,
    height: GUIDE_SIZE,
    position: "relative",
  },
  corner: {
    position: "absolute",
    width: CORNER_SIZE,
    height: CORNER_SIZE,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderTopWidth: CORNER_WIDTH,
    borderLeftWidth: CORNER_WIDTH,
    borderColor: Colors.primary,
  },
  topRight: {
    top: 0,
    right: 0,
    borderTopWidth: CORNER_WIDTH,
    borderRightWidth: CORNER_WIDTH,
    borderColor: Colors.primary,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderBottomWidth: CORNER_WIDTH,
    borderLeftWidth: CORNER_WIDTH,
    borderColor: Colors.primary,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderBottomWidth: CORNER_WIDTH,
    borderRightWidth: CORNER_WIDTH,
    borderColor: Colors.primary,
  },
  statusContainer: {
    position: "absolute",
    bottom: 80,
    alignItems: "center",
    paddingHorizontal: Spacing.lg,
  },
  statusText: {
    color: Colors.text,
    fontSize: FontSize.xl,
    fontWeight: "700",
    textAlign: "center",
    backgroundColor: Colors.overlay,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderRadius: 12,
    overflow: "hidden",
  },
  qualityLabel: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    marginTop: Spacing.sm,
    backgroundColor: Colors.overlay,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: 8,
    overflow: "hidden",
  },
});
