from __future__ import annotations

from app.core.logging import logger
from app.core.exceptions import PanelMapValidationError
from app.domain.models.panel import PanelMap, ControlNode, ControlType


class PanelMapValidationService:
    """Validates, normalizes, and deduplicates PanelMap data."""

    LABEL_SYNONYMS: dict[str, list[str]] = {
        "start": ["begin", "go", "run"],
        "stop": ["cancel", "clear", "off", "reset"],
        "time cook": ["cook time", "timed cook", "time", "manual cook"],
        "defrost": ["thaw", "defrost by weight", "defrost by time"],
        "power": ["power level", "power setting"],
        "clock": ["time of day", "set clock"],
        "+30 sec": ["30 sec", "+30", "add 30"],
    }

    PRIMARY_ACTION_LABELS = {"start", "stop", "cancel", "clear", "enter", "ok", "confirm"}

    async def validate_and_normalize(self, panel_map: PanelMap) -> PanelMap:
        logger.info(f"Validating PanelMap: {len(panel_map.controls)} controls")

        violations: list[str] = []

        if not panel_map.controls:
            violations.append("PanelMap has no controls")

        if not panel_map.panel_id:
            violations.append("Missing panel_id")

        self._validate_bboxes(panel_map, violations)

        if violations:
            logger.warning(f"Validation violations: {violations}")

        panel_map = self._deduplicate_controls(panel_map)
        panel_map = self._normalize_labels(panel_map)
        panel_map = self._fill_aliases(panel_map)
        panel_map = self._identify_primary_actions(panel_map)
        panel_map = self._infer_control_types(panel_map)
        panel_map = self._compute_confidence(panel_map)

        logger.info(f"Validation complete: {len(panel_map.controls)} controls after normalization")
        return panel_map

    def _validate_bboxes(self, panel_map: PanelMap, violations: list[str]):
        for control in panel_map.controls:
            bbox = control.bbox
            if bbox.x2 <= bbox.x1 or bbox.y2 <= bbox.y1:
                violations.append(f"Invalid bbox for control '{control.label}': zero or negative area")
            if bbox.area < 0.0001:
                violations.append(f"Suspiciously small bbox for '{control.label}': area={bbox.area:.6f}")

    def _deduplicate_controls(self, panel_map: PanelMap) -> PanelMap:
        seen: list[ControlNode] = []
        for control in panel_map.controls:
            is_dup = False
            for existing in seen:
                if control.label.lower() == existing.label.lower() and control.bbox.iou(existing.bbox) > 0.5:
                    is_dup = True
                    if control.confidence > existing.confidence:
                        seen.remove(existing)
                        seen.append(control)
                    break
            if not is_dup:
                seen.append(control)

        if len(seen) < len(panel_map.controls):
            logger.info(f"Deduplicated: {len(panel_map.controls)} -> {len(seen)} controls")

        panel_map.controls = seen
        return panel_map

    def _normalize_labels(self, panel_map: PanelMap) -> PanelMap:
        for control in panel_map.controls:
            control.label = control.label.strip()
            if not control.id:
                control.id = f"ctrl_{control.label.lower().replace(' ', '_')}"
        return panel_map

    def _fill_aliases(self, panel_map: PanelMap) -> PanelMap:
        for control in panel_map.controls:
            label_lower = control.label.lower()
            for canonical, synonyms in self.LABEL_SYNONYMS.items():
                if label_lower == canonical or label_lower in synonyms:
                    all_names = [canonical] + synonyms
                    new_aliases = [a for a in all_names if a.lower() != label_lower and a not in control.aliases]
                    control.aliases.extend(new_aliases)
                    break
        return panel_map

    def _identify_primary_actions(self, panel_map: PanelMap) -> PanelMap:
        for control in panel_map.controls:
            if control.label.lower() in self.PRIMARY_ACTION_LABELS:
                control.is_primary_action = True
        return panel_map

    def _infer_control_types(self, panel_map: PanelMap) -> PanelMap:
        for control in panel_map.controls:
            if control.type != ControlType.OTHER:
                continue
            label = control.label.lower()
            if label.isdigit() or label in ("+30 sec", "+30"):
                control.type = ControlType.NUMBER
            elif label in ("start", "stop", "cancel", "clear", "enter", "ok"):
                control.type = ControlType.ACTION
            elif label in ("defrost", "reheat", "popcorn", "pizza", "beverage", "frozen"):
                control.type = ControlType.MODE
            elif label in ("power", "power level", "clock", "timer"):
                control.type = ControlType.SETTING
            elif label in ("time cook", "cook time"):
                control.type = ControlType.ACTION
        return panel_map

    def _compute_confidence(self, panel_map: PanelMap) -> PanelMap:
        if not panel_map.controls:
            panel_map.scan_confidence = 0.0
            return panel_map

        avg_confidence = sum(c.confidence for c in panel_map.controls) / len(panel_map.controls)
        has_numbers = any(c.type == ControlType.NUMBER for c in panel_map.controls)
        has_actions = any(c.type == ControlType.ACTION for c in panel_map.controls)

        score = avg_confidence
        if has_numbers:
            score = min(1.0, score + 0.05)
        if has_actions:
            score = min(1.0, score + 0.05)

        panel_map.scan_confidence = round(score, 3)
        return panel_map
