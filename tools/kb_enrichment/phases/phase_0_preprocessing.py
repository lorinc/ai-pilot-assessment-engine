"""Phase 0: Pre-processing and script generation."""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from ..gemini.client import GeminiClient
from ..gemini.prompts import PromptTemplates
from ..utils.file_io import load_json, save_json, ensure_dir

logger = logging.getLogger(__name__)


class Phase0Preprocessing:
    """Phase 0: Node explosion and preprocessing."""
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        input_dir: Path,
        output_dir: Path,
        test_mode: bool = False,
        test_limits: Dict[str, int] = None
    ):
        """Initialize Phase 0.
        
        Args:
            gemini_client: Gemini API client
            input_dir: Input data directory
            output_dir: Output directory
            test_mode: Whether to run in test mode
            test_limits: Test mode node limits
        """
        self.gemini = gemini_client
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.test_mode = test_mode
        self.test_limits = test_limits or {}
        
        self.phase_output_dir = self.output_dir / "phase_0"
        ensure_dir(self.phase_output_dir)
    
    def run(self) -> List[str]:
        """Execute Phase 0.
        
        Returns:
            List of generated file paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 0: PRE-PROCESSING AND SCRIPT GENERATION")
        logger.info("=" * 60)
        
        generated_files = []
        
        # Task 0.1: Generate explosion script
        logger.info("\n[Task 0.1] Generating node explosion script...")
        script_path = self._generate_explosion_script()
        logger.info(f"✓ Script generated: {script_path}")
        
        # Task 0.2: Execute script
        logger.info("\n[Task 0.2] Executing node explosion...")
        output_files = self._execute_explosion_script(script_path)
        generated_files.extend(output_files)
        
        logger.info(f"\n✓ Phase 0 complete. Generated {len(generated_files)} files.")
        return generated_files
    
    def _generate_explosion_script(self) -> Path:
        """Generate the node explosion script using Gemini.
        
        Returns:
            Path to generated script
        """
        prompt = PromptTemplates.PHASE_0_1_SCRIPT_GENERATION
        
        logger.info("Requesting script from Gemini...")
        script_code = self.gemini.generate(prompt, temperature=0.1)
        
        # Clean up the response (remove markdown if present)
        script_code = script_code.strip()
        if script_code.startswith("```python"):
            script_code = script_code[9:]
        if script_code.startswith("```"):
            script_code = script_code[3:]
        if script_code.endswith("```"):
            script_code = script_code[:-3]
        script_code = script_code.strip()
        
        # Save script
        script_path = self.phase_output_dir / "explode_discovery.py"
        with open(script_path, 'w') as f:
            f.write(script_code)
        
        logger.info(f"Script saved to {script_path}")
        return script_path
    
    def _execute_explosion_script(self, script_path: Path) -> List[str]:
        """Execute the generated explosion script.
        
        Args:
            script_path: Path to the script
            
        Returns:
            List of generated output files
        """
        logger.info(f"Executing {script_path}...")
        
        try:
            # Run the script
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(self.phase_output_dir.parent.parent),  # Run from tool root
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Script execution failed:\n{result.stderr}")
                raise RuntimeError(f"Script execution failed: {result.stderr}")
            
            logger.info(f"Script output:\n{result.stdout}")
            
        except subprocess.TimeoutExpired:
            logger.error("Script execution timed out")
            raise
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise
        
        # Check for expected output files
        expected_files = [
            "FUNCTION_NODES.json",
            "SECTOR_NODES.json",
            "TOOL_NODES.json"
        ]
        
        output_files = []
        for filename in expected_files:
            file_path = self.phase_output_dir / filename
            if file_path.exists():
                logger.info(f"✓ Generated: {filename}")
                output_files.append(str(file_path))
                
                # Apply test mode limits if needed
                if self.test_mode:
                    self._apply_test_limits(file_path)
            else:
                logger.warning(f"✗ Missing expected file: {filename}")
        
        return output_files
    
    def _apply_test_limits(self, file_path: Path) -> None:
        """Apply test mode limits to a node file.
        
        Args:
            file_path: Path to node file
        """
        limit = self.test_limits.get("nodes_per_category", 3)
        
        try:
            data = load_json(file_path)
            
            if isinstance(data, list) and len(data) > limit:
                original_count = len(data)
                data = data[:limit]
                save_json(data, file_path)
                logger.info(f"  Applied test limit: {original_count} → {limit} nodes")
        
        except Exception as e:
            logger.warning(f"Failed to apply test limits to {file_path}: {e}")
