/**
 * Locate Mode — find a specific control by name.
 * Returns a spatial description and optionally routes to live guidance.
 */
import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import { Colors, FontSize, Spacing, TouchTarget } from "../constants/design-tokens";
import ScreenGradientBackground from "../components/full-screen-gradient-background";
import StatusBanner from "../components/screen-status-banner";
import VoiceButton from "../components/haptic-feedback-button";
import SpokenPromptCard from "../components/spoken-prompt-card";
import { speechService } from "../services/speech/text-to-speech-service";
import { hapticService } from "../services/haptics/haptic-feedback-service";
import { apiClient } from "../services/api/touchmap-backend-api-client";
import type { LocateResponse } from "../models/touchmap-backend-api-types";

interface LocateModeScreenProps {
  scanId: string;
  onStartGuidance: (controlId: string) => void;
  onBack: () => void;
}

export default function LocateModeScreen({
  scanId,
  onStartGuidance,
  onBack,
}: LocateModeScreenProps) {
  const [controlQueryText, setControlQueryText] = useState("");
  const [locateResult, setLocateResult] = useState<LocateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async () => {
    const trimmedQuery = controlQueryText.trim();
    if (!trimmedQuery) {
      const msg = "Please enter a query";
      setErrorMessage(msg);
      await speechService.announceError(msg);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const locateResponse = await apiClient.locateControl(scanId, trimmedQuery);
      setLocateResult(locateResponse);
      await hapticService.success();
      const spokenInstruction =
        locateResponse.spoken_instruction?.trim() || "I found a match, but no directions were provided.";
      await speechService.speak(spokenInstruction);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not locate control";
      setErrorMessage(msg);
      await hapticService.error();
      await speechService.announceError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetGuidance = () => {
    if (locateResult?.guidance_target) {
      onStartGuidance(locateResult.guidance_target.target_control_id);
    }
  };

  const handleNewSearch = () => {
    setLocateResult(null);
    setControlQueryText("");
  };

  return (
    <ScreenGradientBackground>
      <SafeAreaView style={styles.container}>
        <StatusBanner title="Find a Control" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        {!locateResult && (
          <>
            <Text style={styles.prompt}>What control are you looking for?</Text>
            <TextInput
              style={styles.input}
              value={controlQueryText}
              onChangeText={setControlQueryText}
              placeholder='e.g. "Start" or "the 5 button"'
              placeholderTextColor={Colors.textMuted}
              accessibilityLabel="Control name"
              accessibilityHint="Type the name of the control you want to find"
              returnKeyType="search"
              onSubmitEditing={handleSearch}
            />
            <VoiceButton
              label={isLoading ? "Searching..." : "Find Control"}
              onPress={handleSearch}
              disabled={isLoading || !controlQueryText.trim()}
              accessibilityHint="Searches for the control on the panel"
            />
          </>
        )}

        {errorMessage && (
          <SpokenPromptCard text={errorMessage} autoSpeak={false} />
        )}

        {locateResult && (
          <View>
            <SpokenPromptCard
              text={locateResult.spoken_instruction || "No directions available."}
            />

            {locateResult.guidance_target && (
              <VoiceButton
                label="Get Live Guidance"
                onPress={handleGetGuidance}
                variant="secondary"
                accessibilityHint="Opens the camera to guide you to this control"
              />
            )}

            <VoiceButton
              label="Find Another Control"
              onPress={handleNewSearch}
              variant="outline"
              accessibilityHint="Search for a different control"
            />
          </View>
        )}
      </ScrollView>
      </SafeAreaView>
    </ScreenGradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "transparent",
  },
  content: {
    flex: 1,
  },
  contentInner: {
    padding: Spacing.lg,
  },
  prompt: {
    color: Colors.text,
    fontSize: FontSize.xl,
    fontWeight: "700",
    marginBottom: Spacing.lg,
  },
  input: {
    backgroundColor: Colors.surface,
    color: Colors.text,
    fontSize: FontSize.lg,
    padding: Spacing.lg,
    borderRadius: TouchTarget.borderRadius,
    borderWidth: 1,
    borderColor: Colors.border,
    minHeight: TouchTarget.minHeight,
    marginBottom: Spacing.md,
  },
});
