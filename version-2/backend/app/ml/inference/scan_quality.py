"""Scan quality classifier inference.

This module loads a trained CNN model for classifying scan quality.
The model is trained separately (see ml/training/) and loaded at inference time.
"""
from __future__ import annotations

from pathlib import Path
from enum import Enum

import numpy as np

from app.core.config import settings
from app.core.logging import logger


class ScanQuality(str, Enum):
    GOOD = "good"
    BLURRY = "blurry"
    GLARE = "glare"
    PARTIAL = "partial"
    TILTED = "tilted"
    TOO_FAR = "too_far"
    TOO_CLOSE = "too_close"


class ScanQualityClassifier:
    """Lightweight CNN classifier for scan quality assessment.

    Falls back to heuristic-based classification if no trained model is available.
    """

    CLASSES = list(ScanQuality)

    def __init__(self):
        self._model = None
        self._model_loaded = False

    def load_model(self):
        model_path = Path(settings.ml_model_path)
        if not model_path.exists():
            logger.warning(f"ML model not found at {model_path}, using heuristic fallback")
            return

        try:
            import torch
            import torchvision.transforms as transforms

            self._model = torch.load(model_path, map_location="cpu")
            self._model.eval()
            self._model_loaded = True
            logger.info("Scan quality ML model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}, using heuristic fallback")

    def predict(self, image: np.ndarray) -> tuple[ScanQuality, float]:
        if self._model_loaded and self._model is not None:
            return self._predict_ml(image)
        return self._predict_heuristic(image)

    def _predict_ml(self, image: np.ndarray) -> tuple[ScanQuality, float]:
        import torch
        import torchvision.transforms as transforms
        import cv2

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        tensor = transform(img_rgb).unsqueeze(0)

        with torch.no_grad():
            output = self._model(tensor)
            probs = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probs, 1)

        quality = self.CLASSES[predicted.item()]
        return quality, confidence.item()

    def _predict_heuristic(self, image: np.ndarray) -> tuple[ScanQuality, float]:
        gray = image if len(image.shape) == 2 else np.mean(image, axis=2)

        laplacian_var = np.var(np.gradient(gray.astype(np.float64)))
        if laplacian_var < 50:
            return ScanQuality.BLURRY, 0.8

        brightness = np.mean(gray)
        if brightness > 240:
            return ScanQuality.GLARE, 0.7

        h, w = image.shape[:2]
        if h < 200 or w < 200:
            return ScanQuality.TOO_FAR, 0.6
        if h > 3000 or w > 3000:
            return ScanQuality.TOO_CLOSE, 0.6

        return ScanQuality.GOOD, 0.85
