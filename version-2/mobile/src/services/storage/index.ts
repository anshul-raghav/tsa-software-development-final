/**
 * Local storage service for persisting scan history and user preferences.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import type { PanelMap } from "../../models/panel";

const KEYS = {
  RECENT_SCANS: "@touchmap/recent_scans",
  USER_PREFERENCES: "@touchmap/preferences",
} as const;

export interface ScanHistoryEntry {
  scanId: string;
  sessionId: string;
  applianceType: string;
  controlCount: number;
  timestamp: number;
}

interface UserPreferences {
  speechRate: number;
  speechPitch: number;
  hapticsEnabled: boolean;
  apiBaseUrl: string;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  speechRate: 0.9,
  speechPitch: 1.0,
  hapticsEnabled: true,
  apiBaseUrl: "http://localhost:8000/api/v1",
};

class StorageService {
  /** Save a scan to recent history (keeps last 20). */
  async addScanToHistory(entry: ScanHistoryEntry): Promise<void> {
    const history = await this.getRecentScans();
    history.unshift(entry);
    const trimmed = history.slice(0, 20);
    await AsyncStorage.setItem(KEYS.RECENT_SCANS, JSON.stringify(trimmed));
  }

  /** Retrieve the list of recent scans. */
  async getRecentScans(): Promise<ScanHistoryEntry[]> {
    const data = await AsyncStorage.getItem(KEYS.RECENT_SCANS);
    if (!data) return [];
    try {
      return JSON.parse(data) as ScanHistoryEntry[];
    } catch {
      return [];
    }
  }

  /** Clear all scan history. */
  async clearHistory(): Promise<void> {
    await AsyncStorage.removeItem(KEYS.RECENT_SCANS);
  }

  /** Load user preferences, falling back to defaults. */
  async getPreferences(): Promise<UserPreferences> {
    const data = await AsyncStorage.getItem(KEYS.USER_PREFERENCES);
    if (!data) return { ...DEFAULT_PREFERENCES };
    try {
      return { ...DEFAULT_PREFERENCES, ...JSON.parse(data) };
    } catch {
      return { ...DEFAULT_PREFERENCES };
    }
  }

  /** Save user preferences. */
  async savePreferences(prefs: Partial<UserPreferences>): Promise<void> {
    const current = await this.getPreferences();
    const merged = { ...current, ...prefs };
    await AsyncStorage.setItem(KEYS.USER_PREFERENCES, JSON.stringify(merged));
  }
}

export const storageService = new StorageService();
export default StorageService;
