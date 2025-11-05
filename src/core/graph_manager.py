"""Graph management with NetworkX in-memory operations and Firestore persistence."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import networkx as nx

from core.firebase_client import FirebaseClient
from utils.logger import TechnicalLogger


class GraphManager:
    """
    Manages assessment graph with hybrid storage:
    - NetworkX for fast in-memory operations
    - Firestore for persistence across sessions
    """
    
    def __init__(
        self,
        firebase_client: Optional[FirebaseClient] = None,
        user_id: Optional[str] = None,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize graph manager.
        
        Args:
            firebase_client: Firebase client for persistence
            user_id: Current user ID
            logger: Technical logger instance
        """
        self.firebase = firebase_client
        self.user_id = user_id
        self.logger = logger
        self.graph = nx.DiGraph()  # Directed graph for edge directionality
        self.graph_id = None
        self.metadata = {}
    
    # ========== Load/Save Operations ==========
    
    def load_graph(self, graph_id: str) -> bool:
        """
        Load graph from Firestore into NetworkX.
        
        Args:
            graph_id: Graph ID to load
            
        Returns:
            True if loaded successfully
        """
        if not self.firebase or not self.user_id:
            if self.logger:
                self.logger.warning("graph_load", "Cannot load: no Firebase or user_id")
            return False
        
        try:
            # Load metadata
            metadata = self.firebase.get_graph_metadata(self.user_id, graph_id)
            if not metadata:
                if self.logger:
                    self.logger.warning("graph_load", f"Graph {graph_id} not found")
                return False
            
            self.graph_id = graph_id
            self.metadata = metadata
            
            # Load nodes
            nodes = self.firebase.get_graph_nodes(self.user_id, graph_id)
            for node_id, node_data in nodes.items():
                self.graph.add_node(node_id, **node_data)
            
            # Load edges
            edges = self.firebase.get_graph_edges(self.user_id, graph_id)
            for edge_id, edge_data in edges.items():
                source_id = edge_data.pop('source_id')
                target_id = edge_data.pop('target_id')
                self.graph.add_edge(source_id, target_id, edge_id=edge_id, **edge_data)
            
            if self.logger:
                self.logger.info("graph_load", f"Graph loaded: {graph_id}", {
                    "graph_id": graph_id,
                    "node_count": self.graph.number_of_nodes(),
                    "edge_count": self.graph.number_of_edges()
                })
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_load", f"Failed to load graph: {str(e)}")
            return False
    
    def save_graph(self) -> bool:
        """
        Save current graph to Firestore.
        
        Returns:
            True if saved successfully
        """
        if not self.firebase or not self.user_id or not self.graph_id:
            if self.logger:
                self.logger.warning("graph_save", "Cannot save: missing Firebase, user_id, or graph_id")
            return False
        
        try:
            # Update metadata timestamp
            self.metadata['updated_at'] = datetime.utcnow().isoformat() + "Z"
            
            # Save metadata
            self.firebase.save_graph_metadata(self.user_id, self.graph_id, self.metadata)
            
            # Save nodes
            for node_id in self.graph.nodes():
                node_data = dict(self.graph.nodes[node_id])
                self.firebase.save_graph_node(self.user_id, self.graph_id, node_id, node_data)
            
            # Save edges
            for source_id, target_id, edge_data in self.graph.edges(data=True):
                edge_id = edge_data.get('edge_id', f"{source_id}_to_{target_id}")
                edge_dict = dict(edge_data)
                edge_dict['source_id'] = source_id
                edge_dict['target_id'] = target_id
                self.firebase.save_graph_edge(self.user_id, self.graph_id, edge_id, edge_dict)
            
            if self.logger:
                self.logger.info("graph_save", f"Graph saved: {self.graph_id}", {
                    "graph_id": self.graph_id,
                    "node_count": self.graph.number_of_nodes(),
                    "edge_count": self.graph.number_of_edges()
                })
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_save", f"Failed to save graph: {str(e)}")
            return False
    
    def create_graph(self, output_id: str, output_name: str) -> str:
        """
        Create new graph for an output assessment.
        
        Args:
            output_id: Primary output being assessed
            output_name: Output name
            
        Returns:
            Graph ID
        """
        self.graph_id = f"graph_{uuid.uuid4().hex[:12]}"
        self.metadata = {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "output_id": output_id,
            "output_name": output_name
        }
        
        # Initialize empty graph
        self.graph = nx.DiGraph()
        
        if self.logger:
            self.logger.info("graph_create", f"Graph created: {self.graph_id}", {
                "graph_id": self.graph_id,
                "output_id": output_id
            })
        
        return self.graph_id
    
    # ========== Node Operations ==========
    
    def add_node(self, node_id: str, node_type: str, **attributes) -> bool:
        """
        Add node to graph.
        
        Args:
            node_id: Unique node identifier
            node_type: Node type (output, tool, process, people)
            **attributes: Additional node attributes
            
        Returns:
            True if added successfully
        """
        try:
            attributes['node_type'] = node_type
            attributes['created_at'] = datetime.utcnow().isoformat() + "Z"
            
            self.graph.add_node(node_id, **attributes)
            
            if self.logger:
                self.logger.info("graph_node_add", f"Node added: {node_id}", {
                    "node_id": node_id,
                    "node_type": node_type
                })
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                self.firebase.save_graph_node(self.user_id, self.graph_id, node_id, attributes)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_node_add", f"Failed to add node: {str(e)}")
            return False
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove node from graph.
        
        Args:
            node_id: Node to remove
            
        Returns:
            True if removed successfully
        """
        try:
            if node_id not in self.graph:
                return False
            
            self.graph.remove_node(node_id)
            
            if self.logger:
                self.logger.info("graph_node_remove", f"Node removed: {node_id}")
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                self.firebase.delete_graph_node(self.user_id, self.graph_id, node_id)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_node_remove", f"Failed to remove node: {str(e)}")
            return False
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get node data.
        
        Args:
            node_id: Node to retrieve
            
        Returns:
            Node data dict or None
        """
        if node_id not in self.graph:
            return None
        return dict(self.graph.nodes[node_id])
    
    def update_node(self, node_id: str, **attributes) -> bool:
        """
        Update node attributes.
        
        Args:
            node_id: Node to update
            **attributes: Attributes to update
            
        Returns:
            True if updated successfully
        """
        try:
            if node_id not in self.graph:
                return False
            
            self.graph.nodes[node_id].update(attributes)
            
            if self.logger:
                self.logger.info("graph_node_update", f"Node updated: {node_id}")
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                node_data = dict(self.graph.nodes[node_id])
                self.firebase.save_graph_node(self.user_id, self.graph_id, node_id, node_data)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_node_update", f"Failed to update node: {str(e)}")
            return False
    
    # ========== Edge Operations ==========
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        score: Optional[float] = None,
        confidence: float = 0.0,
        **attributes
    ) -> bool:
        """
        Add edge to graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Edge type (team_execution, system_capabilities, process_maturity, dependency_quality)
            score: Current score (1-5 stars)
            confidence: Confidence level (0.0-1.0)
            **attributes: Additional edge attributes
            
        Returns:
            True if added successfully
        """
        try:
            edge_id = f"{source_id}_to_{target_id}"
            
            attributes['edge_id'] = edge_id
            attributes['edge_type'] = edge_type
            attributes['current_score'] = score
            attributes['current_confidence'] = confidence
            attributes['evidence'] = attributes.get('evidence', [])
            attributes['created_at'] = datetime.utcnow().isoformat() + "Z"
            
            self.graph.add_edge(source_id, target_id, **attributes)
            
            if self.logger:
                self.logger.info("graph_edge_add", f"Edge added: {edge_id}", {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "score": score
                })
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                edge_dict = dict(attributes)
                edge_dict['source_id'] = source_id
                edge_dict['target_id'] = target_id
                self.firebase.save_graph_edge(self.user_id, self.graph_id, edge_id, edge_dict)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_edge_add", f"Failed to add edge: {str(e)}")
            return False
    
    def remove_edge(self, source_id: str, target_id: str) -> bool:
        """
        Remove edge from graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if removed successfully
        """
        try:
            if not self.graph.has_edge(source_id, target_id):
                return False
            
            edge_id = f"{source_id}_to_{target_id}"
            self.graph.remove_edge(source_id, target_id)
            
            if self.logger:
                self.logger.info("graph_edge_remove", f"Edge removed: {edge_id}")
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                self.firebase.delete_graph_edge(self.user_id, self.graph_id, edge_id)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_edge_remove", f"Failed to remove edge: {str(e)}")
            return False
    
    def get_edge(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Edge data dict or None
        """
        if not self.graph.has_edge(source_id, target_id):
            return None
        return dict(self.graph[source_id][target_id])
    
    def update_edge_rating(
        self,
        source_id: str,
        target_id: str,
        score: float,
        confidence: float
    ) -> bool:
        """
        Update edge rating.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            score: New score (1-5)
            confidence: New confidence (0.0-1.0)
            
        Returns:
            True if updated successfully
        """
        try:
            if not self.graph.has_edge(source_id, target_id):
                return False
            
            self.graph[source_id][target_id]['current_score'] = score
            self.graph[source_id][target_id]['current_confidence'] = confidence
            self.graph[source_id][target_id]['updated_at'] = datetime.utcnow().isoformat() + "Z"
            
            if self.logger:
                self.logger.info("graph_edge_update", f"Edge rating updated: {source_id} -> {target_id}", {
                    "score": score,
                    "confidence": confidence
                })
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                edge_id = f"{source_id}_to_{target_id}"
                edge_dict = dict(self.graph[source_id][target_id])
                edge_dict['source_id'] = source_id
                edge_dict['target_id'] = target_id
                self.firebase.save_graph_edge(self.user_id, self.graph_id, edge_id, edge_dict)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_edge_update", f"Failed to update edge rating: {str(e)}")
            return False
    
    def add_evidence(
        self,
        source_id: str,
        target_id: str,
        statement: str,
        tier: int,
        conversation_id: str
    ) -> bool:
        """
        Add evidence to edge.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            statement: User statement (evidence)
            tier: Evidence tier (1-5)
            conversation_id: Conversation ID
            
        Returns:
            True if added successfully
        """
        try:
            if not self.graph.has_edge(source_id, target_id):
                return False
            
            evidence_entry = {
                "statement": statement,
                "tier": tier,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_id": conversation_id
            }
            
            self.graph[source_id][target_id]['evidence'].append(evidence_entry)
            
            if self.logger:
                self.logger.info("graph_evidence_add", f"Evidence added: {source_id} -> {target_id}", {
                    "tier": tier
                })
            
            # Auto-save to Firestore
            if self.firebase and self.user_id and self.graph_id:
                edge_id = f"{source_id}_to_{target_id}"
                edge_dict = dict(self.graph[source_id][target_id])
                edge_dict['source_id'] = source_id
                edge_dict['target_id'] = target_id
                self.firebase.save_graph_edge(self.user_id, self.graph_id, edge_id, edge_dict)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error("graph_evidence_add", f"Failed to add evidence: {str(e)}")
            return False
    
    # ========== Graph Queries ==========
    
    def get_incoming_edges(self, node_id: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Get all incoming edges to a node.
        
        Args:
            node_id: Target node ID
            
        Returns:
            List of (source_id, target_id, edge_data) tuples
        """
        if node_id not in self.graph:
            return []
        
        edges = []
        for source_id in self.graph.predecessors(node_id):
            edge_data = dict(self.graph[source_id][node_id])
            edges.append((source_id, node_id, edge_data))
        
        return edges
    
    def get_outgoing_edges(self, node_id: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Get all outgoing edges from a node.
        
        Args:
            node_id: Source node ID
            
        Returns:
            List of (source_id, target_id, edge_data) tuples
        """
        if node_id not in self.graph:
            return []
        
        edges = []
        for target_id in self.graph.successors(node_id):
            edge_data = dict(self.graph[node_id][target_id])
            edges.append((node_id, target_id, edge_data))
        
        return edges
    
    def calculate_output_quality(self, output_id: str) -> Optional[float]:
        """
        Calculate output quality using MIN of incoming edge scores.
        
        Args:
            output_id: Output node ID
            
        Returns:
            MIN score or None if no edges
        """
        incoming_edges = self.get_incoming_edges(output_id)
        
        if not incoming_edges:
            return None
        
        # Get scores from edges that have a score
        scores = [
            edge_data['current_score']
            for _, _, edge_data in incoming_edges
            if edge_data.get('current_score') is not None
        ]
        
        if not scores:
            return None
        
        min_score = min(scores)
        
        if self.logger:
            self.logger.info("graph_quality_calc", f"Output quality calculated: {output_id}", {
                "output_id": output_id,
                "min_score": min_score,
                "edge_count": len(incoming_edges)
            })
        
        return min_score
    
    def identify_bottlenecks(self, output_id: str) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Identify bottleneck edges (those with MIN score).
        
        Args:
            output_id: Output node ID
            
        Returns:
            List of bottleneck edges
        """
        min_score = self.calculate_output_quality(output_id)
        
        if min_score is None:
            return []
        
        incoming_edges = self.get_incoming_edges(output_id)
        
        bottlenecks = [
            (source_id, target_id, edge_data)
            for source_id, target_id, edge_data in incoming_edges
            if edge_data.get('current_score') == min_score
        ]
        
        if self.logger:
            self.logger.info("graph_bottleneck_id", f"Bottlenecks identified: {output_id}", {
                "output_id": output_id,
                "bottleneck_count": len(bottlenecks),
                "min_score": min_score
            })
        
        return bottlenecks
    
    def get_all_nodes_by_type(self, node_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all nodes of a specific type.
        
        Args:
            node_type: Node type to filter by
            
        Returns:
            List of (node_id, node_data) tuples
        """
        nodes = [
            (node_id, dict(node_data))
            for node_id, node_data in self.graph.nodes(data=True)
            if node_data.get('node_type') == node_type
        ]
        return nodes
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """
        Get summary of current graph state.
        
        Returns:
            Summary dict with counts and metadata
        """
        return {
            "graph_id": self.graph_id,
            "metadata": self.metadata,
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "nodes_by_type": {
                "output": len([n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'output']),
                "tool": len([n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'tool']),
                "process": len([n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'process']),
                "people": len([n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'people'])
            }
        }
