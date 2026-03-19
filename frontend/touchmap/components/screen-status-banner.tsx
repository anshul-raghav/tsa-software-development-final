/**
 * Top-of-screen status banner showing current mode and back button.
 */
import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Colors, FontSize, Spacing } from "../constants/design-tokens";

interface StatusBannerProps {
  title: string;
  onBack?: () => void;
  showBack?: boolean;
}

export default function StatusBanner({
  title,
  onBack,
  showBack = true,
}: StatusBannerProps) {
  return (
    <View style={styles.banner}>
      {showBack && onBack ? (
        <TouchableOpacity
          onPress={onBack}
          style={styles.backButton}
          accessibilityRole="button"
          accessibilityLabel="Go back"
          accessibilityHint="Returns to the previous screen"
        >
          <Text style={styles.backText}>Back</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.backPlaceholder} />
      )}

      <Text style={styles.title} accessibilityRole="header">
        {title}
      </Text>

      <View style={styles.backPlaceholder} />
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.lg,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  backButton: {
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minWidth: 64,
  },
  backText: {
    color: Colors.primary,
    fontSize: FontSize.md,
    fontWeight: "600",
  },
  backPlaceholder: {
    minWidth: 64,
  },
  title: {
    color: Colors.text,
    fontSize: FontSize.lg,
    fontWeight: "700",
    textAlign: "center",
    flex: 1,
  },
});
