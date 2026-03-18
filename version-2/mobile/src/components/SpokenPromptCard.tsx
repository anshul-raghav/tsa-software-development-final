/**
 * Card that displays spoken text and auto-speaks on mount.
 * Includes a repeat button for re-reading the content aloud.
 */
import React, { useEffect } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Colors, FontSize, Spacing, TouchTarget } from "../constants/theme";
import { speechService } from "../services/speech";

interface SpokenPromptCardProps {
  text: string;
  autoSpeak?: boolean;
  showRepeatButton?: boolean;
}

export default function SpokenPromptCard({
  text,
  autoSpeak = true,
  showRepeatButton = true,
}: SpokenPromptCardProps) {
  useEffect(() => {
    if (autoSpeak && text) {
      speechService.speak(text);
    }
  }, [text, autoSpeak]);

  const handleRepeat = () => {
    speechService.speak(text);
  };

  if (!text) return null;

  return (
    <View
      style={styles.card}
      accessibilityRole="text"
      accessibilityLabel={text}
    >
      <Text style={styles.text}>{text}</Text>

      {showRepeatButton && (
        <TouchableOpacity
          style={styles.repeatButton}
          onPress={handleRepeat}
          accessibilityRole="button"
          accessibilityLabel="Repeat"
          accessibilityHint="Reads the message aloud again"
        >
          <Text style={styles.repeatLabel}>Repeat</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: TouchTarget.borderRadius,
    padding: Spacing.lg,
    marginVertical: Spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  text: {
    color: Colors.text,
    fontSize: FontSize.lg,
    lineHeight: FontSize.lg * 1.5,
  },
  repeatButton: {
    marginTop: Spacing.md,
    alignSelf: "flex-start",
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    backgroundColor: Colors.surfaceLight,
    borderRadius: 8,
  },
  repeatLabel: {
    color: Colors.primary,
    fontSize: FontSize.md,
    fontWeight: "600",
  },
});
