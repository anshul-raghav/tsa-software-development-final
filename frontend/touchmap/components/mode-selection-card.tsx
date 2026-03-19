/**
 * Mode selection card — one per mode on the PanelReady screen.
 * Large tap target with icon, title, and short description.
 */
import React from "react";
import { TouchableOpacity, Text, View, StyleSheet } from "react-native";
import { Colors, FontSize, Spacing, TouchTarget, Shadow, Radius } from "../constants/design-tokens";
import { hapticService } from "../services/haptics/haptic-feedback-service";

interface ModeCardProps {
  title: string;
  description: string;
  iconLabel: string;
  onPress: () => void;
  accessibilityHint: string;
}

export default function ModeCard({
  title,
  description,
  iconLabel,
  onPress,
  accessibilityHint,
}: ModeCardProps) {
  const handlePress = async () => {
    await hapticService.mediumTap();
    onPress();
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={handlePress}
      accessibilityRole="button"
      accessibilityLabel={`${title}: ${description}`}
      accessibilityHint={accessibilityHint}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>{iconLabel}</Text>
      </View>
      <View style={styles.textContainer}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.description}>{description}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    borderRadius: Radius.cardLg,
    padding: Spacing.lg,
    marginVertical: Spacing.sm,
    minHeight: 88,
    borderWidth: 1,
    borderColor: Colors.border,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primaryMuted,
    ...Shadow.card,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: Colors.primaryMuted,
    justifyContent: "center",
    alignItems: "center",
    marginRight: Spacing.lg,
  },
  icon: {
    fontSize: FontSize.xl,
    color: Colors.primary,
    fontWeight: "700",
  },
  textContainer: {
    flex: 1,
  },
  title: {
    color: Colors.text,
    fontSize: FontSize.lg,
    fontWeight: "700",
    marginBottom: Spacing.xs,
  },
  description: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    lineHeight: FontSize.sm * 1.4,
  },
});
