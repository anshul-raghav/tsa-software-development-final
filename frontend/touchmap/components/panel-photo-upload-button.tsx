/**
 * Self-contained image upload button using expo-image-picker.
 * Lets the user pick an image from their device library as an alternative to the live camera capture.
 */
import React from "react";
import * as ImagePicker from "expo-image-picker";
import VoiceButton from "./haptic-feedback-button";
import { hapticService } from "../services/haptics/haptic-feedback-service";
import { speechService } from "../services/speech/text-to-speech-service";

interface ImageUploadButtonProps {
  onImageSelected: (uri: string) => void;
  disabled?: boolean;
}

export default function ImageUploadButton({
  onImageSelected,
  disabled = false,
}: ImageUploadButtonProps) {
  const handleUpload = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permissionResult.granted) {
        await speechService.announceError("Photo library access is needed to upload an image.");
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        quality: 0.85,
        allowsEditing: false,
      });

      if (result.canceled || !result.assets?.[0]?.uri) {
        return;
      }

      await hapticService.lightTap();
      onImageSelected(result.assets[0].uri);
    } catch (error) {
      await hapticService.error();
      await speechService.announceError("Could not open photo library.");
    }
  };

  return (
    <VoiceButton
      label="Upload Image"
      onPress={handleUpload}
      variant="outline"
      disabled={disabled}
      accessibilityHint="Choose a photo from your device instead of using the camera"
    />
  );
}
