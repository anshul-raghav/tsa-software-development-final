/**
 * Task Mode — goal-first interaction.
 * User says what they want to do; app provides step-by-step instructions.
 */
import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import { Colors, FontSize, Spacing, TouchTarget } from "../constants/design-tokens";
import ScreenGradientBackground from "../components/full-screen-gradient-background";
import StatusBanner from "../components/screen-status-banner";
import VoiceButton from "../components/haptic-feedback-button";
import SpokenPromptCard from "../components/spoken-prompt-card";
import { speechService } from "../services/speech/text-to-speech-service";
import { hapticService } from "../services/haptics/haptic-feedback-service";
import { apiClient } from "../services/api/touchmap-backend-api-client";
import type { TaskPlan, TaskStep } from "../models/task-planning-types";

interface TaskModeScreenProps {
  scanId: string;
  onStartGuidance: (controlId: string) => void;
  onBack: () => void;
}

export default function TaskModeScreen({
  scanId,
  onStartGuidance,
  onBack,
}: TaskModeScreenProps) {
  const [userRequestText, setUserRequestText] = useState("");
  const [taskPlan, setTaskPlan] = useState<TaskPlan | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentStep: TaskStep | undefined = taskPlan?.steps[currentStepIndex];

  const handleSubmitQuery = async () => {
    const trimmedRequest = userRequestText.trim();
    if (!trimmedRequest) {
      const msg = "Please enter a task description";
      setErrorMessage(msg);
      await speechService.announceError(msg);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    await speechService.speak("Planning your task.");

    try {
      const planResponse = await apiClient.planTask(scanId, trimmedRequest);
      setTaskPlan(planResponse.task_plan);
      setCurrentStepIndex(0);

      if (planResponse.task_plan.clarification_needed) {
        await speechService.speak(planResponse.task_plan.fallback_message);
      } else if (planResponse.task_plan.steps.length > 0) {
        await speechService.speak(
          `I have ${planResponse.task_plan.steps.length} steps for you. ` +
          `Step 1: ${planResponse.task_plan.steps[0].instruction}`
        );
      }
      await hapticService.success();
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Could not plan this task";
      setErrorMessage(msg);
      await hapticService.error();
      await speechService.announceError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextStep = async () => {
    if (!taskPlan) return;
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < taskPlan.steps.length) {
      setCurrentStepIndex(nextIndex);
      await hapticService.lightTap();
      await speechService.speak(
        `Step ${nextIndex + 1}: ${taskPlan.steps[nextIndex].instruction}`
      );
    } else {
      await hapticService.success();
      await speechService.speak("You have completed all steps.");
    }
  };

  const handleRepeatStep = async () => {
    if (currentStep) {
      await speechService.speak(
        `Step ${currentStepIndex + 1}: ${currentStep.instruction}`
      );
    }
  };

  const handleWhereIsThis = () => {
    if (currentStep) {
      onStartGuidance(currentStep.control_id);
    }
  };

  return (
    <ScreenGradientBackground>
      <SafeAreaView style={styles.container}>
        <StatusBanner title="Task Mode" onBack={onBack} />

      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        {!taskPlan && (
          <>
            <Text style={styles.prompt}>What would you like to do?</Text>
            <TextInput
              style={styles.input}
              value={userRequestText}
              onChangeText={setUserRequestText}
              placeholder='e.g. "Set the microwave for 60 seconds"'
              placeholderTextColor={Colors.textMuted}
              accessibilityLabel="Task description"
              accessibilityHint="Type what you want to accomplish"
              returnKeyType="send"
              onSubmitEditing={handleSubmitQuery}
              multiline
            />
            <VoiceButton
              label={isLoading ? "Planning..." : "Plan Task"}
              onPress={handleSubmitQuery}
              disabled={isLoading || !userRequestText.trim()}
              accessibilityHint="Sends your task request to the system"
            />
          </>
        )}

        {errorMessage && (
          <SpokenPromptCard text={errorMessage} autoSpeak={false} />
        )}

        {taskPlan && currentStep && (
          <View style={styles.stepContainer}>
            <Text style={styles.stepCounter}>
              Step {currentStepIndex + 1} of {taskPlan.steps.length}
            </Text>

            <SpokenPromptCard
              text={currentStep.instruction}
              autoSpeak={false}
            />

            {currentStep.spoken_hint ? (
              <Text style={styles.hint}>{currentStep.spoken_hint}</Text>
            ) : null}

            <View style={styles.buttonRow}>
              <VoiceButton
                label="Repeat"
                onPress={handleRepeatStep}
                variant="outline"
                accessibilityHint="Reads the current step again"
              />
              <VoiceButton
                label="Where is this?"
                onPress={handleWhereIsThis}
                variant="secondary"
                accessibilityHint="Helps you locate this control on the panel"
              />
              <VoiceButton
                label={currentStepIndex < taskPlan.steps.length - 1 ? "Next Step" : "Done"}
                onPress={handleNextStep}
                variant="primary"
                accessibilityHint="Moves to the next step in the task"
              />
            </View>
          </View>
        )}

        {taskPlan && taskPlan.steps.length === 0 && (
          <SpokenPromptCard
            text={taskPlan.fallback_message || "I couldn't determine the steps for this task."}
          />
        )}
      </ScrollView>
      </SafeAreaView>
    </ScreenGradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "transparent",
  },
  content: {
    flex: 1,
  },
  contentInner: {
    padding: Spacing.lg,
  },
  prompt: {
    color: Colors.text,
    fontSize: FontSize.xl,
    fontWeight: "700",
    marginBottom: Spacing.lg,
  },
  input: {
    backgroundColor: Colors.surface,
    color: Colors.text,
    fontSize: FontSize.lg,
    padding: Spacing.lg,
    borderRadius: TouchTarget.borderRadius,
    borderWidth: 1,
    borderColor: Colors.border,
    minHeight: 80,
    textAlignVertical: "top",
    marginBottom: Spacing.md,
  },
  stepContainer: {
    marginTop: Spacing.md,
  },
  stepCounter: {
    color: Colors.primary,
    fontSize: FontSize.lg,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: Spacing.md,
  },
  hint: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    fontStyle: "italic",
    marginVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
  },
  buttonRow: {
    marginTop: Spacing.lg,
    gap: Spacing.sm,
  },
});
