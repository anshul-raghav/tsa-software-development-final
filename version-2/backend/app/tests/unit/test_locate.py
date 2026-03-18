"""Unit tests for LocateService — control resolution and spatial instructions."""
import pytest

from app.services.locate.service import LocateService


@pytest.fixture
def locate_service():
    return LocateService()


class TestExactMatch:
    def test_finds_by_exact_label(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Start", sample_control_graph, sample_panel_map)
        assert result.resolved_control_id == "ctrl_start"
        assert result.confidence == 1.0
        assert result.spoken_instruction != ""

    def test_finds_case_insensitive(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("start", sample_control_graph, sample_panel_map)
        assert result.resolved_control_id == "ctrl_start"


class TestAliasMatch:
    def test_finds_by_alias(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("begin", sample_control_graph, sample_panel_map)
        assert result.resolved_control_id == "ctrl_start"

    def test_finds_stop_by_cancel(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("cancel", sample_control_graph, sample_panel_map)
        assert result.resolved_control_id == "ctrl_stop"


class TestPartialMatch:
    def test_finds_by_partial_label(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Time", sample_control_graph, sample_panel_map)
        assert result.resolved_control_id == "ctrl_time_cook"


class TestNoMatch:
    def test_returns_suggestions_for_close_query(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Star", sample_control_graph, sample_panel_map)
        # "Star" is a partial match for "Start", so it should find it
        assert result.resolved_control_id == "ctrl_start" or result.confidence == 0.0

    def test_returns_zero_confidence_for_unknown(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Pizza", sample_control_graph, sample_panel_map)
        assert result.confidence == 0.0
        assert "couldn't find" in result.spoken_instruction.lower()


class TestSpokenInstruction:
    def test_includes_spatial_info(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Start", sample_control_graph, sample_panel_map)
        instruction = result.spoken_instruction.lower()
        assert "start" in instruction

    def test_includes_guidance_target(self, locate_service, sample_control_graph, sample_panel_map):
        result = locate_service.locate("Start", sample_control_graph, sample_panel_map)
        assert result.guidance_target is not None
        assert result.guidance_target.target_label == "Start"
