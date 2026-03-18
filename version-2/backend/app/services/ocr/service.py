from __future__ import annotations

import numpy as np

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import OCRError
from app.domain.models.panel import BoundingBox, OCRToken
from app.domain.schemas.scan import OCRResult


class OCRService:
    """Extracts text tokens with bounding boxes from a preprocessed panel image."""

    def __init__(self):
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            try:
                import easyocr
                self._reader = easyocr.Reader(
                    settings.ocr_languages,
                    gpu=False,
                    verbose=False,
                )
            except Exception as e:
                raise OCRError(f"Failed to initialize OCR reader: {e}")
        return self._reader

    async def extract(self, image: np.ndarray) -> OCRResult:
        logger.info("Running OCR extraction")
        try:
            reader = self._get_reader()
            results = reader.readtext(image)

            h, w = image.shape[:2]
            tokens: list[OCRToken] = []

            for bbox_points, text, confidence in results:
                if confidence < settings.ocr_confidence_threshold:
                    continue

                xs = [p[0] for p in bbox_points]
                ys = [p[1] for p in bbox_points]
                normalized_bbox = BoundingBox(
                    x1=max(0.0, min(xs) / w),
                    y1=max(0.0, min(ys) / h),
                    x2=min(1.0, max(xs) / w),
                    y2=min(1.0, max(ys) / h),
                )

                tokens.append(OCRToken(
                    text=text.strip(),
                    bbox=normalized_bbox,
                    confidence=confidence,
                ))

            raw_text = " ".join(t.text for t in tokens)
            logger.info(f"OCR extracted {len(tokens)} tokens: '{raw_text[:100]}'")

            return OCRResult(tokens=tokens, raw_text=raw_text)
        except OCRError:
            raise
        except Exception as e:
            raise OCRError(f"OCR extraction failed: {e}")
