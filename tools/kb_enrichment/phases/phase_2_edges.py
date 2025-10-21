"""Phase 2: Explicit edge generation (rule-based linking)."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from ..gemini.client import GeminiClient
from ..gemini.prompts import PromptTemplates
from ..utils.file_io import load_json, save_json, ensure_dir

logger = logging.getLogger(__name__)


class Phase2EdgeGeneration:
    """Phase 2: Rule-based edge generation."""
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        input_dir: Path,
        output_dir: Path,
        test_mode: bool = False
    ):
        """Initialize Phase 2.
        
        Args:
            gemini_client: Gemini API client
            input_dir: Input data directory
            output_dir: Output directory
            test_mode: Whether to run in test mode
        """
        self.gemini = gemini_client
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.test_mode = test_mode
        
        self.phase_output_dir = self.output_dir / "phase_2"
        ensure_dir(self.phase_output_dir)
    
    def run(self) -> List[str]:
        """Execute Phase 2.
        
        Returns:
            List of generated file paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 2: EXPLICIT EDGE GENERATION")
        logger.info("=" * 60)
        
        generated_files = []
        
        # Task 2.1: Generate compositional and prerequisite edges
        logger.info("\n[Task 2.1] Generating compositional and prerequisite edges...")
        explicit_edges_file = self._generate_explicit_edges()
        generated_files.append(explicit_edges_file)
        
        # Task 2.2: Generate contextual tool edges
        logger.info("\n[Task 2.2] Generating contextual tool edges...")
        contextual_edges_file = self._generate_contextual_edges()
        generated_files.append(contextual_edges_file)
        
        logger.info(f"\n✓ Phase 2 complete. Generated {len(generated_files)} files.")
        return generated_files
    
    def _generate_explicit_edges(self) -> str:
        """Generate explicit edges from archetype and prerequisite data.
        
        Returns:
            Path to generated edge file
        """
        # Load source data
        archetypes_file = self.input_dir / "AI_archetypes.json"
        prerequisites_file = self.input_dir / "AI_prerequisites.json"
        
        archetypes_data = load_json(archetypes_file)
        prerequisites_data = load_json(prerequisites_file)
        
        # Also load Phase 1 node files for ID mapping
        phase_1_dir = self.output_dir / "phase_1"
        node_files = {
            "archetypes": phase_1_dir / "AI_ARCHETYPE_NODES.json",
            "models": phase_1_dir / "COMMON_MODEL_NODES.json",
            "outputs": phase_1_dir / "AI_OUTPUT_NODES.json",
            "prerequisites": phase_1_dir / "AI_PREREQUISITE_NODES.json"
        }
        
        node_data = {}
        for key, file_path in node_files.items():
            if file_path.exists():
                node_data[key] = load_json(file_path)
        
        # Combine for prompt
        input_data = {
            "source_archetypes": archetypes_data,
            "source_prerequisites": prerequisites_data,
            "extracted_nodes": node_data
        }
        
        # Format prompt
        prompt = PromptTemplates.PHASE_2_1_EXPLICIT_EDGES.format(
            input_data=PromptTemplates.format_input_data(input_data)
        )
        
        logger.info("Requesting edge generation from Gemini...")
        edges = self.gemini.generate_json(prompt, temperature=0.1)
        
        # Ensure we have a list
        if isinstance(edges, dict) and "edges" in edges:
            edges = edges["edges"]
        
        # Save edges
        output_file = self.phase_output_dir / "EXPLICIT_EDGES.json"
        save_json(edges, output_file)
        
        logger.info(f"✓ Generated {len(edges)} explicit edges")
        return str(output_file)
    
    def _generate_contextual_edges(self) -> str:
        """Generate contextual edges from discovery data.
        
        Returns:
            Path to generated edge file
        """
        # Load source data
        discovery_file = self.input_dir / "AI_discovery.json"
        discovery_data = load_json(discovery_file)
        
        # Load Phase 0 node files for ID mapping
        phase_0_dir = self.output_dir / "phase_0"
        node_files = {
            "functions": phase_0_dir / "FUNCTION_NODES.json",
            "sectors": phase_0_dir / "SECTOR_NODES.json",
            "tools": phase_0_dir / "TOOL_NODES.json"
        }
        
        node_data = {}
        for key, file_path in node_files.items():
            if file_path.exists():
                node_data[key] = load_json(file_path)
        
        # Combine for prompt
        input_data = {
            "source_discovery": discovery_data,
            "extracted_nodes": node_data
        }
        
        # Format prompt
        prompt = PromptTemplates.PHASE_2_2_CONTEXTUAL_EDGES.format(
            input_data=PromptTemplates.format_input_data(input_data)
        )
        
        logger.info("Requesting contextual edge generation from Gemini...")
        edges = self.gemini.generate_json(prompt, temperature=0.1)
        
        # Ensure we have a list
        if isinstance(edges, dict) and "edges" in edges:
            edges = edges["edges"]
        
        # Save edges
        output_file = self.phase_output_dir / "CONTEXTUAL_EDGES.json"
        save_json(edges, output_file)
        
        logger.info(f"✓ Generated {len(edges)} contextual edges")
        return str(output_file)
