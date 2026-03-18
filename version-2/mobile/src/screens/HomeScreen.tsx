/**
 * Home screen — entry point with large "Scan a Panel" CTA.
 * Auto-speaks a welcome message on mount.
 */
import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, SafeAreaView, FlatList } from "react-native";
import { Colors, FontSize, Spacing } from "../constants/theme";
import VoiceButton from "../components/VoiceButton";
import { speechService } from "../services/speech";
import { storageService, ScanHistoryEntry } from "../services/storage";

interface HomeScreenProps {
  onStartScan: () => void;
}

export default function HomeScreen({ onStartScan }: HomeScreenProps) {
  const [recentScans, setRecentScans] = useState<ScanHistoryEntry[]>([]);

  useEffect(() => {
    speechService.speak(
      "Welcome to TouchMap. Tap the large button to scan a control panel, or use voice commands."
    );
    loadHistory();
  }, []);

  const loadHistory = async () => {
    const scans = await storageService.getRecentScans();
    setRecentScans(scans);
  };

  return (
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
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
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
    borderRadius: 12,
    marginBottom: Spacing.sm,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
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
});
