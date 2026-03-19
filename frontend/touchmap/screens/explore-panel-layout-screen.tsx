/**
 * Explore Mode — describe panel layout sections to build a mental map.
 * Supports follow-up questions about different regions, rows, and sides.
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
import type { ExploreResponse } from "../models/touchmap-backend-api-types";

interface ExploreModeScreenProps {
  scanId: string;
  onBack: () => void;
}

interface ExploreEntry {
  query: string;
  response: ExploreResponse;
}

export default function ExploreModeScreen({ scanId, onBack }: ExploreModeScreenProps) {
  const [layoutQueryText, setLayoutQueryText] = useState("");
  const [exploreHistory, setExploreHistory] = useState<ExploreEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleExplore = async () => {
    const trimmedQuery = layoutQueryText.trim();
    if (!trimmedQuery) {
      const msg = "Please enter a question about the panel";
      setErrorMessage(msg);
      await speechService.announceError(msg);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const exploreResponse = await apiClient.explorePanel(scanId, trimmedQuery);
      setExploreHistory((prev) => [{ query: trimmedQuery, response: exploreResponse }, ...prev]);
      setLayoutQueryText("");
      await hapticService.success();
      const spokenDescription =
        exploreResponse.spoken_description?.trim() ||
        "I couldn't generate a description for that. Try asking about a specific area.";
      await speechService.speak(spokenDescription);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not explore panel";
      setErrorMessage(msg);
      await hapticService.error();
      await speechService.announceError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScreenGradientBackground>
      <SafeAreaView style={styles.container}>
        <StatusBanner title="Explore Layout" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        <Text style={styles.prompt}>What would you like to know about the panel?</Text>

        <TextInput
          style={styles.input}
          value={layoutQueryText}
          onChangeText={setLayoutQueryText}
          placeholder='e.g. "Describe the number pad" or "What is on the bottom row?"'
          placeholderTextColor={Colors.textMuted}
          accessibilityLabel="Layout question"
          accessibilityHint="Type a question about the panel layout"
          returnKeyType="send"
          onSubmitEditing={handleExplore}
          multiline
        />

        <VoiceButton
          label={isLoading ? "Describing..." : "Explore"}
          onPress={handleExplore}
          disabled={isLoading || !layoutQueryText.trim()}
          accessibilityHint="Describes the requested area of the panel"
        />

        {errorMessage && (
          <SpokenPromptCard text={errorMessage} autoSpeak={false} />
        )}

        {exploreHistory.map((entry, index) => (
          <View key={index} style={styles.entryContainer}>
            <Text style={styles.entryQuery}>"{entry.query}"</Text>
            <SpokenPromptCard
              text={entry.response.spoken_description || "No description available."}
              autoSpeak={false}
            />
          </View>
        ))}

        {exploreHistory.length === 0 && (
          <View style={styles.suggestions}>
            <Text style={styles.suggestionsTitle}>Try asking:</Text>
            {[
              "Describe the whole panel",
              "What's on the top row?",
              "Describe the number pad",
              "What controls are on the right side?",
            ].map((suggestion) => (
              <VoiceButton
                key={suggestion}
                label={suggestion}
                onPress={() => {
                  setLayoutQueryText(suggestion);
                }}
                variant="outline"
                accessibilityHint={`Sets your question to: ${suggestion}`}
              />
            ))}
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
    paddingBottom: Spacing.xxl,
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
    minHeight: 80,
    textAlignVertical: "top",
    marginBottom: Spacing.md,
  },
  entryContainer: {
    marginTop: Spacing.lg,
  },
  entryQuery: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    fontStyle: "italic",
    marginBottom: Spacing.xs,
  },
  suggestions: {
    marginTop: Spacing.xl,
  },
  suggestionsTitle: {
    color: Colors.textMuted,
    fontSize: FontSize.md,
    marginBottom: Spacing.md,
  },
});
