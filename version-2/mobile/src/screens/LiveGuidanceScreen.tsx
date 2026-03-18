/**
 * Live Guidance — real-time camera-based spoken cues to find a control.
 * Periodically captures frames and provides directional feedback.
 */
import React, { useRef, useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet, SafeAreaView } from "react-native";
import { CameraView } from "expo-camera";
import { Colors, FontSize, Spacing } from "../constants/theme";
import StatusBanner from "../components/StatusBanner";
import VoiceButton from "../components/VoiceButton";
import { speechService } from "../services/speech";
import { hapticService } from "../services/haptics";
import { apiClient } from "../services/api/client";
import { SCAN_SETTINGS } from "../constants/config";

interface LiveGuidanceScreenProps {
  scanId: string;
  targetControlId: string;
  onStop: () => void;
}

export default function LiveGuidanceScreen({
  scanId,
  targetControlId,
  onStop,
}: LiveGuidanceScreenProps) {
  const cameraRef = useRef<CameraView>(null);
  const [guidanceSessionId, setGuidanceSessionId] = useState<string | null>(null);
  const [currentFeedback, setCurrentFeedback] = useState("Starting guidance...");
  const [proximity, setProximity] = useState(0);
  const activeRef = useRef(true);
  const processingRef = useRef(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    activeRef.current = true;
    startSession();
    return () => {
      activeRef.current = false;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const startSession = async () => {
    try {
      const result = await apiClient.startGuidance(scanId, targetControlId);
      setGuidanceSessionId(result.guidance_session_id);
      await speechService.speak(
        `Guiding you to ${result.target_label}. ${result.spoken_reference}. Point your camera at the panel.`
      );
      scheduleNextFrame(result.guidance_session_id);
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      console.error("Guidance start failed:", detail);
      await speechService.announceError(`Could not start guidance. ${detail}`);
      onStop();
    }
  };

  const scheduleNextFrame = (sessionId: string) => {
    if (!activeRef.current) return;
    timeoutRef.current = setTimeout(
      () => captureAndProcess(sessionId),
      SCAN_SETTINGS.guidanceFrameIntervalMs,
    );
  };

  const captureAndProcess = async (sessionId: string) => {
    if (!activeRef.current || processingRef.current || !cameraRef.current) {
      scheduleNextFrame(sessionId);
      return;
    }

    processingRef.current = true;

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.5,
        base64: false,
        shutterSound: false,
      });

      if (!photo?.uri || !activeRef.current) {
        processingRef.current = false;
        scheduleNextFrame(sessionId);
        return;
      }

      const formData = new FormData();
      formData.append("frame", {
        uri: photo.uri,
        type: "image/jpeg",
        name: "frame.jpg",
      } as unknown as Blob);

      const response = await apiClient.processGuidanceFrame(sessionId, formData);
      const feedback = response.feedback;

      setCurrentFeedback(feedback.spoken_feedback);
      setProximity(feedback.proximity_estimate);

      if (feedback.proximity_estimate > 0.8) {
        await hapticService.heavyTap();
      } else if (feedback.proximity_estimate > 0.5) {
        await hapticService.mediumTap();
      } else {
        await hapticService.lightTap();
      }

      await speechService.speak(feedback.spoken_feedback);
    } catch {
      // Frame processing errors are non-fatal; skip and try next frame
    } finally {
      processingRef.current = false;
      scheduleNextFrame(sessionId);
    }
  };

  const handleStop = async () => {
    activeRef.current = false;
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    if (guidanceSessionId) {
      try {
        await apiClient.stopGuidance(guidanceSessionId);
      } catch {
        // Non-critical if stop request fails
      }
    }

    await speechService.speak("Guidance stopped.");
    onStop();
  };

  const proximityColor =
    proximity > 0.7 ? Colors.success : proximity > 0.4 ? Colors.warning : Colors.danger;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBanner title="Live Guidance" showBack={false} />

      <View style={styles.cameraContainer}>
        <CameraView ref={cameraRef} style={styles.camera} facing="back" />

        <View style={styles.feedbackOverlay}>
          <Text
            style={styles.feedbackText}
            accessibilityRole="text"
            accessibilityLiveRegion="assertive"
          >
            {currentFeedback}
          </Text>

          <View style={styles.proximityContainer}>
            <View
              style={[
                styles.proximityBar,
                { width: `${proximity * 100}%`, backgroundColor: proximityColor },
              ]}
            />
          </View>
          <Text style={styles.proximityLabel}>
            Proximity: {Math.round(proximity * 100)}%
          </Text>
        </View>
      </View>

      <View style={styles.controls}>
        <VoiceButton
          label="Stop Guidance"
          onPress={handleStop}
          variant="danger"
          accessibilityHint="Stops live guidance and returns to the previous screen"
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  cameraContainer: {
    flex: 1,
    position: "relative",
  },
  camera: {
    flex: 1,
  },
  feedbackOverlay: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: Colors.overlay,
    padding: Spacing.lg,
    alignItems: "center",
  },
  feedbackText: {
    color: Colors.text,
    fontSize: FontSize.xl,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: Spacing.md,
  },
  proximityContainer: {
    width: "100%",
    height: 8,
    backgroundColor: Colors.surfaceLight,
    borderRadius: 4,
    overflow: "hidden",
    marginBottom: Spacing.sm,
  },
  proximityBar: {
    height: "100%",
    borderRadius: 4,
  },
  proximityLabel: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
  },
  controls: {
    padding: Spacing.lg,
  },
});
