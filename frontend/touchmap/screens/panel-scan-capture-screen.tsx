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
import { Colors, Spacing } from "../constants/design-tokens";
import VoiceButton from "../components/haptic-feedback-button";
import ImageUploadButton from "../components/panel-photo-upload-button"; // REMOVABLE: delete this line to remove upload
import ScanOverlay from "../components/panel-scan-guidance-overlay";
import StatusBanner from "../components/screen-status-banner";
import { speechService } from "../services/speech/text-to-speech-service";
import { hapticService } from "../services/haptics/haptic-feedback-service";
import { apiClient } from "../services/api/touchmap-backend-api-client";
import type { ScanResponse } from "../models/touchmap-backend-api-types";

interface ScanScreenProps {
  onScanComplete: (scanResult: ScanResponse) => void;
  onBack: () => void;
}

export default function ScanScreen({ onScanComplete, onBack }: ScanScreenProps) {
  const cameraRef = useRef<CameraView>(null);
  const [cameraPermission, requestPermission] = useCameraPermissions();
  const [isProcessing, setIsProcessing] = useState(false);
  const [scanStatusMessage, setScanStatusMessage] = useState("Point camera at a control panel");

  const uploadScanImage = async (imageUri: string) => {
    setIsProcessing(true);
    setScanStatusMessage("Processing scan...");
    await speechService.speak("Processing your scan.");

    try {
      const formData = new FormData();

      if (Platform.OS === "web") {
        const response = await fetch(imageUri);
        const blob = await response.blob();
        formData.append("image", blob, "scan.jpg");
      } else {
        formData.append("image", {
          uri: imageUri,
          type: "image/jpeg",
          name: "scan.jpg",
        } as unknown as Blob);
      }

      const scanResult = await apiClient.scanPanel(formData);
      await hapticService.success();
      const controlCount = scanResult.panel_map?.controls?.length ?? 0;
      await speechService.speak(
        `Panel scanned successfully. Found ${controlCount} controls.`
      );
      onScanComplete(scanResult);
    } catch (error) {
      await hapticService.error();
      const message = error instanceof Error ? error.message : "Scan failed";
      setScanStatusMessage("Scan failed. Try again.");
      await speechService.announceError(`Scan failed: ${message}. Please try again.`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCapture = async () => {
    if (!cameraRef.current || isProcessing) return;

    setIsProcessing(true);
    setScanStatusMessage("Hold still...");
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

      await uploadScanImage(photo.uri);
    } catch (error) {
      await hapticService.error();
      const message = error instanceof Error ? error.message : "Capture failed";
      setScanStatusMessage("Capture failed. Try again.");
      await speechService.announceError(`Capture failed: ${message}. Please try again.`);
      setIsProcessing(false);
    }
  };

  // REMOVABLE: delete this handler to remove upload
  const handleImageSelected = async (uri: string) => {
    await uploadScanImage(uri);
  };

  if (!cameraPermission?.granted) {
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
            disabled={isProcessing}
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
            statusText={scanStatusMessage}
            isProcessing={isProcessing}
          />
        </CameraView>
      </View>

      <View style={styles.controls}>
        <VoiceButton
          label={isProcessing ? "Processing..." : "Capture"}
          onPress={handleCapture}
          disabled={isProcessing}
          variant="primary"
          accessibilityHint="Takes a photo of the control panel"
        />
        {/* REMOVABLE: delete this block to remove upload */}
        <ImageUploadButton
          onImageSelected={handleImageSelected}
          disabled={isProcessing}
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
