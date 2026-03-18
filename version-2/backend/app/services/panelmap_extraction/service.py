from __future__ import annotations

import base64
import json
import uuid

import cv2
import numpy as np
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import PanelMapExtractionError
from app.domain.models.panel import PanelMap, OCRToken
from app.prompts.panelmap.system_prompt import build_panelmap_prompt


class PanelMapExtractionService:
    """Uses OpenAI Vision to extract a structured PanelMap from a panel image + OCR."""

    def __init__(self):
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def extract(
        self,
        cleaned_image: np.ndarray,
        ocr_tokens: list[OCRToken],
        scan_id: str,
    ) -> PanelMap:
        logger.info(f"Extracting PanelMap via OpenAI: scan_id={scan_id}")

        image_b64 = self._encode_image(cleaned_image)
        ocr_context = self._format_ocr_context(ocr_tokens)
        prompt = build_panelmap_prompt(ocr_context=ocr_context)

        try:
            response = await self._call_openai(image_b64, prompt)
            panel_map = self._parse_response(response, scan_id)
            logger.info(f"PanelMap extracted: {len(panel_map.controls)} controls, {len(panel_map.regions)} regions")
            return panel_map
        except PanelMapExtractionError:
            raise
        except Exception as e:
            logger.warning(f"First extraction attempt failed: {e}. Retrying...")
            try:
                response = await self._call_openai(image_b64, prompt, strict=True)
                return self._parse_response(response, scan_id)
            except Exception as retry_err:
                raise PanelMapExtractionError(f"PanelMap extraction failed after retry: {retry_err}")

    async def _call_openai(self, image_b64: str, prompt: str, strict: bool = False) -> str:
        client = self._get_client()

        system_msg = prompt
        if strict:
            system_msg += "\n\nCRITICAL: Return ONLY valid JSON. No markdown, no explanation, no commentary."

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                        },
                        {
                            "type": "text",
                            "text": "Analyze this control panel image and return the structured PanelMap JSON.",
                        },
                    ],
                },
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise PanelMapExtractionError("Empty response from OpenAI")
        return content

    def _parse_response(self, response: str, scan_id: str) -> PanelMap:
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise PanelMapExtractionError(f"Invalid JSON from OpenAI: {e}")

        if "panel_id" not in data:
            data["panel_id"] = scan_id

        try:
            return PanelMap.model_validate(data)
        except Exception as e:
            raise PanelMapExtractionError(f"PanelMap schema validation failed: {e}")

    def _encode_image(self, image: np.ndarray) -> str:
        _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer.tobytes()).decode("utf-8")

    def _format_ocr_context(self, tokens: list[OCRToken]) -> str:
        if not tokens:
            return "No OCR tokens detected."
        lines = []
        for t in tokens:
            lines.append(
                f'  "{t.text}" at bbox({t.bbox.x1:.3f}, {t.bbox.y1:.3f}, {t.bbox.x2:.3f}, {t.bbox.y2:.3f}) '
                f"conf={t.confidence:.2f}"
            )
        return "Detected OCR tokens:\n" + "\n".join(lines)
