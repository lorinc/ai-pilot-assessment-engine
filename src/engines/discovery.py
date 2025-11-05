"""Output discovery engine - identifies outputs from natural language descriptions."""

import json
import os
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

from core.llm_client import LLMClient
from utils.logger import TechnicalLogger


class OutputDiscoveryEngine:
    """
    Discovers outputs from user descriptions using semantic matching.
    
    Process:
    1. User describes problem ("Sales forecasts are always wrong")
    2. LLM extracts keywords, pain points, system mentions
    3. Match against output catalog
    4. Present top candidates for confirmation
    5. Infer creation context (Team, Process, System)
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        data_dir: str = "src/data",
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize discovery engine.
        
        Args:
            llm_client: LLM client for semantic matching
            data_dir: Path to data directory
            logger: Technical logger instance
        """
        self.llm = llm_client
        self.data_dir = Path(data_dir)
        self.logger = logger
        self._output_catalog = None  # Lazy load
        self._system_catalog = None  # Lazy load
        self._process_catalog = None  # Lazy load
    
    @property
    def output_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Lazy load output catalog."""
        if self._output_catalog is None:
            self._output_catalog = self._load_output_catalog()
        return self._output_catalog
    
    @property
    def system_catalog(self) -> Dict[str, Any]:
        """Lazy load system catalog."""
        if self._system_catalog is None:
            self._system_catalog = self._load_system_catalog()
        return self._system_catalog
    
    @property
    def process_catalog(self) -> Dict[str, Any]:
        """Lazy load process catalog."""
        if self._process_catalog is None:
            self._process_catalog = self._load_process_catalog()
        return self._process_catalog
    
    def _load_output_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all outputs from function templates.
        
        Returns:
            Dict of output_id -> output_data
        """
        catalog = {}
        functions_dir = self.data_dir / "organizational_templates" / "functions"
        
        if not functions_dir.exists():
            if self.logger:
                self.logger.warning("discovery_init", f"Functions directory not found: {functions_dir}")
            return catalog
        
        for json_file in functions_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    function_name = data.get("function", "Unknown")
                    
                    for output in data.get("common_outputs", []):
                        output_id = output.get("id")
                        if output_id:
                            output["function"] = function_name
                            catalog[output_id] = output
                
                if self.logger:
                    self.logger.info("discovery_load", f"Loaded outputs from {json_file.name}", {
                        "file": json_file.name,
                        "function": function_name
                    })
            
            except Exception as e:
                if self.logger:
                    self.logger.error("discovery_load", f"Failed to load {json_file.name}: {str(e)}")
        
        if self.logger:
            self.logger.info("discovery_init", f"Output catalog loaded", {
                "total_outputs": len(catalog)
            })
        
        return catalog
    
    def _load_system_catalog(self) -> Dict[str, Any]:
        """Load common systems catalog."""
        try:
            systems_file = self.data_dir / "organizational_templates" / "cross_functional" / "common_systems.json"
            if systems_file.exists():
                with open(systems_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            if self.logger:
                self.logger.error("discovery_load", f"Failed to load systems catalog: {str(e)}")
        return {}
    
    def _load_process_catalog(self) -> Dict[str, Any]:
        """Load common processes catalog."""
        try:
            processes_file = self.data_dir / "organizational_templates" / "cross_functional" / "common_processes.json"
            if processes_file.exists():
                with open(processes_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            if self.logger:
                self.logger.error("discovery_load", f"Failed to load processes catalog: {str(e)}")
        return {}
    
    def discover_output(
        self,
        user_description: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover outputs matching user description.
        
        Args:
            user_description: User's problem description
            conversation_history: Previous conversation messages
            
        Returns:
            List of candidate outputs with confidence scores
        """
        if self.logger:
            self.logger.info("discovery_start", "Starting output discovery", {
                "description_length": len(user_description)
            })
        
        # Build prompt for LLM to extract features and match outputs
        prompt = self._build_discovery_prompt(user_description, conversation_history)
        
        # Get LLM response (non-streaming)
        response = self.llm.generate(prompt, caller="OutputDiscoveryEngine.discover_output")
        
        # Parse LLM response to get candidate outputs
        candidates = self._parse_discovery_response(response)
        
        if self.logger:
            self.logger.info("discovery_complete", "Output discovery complete", {
                "candidates_found": len(candidates)
            })
        
        return candidates
    
    def _build_discovery_prompt(
        self,
        user_description: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build prompt for output discovery."""
        
        # Build catalog summary for LLM
        catalog_summary = self._build_catalog_summary()
        
        prompt = f"""You are helping identify which business output the user is struggling with.

USER'S PROBLEM:
"{user_description}"

AVAILABLE OUTPUTS (by function):
{catalog_summary}

INSTRUCTIONS:
1. Identify which output(s) best match the user's problem
2. Return 1-3 candidates with confidence scores
3. Focus on the PROBLEM being described, not just keywords

EXAMPLES:
- "Sales forecasts are wrong" → sales_forecast (Sales function)
- "Campaigns aren't working" → campaign_performance_reports (Marketing function)  
- "Can't track inventory" → inventory_reports (Supply Chain function)

Return ONLY valid JSON in this format:
{{
  "extracted_features": {{
    "keywords": ["keyword1", "keyword2"],
    "pain_points": ["pain1", "pain2"],
    "systems": [],
    "function": "function_name"
  }},
  "candidates": [
    {{
      "output_id": "exact_output_id_from_catalog",
      "confidence": 0.9,
      "reasoning": "Why this matches"
    }}
  ]
}}

CRITICAL: Use exact output_id values from the catalog above. If unsure, return empty candidates array."""
        
        return prompt
    
    def _build_catalog_summary(self) -> str:
        """Build a concise summary of the output catalog for the LLM."""
        # Group outputs by function for more concise presentation
        by_function = {}
        for output_id, output_data in self.output_catalog.items():
            function = output_data.get("function", "Unknown")
            if function not in by_function:
                by_function[function] = []
            by_function[function].append({
                "id": output_id,
                "name": output_data.get("name", "Unknown"),
                "keywords": output_data.get("name", "").lower().split()
            })
        
        # Build concise summary
        summary_lines = []
        for function, outputs in by_function.items():
            output_list = ", ".join([f"{o['id']} ({o['name']})" for o in outputs])
            summary_lines.append(f"**{function}**: {output_list}")
        
        return "\n".join(summary_lines)
    
    def _parse_discovery_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract candidate outputs.
        
        Args:
            response: LLM JSON response
            
        Returns:
            List of candidate outputs with enriched data
        """
        try:
            # Try to extract JSON from response (LLM might add extra text)
            # Look for JSON block between ```json and ``` or just find { }
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response
            
            # Parse JSON response
            data = json.loads(json_str)
            candidates = data.get("candidates", [])
            
            if self.logger:
                self.logger.info("discovery_parse", f"Parsed {len(candidates)} candidates from LLM", {
                    "candidate_count": len(candidates)
                })
            
            # Enrich candidates with full output data
            enriched_candidates = []
            for candidate in candidates:
                output_id = candidate.get("output_id")
                if output_id in self.output_catalog:
                    output_data = self.output_catalog[output_id].copy()
                    output_data["confidence"] = candidate.get("confidence", 0.0)
                    output_data["reasoning"] = candidate.get("reasoning", "")
                    enriched_candidates.append(output_data)
                elif self.logger:
                    self.logger.warning("discovery_parse", f"Unknown output_id: {output_id}")
            
            # Sort by confidence
            enriched_candidates.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
            
            return enriched_candidates
        
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error("discovery_parse", f"Failed to parse LLM response as JSON: {str(e)}", {
                    "error": str(e),
                    "response_length": len(response)
                })
            return []
        except Exception as e:
            if self.logger:
                self.logger.error("discovery_parse", f"Unexpected error parsing response: {str(e)}", {
                    "error": str(e),
                    "response_length": len(response)
                })
            return []
    
    def get_output_details(self, output_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details for a specific output.
        
        Args:
            output_id: Output ID
            
        Returns:
            Output data or None
        """
        return self.output_catalog.get(output_id)
    
    def infer_creation_context(self, output_id: str) -> Dict[str, Any]:
        """
        Infer creation context (Team, Process, System) for an output.
        
        Args:
            output_id: Output ID
            
        Returns:
            Dict with team, process, system information
        """
        output_data = self.output_catalog.get(output_id)
        if not output_data:
            return {}
        
        typical_context = output_data.get("typical_creation_context", {})
        
        context = {
            "team": {
                "name": typical_context.get("team", "Unknown Team"),
                "archetype": self._infer_team_archetype(typical_context.get("team", ""))
            },
            "process": {
                "name": typical_context.get("process", "Unknown Process"),
                "step": typical_context.get("step", "")
            },
            "system": {
                "name": typical_context.get("system", "Unknown System"),
                "category": self._infer_system_category(typical_context.get("system", ""))
            }
        }
        
        if self.logger:
            self.logger.info("discovery_context", f"Inferred context for {output_id}", {
                "output_id": output_id,
                "team": context["team"]["name"],
                "system": context["system"]["name"]
            })
        
        return context
    
    def _infer_team_archetype(self, team_name: str) -> str:
        """Infer team archetype from team name."""
        team_lower = team_name.lower()
        
        if "operations" in team_lower or "ops" in team_lower:
            return "Operations"
        elif "development" in team_lower or "sdr" in team_lower:
            return "Development"
        elif "executive" in team_lower or "ae" in team_lower:
            return "Execution"
        elif "leadership" in team_lower or "management" in team_lower:
            return "Leadership"
        else:
            return "Specialist"
    
    def _infer_system_category(self, system_name: str) -> str:
        """Infer system category from system name."""
        system_lower = system_name.lower()
        
        if "crm" in system_lower or "salesforce" in system_lower:
            return "CRM"
        elif "spreadsheet" in system_lower or "excel" in system_lower or "sheets" in system_lower:
            return "Spreadsheet"
        elif "erp" in system_lower:
            return "ERP"
        elif "bi" in system_lower or "tableau" in system_lower or "looker" in system_lower:
            return "Business Intelligence"
        else:
            return "Other"
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded catalog."""
        stats = {
            "total_outputs": len(self.output_catalog),
            "outputs_by_function": {},
            "outputs_by_team_type": {}
        }
        
        for output_id, output_data in self.output_catalog.items():
            function = output_data.get("function", "Unknown")
            stats["outputs_by_function"][function] = stats["outputs_by_function"].get(function, 0) + 1
            
            team = output_data.get("typical_creation_context", {}).get("team", "Unknown")
            team_type = self._infer_team_archetype(team)
            stats["outputs_by_team_type"][team_type] = stats["outputs_by_team_type"].get(team_type, 0) + 1
        
        return stats
