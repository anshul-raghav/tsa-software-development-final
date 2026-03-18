/**
 * Design tokens for the TouchMap accessible UI.
 * High contrast, large targets, voice-first design.
 */
export const Colors = {
  background: "#0A0A0A",
  surface: "#1A1A2E",
  surfaceLight: "#252540",
  primary: "#4FC3F7",
  primaryDark: "#0288D1",
  secondary: "#81C784",
  danger: "#EF5350",
  warning: "#FFB74D",
  text: "#FFFFFF",
  textMuted: "#B0BEC5",
  textOnPrimary: "#000000",
  border: "#37474F",
  success: "#66BB6A",
  overlay: "rgba(0, 0, 0, 0.7)",
} as const;

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const FontSize = {
  sm: 16,
  md: 20,
  lg: 24,
  xl: 28,
  xxl: 36,
  title: 44,
} as const;

export const TouchTarget = {
  minHeight: 64,
  minWidth: 64,
  borderRadius: 16,
} as const;

export const Accessibility = {
  minimumFontScale: 1.2,
  maximumFontScale: 2.0,
} as const;
