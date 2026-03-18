/**
 * Scan screen — camera view with audio-guided capture.
 * Provides spoken feedback during alignment and a large capture button.
 *
 * Also supports file upload as an alternative input method.
 * To remove upload support: delete the ImageUploadButton import and usage below.
 */
import React, { useRef, useState } from "react";
import { View, StyleSheet, SafeAreaView, Platform } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { Colors, Spacing } from "../constants/theme";
import VoiceButton from "../components/VoiceButton";
import ImageUploadButton from "../components/ImageUploadButton"; // REMOVABLE: delete this line to remove upload
import ScanOverlay from "../components/ScanOverlay";
import StatusBanner from "../components/StatusBanner";
import { speechService } from "../services/speech";
import { hapticService } from "../services/haptics";
import { apiClient } from "../services/api/client";
import type { ScanResponse } from "../models/api";

interface ScanScreenProps {
  onScanComplete: (result: ScanResponse) => void;
  onBack: () => void;
}

export default function ScanScreen({ onScanComplete, onBack }: ScanScreenProps) {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [isCapturing, setIsCapturing] = useState(false);
  const [statusText, setStatusText] = useState("Point camera at a control panel");

  const submitImage = async (uri: string) => {
    setIsCapturing(true);
    setStatusText("Processing scan...");
    await speechService.speak("Processing your scan.");

    try {
      const formData = new FormData();

      if (Platform.OS === "web") {
        const response = await fetch(uri);
        const blob = await response.blob();
        formData.append("image", blob, "scan.jpg");
      } else {
        formData.append("image", {
          uri,
          type: "image/jpeg",
          name: "scan.jpg",
        } as unknown as Blob);
      }

      const result = await apiClient.scanPanel(formData);
      await hapticService.success();
      await speechService.speak(
        `Panel scanned successfully. Found ${result.panel_map.controls.length} controls.`
      );
      onScanComplete(result);
    } catch (error) {
      await hapticService.error();
      const message = error instanceof Error ? error.message : "Scan failed";
      setStatusText("Scan failed. Try again.");
      await speechService.announceError(`Scan failed: ${message}. Please try again.`);
    } finally {
      setIsCapturing(false);
    }
  };

  const handleCapture = async () => {
    if (!cameraRef.current || isCapturing) return;

    setIsCapturing(true);
    setStatusText("Hold still...");
    await speechService.speak("Capturing. Hold still.");
    await hapticService.mediumTap();

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.85,
        base64: false,
        shutterSound: false,
      });

      if (!photo?.uri) {
        throw new Error("No photo captured");
      }

      await submitImage(photo.uri);
    } catch (error) {
      await hapticService.error();
      const message = error instanceof Error ? error.message : "Capture failed";
      setStatusText("Capture failed. Try again.");
      await speechService.announceError(`Capture failed: ${message}. Please try again.`);
      setIsCapturing(false);
    }
  };

  // REMOVABLE: delete this handler to remove upload
  const handleImageSelected = async (uri: string) => {
    await submitImage(uri);
  };

  if (!permission?.granted) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBanner title="Camera Access" onBack={onBack} />
        <View style={styles.permissionContainer}>
          <VoiceButton
            label="Grant Camera Permission"
            onPress={requestPermission}
            accessibilityHint="Requests access to your camera for scanning"
          />
          {/* REMOVABLE: delete this block to remove upload */}
          <ImageUploadButton
            onImageSelected={handleImageSelected}
            disabled={isCapturing}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBanner title="Scan Panel" onBack={onBack} />

      <View style={styles.cameraContainer}>
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          facing="back"
        >
          <ScanOverlay
            statusText={statusText}
            isProcessing={isCapturing}
          />
        </CameraView>
      </View>

      <View style={styles.controls}>
        <VoiceButton
          label={isCapturing ? "Processing..." : "Capture"}
          onPress={handleCapture}
          disabled={isCapturing}
          variant="primary"
          accessibilityHint="Takes a photo of the control panel"
        />
        {/* REMOVABLE: delete this block to remove upload */}
        <ImageUploadButton
          onImageSelected={handleImageSelected}
          disabled={isCapturing}
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
  },
  camera: {
    flex: 1,
  },
  controls: {
    padding: Spacing.lg,
    backgroundColor: Colors.background,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: "center",
    padding: Spacing.xl,
  },
});
