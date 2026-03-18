from __future__ import annotations

import re
import json

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import IntentParsingError
from app.domain.models.task import TaskIntent


class IntentParsingService:
    """Parses natural language user requests into structured task intents.

    Uses rules-based parsing first; falls back to OpenAI for ambiguous requests.
    """

    DURATION_PATTERNS = [
        (r"(\d+)\s*(?:seconds?|secs?|s)\b", "seconds"),
        (r"(\d+)\s*(?:minutes?|mins?|m)\b", "minutes"),
        (r"(\d+)\s*:\s*(\d+)", "mm:ss"),
    ]

    MICROWAVE_INTENT_PATTERNS = {
        "heat_for_time": [
            r"(?:set|heat|cook|run|microwave)\s+(?:for|at)?\s*(\d+)",
            r"(\d+)\s*(?:seconds?|minutes?)",
            r"time\s+cook",
        ],
        "defrost": [
            r"defrost",
            r"thaw",
        ],
        "set_power": [
            r"(?:set|change)\s+(?:the\s+)?power",
            r"power\s+(?:level\s+)?(?:to\s+)?(\d+)",
        ],
        "stop": [
            r"\b(?:stop|cancel|clear|off)\b",
        ],
        "start": [
            r"\bstart\b",
            r"\bbegin\b",
            r"\bgo\b",
        ],
    }

    def __init__(self):
        self._client: AsyncOpenAI | None = None

    async def parse(self, user_request: str, appliance_type: str) -> TaskIntent:
        logger.info(f"Parsing intent: '{user_request}' for {appliance_type}")

        intent = self._try_rules_based(user_request, appliance_type)
        if intent and intent.confidence >= 0.7:
            logger.info(f"Rules-based intent: {intent.intent} (conf={intent.confidence})")
            return intent

        logger.info("Rules-based parsing low confidence, trying OpenAI fallback")
        try:
            return await self._openai_parse(user_request, appliance_type)
        except Exception as e:
            if intent:
                logger.warning(f"OpenAI fallback failed, using rules-based result: {e}")
                return intent
            raise IntentParsingError(f"Could not parse intent: {e}")

    def _try_rules_based(self, request: str, appliance_type: str) -> TaskIntent | None:
        request_lower = request.lower().strip()

        if appliance_type == "microwave":
            return self._parse_microwave_intent(request_lower, request)

        return self._parse_generic_intent(request_lower, request, appliance_type)

    def _parse_microwave_intent(self, request_lower: str, raw: str) -> TaskIntent | None:
        for intent_name, patterns in self.MICROWAVE_INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, request_lower)
                if match:
                    params = self._extract_parameters(request_lower, intent_name)
                    return TaskIntent(
                        appliance_type="microwave",
                        intent=intent_name,
                        parameters=params,
                        raw_query=raw,
                        confidence=0.85,
                    )
        return None

    def _parse_generic_intent(self, request_lower: str, raw: str, appliance_type: str) -> TaskIntent | None:
        if any(word in request_lower for word in ["stop", "cancel", "clear", "off"]):
            return TaskIntent(appliance_type=appliance_type, intent="stop", raw_query=raw, confidence=0.9)
        if any(word in request_lower for word in ["start", "begin", "go", "run"]):
            return TaskIntent(appliance_type=appliance_type, intent="start", raw_query=raw, confidence=0.9)
        return TaskIntent(appliance_type=appliance_type, intent="unknown", raw_query=raw, confidence=0.3)

    def _extract_parameters(self, request_lower: str, intent: str) -> dict:
        params: dict = {}

        for pattern, unit in self.DURATION_PATTERNS:
            match = re.search(pattern, request_lower)
            if match:
                if unit == "mm:ss":
                    minutes, seconds = int(match.group(1)), int(match.group(2))
                    params["duration_seconds"] = minutes * 60 + seconds
                elif unit == "minutes":
                    params["duration_seconds"] = int(match.group(1)) * 60
                else:
                    params["duration_seconds"] = int(match.group(1))
                break

        power_match = re.search(r"power\s+(?:level\s+)?(?:to\s+)?(\d+)", request_lower)
        if power_match:
            params["power_level"] = int(power_match.group(1))

        return params

    async def _openai_parse(self, request: str, appliance_type: str) -> TaskIntent:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)

        response = await self._client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a task intent parser for a {appliance_type} control panel. "
                        "Parse the user's request into structured JSON with fields: "
                        '"intent" (string), "parameters" (object with duration_seconds, power_level, etc), '
                        '"confidence" (float 0-1). Return ONLY valid JSON.'
                    ),
                },
                {"role": "user", "content": request},
            ],
            max_tokens=256,
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise IntentParsingError("Empty response from OpenAI intent parser")

        data = json.loads(content)
        return TaskIntent(
            appliance_type=appliance_type,
            intent=data.get("intent", "unknown"),
            parameters=data.get("parameters", {}),
            raw_query=request,
            confidence=data.get("confidence", 0.5),
        )
