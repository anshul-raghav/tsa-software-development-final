/**
 * Home screen — entry point with large "Scan a Panel" CTA.
 * Auto-speaks a welcome message on mount.
 */
import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, SafeAreaView, FlatList } from "react-native";
import { Colors, FontSize, Spacing, Radius, Shadow } from "../constants/design-tokens";
import ScreenGradientBackground from "../components/full-screen-gradient-background";
import VoiceButton from "../components/haptic-feedback-button";
import { speechService } from "../services/speech/text-to-speech-service";
import { storageService, ScanHistoryEntry } from "../services/storage/scan-history-storage-service";

interface HomeScreenProps {
  onStartScan: () => void;
}

export default function HomeScreen({ onStartScan }: HomeScreenProps) {
  const [recentScans, setRecentScans] = useState<ScanHistoryEntry[]>([]);
  const [historyLoadError, setHistoryLoadError] = useState<string | null>(null);

  useEffect(() => {
    speechService.speak(
      "Welcome to TouchMap. Tap the large button to scan a control panel, or use voice commands."
    );
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setHistoryLoadError(null);
      const scans = await storageService.getRecentScans();
      setRecentScans(scans);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not load scan history";
      setHistoryLoadError(msg);
      setRecentScans([]);
    }
  };

  return (
    <ScreenGradientBackground>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
        <Text style={styles.title} accessibilityRole="header">
          TouchMap
        </Text>
        <Text style={styles.subtitle}>
          Audio-guided navigation for flat control panels
        </Text>
      </View>

      <View style={styles.ctaContainer}>
        <VoiceButton
          label="Scan a Panel"
          onPress={onStartScan}
          variant="primary"
          accessibilityHint="Opens the camera to scan a control panel"
        />
      </View>

      {historyLoadError && (
        <Text style={styles.historyError} accessibilityRole="text">
          {historyLoadError}
        </Text>
      )}

      {recentScans.length > 0 && (
        <View style={styles.historySection}>
          <Text style={styles.sectionTitle} accessibilityRole="header">
            Recent Scans
          </Text>
          <FlatList
            data={recentScans.slice(0, 5)}
            keyExtractor={(item) => item.scanId}
            renderItem={({ item }) => (
              <View style={styles.historyItem}>
                <Text style={styles.historyLabel}>
                  {item.applianceType} — {item.controlCount} controls
                </Text>
                <Text style={styles.historyDate}>
                  {new Date(item.timestamp).toLocaleDateString()}
                </Text>
              </View>
            )}
          />
        </View>
      )}
      </SafeAreaView>
    </ScreenGradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "transparent",
    padding: Spacing.lg,
  },
  header: {
    alignItems: "center",
    marginTop: Spacing.xxl,
    marginBottom: Spacing.xl,
  },
  title: {
    color: Colors.text,
    fontSize: FontSize.title,
    fontWeight: "800",
    letterSpacing: 1,
  },
  subtitle: {
    color: Colors.textMuted,
    fontSize: FontSize.md,
    textAlign: "center",
    marginTop: Spacing.sm,
    lineHeight: FontSize.md * 1.4,
  },
  ctaContainer: {
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.xl,
  },
  historySection: {
    flex: 1,
    marginTop: Spacing.md,
  },
  sectionTitle: {
    color: Colors.text,
    fontSize: FontSize.lg,
    fontWeight: "700",
    marginBottom: Spacing.md,
  },
  historyItem: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: Radius.card,
    marginBottom: Spacing.sm,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    ...Shadow.card,
  },
  historyLabel: {
    color: Colors.text,
    fontSize: FontSize.sm,
    textTransform: "capitalize",
  },
  historyDate: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
  },
  historyError: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    textAlign: "center",
    marginBottom: Spacing.md,
  },
});
