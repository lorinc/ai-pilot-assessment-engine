"""Tests for phase implementations."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from ..utils.file_io import load_json, save_json, ensure_dir
from ..utils.checkpoint import CheckpointManager
from ..utils.validation import validate_nodes, validate_edges


class TestFileIO:
    """Test file I/O utilities."""
    
    def test_ensure_dir(self, tmp_path):
        """Test directory creation."""
        test_dir = tmp_path / "test" / "nested"
        result = ensure_dir(test_dir)
        
        assert result.exists()
        assert result.is_dir()
    
    def test_save_and_load_json(self, tmp_path):
        """Test JSON save and load."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "list": [1, 2, 3]}
        
        save_json(test_data, test_file)
        loaded_data = load_json(test_file)
        
        assert loaded_data == test_data


class TestCheckpoint:
    """Test checkpoint manager."""
    
    def test_checkpoint_creation(self, tmp_path):
        """Test checkpoint initialization."""
        checkpoint_file = tmp_path / "checkpoint.json"
        manager = CheckpointManager(checkpoint_file)
        
        assert manager.state is not None
        assert "created_at" in manager.state
        assert checkpoint_file.exists()
    
    def test_mark_phase_complete(self, tmp_path):
        """Test marking phase as complete."""
        checkpoint_file = tmp_path / "checkpoint.json"
        manager = CheckpointManager(checkpoint_file)
        
        manager.mark_phase_complete("0", ["file1.json", "file2.json"])
        
        assert manager.is_phase_complete("0")
        assert manager.state["last_completed_phase"] == "0"
        assert manager.state["phase_0"]["files_generated"] == ["file1.json", "file2.json"]
    
    def test_phase_3_progress(self, tmp_path):
        """Test Phase 3 progress tracking."""
        checkpoint_file = tmp_path / "checkpoint.json"
        manager = CheckpointManager(checkpoint_file)
        
        manager.update_phase_3_progress("CHUNK_001", total_chunks=10)
        manager.update_phase_3_progress("CHUNK_002")
        
        assert manager.state["phase_3"]["total_chunks"] == 10
        assert manager.state["phase_3"]["chunks_processed"] == 2
        assert "CHUNK_001" in manager.state["phase_3"]["chunks_completed"]
        
        remaining = manager.get_phase_3_remaining_chunks(
            ["CHUNK_001", "CHUNK_002", "CHUNK_003"]
        )
        assert remaining == ["CHUNK_003"]


class TestValidation:
    """Test validation utilities."""
    
    def test_validate_nodes_valid(self):
        """Test node validation with valid data."""
        nodes = [
            {"id": "NODE_001", "node_type": "AI_ARCHETYPE", "name": "Test"},
            {"id": "NODE_002", "node_type": "COMMON_MODEL", "name": "Test Model"}
        ]
        
        report = validate_nodes(nodes)
        
        assert report["valid"]
        assert report["total_nodes"] == 2
        assert len(report["errors"]) == 0
    
    def test_validate_nodes_missing_id(self):
        """Test node validation with missing ID."""
        nodes = [
            {"node_type": "AI_ARCHETYPE", "name": "Test"}
        ]
        
        report = validate_nodes(nodes)
        
        assert not report["valid"]
        assert len(report["errors"]) > 0
    
    def test_validate_edges_valid(self):
        """Test edge validation with valid data."""
        edges = [
            {
                "source": "NODE_001",
                "target": "NODE_002",
                "edge_type": "IMPLEMENTED_BY"
            }
        ]
        
        valid_node_ids = {"NODE_001", "NODE_002"}
        report = validate_edges(edges, valid_node_ids)
        
        assert report["valid"]
        assert report["total_edges"] == 1
    
    def test_validate_edges_invalid_reference(self):
        """Test edge validation with invalid node reference."""
        edges = [
            {
                "source": "NODE_001",
                "target": "NODE_999",
                "edge_type": "IMPLEMENTED_BY"
            }
        ]
        
        valid_node_ids = {"NODE_001", "NODE_002"}
        report = validate_edges(edges, valid_node_ids)
        
        assert not report["valid"]
        assert len(report["errors"]) > 0


class TestGeminiClient:
    """Test Gemini client (mocked)."""
    
    def test_generate_text(self):
        """Test text generation."""
        # This would require mocking Vertex AI
        # For now, just test the interface
        pass
    
    def test_generate_json(self):
        """Test JSON generation."""
        # This would require mocking Vertex AI
        pass


# Integration test placeholder
class TestIntegration:
    """Integration tests for full pipeline."""
    
    @pytest.mark.skip(reason="Requires Vertex AI credentials")
    def test_full_pipeline(self):
        """Test complete pipeline execution."""
        # This would run the full pipeline in test mode
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
