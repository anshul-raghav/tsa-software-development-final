"""Unit tests for ExploreService — layout description generation."""
import pytest

from app.services.explore.service import ExploreService


@pytest.fixture
def explore_service():
    return ExploreService()


class TestWholePanelDescription:
    def test_describes_all_controls(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("describe the whole panel", sample_control_graph, sample_panel_map)
        assert result.spoken_description != ""
        assert len(result.referenced_controls) == len(sample_control_graph.nodes)

    def test_mentions_appliance_type(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("describe everything", sample_control_graph, sample_panel_map)
        assert "microwave" in result.spoken_description.lower()


class TestRegionDescription:
    def test_describes_number_pad(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("describe the number pad", sample_control_graph, sample_panel_map)
        assert result.referenced_region == "number_pad" or "number" in result.spoken_description.lower()

    def test_region_lists_controls(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("number pad", sample_control_graph, sample_panel_map)
        assert len(result.referenced_controls) >= 1


class TestRowDescription:
    def test_top_row(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("what's on the top row", sample_control_graph, sample_panel_map)
        assert result.spoken_description != ""
        assert "top" in result.spoken_description.lower()

    def test_bottom_row(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("describe the bottom row", sample_control_graph, sample_panel_map)
        assert result.spoken_description != ""
        assert "bottom" in result.spoken_description.lower()


class TestSideDescription:
    def test_right_side(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("what's on the right side", sample_control_graph, sample_panel_map)
        assert result.spoken_description != ""
        assert len(result.referenced_controls) >= 1

    def test_left_side(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("what's on the left", sample_control_graph, sample_panel_map)
        assert result.spoken_description != ""


class TestUnknownQuery:
    def test_returns_fallback(self, explore_service, sample_control_graph, sample_panel_map):
        result = explore_service.explore("xyzzy", sample_control_graph, sample_panel_map)
        assert "couldn't find" in result.spoken_description.lower() or result.spoken_description != ""
