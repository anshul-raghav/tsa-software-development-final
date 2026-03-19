"""Unit tests for IntentParsingService — rules-based intent extraction."""
import pytest

from app.services.tasks.task_intent_parser import IntentParsingService


@pytest.fixture
def parser():
    return IntentParsingService()


class TestMicrowaveIntentParsing:
    @pytest.mark.asyncio
    async def test_heat_for_60_seconds(self, parser):
        intent = await parser.parse("set the microwave for 60 seconds", "microwave")
        assert intent.intent == "heat_for_time"
        assert intent.parameters["duration_seconds"] == 60
        assert intent.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_heat_for_2_minutes(self, parser):
        intent = await parser.parse("cook for 2 minutes", "microwave")
        assert intent.intent == "heat_for_time"
        assert intent.parameters["duration_seconds"] == 120

    @pytest.mark.asyncio
    async def test_defrost(self, parser):
        intent = await parser.parse("defrost my food", "microwave")
        assert intent.intent == "defrost"
        assert intent.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_set_power(self, parser):
        intent = await parser.parse("set power to 5", "microwave")
        assert intent.intent == "set_power"
        assert intent.parameters["power_level"] == 5

    @pytest.mark.asyncio
    async def test_stop(self, parser):
        intent = await parser.parse("stop the microwave", "microwave")
        assert intent.intent == "stop"

    @pytest.mark.asyncio
    async def test_cancel(self, parser):
        intent = await parser.parse("cancel", "microwave")
        assert intent.intent == "stop"


class TestGenericIntentParsing:
    @pytest.mark.asyncio
    async def test_generic_stop(self, parser):
        intent = await parser.parse("turn it off", "thermostat")
        assert intent.intent == "stop"
        assert intent.appliance_type == "thermostat"

    @pytest.mark.asyncio
    async def test_generic_start(self, parser):
        intent = await parser.parse("start it", "washer")
        assert intent.intent == "start"
        assert intent.appliance_type == "washer"

    @pytest.mark.asyncio
    async def test_unknown_intent(self, parser):
        intent = await parser.parse("do something weird", "unknown")
        assert intent.intent == "unknown"
        assert intent.confidence < 0.5
