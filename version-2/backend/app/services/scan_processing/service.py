from __future__ import annotations

import uuid
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image
import io

from app.core.config import settings, UPLOAD_PATH
from app.core.logging import logger
from app.core.exceptions import ScanError


@dataclass
class PreprocessedResult:
    cleaned_image: np.ndarray
    image_ref: str
    original_size: tuple[int, int]
    processed_size: tuple[int, int]
    corrections_applied: list[str]


class ScanProcessingService:
    """Handles image preprocessing: crop, normalize, perspective, contrast, glare."""

    TARGET_SIZE = 1024

    async def process(self, image_bytes: bytes, scan_id: str) -> PreprocessedResult:
        logger.info(f"Preprocessing scan image: scan_id={scan_id}")
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ScanError("Failed to decode image")

            original_size = (img.shape[1], img.shape[0])
            corrections: list[str] = []

            img = self._resize(img)
            corrections.append("resize")

            img = self._correct_orientation(img)
            corrections.append("orientation")

            img = self._enhance_contrast(img)
            corrections.append("contrast")

            img = self._reduce_glare(img)
            corrections.append("glare_reduction")

            panel_crop = self._detect_panel_crop(img)
            if panel_crop is not None:
                img = panel_crop
                corrections.append("panel_crop")

            image_ref = f"{scan_id}_preprocessed.jpg"
            save_path = UPLOAD_PATH / image_ref
            cv2.imwrite(str(save_path), img)

            processed_size = (img.shape[1], img.shape[0])

            logger.info(f"Preprocessing complete: {original_size} -> {processed_size}, corrections={corrections}")

            return PreprocessedResult(
                cleaned_image=img,
                image_ref=image_ref,
                original_size=original_size,
                processed_size=processed_size,
                corrections_applied=corrections,
            )
        except ScanError:
            raise
        except Exception as e:
            raise ScanError(f"Image preprocessing failed: {e}")

    def _resize(self, img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]
        if max(h, w) <= self.TARGET_SIZE:
            return img
        scale = self.TARGET_SIZE / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def _correct_orientation(self, img: np.ndarray) -> np.ndarray:
        """Basic orientation correction using edge detection heuristics."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

        if lines is None or len(lines) < 5:
            return img

        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) < 15:
                angles.append(angle)

        if not angles:
            return img

        median_angle = np.median(angles)
        if abs(median_angle) < 1.0:
            return img

        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        return cv2.warpAffine(img, rotation_matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_channel)
        enhanced = cv2.merge([l_enhanced, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    def _reduce_glare(self, img: np.ndarray) -> np.ndarray:
        """Reduce specular highlights by blending with median-filtered version."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)

        glare_mask = v > 240
        glare_ratio = np.sum(glare_mask) / glare_mask.size

        if glare_ratio < 0.01:
            return img

        blurred = cv2.medianBlur(img, 5)
        mask_3ch = np.stack([glare_mask] * 3, axis=-1).astype(np.float32)
        result = (img.astype(np.float32) * (1 - mask_3ch * 0.7) + blurred.astype(np.float32) * mask_3ch * 0.7)
        return result.astype(np.uint8)

    def _detect_panel_crop(self, img: np.ndarray) -> np.ndarray | None:
        """Attempt to detect and crop the main panel region."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        area_ratio = cv2.contourArea(largest) / (img.shape[0] * img.shape[1])

        if area_ratio < 0.2:
            return None

        x, y, w, h = cv2.boundingRect(largest)
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2 * padding)
        h = min(img.shape[0] - y, h + 2 * padding)

        return img[y : y + h, x : x + w]
