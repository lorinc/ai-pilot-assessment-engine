"""Semantic deduplication using Vertex AI embeddings."""

import logging
import time
from typing import Any, Dict, List, Set, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SemanticDeduplicator:
    """Deduplicates nodes using semantic similarity."""
    
    def __init__(
        self,
        embedding_client,
        similarity_threshold: float = 0.85,
        batch_size: int = 100
    ):
        """Initialize deduplicator.
        
        Args:
            embedding_client: Vertex AI embedding client
            similarity_threshold: Similarity threshold for merging (0-1)
            batch_size: Number of texts to embed at once
        """
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
    
    def _get_node_text(self, node: Dict[str, Any]) -> str:
        """Extract text representation from node.
        
        Args:
            node: Node dictionary
            
        Returns:
            Text string for embedding
        """
        # Combine name and description if available
        parts = []
        
        if "name" in node:
            parts.append(node["name"])
        elif "label" in node:
            parts.append(node["label"])
        
        if "description" in node:
            parts.append(node["description"])
        
        if "context" in node:
            parts.append(node["context"])
        
        return " | ".join(parts) if parts else node.get("id", "")
    
    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts using Vertex AI.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Call Vertex AI embedding API
                embeddings = self.embedding_client.get_embeddings(batch)
                all_embeddings.extend(embeddings)
                
                # Rate limiting
                if i + self.batch_size < len(texts):
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to embed batch {i}-{i+len(batch)}: {e}")
                # Return zero vectors for failed batch
                all_embeddings.extend([np.zeros(768)] * len(batch))
        
        return np.array(all_embeddings)
    
    def _find_duplicates(
        self,
        nodes: List[Dict[str, Any]],
        embeddings: np.ndarray
    ) -> List[Set[int]]:
        """Find duplicate node groups based on similarity.
        
        Args:
            nodes: List of nodes
            embeddings: Embedding matrix
            
        Returns:
            List of sets, each containing indices of duplicate nodes
        """
        n = len(nodes)
        similarity_matrix = cosine_similarity(embeddings)
        
        # Track which nodes have been merged
        merged = set()
        duplicate_groups = []
        
        for i in range(n):
            if i in merged:
                continue
            
            # Find all nodes similar to node i
            similar_indices = set()
            for j in range(i + 1, n):
                if j in merged:
                    continue
                
                if similarity_matrix[i, j] >= self.similarity_threshold:
                    similar_indices.add(j)
            
            # If we found duplicates, create a group
            if similar_indices:
                group = {i} | similar_indices
                duplicate_groups.append(group)
                merged.update(group)
                
                logger.debug(
                    f"Found duplicate group of size {len(group)}: "
                    f"{[nodes[idx].get('name', nodes[idx].get('id')) for idx in group]}"
                )
        
        return duplicate_groups
    
    def _merge_nodes(
        self,
        nodes: List[Dict[str, Any]],
        duplicate_groups: List[Set[int]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Merge duplicate nodes.
        
        Args:
            nodes: Original node list
            duplicate_groups: Groups of duplicate node indices
            
        Returns:
            Tuple of (deduplicated nodes, ID mapping dict)
        """
        # Track which nodes to keep
        keep_indices = set(range(len(nodes)))
        id_mapping = {}  # old_id -> new_id
        
        for group in duplicate_groups:
            # Keep the first node in each group
            group_list = sorted(group)
            primary_idx = group_list[0]
            primary_node = nodes[primary_idx]
            primary_id = primary_node["id"]
            
            # Map all other nodes to the primary
            for idx in group_list[1:]:
                old_id = nodes[idx]["id"]
                id_mapping[old_id] = primary_id
                keep_indices.remove(idx)
                
                logger.debug(f"Merging {old_id} -> {primary_id}")
        
        # Create deduplicated list
        deduplicated = [nodes[i] for i in sorted(keep_indices)]
        
        logger.info(
            f"Deduplication: {len(nodes)} -> {len(deduplicated)} nodes "
            f"({len(nodes) - len(deduplicated)} merged)"
        )
        
        return deduplicated, id_mapping
    
    def deduplicate_nodes(
        self,
        nodes: List[Dict[str, Any]],
        node_type_filter: str = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Deduplicate nodes using semantic similarity.
        
        Args:
            nodes: List of node dictionaries
            node_type_filter: Only deduplicate nodes of this type (optional)
            
        Returns:
            Tuple of (deduplicated nodes, ID mapping dict)
        """
        if not nodes:
            return [], {}
        
        # Filter nodes if needed
        if node_type_filter:
            target_nodes = [n for n in nodes if n.get("node_type") == node_type_filter]
            other_nodes = [n for n in nodes if n.get("node_type") != node_type_filter]
            
            logger.info(
                f"Deduplicating {len(target_nodes)} nodes of type {node_type_filter}"
            )
        else:
            target_nodes = nodes
            other_nodes = []
        
        if not target_nodes:
            return nodes, {}
        
        # Extract text for embedding
        texts = [self._get_node_text(node) for node in target_nodes]
        
        logger.info(f"Generating embeddings for {len(texts)} nodes...")
        embeddings = self._embed_texts(texts)
        
        logger.info("Finding duplicates...")
        duplicate_groups = self._find_duplicates(target_nodes, embeddings)
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        
        # Merge duplicates
        deduplicated_target, id_mapping = self._merge_nodes(target_nodes, duplicate_groups)
        
        # Combine with other nodes
        final_nodes = deduplicated_target + other_nodes
        
        return final_nodes, id_mapping
    
    def update_edge_references(
        self,
        edges: List[Dict[str, Any]],
        id_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Update edge references after node deduplication.
        
        Args:
            edges: List of edge dictionaries
            id_mapping: Mapping of old node IDs to new node IDs
            
        Returns:
            Updated edge list
        """
        updated_edges = []
        removed_count = 0
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            
            # Update references
            new_source = id_mapping.get(source, source)
            new_target = id_mapping.get(target, target)
            
            # Skip self-loops created by merging
            if new_source == new_target:
                removed_count += 1
                continue
            
            # Create updated edge
            updated_edge = edge.copy()
            updated_edge["source"] = new_source
            updated_edge["target"] = new_target
            
            updated_edges.append(updated_edge)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} self-loop edges after deduplication")
        
        return updated_edges
