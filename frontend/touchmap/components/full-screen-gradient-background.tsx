/**
 * Full-screen vertical gradient background for content screens.
 * Uses theme gradient colors; children (e.g. SafeAreaView) should use transparent background.
 */
import React from "react";
import { StyleSheet, ViewStyle } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Gradient } from "../constants/design-tokens";

interface ScreenGradientBackgroundProps {
  children: React.ReactNode;
  style?: ViewStyle;
}

export default function ScreenGradientBackground({
  children,
  style,
}: ScreenGradientBackgroundProps) {
  return (
    <LinearGradient
      colors={[...Gradient.colors]}
      style={[styles.gradient, style]}
      start={{ x: 0.5, y: 0 }}
      end={{ x: 0.5, y: 1 }}
    >
      {children}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
});
