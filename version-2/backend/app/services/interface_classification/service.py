from __future__ import annotations

import numpy as np

from app.core.logging import logger
from app.domain.schemas.scan import ClassifierResult


class InterfaceClassificationService:
    """Classifies the type of interface panel and scan quality.

    Uses a rule-based placeholder initially; replaced with a trained CNN in Phase 6.
    """

    KNOWN_TYPES = ["microwave", "thermostat", "washer", "vending", "oven", "dishwasher", "unknown"]

    async def classify(self, image: np.ndarray) -> ClassifierResult:
        logger.info("Running interface classification (placeholder)")

        scan_quality, sq_confidence = self._assess_scan_quality(image)

        appliance_type = "microwave"
        type_confidence = 0.6

        return ClassifierResult(
            appliance_type=appliance_type,
            confidence=type_confidence,
            scan_quality=scan_quality,
            scan_quality_confidence=sq_confidence,
        )

    def _assess_scan_quality(self, image: np.ndarray) -> tuple[str, float]:
        """Basic heuristic scan quality assessment."""
        gray = image if len(image.shape) == 2 else np.mean(image, axis=2)

        laplacian_var = np.var(np.gradient(gray.astype(np.float64)))
        if laplacian_var < 50:
            return "blurry", 0.8

        brightness = np.mean(gray)
        if brightness > 240:
            return "glare", 0.7
        if brightness < 30:
            return "too_dark", 0.7

        h, w = image.shape[:2]
        if h < 200 or w < 200:
            return "too_far", 0.6

        return "good", 0.9
