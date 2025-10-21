"""Phase 1: Core node extraction and formatting."""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from ..gemini.client import GeminiClient
from ..gemini.prompts import PromptTemplates
from ..utils.file_io import load_json, save_json, ensure_dir

logger = logging.getLogger(__name__)


class Phase1Extraction:
    """Phase 1: Node extraction and chunking."""
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        input_dir: Path,
        output_dir: Path,
        test_mode: bool = False,
        test_limits: Dict[str, int] = None,
        chunk_size: int = 15
    ):
        """Initialize Phase 1.
        
        Args:
            gemini_client: Gemini API client
            input_dir: Input data directory
            output_dir: Output directory
            test_mode: Whether to run in test mode
            test_limits: Test mode node limits
            chunk_size: Inference chunk size
        """
        self.gemini = gemini_client
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.test_mode = test_mode
        self.test_limits = test_limits or {}
        self.chunk_size = chunk_size
        
        self.phase_output_dir = self.output_dir / "phase_1"
        ensure_dir(self.phase_output_dir)
    
    def run(self) -> List[str]:
        """Execute Phase 1.
        
        Returns:
            List of generated file paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: CORE NODE EXTRACTION AND FORMATTING")
        logger.info("=" * 60)
        
        generated_files = []
        
        # Task 1.1: Extract archetype and prerequisite nodes
        logger.info("\n[Task 1.1] Extracting AI archetype and prerequisite nodes...")
        node_files = self._extract_archetype_nodes()
        generated_files.extend(node_files)
        
        # Task 1.2: Generate chunking script
        logger.info("\n[Task 1.2] Generating inference task chunking script...")
        script_path = self._generate_chunking_script()
        logger.info(f"✓ Script generated: {script_path}")
        
        # Task 1.3: Execute chunking
        logger.info("\n[Task 1.3] Executing task chunking...")
        chunk_files = self._execute_chunking_script(script_path)
        generated_files.extend(chunk_files)
        
        logger.info(f"\n✓ Phase 1 complete. Generated {len(generated_files)} files.")
        return generated_files
    
    def _extract_archetype_nodes(self) -> List[str]:
        """Extract archetype and prerequisite nodes using Gemini.
        
        Returns:
            List of generated node files
        """
        # Load source data
        archetypes_file = self.input_dir / "AI_archetypes.json"
        prerequisites_file = self.input_dir / "AI_prerequisites.json"
        
        archetypes_data = load_json(archetypes_file)
        prerequisites_data = load_json(prerequisites_file)
        
        # Combine for prompt
        input_data = {
            "archetypes": archetypes_data,
            "prerequisites": prerequisites_data
        }
        
        # Apply test limits to input if needed
        if self.test_mode:
            input_data = self._limit_input_data(input_data)
        
        # Format prompt
        prompt = PromptTemplates.PHASE_1_1_ARCHETYPE_EXTRACTION.format(
            input_data=PromptTemplates.format_input_data(input_data)
        )
        
        logger.info("Requesting node extraction from Gemini...")
        response = self.gemini.generate_json(prompt, temperature=0.1)
        
        # Save each category to separate files
        output_files = []
        categories = ["AI_ARCHETYPE", "COMMON_MODEL", "AI_OUTPUT", "AI_PREREQUISITE"]
        
        for category in categories:
            if category in response:
                nodes = response[category]
                filename = f"{category}_NODES.json"
                file_path = self.phase_output_dir / filename
                save_json(nodes, file_path)
                output_files.append(str(file_path))
                logger.info(f"✓ Saved {len(nodes)} {category} nodes")
            else:
                logger.warning(f"✗ Missing category in response: {category}")
        
        # Also extract PROBLEM_TYPE nodes for chunking
        self._extract_problem_nodes()
        
        return output_files
    
    def _extract_problem_nodes(self) -> None:
        """Extract problem type nodes from discovery data."""
        # For now, create a simple set of problem types
        # These would ideally come from the source data
        problem_types = [
            {
                "id": "PROBLEM_001",
                "name": "Quality or reliability gap",
                "node_type": "PROBLEM_TYPE",
                "description": "Issues with product/service quality or system reliability"
            },
            {
                "id": "PROBLEM_002",
                "name": "Efficiency or cost gap",
                "node_type": "PROBLEM_TYPE",
                "description": "Suboptimal resource utilization or excessive costs"
            },
            {
                "id": "PROBLEM_003",
                "name": "Customer experience gap",
                "node_type": "PROBLEM_TYPE",
                "description": "Poor customer satisfaction or engagement"
            },
            {
                "id": "PROBLEM_004",
                "name": "Risk or compliance gap",
                "node_type": "PROBLEM_TYPE",
                "description": "Exposure to risks or regulatory non-compliance"
            },
            {
                "id": "PROBLEM_005",
                "name": "Innovation or growth gap",
                "node_type": "PROBLEM_TYPE",
                "description": "Lack of innovation or market growth opportunities"
            }
        ]
        
        file_path = self.phase_output_dir / "PROBLEM_NODES.json"
        save_json(problem_types, file_path)
        logger.info(f"✓ Created {len(problem_types)} PROBLEM_TYPE nodes")
    
    def _limit_input_data(self, data: Dict) -> Dict:
        """Apply test mode limits to input data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Limited data
        """
        limit = self.test_limits.get("nodes_per_category", 3)
        
        limited = {}
        for key, value in data.items():
            if isinstance(value, list):
                limited[key] = value[:limit]
            elif isinstance(value, dict):
                # Handle nested structures
                limited[key] = {}
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):
                        limited[key][subkey] = subvalue[:limit]
                    else:
                        limited[key][subkey] = subvalue
            else:
                limited[key] = value
        
        return limited
    
    def _generate_chunking_script(self) -> Path:
        """Generate the inference task chunking script.
        
        Returns:
            Path to generated script
        """
        prompt = PromptTemplates.PHASE_1_2_CHUNKING_SCRIPT.format(
            chunk_size=self.chunk_size
        )
        
        logger.info("Requesting chunking script from Gemini...")
        script_code = self.gemini.generate(prompt, temperature=0.1)
        
        # Clean up the response
        script_code = script_code.strip()
        if script_code.startswith("```python"):
            script_code = script_code[9:]
        if script_code.startswith("```"):
            script_code = script_code[3:]
        if script_code.endswith("```"):
            script_code = script_code[:-3]
        script_code = script_code.strip()
        
        # Save script
        script_path = self.phase_output_dir / "chunk_inference_tasks.py"
        with open(script_path, 'w') as f:
            f.write(script_code)
        
        logger.info(f"Script saved to {script_path}")
        return script_path
    
    def _execute_chunking_script(self, script_path: Path) -> List[str]:
        """Execute the chunking script.
        
        Args:
            script_path: Path to the script
            
        Returns:
            List of generated chunk files
        """
        logger.info(f"Executing {script_path}...")
        
        try:
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(self.phase_output_dir.parent.parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Script execution failed:\n{result.stderr}")
                raise RuntimeError(f"Script execution failed: {result.stderr}")
            
            logger.info(f"Script output:\n{result.stdout}")
            
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise
        
        # Find generated chunk files
        chunk_files = sorted(self.phase_output_dir.glob("INFERENCE_CHUNK_*.json"))
        
        logger.info(f"✓ Generated {len(chunk_files)} inference chunks")
        return [str(f) for f in chunk_files]
