/**
 * Application configuration constants.
 * Environment-specific values for API connectivity and feature flags.
 */
export const API_BASE_URL = "http://192.168.1.170:8001/api/v1";

export const SCAN_SETTINGS = {
  maxImageSizeMB: 10,
  captureQuality: 0.85,
  guidanceFrameIntervalMs: 4000,
  maxRetries: 3,
} as const;

export const SPEECH_SETTINGS = {
  rate: 0.9,
  pitch: 1.0,
  language: "en-US",
} as const;

export const HAPTIC_SETTINGS = {
  enableOnButtonPress: true,
  enableOnProximity: true,
  enableOnModeSwitch: true,
} as const;
