"""Unit tests for PanelMapValidationService — deduplication, normalization, type inference."""
import pytest

from app.domain.models.panel_map_models import (
    BoundingBox,
    ControlNode,
    ControlType,
    PanelMap,
    Region,
)
from app.services.panelmap.panelmap_normalization_service import PanelMapValidationService


@pytest.fixture
def validator():
    return PanelMapValidationService()


def _bbox(x1, y1, x2, y2):
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def _control(id: str, label: str, bbox: BoundingBox, **kwargs) -> ControlNode:
    return ControlNode(id=id, label=label, bbox=bbox, **kwargs)


class TestDeduplication:
    @pytest.mark.asyncio
    async def test_removes_duplicate_controls(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[
                _control("c1", "Start", _bbox(0.7, 0.8, 0.9, 0.95), confidence=0.8),
                _control("c2", "Start", _bbox(0.72, 0.81, 0.91, 0.96), confidence=0.9),
            ],
        )
        result = await validator.validate_and_normalize(panel)
        assert len(result.controls) == 1
        assert result.controls[0].confidence == 0.9

    @pytest.mark.asyncio
    async def test_keeps_distinct_controls(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[
                _control("c1", "Start", _bbox(0.7, 0.8, 0.9, 0.95)),
                _control("c2", "Stop", _bbox(0.7, 0.6, 0.9, 0.75)),
            ],
        )
        result = await validator.validate_and_normalize(panel)
        assert len(result.controls) == 2


class TestLabelNormalization:
    @pytest.mark.asyncio
    async def test_strips_whitespace(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "  Start  ", _bbox(0.7, 0.8, 0.9, 0.95))],
        )
        result = await validator.validate_and_normalize(panel)
        assert result.controls[0].label == "Start"

    @pytest.mark.asyncio
    async def test_generates_id_for_empty(self, validator):
        ctrl = _control("", "Defrost", _bbox(0.1, 0.1, 0.3, 0.2))
        panel = PanelMap(panel_id="test", controls=[ctrl])
        result = await validator.validate_and_normalize(panel)
        assert result.controls[0].id == "ctrl_defrost"


class TestAliasFilling:
    @pytest.mark.asyncio
    async def test_fills_start_aliases(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "Start", _bbox(0.7, 0.8, 0.9, 0.95))],
        )
        result = await validator.validate_and_normalize(panel)
        aliases = result.controls[0].aliases
        assert "begin" in aliases or "go" in aliases

    @pytest.mark.asyncio
    async def test_fills_stop_aliases(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "Stop", _bbox(0.7, 0.6, 0.9, 0.75))],
        )
        result = await validator.validate_and_normalize(panel)
        assert "cancel" in result.controls[0].aliases


class TestPrimaryActionIdentification:
    @pytest.mark.asyncio
    async def test_flags_primary_actions(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[
                _control("c1", "Start", _bbox(0.7, 0.8, 0.9, 0.95)),
                _control("c2", "5", _bbox(0.3, 0.5, 0.45, 0.6)),
            ],
        )
        result = await validator.validate_and_normalize(panel)
        start = next(c for c in result.controls if c.label == "Start")
        five = next(c for c in result.controls if c.label == "5")
        assert start.is_primary_action is True
        assert five.is_primary_action is False


class TestControlTypeInference:
    @pytest.mark.asyncio
    async def test_digit_becomes_number(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "5", _bbox(0.3, 0.5, 0.45, 0.6))],
        )
        result = await validator.validate_and_normalize(panel)
        assert result.controls[0].type == ControlType.NUMBER

    @pytest.mark.asyncio
    async def test_start_becomes_action(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "start", _bbox(0.7, 0.8, 0.9, 0.95))],
        )
        result = await validator.validate_and_normalize(panel)
        assert result.controls[0].type == ControlType.ACTION

    @pytest.mark.asyncio
    async def test_defrost_becomes_mode(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[_control("c1", "Defrost", _bbox(0.1, 0.1, 0.3, 0.2))],
        )
        result = await validator.validate_and_normalize(panel)
        assert result.controls[0].type == ControlType.MODE


class TestConfidenceComputation:
    @pytest.mark.asyncio
    async def test_empty_controls_zero_confidence(self, validator):
        panel = PanelMap(panel_id="test", controls=[])
        result = await validator.validate_and_normalize(panel)
        assert result.scan_confidence == 0.0

    @pytest.mark.asyncio
    async def test_high_confidence_with_numbers_and_actions(self, validator):
        panel = PanelMap(
            panel_id="test",
            controls=[
                _control("c1", "1", _bbox(0.1, 0.3, 0.25, 0.4), confidence=0.9),
                _control("c2", "Start", _bbox(0.7, 0.8, 0.9, 0.95), confidence=0.9),
            ],
        )
        result = await validator.validate_and_normalize(panel)
        assert result.scan_confidence >= 0.9
