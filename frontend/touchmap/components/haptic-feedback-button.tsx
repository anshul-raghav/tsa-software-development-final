/**
 * Large, accessible button with haptic feedback.
 * Meets minimum 64px touch target, high contrast, full a11y labeling.
 */
import React from "react";
import { TouchableOpacity, Text, StyleSheet, ViewStyle } from "react-native";
import { Colors, FontSize, TouchTarget, Spacing, Shadow } from "../constants/design-tokens";
import { hapticService } from "../services/haptics/haptic-feedback-service";

type ButtonVariant = "primary" | "secondary" | "danger" | "outline";

interface VoiceButtonProps {
  label: string;
  onPress: () => void;
  variant?: ButtonVariant;
  accessibilityHint?: string;
  disabled?: boolean;
  fullWidth?: boolean;
}

const VARIANT_STYLES: Record<ButtonVariant, ViewStyle> = {
  primary: { backgroundColor: Colors.primary },
  secondary: { backgroundColor: Colors.secondary },
  danger: { backgroundColor: Colors.danger },
  outline: { backgroundColor: "transparent", borderWidth: 2, borderColor: Colors.primary },
};

const VARIANT_TEXT_COLORS: Record<ButtonVariant, string> = {
  primary: Colors.textOnPrimary,
  secondary: Colors.textOnPrimary,
  danger: Colors.text,
  outline: Colors.primary,
};

export default function VoiceButton({
  label,
  onPress,
  variant = "primary",
  accessibilityHint,
  disabled = false,
  fullWidth = true,
}: VoiceButtonProps) {
  const handlePress = async () => {
    await hapticService.lightTap();
    onPress();
  };

  return (
    <TouchableOpacity
      style={[
        styles.button,
        VARIANT_STYLES[variant],
        fullWidth && styles.fullWidth,
        disabled && styles.disabled,
      ]}
      onPress={handlePress}
      disabled={disabled}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled }}
      activeOpacity={0.7}
    >
      <Text
        style={[styles.label, { color: VARIANT_TEXT_COLORS[variant] }]}
        numberOfLines={2}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: TouchTarget.minHeight,
    borderRadius: TouchTarget.borderRadius,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    marginVertical: Spacing.sm,
    ...Shadow.card,
  },
  fullWidth: {
    width: "100%",
  },
  label: {
    fontSize: FontSize.lg,
    fontWeight: "700",
    textAlign: "center",
    letterSpacing: 0.5,
  },
  disabled: {
    opacity: 0.4,
  },
});
