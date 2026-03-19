"""
Generates deterministic task plans from TaskIntent using appliance-specific templates.

Microwave: heat_for_time, defrost, set_power, stop, start. Generic: start/stop. Returns TaskPlan with steps.
"""
from __future__ import annotations

import uuid

from app.core.logging import logger
from app.core.exceptions import TaskPlanningError
from app.domain.models.panel_map_models import PanelMap, ControlGraph
from app.domain.models.task_models import TaskIntent, TaskPlan, TaskStep, ActionType


class TaskPlanningService:
    """Generates deterministic task plans from structured intents using templates."""

    async def plan(
        self,
        intent: TaskIntent,
        control_graph: ControlGraph,
        panel_map: PanelMap,
    ) -> TaskPlan:
        logger.info(f"Planning task: intent={intent.intent}, appliance={intent.appliance_type}")

        if intent.appliance_type == "microwave":
            plan = self._plan_microwave(intent, control_graph)
        else:
            plan = self._plan_generic(intent, control_graph)

        if not plan.steps:
            plan.fallback_message = (
                f"I understood you want to '{intent.raw_query}', but I couldn't determine "
                f"the exact button sequence. Try asking to locate specific controls instead."
            )
            plan.clarification_needed = True
            plan.confidence = 0.3

        return plan

    def _plan_microwave(self, intent: TaskIntent, graph: ControlGraph) -> TaskPlan:
        task_id = str(uuid.uuid4())
        steps: list[TaskStep] = []

        if intent.intent == "heat_for_time":
            steps = self._microwave_heat_for_time(intent, graph)
        elif intent.intent == "defrost":
            steps = self._microwave_defrost(intent, graph)
        elif intent.intent == "set_power":
            steps = self._microwave_set_power(intent, graph)
        elif intent.intent == "stop":
            steps = self._microwave_stop(graph)
        elif intent.intent == "start":
            steps = self._microwave_start(graph)

        return TaskPlan(
            task_id=task_id,
            user_goal=intent.raw_query,
            appliance_type=intent.appliance_type,
            intent=intent.intent,
            parameters=intent.parameters,
            steps=steps,
            confidence=0.9 if steps else 0.3,
        )

    def _microwave_heat_for_time(self, intent: TaskIntent, graph: ControlGraph) -> list[TaskStep]:
        duration = intent.parameters.get("duration_seconds", 30)
        steps: list[TaskStep] = []
        step_num = 1

        time_cook = self._find_control(graph, ["time cook", "cook time", "timed cook", "manual cook"])
        if time_cook:
            steps.append(TaskStep(
                step_number=step_num,
                action_type=ActionType.PRESS,
                control_id=time_cook.id,
                instruction=f"Press {time_cook.label}",
                spoken_hint=time_cook.spoken_description,
            ))
            step_num += 1

        digits = self._duration_to_digits(duration)
        for digit in digits:
            digit_control = self._find_control(graph, [str(digit)])
            if digit_control:
                steps.append(TaskStep(
                    step_number=step_num,
                    action_type=ActionType.PRESS,
                    control_id=digit_control.id,
                    instruction=f"Press {digit}",
                    spoken_hint=digit_control.spoken_description,
                ))
                step_num += 1

        start = self._find_control(graph, ["start", "begin", "go"])
        if start:
            steps.append(TaskStep(
                step_number=step_num,
                action_type=ActionType.PRESS,
                control_id=start.id,
                instruction=f"Press {start.label}",
                spoken_hint=start.spoken_description,
            ))

        return steps

    def _microwave_defrost(self, intent: TaskIntent, graph: ControlGraph) -> list[TaskStep]:
        steps: list[TaskStep] = []
        step_num = 1

        defrost = self._find_control(graph, ["defrost", "thaw"])
        if defrost:
            steps.append(TaskStep(
                step_number=step_num,
                action_type=ActionType.PRESS,
                control_id=defrost.id,
                instruction=f"Press {defrost.label}",
                spoken_hint=defrost.spoken_description,
            ))
            step_num += 1

        duration = intent.parameters.get("duration_seconds")
        if duration:
            for digit in self._duration_to_digits(duration):
                digit_control = self._find_control(graph, [str(digit)])
                if digit_control:
                    steps.append(TaskStep(
                        step_number=step_num,
                        action_type=ActionType.PRESS,
                        control_id=digit_control.id,
                        instruction=f"Press {digit}",
                        spoken_hint=digit_control.spoken_description,
                    ))
                    step_num += 1

        start = self._find_control(graph, ["start", "begin"])
        if start:
            steps.append(TaskStep(
                step_number=step_num,
                action_type=ActionType.PRESS,
                control_id=start.id,
                instruction=f"Press {start.label}",
                spoken_hint=start.spoken_description,
            ))

        return steps

    def _microwave_set_power(self, intent: TaskIntent, graph: ControlGraph) -> list[TaskStep]:
        steps: list[TaskStep] = []
        step_num = 1

        power = self._find_control(graph, ["power", "power level"])
        if power:
            steps.append(TaskStep(
                step_number=step_num,
                action_type=ActionType.PRESS,
                control_id=power.id,
                instruction=f"Press {power.label}",
                spoken_hint=power.spoken_description,
            ))
            step_num += 1

        level = intent.parameters.get("power_level")
        if level is not None:
            digit_control = self._find_control(graph, [str(level)])
            if digit_control:
                steps.append(TaskStep(
                    step_number=step_num,
                    action_type=ActionType.PRESS,
                    control_id=digit_control.id,
                    instruction=f"Press {level}",
                    spoken_hint=digit_control.spoken_description,
                ))

        return steps

    def _microwave_stop(self, graph: ControlGraph) -> list[TaskStep]:
        stop = self._find_control(graph, ["stop", "cancel", "clear"])
        if stop:
            return [TaskStep(
                step_number=1,
                action_type=ActionType.PRESS,
                control_id=stop.id,
                instruction=f"Press {stop.label}",
                spoken_hint=stop.spoken_description,
            )]
        return []

    def _microwave_start(self, graph: ControlGraph) -> list[TaskStep]:
        start = self._find_control(graph, ["start", "begin", "go"])
        if start:
            return [TaskStep(
                step_number=1,
                action_type=ActionType.PRESS,
                control_id=start.id,
                instruction=f"Press {start.label}",
                spoken_hint=start.spoken_description,
            )]
        return []

    def _plan_generic(self, intent: TaskIntent, graph: ControlGraph) -> TaskPlan:
        task_id = str(uuid.uuid4())
        steps: list[TaskStep] = []

        if intent.intent == "start":
            ctrl = self._find_control(graph, ["start", "begin", "go", "on"])
            if ctrl:
                steps.append(TaskStep(
                    step_number=1,
                    action_type=ActionType.PRESS,
                    control_id=ctrl.id,
                    instruction=f"Press {ctrl.label}",
                    spoken_hint=ctrl.spoken_description,
                ))
        elif intent.intent == "stop":
            ctrl = self._find_control(graph, ["stop", "cancel", "off", "clear"])
            if ctrl:
                steps.append(TaskStep(
                    step_number=1,
                    action_type=ActionType.PRESS,
                    control_id=ctrl.id,
                    instruction=f"Press {ctrl.label}",
                    spoken_hint=ctrl.spoken_description,
                ))

        return TaskPlan(
            task_id=task_id,
            user_goal=intent.raw_query,
            appliance_type=intent.appliance_type,
            intent=intent.intent,
            parameters=intent.parameters,
            steps=steps,
            confidence=0.7 if steps else 0.2,
        )

    def _find_control(self, graph: ControlGraph, labels: list[str]):
        for label in labels:
            ctrl = graph.find_control(label)
            if ctrl:
                return ctrl
        return None

    def _duration_to_digits(self, seconds: int) -> list[int]:
        """Convert duration in seconds to digit sequence (MMSS format)."""
        minutes = seconds // 60
        remaining_secs = seconds % 60
        time_str = f"{minutes:01d}{remaining_secs:02d}"
        digits = [int(d) for d in time_str]
        while len(digits) > 1 and digits[0] == 0:
            digits.pop(0)
        return digits
