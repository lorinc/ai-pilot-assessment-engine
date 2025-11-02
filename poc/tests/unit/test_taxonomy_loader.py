"""Unit tests for TaxonomyLoader."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from core.taxonomy_loader import TaxonomyLoader


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary data directory with mock taxonomy files."""
    # Create directory structure
    functions_dir = tmp_path / "organizational_templates" / "functions"
    functions_dir.mkdir(parents=True)
    
    cross_functional_dir = tmp_path / "organizational_templates" / "cross_functional"
    cross_functional_dir.mkdir(parents=True)
    
    inference_dir = tmp_path / "inference_rules"
    inference_dir.mkdir(parents=True)
    
    # Create mock function template
    sales_template = {
        "function": "Sales",
        "common_outputs": [
            {
                "id": "sales_forecast",
                "name": "Sales Forecast",
                "description": "Monthly sales predictions"
            }
        ],
        "inference_triggers": {
            "keywords": ["sales", "forecast", "prediction"],
            "pain_points": ["forecasts are wrong", "inaccurate predictions"]
        }
    }
    
    with open(functions_dir / "sales.json", 'w') as f:
        json.dump(sales_template, f)
    
    # Create mock component scales
    component_scales = {
        "components": ["team_execution", "system_capabilities", "process_maturity", "dependency_quality"]
    }
    
    with open(tmp_path / "component_scales.json", 'w') as f:
        json.dump(component_scales, f)
    
    # Create mock pilot types
    pilot_types = {
        "pilot_categories": {
            "team_execution": {"pilot_types": []}
        }
    }
    
    with open(tmp_path / "pilot_types.json", 'w') as f:
        json.dump(pilot_types, f)
    
    # Create mock pilot catalog
    pilot_catalog = {
        "categories": []
    }
    
    with open(tmp_path / "pilot_catalog.json", 'w') as f:
        json.dump(pilot_catalog, f)
    
    # Create mock inference rules
    inference_rules = {
        "inference_strategies": []
    }
    
    with open(inference_dir / "output_discovery.json", 'w') as f:
        json.dump(inference_rules, f)
    
    # Create mock common systems
    common_systems = {
        "system_categories": {}
    }
    
    with open(cross_functional_dir / "common_systems.json", 'w') as f:
        json.dump(common_systems, f)
    
    # Create mock pain point mapping
    pain_point_mapping = {
        "categories": []
    }
    
    with open(inference_dir / "pain_point_mapping.json", 'w') as f:
        json.dump(pain_point_mapping, f)
    
    # Create mock AI archetypes
    ai_archetypes = {
        "archetypes": []
    }
    
    with open(inference_dir / "ai_archetypes.json", 'w') as f:
        json.dump(ai_archetypes, f)
    
    return tmp_path


class TestTaxonomyLoader:
    """Test suite for TaxonomyLoader class."""
    
    def test_init_with_default_data_dir(self):
        """Test initialization with default data directory."""
        loader = TaxonomyLoader()
        assert loader.data_dir is not None
        assert isinstance(loader._cache, dict)
    
    def test_init_with_custom_data_dir(self, mock_data_dir):
        """Test initialization with custom data directory."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        assert loader.data_dir == mock_data_dir
    
    def test_load_function_templates(self, mock_data_dir):
        """Test loading function templates."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        templates = loader.load_function_templates()
        
        assert isinstance(templates, list)
        assert len(templates) == 1
        assert templates[0]["function"] == "Sales"
        assert len(templates[0]["common_outputs"]) == 1
    
    def test_load_function_templates_caching(self, mock_data_dir):
        """Test that function templates are cached."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        
        # Load twice
        templates1 = loader.load_function_templates()
        templates2 = loader.load_function_templates()
        
        # Should return same object (cached)
        assert templates1 is templates2
    
    def test_load_function_templates_missing_dir(self, tmp_path):
        """Test error when functions directory doesn't exist."""
        loader = TaxonomyLoader(data_dir=tmp_path)
        
        with pytest.raises(FileNotFoundError, match="Functions directory not found"):
            loader.load_function_templates()
    
    def test_load_component_scales(self, mock_data_dir):
        """Test loading component scales."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        scales = loader.load_component_scales()
        
        assert isinstance(scales, dict)
        assert "components" in scales
    
    def test_load_pilot_types(self, mock_data_dir):
        """Test loading pilot types."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        pilot_types = loader.load_pilot_types()
        
        assert isinstance(pilot_types, dict)
        assert "pilot_categories" in pilot_types
    
    def test_load_pilot_catalog(self, mock_data_dir):
        """Test loading pilot catalog."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        catalog = loader.load_pilot_catalog()
        
        assert isinstance(catalog, dict)
        assert "categories" in catalog
    
    def test_load_inference_rules(self, mock_data_dir):
        """Test loading inference rules."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        rules = loader.load_inference_rules()
        
        assert isinstance(rules, dict)
        assert "inference_strategies" in rules
    
    def test_load_common_systems(self, mock_data_dir):
        """Test loading common systems."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        systems = loader.load_common_systems()
        
        assert isinstance(systems, dict)
        assert "system_categories" in systems
    
    def test_load_pain_point_mapping(self, mock_data_dir):
        """Test loading pain point mapping."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        mapping = loader.load_pain_point_mapping()
        
        assert isinstance(mapping, dict)
        assert "categories" in mapping
    
    def test_load_ai_archetypes(self, mock_data_dir):
        """Test loading AI archetypes."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        archetypes = loader.load_ai_archetypes()
        
        assert isinstance(archetypes, dict)
        assert "archetypes" in archetypes
    
    def test_get_output_by_id_found(self, mock_data_dir):
        """Test finding output by ID."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        output = loader.get_output_by_id("sales_forecast")
        
        assert output is not None
        assert output["id"] == "sales_forecast"
        assert output["name"] == "Sales Forecast"
        assert output["function"] == "Sales"
    
    def test_get_output_by_id_not_found(self, mock_data_dir):
        """Test output not found returns None."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        output = loader.get_output_by_id("nonexistent_output")
        
        assert output is None
    
    def test_search_outputs_by_name(self, mock_data_dir):
        """Test searching outputs by name keyword."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["forecast"])
        
        assert len(matches) > 0
        assert matches[0]["output"]["id"] == "sales_forecast"
        assert matches[0]["score"] > 0
    
    def test_search_outputs_by_description(self, mock_data_dir):
        """Test searching outputs by description keyword."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["predictions"])
        
        assert len(matches) > 0
        assert matches[0]["output"]["id"] == "sales_forecast"
    
    def test_search_outputs_by_trigger_keyword(self, mock_data_dir):
        """Test searching outputs by inference trigger keyword."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["sales"])
        
        assert len(matches) > 0
        assert matches[0]["output"]["id"] == "sales_forecast"
    
    def test_search_outputs_by_pain_point(self, mock_data_dir):
        """Test searching outputs by pain point."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["forecasts", "wrong"])
        
        assert len(matches) > 0
        assert matches[0]["output"]["id"] == "sales_forecast"
    
    def test_search_outputs_no_matches(self, mock_data_dir):
        """Test search with no matches returns empty list."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["nonexistent", "keywords"])
        
        assert len(matches) == 0
    
    def test_search_outputs_sorted_by_score(self, mock_data_dir):
        """Test search results are sorted by relevance score."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        matches = loader.search_outputs(["sales", "forecast"])
        
        # Should have matches
        assert len(matches) > 0
        
        # Scores should be descending
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i]["score"] >= matches[i + 1]["score"]
    
    def test_clear_cache(self, mock_data_dir):
        """Test clearing cache."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        
        # Load data to populate cache
        loader.load_function_templates()
        loader.load_component_scales()
        
        # Cache should have data
        assert len(loader._cache) > 0
        
        # Clear cache
        loader.clear_cache()
        
        # Cache should be empty
        assert len(loader._cache) == 0
    
    def test_load_json_file_not_found(self, tmp_path):
        """Test error when JSON file doesn't exist."""
        loader = TaxonomyLoader(data_dir=tmp_path)
        
        with pytest.raises(FileNotFoundError):
            loader._load_json("nonexistent.json")
    
    def test_load_json_invalid_json(self, tmp_path):
        """Test error when JSON file is invalid."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")
        
        loader = TaxonomyLoader(data_dir=tmp_path)
        
        with pytest.raises(json.JSONDecodeError):
            loader._load_json("invalid.json")
    
    def test_load_json_caching(self, mock_data_dir):
        """Test that _load_json caches results."""
        loader = TaxonomyLoader(data_dir=mock_data_dir)
        
        # Load same file twice
        data1 = loader._load_json("component_scales.json")
        data2 = loader._load_json("component_scales.json")
        
        # Should return same object (cached)
        assert data1 is data2
