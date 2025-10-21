"""Phase 3: LLM enrichment and inference."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from ..gemini.client import GeminiClient
from ..gemini.prompts import PromptTemplates
from ..utils.file_io import load_json, save_json, ensure_dir
from ..utils.deduplication import SemanticDeduplicator
from ..utils.checkpoint import CheckpointManager

logger = logging.getLogger(__name__)


class Phase3Inference:
    """Phase 3: LLM-based pain inference and final assembly."""
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        output_dir: Path,
        checkpoint_manager: CheckpointManager,
        similarity_threshold: float = 0.85,
        test_mode: bool = False
    ):
        """Initialize Phase 3.
        
        Args:
            gemini_client: Gemini API client
            output_dir: Output directory
            checkpoint_manager: Checkpoint manager for resumable processing
            similarity_threshold: Similarity threshold for deduplication
            test_mode: Whether to run in test mode
        """
        self.gemini = gemini_client
        self.output_dir = Path(output_dir)
        self.checkpoint = checkpoint_manager
        self.similarity_threshold = similarity_threshold
        self.test_mode = test_mode
        
        self.phase_output_dir = self.output_dir / "phase_3"
        ensure_dir(self.phase_output_dir)
        
        # Initialize deduplicator
        self.deduplicator = SemanticDeduplicator(
            embedding_client=gemini_client,
            similarity_threshold=similarity_threshold
        )
    
    def run(self) -> List[str]:
        """Execute Phase 3.
        
        Returns:
            List of generated file paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 3: LLM ENRICHMENT AND INFERENCE")
        logger.info("=" * 60)
        
        generated_files = []
        
        # Task 3.1: Granular pain node and mitigation inference (iterative)
        logger.info("\n[Task 3.1] Processing inference chunks...")
        chunk_output_files = self._process_inference_chunks()
        generated_files.extend(chunk_output_files)
        
        # Task 3.2: Final knowledge graph assembly and deduplication
        logger.info("\n[Task 3.2] Assembling final knowledge graph...")
        final_graph_file = self._assemble_final_graph()
        generated_files.append(final_graph_file)
        
        logger.info(f"\n✓ Phase 3 complete. Generated {len(generated_files)} files.")
        return generated_files
    
    def _process_inference_chunks(self) -> List[str]:
        """Process all inference chunks iteratively.
        
        Returns:
            List of chunk output files
        """
        # Find all chunk files
        phase_1_dir = self.output_dir / "phase_1"
        chunk_files = sorted(phase_1_dir.glob("INFERENCE_CHUNK_*.json"))
        
        if not chunk_files:
            logger.warning("No inference chunk files found!")
            return []
        
        logger.info(f"Found {len(chunk_files)} inference chunks to process")
        
        # Get remaining chunks (for resumption)
        all_chunk_ids = [f.stem for f in chunk_files]
        remaining_chunk_ids = self.checkpoint.get_phase_3_remaining_chunks(all_chunk_ids)
        
        if not remaining_chunk_ids:
            logger.info("All chunks already processed (resuming from checkpoint)")
            return [str(self.phase_output_dir / f"{cid}.json") for cid in all_chunk_ids]
        
        logger.info(f"Processing {len(remaining_chunk_ids)} remaining chunks...")
        
        # Update checkpoint with total
        self.checkpoint.update_phase_3_progress(
            chunk_id=None,
            total_chunks=len(chunk_files)
        )
        
        output_files = []
        
        # Process each chunk
        for chunk_file in tqdm(chunk_files, desc="Processing chunks"):
            chunk_id = chunk_file.stem
            
            # Skip if already processed
            if chunk_id not in remaining_chunk_ids:
                logger.debug(f"Skipping already processed chunk: {chunk_id}")
                continue
            
            try:
                # Load chunk
                chunk_data = load_json(chunk_file)
                
                # Process chunk
                logger.info(f"\nProcessing {chunk_id} ({len(chunk_data)} triplets)...")
                result = self._process_single_chunk(chunk_data, chunk_id)
                
                # Save result
                output_file = self.phase_output_dir / f"INFERENCE_OUTPUT_{chunk_id}.json"
                save_json(result, output_file)
                output_files.append(str(output_file))
                
                # Update checkpoint
                self.checkpoint.update_phase_3_progress(chunk_id)
                
                logger.info(f"✓ Processed {chunk_id}: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges")
                
            except Exception as e:
                logger.error(f"Failed to process {chunk_id}: {e}")
                self.checkpoint.add_error("3.1", f"Chunk {chunk_id}: {str(e)}")
                
                if not self.test_mode:
                    raise
        
        return output_files
    
    def _process_single_chunk(self, chunk_data: List[Dict], chunk_id: str) -> Dict[str, Any]:
        """Process a single inference chunk.
        
        Args:
            chunk_data: List of triplet dictionaries
            chunk_id: Chunk identifier
            
        Returns:
            Dictionary with 'nodes' and 'edges' arrays
        """
        # Format prompt
        prompt = PromptTemplates.PHASE_3_1_PAIN_INFERENCE.format(
            chunk_data=PromptTemplates.format_chunk_data(chunk_data)
        )
        
        # Generate inference
        result = self.gemini.generate_json(prompt, temperature=0.3)
        
        # Validate structure
        if "nodes" not in result or "edges" not in result:
            logger.warning(f"Invalid response structure for {chunk_id}, attempting to fix...")
            if isinstance(result, list):
                # Sometimes the model returns just a list
                result = {"nodes": result, "edges": []}
        
        return result
    
    def _assemble_final_graph(self) -> str:
        """Assemble and deduplicate the final knowledge graph.
        
        Returns:
            Path to final graph file
        """
        logger.info("Collecting all nodes and edges...")
        
        all_nodes = []
        all_edges = []
        
        # Collect nodes from Phase 0
        phase_0_dir = self.output_dir / "phase_0"
        for node_file in phase_0_dir.glob("*_NODES.json"):
            nodes = load_json(node_file)
            all_nodes.extend(nodes)
            logger.info(f"  Loaded {len(nodes)} nodes from {node_file.name}")
        
        # Collect nodes from Phase 1
        phase_1_dir = self.output_dir / "phase_1"
        for node_file in phase_1_dir.glob("*_NODES.json"):
            nodes = load_json(node_file)
            all_nodes.extend(nodes)
            logger.info(f"  Loaded {len(nodes)} nodes from {node_file.name}")
        
        # Collect edges from Phase 2
        phase_2_dir = self.output_dir / "phase_2"
        for edge_file in phase_2_dir.glob("*_EDGES.json"):
            edges = load_json(edge_file)
            all_edges.extend(edges)
            logger.info(f"  Loaded {len(edges)} edges from {edge_file.name}")
        
        # Collect nodes and edges from Phase 3 chunks
        for chunk_output in self.phase_output_dir.glob("INFERENCE_OUTPUT_*.json"):
            data = load_json(chunk_output)
            if "nodes" in data:
                all_nodes.extend(data["nodes"])
            if "edges" in data:
                all_edges.extend(data["edges"])
        
        logger.info(f"\nTotal before deduplication: {len(all_nodes)} nodes, {len(all_edges)} edges")
        
        # Deduplicate M1 nodes
        logger.info("\nDeduplicating OPERATIONAL_PAIN_POINT (M1) nodes...")
        all_nodes, m1_mapping = self.deduplicator.deduplicate_nodes(
            all_nodes,
            node_type_filter="OPERATIONAL_PAIN_POINT"
        )
        
        # Deduplicate M2 nodes
        logger.info("\nDeduplicating MEASURABLE_FAILURE_MODE (M2) nodes...")
        all_nodes, m2_mapping = self.deduplicator.deduplicate_nodes(
            all_nodes,
            node_type_filter="MEASURABLE_FAILURE_MODE"
        )
        
        # Combine mappings
        id_mapping = {**m1_mapping, **m2_mapping}
        
        # Update edge references
        if id_mapping:
            logger.info(f"\nUpdating edge references ({len(id_mapping)} merged nodes)...")
            all_edges = self.deduplicator.update_edge_references(all_edges, id_mapping)
        
        # Remove duplicate edges
        all_edges = self._deduplicate_edges(all_edges)
        
        logger.info(f"\nTotal after deduplication: {len(all_nodes)} nodes, {len(all_edges)} edges")
        
        # Generate metadata
        metadata = self._generate_metadata(all_nodes, all_edges)
        
        # Assemble final graph
        final_graph = {
            "metadata": metadata,
            "nodes": all_nodes,
            "edges": all_edges
        }
        
        # Save final graph
        output_file = self.phase_output_dir / "E1S1_Knowledge_Graph_v1.0.json"
        save_json(final_graph, output_file)
        
        logger.info(f"\n✓ Final knowledge graph saved to {output_file}")
        
        # Mark as complete in checkpoint
        self.checkpoint.state["phase_3"]["final_graph_generated"] = True
        self.checkpoint.save()
        
        return str(output_file)
    
    def _deduplicate_edges(self, edges: List[Dict]) -> List[Dict]:
        """Remove duplicate edges.
        
        Args:
            edges: List of edge dictionaries
            
        Returns:
            Deduplicated edge list
        """
        seen = set()
        unique_edges = []
        
        for edge in edges:
            # Create edge signature
            sig = (
                edge.get("source"),
                edge.get("target"),
                edge.get("edge_type")
            )
            
            if sig not in seen:
                seen.add(sig)
                unique_edges.append(edge)
        
        removed = len(edges) - len(unique_edges)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate edges")
        
        return unique_edges
    
    def _generate_metadata(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Generate metadata for the final graph.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            
        Returns:
            Metadata dictionary
        """
        # Count node types
        node_type_counts = {}
        for node in nodes:
            node_type = node.get("node_type", "UNKNOWN")
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        # Count edge types
        edge_type_counts = {}
        for edge in edges:
            edge_type = edge.get("edge_type", "UNKNOWN")
            edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
        
        return {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_type_counts": node_type_counts,
            "edge_type_counts": edge_type_counts,
            "test_mode": self.test_mode,
            "similarity_threshold": self.similarity_threshold
        }
