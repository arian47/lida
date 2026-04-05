"""
LIDA Test Suite

Comprehensive tests for the LIDA visualization library.
These tests verify the core functionality of LIDA including:
- Data summarization
- Goal generation
- Visualization generation
- Visualization editing
- Visualization explanation
- Visualization evaluation
- Visualization repair
- Visualization recommendation
"""

import os
import pytest
from pathlib import Path

from lida.components import Manager
from lida.llm import llm, TextGenerationConfig


# Test configuration
CARS_DATA_URL = "https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv"


@pytest.fixture(scope="module")
def lida_manager():
    """Create a LIDA manager instance for testing."""
    return Manager(text_gen=llm("openai"))


@pytest.fixture(scope="module")
def textgen_config():
    """Create a text generation config for testing."""
    return TextGenerationConfig(
        n=1,
        temperature=0,
        use_cache=False,
        max_tokens=1000
    )


@pytest.fixture(scope="module")
def car_summary(lida_manager, textgen_config):
    """Generate and cache a summary of the cars dataset."""
    return lida_manager.summarize(
        CARS_DATA_URL,
        textgen_config=textgen_config,
        summary_method="default"
    )


@pytest.fixture(scope="module")
def car_goals(lida_manager, car_summary, textgen_config):
    """Generate and cache goals for the cars dataset."""
    return lida_manager.goals(
        car_summary,
        n=3,
        textgen_config=textgen_config
    )


class TestDataSummarization:
    """Tests for data summarization functionality."""

    def test_summarize_returns_summary_object(self, lida_manager, textgen_config):
        """Test that summarize returns a proper summary object."""
        summary = lida_manager.summarize(
            CARS_DATA_URL,
            textgen_config=textgen_config,
            summary_method="default"
        )
        
        assert summary is not None
        assert hasattr(summary, 'name')
        assert hasattr(summary, 'file_name')
        assert hasattr(summary, 'dataset_description')
        assert hasattr(summary, 'field_names')

    def test_summarize_includes_field_info(self, lida_manager, textgen_config):
        """Test that summary includes field information."""
        summary = lida_manager.summarize(
            CARS_DATA_URL,
            textgen_config=textgen_config,
            summary_method="default"
        )
        
        assert len(summary.field_names) > 0
        if summary.fields:
            assert len(summary.fields) == len(summary.field_names)

    def test_summarize_llm_method(self, lida_manager, textgen_config):
        """Test summarization with LLM enrichment method."""
        summary = lida_manager.summarize(
            CARS_DATA_URL,
            textgen_config=textgen_config,
            summary_method="llm"
        )
        
        assert summary is not None
        assert len(summary.dataset_description) > 0


class TestGoalGeneration:
    """Tests for goal generation functionality."""

    def test_goals_returns_list(self, car_goals):
        """Test that goals returns a list."""
        assert isinstance(car_goals, list)
        assert len(car_goals) > 0

    def test_goals_have_required_fields(self, car_goals):
        """Test that each goal has required fields."""
        for goal in car_goals:
            assert hasattr(goal, 'question')
            assert hasattr(goal, 'visualization')
            assert hasattr(goal, 'rationale')
            assert len(goal.question) > 0

    def test_goals_with_persona(self, lida_manager, car_summary, textgen_config):
        """Test goal generation with persona."""
        goals = lida_manager.goals(
            car_summary,
            n=2,
            persona="data analyst",
            textgen_config=textgen_config
        )
        
        assert len(goals) == 2
        assert all(hasattr(g, 'question') for g in goals)


class TestVisualizationGeneration:
    """Tests for visualization generation functionality."""

    def test_visualize_returns_charts(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that visualize returns a list of charts."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="seaborn"
        )
        
        assert isinstance(charts, list)
        assert len(charts) > 0

    def test_chart_has_required_attributes(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that generated chart has required attributes."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        chart = charts[0]
        assert hasattr(chart, 'code')
        assert hasattr(chart, 'status')
        assert hasattr(chart, 'raster')
        assert chart.status is True

    def test_visualize_with_different_libraries(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test visualization with different libraries."""
        libraries = ["matplotlib", "seaborn"]
        
        for lib in libraries:
            charts = lida_manager.visualize(
                summary=car_summary,
                goal=car_goals[0],
                textgen_config=textgen_config,
                library=lib
            )
            assert len(charts) > 0
            assert charts[0].status is True

    def test_chart_savefig(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that charts can be saved to file."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        temp_file = "/tmp/test_chart.png"
        charts[0].savefig(temp_file)
        assert os.path.exists(temp_file)
        os.remove(temp_file)


class TestVisualizationEditing:
    """Tests for visualization editing functionality."""

    def test_edit_returns_modified_charts(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that edit returns modified charts."""
        # First generate a chart
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        # Then edit it
        edited_charts = lida_manager.edit(
            code=charts[0].code,
            summary=car_summary,
            instructions=["change the title to 'Car Data'"],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        assert len(edited_charts) > 0
        assert edited_charts[0].status is True


class TestVisualizationExplanation:
    """Tests for visualization explanation functionality."""

    def test_explain_returns_explanation(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that explain returns a text explanation."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        explanations = lida_manager.explain(
            code=charts[0].code,
            summary=car_summary,
            textgen_config=textgen_config
        )
        
        assert len(explanations) > 0
        assert len(explanations[0]) > 0


class TestVisualizationEvaluation:
    """Tests for visualization evaluation functionality."""

    def test_evaluate_returns_scores(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that evaluate returns evaluation scores."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        evaluations = lida_manager.evaluate(
            code=charts[0].code,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        assert len(evaluations) > 0


class TestVisualizationRepair:
    """Tests for visualization repair functionality."""

    def test_repair_returns_fixed_charts(self, lida_manager, car_summary, car_goals, textgen_config):
        """Test that repair returns fixed charts."""
        charts = lida_manager.visualize(
            summary=car_summary,
            goal=car_goals[0],
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        repaired_charts = lida_manager.repair(
            code=charts[0].code,
            feedback="The x-axis label is overlapping",
            goal=car_goals[0],
            summary=car_summary,
            textgen_config=textgen_config,
            library="matplotlib"
        )
        
        assert len(repaired_charts) > 0


class TestVisualizationRecommendation:
    """Tests for visualization recommendation functionality."""

    def test_recommend_returns_suggestions(self, lida_manager, car_summary, textgen_config):
        """Test that recommend returns recommended visualizations."""
        charts = lida_manager.recommend(
            summary=car_summary,
            textgen_config=textgen_config,
            library="matplotlib",
            n=3
        )
        
        assert len(charts) > 0


class TestManagerIntegration:
    """Integration tests for the Manager class."""

    def test_full_workflow(self, lida_manager, textgen_config):
        """Test a complete visualization workflow."""
        # Summarize
        summary = lida_manager.summarize(
            CARS_DATA_URL,
            textgen_config=textgen_config,
            summary_method="default"
        )
        assert summary is not None
        
        # Generate goals
        goals = lida_manager.goals(
            summary,
            n=2,
            textgen_config=textgen_config
        )
        assert len(goals) == 2
        
        # Generate visualization
        charts = lida_manager.visualize(
            summary=summary,
            goal=goals[0],
            textgen_config=textgen_config,
            library="seaborn"
        )
        assert len(charts) > 0
        assert charts[0].status is True

    def test_check_textgen_provider_switching(self, textgen_config):
        """Test that textgen provider switching works."""
        manager = Manager()
        
        # Initially no provider set
        config1 = TextGenerationConfig(provider=None)
        manager.check_textgen(config1)
        
        # Switch to openai
        config2 = TextGenerationConfig(provider="openai")
        manager.check_textgen(config2)
        assert manager.text_gen.provider == "openai"


# Skip tests that require API calls if no API key is available
def pytest_collection_modifyitems(items):
    """Skip integration tests if no API key is available."""
    if not os.environ.get("OPENAI_API_KEY"):
        skip_integration = pytest.mark.skip(reason="OPENAI_API_KEY not set")
        for item in items:
            if "integration" in item.keywords or "vizgen" in item.keywords:
                item.add_marker(skip_integration)
