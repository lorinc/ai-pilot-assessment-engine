"""Checkpoint management for resumable processing."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .file_io import ensure_dir

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages processing checkpoints for resumable execution."""
    
    def __init__(self, checkpoint_file: Path):
        """Initialize checkpoint manager.
        
        Args:
            checkpoint_file: Path to checkpoint JSON file
        """
        self.checkpoint_file = Path(checkpoint_file)
        ensure_dir(self.checkpoint_file.parent)
        self.state: Dict[str, Any] = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load checkpoint from file.
        
        Returns:
            Checkpoint state dictionary
        """
        if not self.checkpoint_file.exists():
            logger.info("No existing checkpoint found, starting fresh")
            return self._create_initial_state()
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                state = json.load(f)
            logger.info(f"Loaded checkpoint from {self.checkpoint_file}")
            logger.info(f"Last phase completed: {state.get('last_completed_phase', 'None')}")
            return state
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            logger.warning("Starting with fresh checkpoint")
            return self._create_initial_state()
    
    def _create_initial_state(self) -> Dict[str, Any]:
        """Create initial checkpoint state.
        
        Returns:
            Initial state dictionary
        """
        return {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "last_completed_phase": None,
            "phase_0": {"completed": False, "files_generated": []},
            "phase_1": {"completed": False, "files_generated": []},
            "phase_2": {"completed": False, "files_generated": []},
            "phase_3": {
                "completed": False,
                "total_chunks": 0,
                "chunks_processed": 0,
                "chunks_completed": [],
                "final_graph_generated": False
            },
            "mode": None,
            "test_mode_limits": None,
            "errors": []
        }
    
    def save(self) -> None:
        """Save current state to checkpoint file."""
        self.state["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.debug(f"Checkpoint saved to {self.checkpoint_file}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def mark_phase_complete(self, phase: str, files_generated: Optional[list] = None) -> None:
        """Mark a phase as completed.
        
        Args:
            phase: Phase identifier (e.g., "0", "1", "2", "3")
            files_generated: List of output files generated
        """
        phase_key = f"phase_{phase}"
        
        if phase_key in self.state:
            self.state[phase_key]["completed"] = True
            if files_generated:
                self.state[phase_key]["files_generated"] = files_generated
        
        self.state["last_completed_phase"] = phase
        self.save()
        logger.info(f"Phase {phase} marked as complete")
    
    def is_phase_complete(self, phase: str) -> bool:
        """Check if a phase is completed.
        
        Args:
            phase: Phase identifier
            
        Returns:
            True if phase is complete
        """
        phase_key = f"phase_{phase}"
        return self.state.get(phase_key, {}).get("completed", False)
    
    def update_phase_3_progress(
        self,
        chunk_id: str,
        total_chunks: Optional[int] = None
    ) -> None:
        """Update Phase 3 chunk processing progress.
        
        Args:
            chunk_id: Chunk identifier that was processed
            total_chunks: Total number of chunks (optional)
        """
        phase_3 = self.state["phase_3"]
        
        if total_chunks is not None:
            phase_3["total_chunks"] = total_chunks
        
        if chunk_id not in phase_3["chunks_completed"]:
            phase_3["chunks_completed"].append(chunk_id)
            phase_3["chunks_processed"] = len(phase_3["chunks_completed"])
        
        self.save()
        logger.info(
            f"Phase 3 progress: {phase_3['chunks_processed']}/{phase_3['total_chunks']} chunks"
        )
    
    def get_phase_3_remaining_chunks(self, all_chunk_ids: list) -> list:
        """Get list of chunks that still need processing.
        
        Args:
            all_chunk_ids: List of all chunk identifiers
            
        Returns:
            List of chunk IDs not yet processed
        """
        completed = set(self.state["phase_3"]["chunks_completed"])
        remaining = [cid for cid in all_chunk_ids if cid not in completed]
        
        logger.info(f"Remaining chunks: {len(remaining)}/{len(all_chunk_ids)}")
        return remaining
    
    def add_error(self, phase: str, error_msg: str) -> None:
        """Record an error.
        
        Args:
            phase: Phase where error occurred
            error_msg: Error message
        """
        self.state["errors"].append({
            "phase": phase,
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def set_mode(self, mode: str, test_limits: Optional[Dict] = None) -> None:
        """Set processing mode.
        
        Args:
            mode: "test" or "full"
            test_limits: Test mode limits if applicable
        """
        self.state["mode"] = mode
        if test_limits:
            self.state["test_mode_limits"] = test_limits
        self.save()
    
    def reset(self) -> None:
        """Reset checkpoint to initial state."""
        self.state = self._create_initial_state()
        self.save()
        logger.info("Checkpoint reset to initial state")
    
    def get_summary(self) -> str:
        """Get human-readable checkpoint summary.
        
        Returns:
            Summary string
        """
        lines = [
            "=== Checkpoint Summary ===",
            f"Mode: {self.state.get('mode', 'Unknown')}",
            f"Last Updated: {self.state.get('last_updated', 'Unknown')}",
            f"Last Completed Phase: {self.state.get('last_completed_phase', 'None')}",
            "",
            "Phase Status:",
        ]
        
        for i in range(4):
            phase_key = f"phase_{i}"
            status = "✓" if self.state.get(phase_key, {}).get("completed", False) else "✗"
            lines.append(f"  Phase {i}: {status}")
        
        if self.state["phase_3"]["total_chunks"] > 0:
            p3 = self.state["phase_3"]
            lines.append(
                f"  Phase 3 Chunks: {p3['chunks_processed']}/{p3['total_chunks']}"
            )
        
        if self.state["errors"]:
            lines.append(f"\nErrors: {len(self.state['errors'])}")
        
        return "\n".join(lines)
