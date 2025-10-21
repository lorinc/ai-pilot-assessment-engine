"""Orchestrator for coordinating all phases."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .gemini.client import GeminiClient
from .phases import (
    Phase0Preprocessing,
    Phase1Extraction,
    Phase2EdgeGeneration,
    Phase3Inference
)
from .utils.checkpoint import CheckpointManager
from .utils.validation import validate_knowledge_graph, print_validation_report

logger = logging.getLogger(__name__)


class EnrichmentOrchestrator:
    """Coordinates execution of all enrichment phases."""
    
    def __init__(self, config: Dict):
        """Initialize orchestrator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Setup paths
        self.input_dir = Path(config["paths"]["input_data"])
        self.output_dir = Path(config["paths"]["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize checkpoint manager
        checkpoint_file = Path(config["paths"]["checkpoint_file"])
        self.checkpoint = CheckpointManager(checkpoint_file)
        
        # Set mode
        self.mode = config["mode"]
        self.test_mode = (self.mode == "test")
        
        if self.test_mode:
            test_limits = config.get("test_mode", {})
            self.checkpoint.set_mode("test", test_limits)
            logger.info(f"Running in TEST mode (limit: {test_limits.get('nodes_per_category', 3)} nodes per category)")
        else:
            self.checkpoint.set_mode("full")
            logger.info("Running in FULL mode")
        
        # Initialize Gemini client
        gemini_config = config["gemini"]
        self.gemini = GeminiClient(
            model_name=gemini_config["model"],
            temperature=gemini_config["temperature"],
            max_output_tokens=gemini_config["max_output_tokens"],
            location=gemini_config["location"]
        )
        
        # Initialize phases
        self.phases = self._initialize_phases()
    
    def _initialize_phases(self) -> Dict:
        """Initialize all phase handlers.
        
        Returns:
            Dictionary of phase handlers
        """
        test_limits = self.config.get("test_mode", {})
        
        return {
            "0": Phase0Preprocessing(
                gemini_client=self.gemini,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
                test_mode=self.test_mode,
                test_limits=test_limits
            ),
            "1": Phase1Extraction(
                gemini_client=self.gemini,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
                test_mode=self.test_mode,
                test_limits=test_limits,
                chunk_size=self.config["chunking"]["inference_chunk_size"]
            ),
            "2": Phase2EdgeGeneration(
                gemini_client=self.gemini,
                input_dir=self.input_dir,
                output_dir=self.output_dir,
                test_mode=self.test_mode
            ),
            "3": Phase3Inference(
                gemini_client=self.gemini,
                output_dir=self.output_dir,
                checkpoint_manager=self.checkpoint,
                similarity_threshold=self.config["deduplication"]["similarity_threshold"],
                test_mode=self.test_mode
            )
        }
    
    def run_phase(self, phase_id: str, force: bool = False) -> List[str]:
        """Run a single phase.
        
        Args:
            phase_id: Phase identifier ("0", "1", "2", "3")
            force: Force re-run even if already completed
            
        Returns:
            List of generated files
        """
        if phase_id not in self.phases:
            raise ValueError(f"Invalid phase ID: {phase_id}")
        
        # Check if already completed
        if not force and self.checkpoint.is_phase_complete(phase_id):
            logger.info(f"Phase {phase_id} already completed (use --force to re-run)")
            return []
        
        # Run phase
        phase = self.phases[phase_id]
        generated_files = phase.run()
        
        # Mark as complete
        self.checkpoint.mark_phase_complete(phase_id, generated_files)
        
        return generated_files
    
    def run_all(self, start_phase: str = "0", force: bool = False) -> None:
        """Run all phases sequentially.
        
        Args:
            start_phase: Phase to start from
            force: Force re-run of all phases
        """
        logger.info("\n" + "=" * 60)
        logger.info("KNOWLEDGE BASE ENRICHMENT - FULL PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Mode: {self.mode.upper()}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info("=" * 60 + "\n")
        
        # Show checkpoint summary
        if not force:
            logger.info(self.checkpoint.get_summary())
            logger.info("")
        
        # Run phases
        phase_ids = ["0", "1", "2", "3"]
        start_idx = phase_ids.index(start_phase)
        
        for phase_id in phase_ids[start_idx:]:
            try:
                self.run_phase(phase_id, force=force)
            except Exception as e:
                logger.error(f"Phase {phase_id} failed: {e}")
                self.checkpoint.add_error(phase_id, str(e))
                raise
        
        # Final summary
        self._print_final_summary()
    
    def run_phases(self, phase_range: str, force: bool = False) -> None:
        """Run a range of phases.
        
        Args:
            phase_range: Phase range (e.g., "0-2", "1-3")
            force: Force re-run
        """
        if "-" in phase_range:
            start, end = phase_range.split("-")
            phase_ids = [str(i) for i in range(int(start), int(end) + 1)]
        else:
            phase_ids = [phase_range]
        
        for phase_id in phase_ids:
            self.run_phase(phase_id, force=force)
        
        self._print_final_summary()
    
    def validate_output(self) -> None:
        """Validate the final knowledge graph."""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATING FINAL KNOWLEDGE GRAPH")
        logger.info("=" * 60 + "\n")
        
        final_graph_file = self.output_dir / "phase_3" / "E1S1_Knowledge_Graph_v1.0.json"
        
        if not final_graph_file.exists():
            logger.error(f"Final graph not found: {final_graph_file}")
            return
        
        from .utils.file_io import load_json
        
        graph_data = load_json(final_graph_file)
        report = validate_knowledge_graph(graph_data, strict=False)
        
        print_validation_report(report)
        
        if report["valid"]:
            logger.info("✓ Validation PASSED")
        else:
            logger.warning("✗ Validation FAILED - see errors above")
    
    def _print_final_summary(self) -> None:
        """Print final execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("ENRICHMENT COMPLETE")
        logger.info("=" * 60)
        
        # Checkpoint summary
        logger.info("\n" + self.checkpoint.get_summary())
        
        # API usage
        logger.info("\n" + self.gemini.get_usage_summary())
        
        # Output location
        final_graph = self.output_dir / "phase_3" / "E1S1_Knowledge_Graph_v1.0.json"
        if final_graph.exists():
            logger.info(f"\n✓ Final Knowledge Graph: {final_graph}")
            
            from .utils.file_io import get_file_size
            logger.info(f"  File Size: {get_file_size(final_graph)}")
        
        logger.info("\n" + "=" * 60)
    
    def clean_output(self) -> None:
        """Clean output directory."""
        import shutil
        
        if self.output_dir.exists():
            logger.info(f"Cleaning output directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info("✓ Output directory cleaned")
        
        # Reset checkpoint
        self.checkpoint.reset()
        logger.info("✓ Checkpoint reset")
