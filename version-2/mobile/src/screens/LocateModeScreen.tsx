/**
 * Locate Mode — find a specific control by name.
 * Returns a spatial description and optionally routes to live guidance.
 */
import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import { Colors, FontSize, Spacing, TouchTarget } from "../constants/theme";
import StatusBanner from "../components/StatusBanner";
import VoiceButton from "../components/VoiceButton";
import SpokenPromptCard from "../components/SpokenPromptCard";
import { speechService } from "../services/speech";
import { hapticService } from "../services/haptics";
import { apiClient } from "../services/api/client";
import type { LocateResponse } from "../models/api";

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
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<LocateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.locateControl(scanId, query.trim());
      setResult(response);
      await hapticService.success();
      await speechService.speak(response.spoken_instruction);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not locate control";
      await hapticService.error();
      await speechService.announceError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetGuidance = () => {
    if (result?.guidance_target) {
      onStartGuidance(result.guidance_target.target_control_id);
    }
  };

  const handleNewSearch = () => {
    setResult(null);
    setQuery("");
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBanner title="Find a Control" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        {!result && (
          <>
            <Text style={styles.prompt}>What control are you looking for?</Text>
            <TextInput
              style={styles.input}
              value={query}
              onChangeText={setQuery}
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
              disabled={isLoading || !query.trim()}
              accessibilityHint="Searches for the control on the panel"
            />
          </>
        )}

        {result && (
          <View>
            <SpokenPromptCard text={result.spoken_instruction} />

            {result.guidance_target && (
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
