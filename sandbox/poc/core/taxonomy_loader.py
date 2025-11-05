"""Taxonomy data loader for function templates and related data."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

from config.settings import settings


class TaxonomyLoader:
    """Loads and caches taxonomy data from JSON files."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize taxonomy loader.
        
        Args:
            data_dir: Path to data directory. Defaults to settings.DATA_DIR
        """
        self.data_dir = data_dir or settings.DATA_DIR
        self._cache: Dict[str, any] = {}
    
    def _load_json(self, relative_path: str) -> Dict:
        """
        Load JSON file from data directory.
        
        Args:
            relative_path: Path relative to data_dir
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        cache_key = relative_path
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = self.data_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._cache[cache_key] = data
        return data
    
    @lru_cache(maxsize=1)
    def load_function_templates(self) -> List[Dict]:
        """
        Load all function templates from organizational_templates/functions/
        
        Returns:
            List of function template dictionaries
        """
        functions_dir = self.data_dir / "organizational_templates" / "functions"
        
        if not functions_dir.exists():
            raise FileNotFoundError(f"Functions directory not found: {functions_dir}")
        
        templates = []
        for json_file in functions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    templates.append(template)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to load {json_file}: {e}")
                continue
        
        return templates
    
    @lru_cache(maxsize=1)
    def load_component_scales(self) -> Dict:
        """
        Load component_scales.json
        
        Returns:
            Component scales dictionary
        """
        return self._load_json("component_scales.json")
    
    @lru_cache(maxsize=1)
    def load_pilot_types(self) -> Dict:
        """
        Load pilot_types.json
        
        Returns:
            Pilot types dictionary
        """
        return self._load_json("pilot_types.json")
    
    @lru_cache(maxsize=1)
    def load_pilot_catalog(self) -> Dict:
        """
        Load pilot_catalog.json
        
        Returns:
            Pilot catalog dictionary
        """
        return self._load_json("pilot_catalog.json")
    
    @lru_cache(maxsize=1)
    def load_inference_rules(self) -> Dict:
        """
        Load inference_rules/output_discovery.json
        
        Returns:
            Inference rules dictionary
        """
        return self._load_json("inference_rules/output_discovery.json")
    
    @lru_cache(maxsize=1)
    def load_common_systems(self) -> Dict:
        """
        Load organizational_templates/cross_functional/common_systems.json
        
        Returns:
            Common systems dictionary
        """
        return self._load_json("organizational_templates/cross_functional/common_systems.json")
    
    @lru_cache(maxsize=1)
    def load_pain_point_mapping(self) -> Dict:
        """
        Load inference_rules/pain_point_mapping.json
        
        Returns:
            Pain point mapping dictionary
        """
        return self._load_json("inference_rules/pain_point_mapping.json")
    
    @lru_cache(maxsize=1)
    def load_ai_archetypes(self) -> Dict:
        """
        Load inference_rules/ai_archetypes.json
        
        Returns:
            AI archetypes dictionary
        """
        return self._load_json("inference_rules/ai_archetypes.json")
    
    def get_output_by_id(self, output_id: str) -> Optional[Dict]:
        """
        Find output by ID across all function templates.
        
        Args:
            output_id: Output identifier (e.g., 'sales_forecast')
            
        Returns:
            Output dictionary if found, None otherwise
        """
        templates = self.load_function_templates()
        
        for template in templates:
            for output in template.get("common_outputs", []):
                if output.get("id") == output_id:
                    # Add function context
                    output["function"] = template.get("function")
                    return output
        
        return None
    
    def search_outputs(self, keywords: List[str]) -> List[Dict]:
        """
        Search outputs by keywords in name, description, or inference triggers.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching outputs with relevance scores
        """
        templates = self.load_function_templates()
        matches = []
        
        keywords_lower = [k.lower() for k in keywords]
        
        for template in templates:
            function_name = template.get("function", "")
            inference_triggers = template.get("inference_triggers", {})
            
            for output in template.get("common_outputs", []):
                score = 0
                output_with_context = {
                    **output,
                    "function": function_name
                }
                
                # Check output name and description
                name = output.get("name", "").lower()
                desc = output.get("description", "").lower()
                
                for keyword in keywords_lower:
                    if keyword in name:
                        score += 10
                    if keyword in desc:
                        score += 5
                
                # Check inference triggers
                trigger_keywords = inference_triggers.get("keywords", [])
                trigger_pain_points = inference_triggers.get("pain_points", [])
                
                for keyword in keywords_lower:
                    if any(keyword in tk.lower() for tk in trigger_keywords):
                        score += 8
                    if any(keyword in pp.lower() for pp in trigger_pain_points):
                        score += 7
                
                if score > 0:
                    matches.append({
                        "output": output_with_context,
                        "score": score
                    })
        
        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        return matches
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self.load_function_templates.cache_clear()
        self.load_component_scales.cache_clear()
        self.load_pilot_types.cache_clear()
        self.load_pilot_catalog.cache_clear()
        self.load_inference_rules.cache_clear()
        self.load_common_systems.cache_clear()
        self.load_pain_point_mapping.cache_clear()
        self.load_ai_archetypes.cache_clear()
