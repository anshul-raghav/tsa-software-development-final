/**
 * Explore Mode — describe panel layout sections to build a mental map.
 * Supports follow-up questions about different regions, rows, and sides.
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
import type { ExploreResponse } from "../models/api";

interface ExploreModeScreenProps {
  scanId: string;
  onBack: () => void;
}

interface ExploreEntry {
  query: string;
  response: ExploreResponse;
}

export default function ExploreModeScreen({ scanId, onBack }: ExploreModeScreenProps) {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<ExploreEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleExplore = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.explorePanel(scanId, query.trim());
      setHistory((prev) => [{ query: query.trim(), response }, ...prev]);
      setQuery("");
      await hapticService.success();
      await speechService.speak(response.spoken_description);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not explore panel";
      await hapticService.error();
      await speechService.announceError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBanner title="Explore Layout" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        <Text style={styles.prompt}>What would you like to know about the panel?</Text>

        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
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
          disabled={isLoading || !query.trim()}
          accessibilityHint="Describes the requested area of the panel"
        />

        {history.map((entry, index) => (
          <View key={index} style={styles.entryContainer}>
            <Text style={styles.entryQuery}>"{entry.query}"</Text>
            <SpokenPromptCard
              text={entry.response.spoken_description}
              autoSpeak={false}
            />
          </View>
        ))}

        {history.length === 0 && (
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
                  setQuery(suggestion);
                }}
                variant="outline"
                accessibilityHint={`Sets your question to: ${suggestion}`}
              />
            ))}
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
