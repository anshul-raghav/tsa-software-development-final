/**
 * Design tokens for the TouchMap accessible UI.
 * High contrast, large targets, voice-first design.
 * Light theme inspired by the Innovative Minds look (mint/ice backgrounds + blue CTAs).
 */
export const Colors = {
  // Page / gradients
  background: "#DFFCF6",
  // Surfaces and cards
  surface: "#FFFFFF",
  surfaceLight: "#F2F8FF",
  // Brand / CTAs
  primary: "#2563EB",
  primaryDark: "#1D4ED8",
  primaryMuted: "rgba(37, 99, 235, 0.18)",
  secondary: "#22C55E",
  danger: "#EF4444",
  warning: "#F59E0B",
  // Text in normal (light) contexts
  text: "#0F172A",
  textMuted: "#475569",
  textOnPrimary: "#FFFFFF",
  // Borders for light UI chrome
  border: "#E2E8F0",
  // Overlays (camera guidance)
  overlay: "rgba(0, 0, 0, 0.55)",
  overlayText: "#FFFFFF",
  overlayTextMuted: "rgba(255, 255, 255, 0.85)",
  success: "#16A34A",
} as const;

/** Gradient background: top (darker) to bottom. Use with LinearGradient. */
export const Gradient = {
  top: "#CFF8F0",
  middle: "#EAFDFB",
  bottom: "#FFFFFF",
  colors: ["#CFF8F0", "#EAFDFB", "#FFFFFF"] as const,
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

export const Radius = {
  card: 16,
  cardLg: 20,
} as const;

/** Shadow for cards and primary buttons (iOS shadow + Android elevation). */
export const Shadow = {
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 3,
  },
} as const;

export const Accessibility = {
  minimumFontScale: 1.2,
  maximumFontScale: 2.0,
} as const;
