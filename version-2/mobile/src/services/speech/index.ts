/**
 * Speech services — text-to-speech output and speech-to-text input.
 * Voice-first interaction is the primary UX for blind users.
 */
import * as Speech from "expo-speech";
import { SPEECH_SETTINGS } from "../../constants/config";

class SpeechService {
  private currentlySpeaking = false;

  /**
   * Speak text aloud using the device TTS engine.
   * Automatically stops any in-progress speech before starting.
   */
  async speak(text: string, options?: { rate?: number; pitch?: number }): Promise<void> {
    if (this.currentlySpeaking) {
      await this.stopSpeaking();
    }

    this.currentlySpeaking = true;

    return new Promise((resolve) => {
      Speech.speak(text, {
        language: SPEECH_SETTINGS.language,
        rate: options?.rate ?? SPEECH_SETTINGS.rate,
        pitch: options?.pitch ?? SPEECH_SETTINGS.pitch,
        onDone: () => {
          this.currentlySpeaking = false;
          resolve();
        },
        onError: () => {
          this.currentlySpeaking = false;
          resolve();
        },
      });
    });
  }

  /** Immediately stop any in-progress speech. */
  async stopSpeaking(): Promise<void> {
    Speech.stop();
    this.currentlySpeaking = false;
  }

  /** Check if the TTS engine is currently speaking. */
  async isSpeaking(): Promise<boolean> {
    return Speech.isSpeakingAsync();
  }

  /** Speak a short confirmation phrase (e.g. after a button press). */
  async confirm(text: string): Promise<void> {
    return this.speak(text, { rate: 1.1 });
  }

  /** Speak an error or warning message with slightly slower pace. */
  async announceError(text: string): Promise<void> {
    return this.speak(text, { rate: 0.8 });
  }
}

export const speechService = new SpeechService();
export default SpeechService;
