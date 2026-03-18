/**
 * Haptic feedback service — tactile cues for blind users.
 * Maps interaction types to appropriate vibration patterns.
 */
import * as Haptics from "expo-haptics";

class HapticService {
  /** Light tap for button presses and selections. */
  async lightTap(): Promise<void> {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  }

  /** Medium tap for mode switches and significant actions. */
  async mediumTap(): Promise<void> {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  }

  /** Heavy tap for important alerts or proximity changes. */
  async heavyTap(): Promise<void> {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
  }

  /** Success pattern — scan complete, task done. */
  async success(): Promise<void> {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  }

  /** Warning pattern — low confidence, retry suggested. */
  async warning(): Promise<void> {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
  }

  /** Error pattern — scan failed, API error. */
  async error(): Promise<void> {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
  }

  /** Selection changed — used in lists and mode pickers. */
  async selectionChanged(): Promise<void> {
    await Haptics.selectionAsync();
  }
}

export const hapticService = new HapticService();
export default HapticService;
