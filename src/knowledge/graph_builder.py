"""Knowledge graph builder from existing JSON data files.

This module loads AI archetypes, prerequisites, and organizational context
from JSON files and constructs a NetworkX directed graph with typed nodes
and edges.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx

from .schemas import (
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType,
    AIArchetypeNode,
    CommonModelNode,
    AIOutputNode,
    AIPrerequisiteNode,
    BusinessFunctionNode,
    MaturityDimensionNode,
)

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds a NetworkX knowledge graph from JSON data files."""

    def __init__(self, data_dir: Path):
        """Initialize the graph builder.

        Args:
            data_dir: Path to directory containing JSON data files
        """
        self.data_dir = Path(data_dir)
        self.graph = nx.DiGraph()
        self.node_counter = 0
        self.edge_counter = 0

        # Track created nodes to avoid duplicates
        self._node_ids: Set[str] = set()

    def build(self) -> nx.DiGraph:
        """Build the complete knowledge graph from all data sources.

        Returns:
            NetworkX DiGraph with typed nodes and edges
        """
        logger.info("Starting knowledge graph construction...")

        # Load nodes from each data source
        self._load_archetypes()
        self._load_prerequisites()
        self._load_organizational_context()

        # Create edges based on relationships in data
        self._create_archetype_edges()
        self._create_prerequisite_edges()

        logger.info(
            f"Graph construction complete: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )

        return self.graph

    # ========================================================================
    # Node Loading Methods
    # ========================================================================

    def _load_archetypes(self) -> None:
        """Load AI archetypes, models, and outputs from AI_archetypes.json."""
        file_path = self.data_dir / "AI_archetypes.json"
        logger.info(f"Loading archetypes from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            archetypes = data.get("AI_Use_Case_Archetypes", [])

            for archetype_data in archetypes:
                # Create archetype node
                archetype_id = self._create_archetype_node(archetype_data)

                # Create model nodes
                models = archetype_data.get("common_models", [])
                for model_name in models:
                    self._create_model_node(model_name, archetype_id)

                # Create output nodes
                outputs = archetype_data.get("example_outputs", [])
                for output_name in outputs:
                    self._create_output_node(output_name, archetype_id)

            logger.info(f"Loaded {len(archetypes)} archetypes")

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise

    def _create_archetype_node(self, data: Dict) -> str:
        """Create an AI archetype node.

        Args:
            data: Archetype data from JSON

        Returns:
            Node ID of created archetype
        """
        archetype_name = data.get("archetype", "Unknown")
        node_id = self._generate_node_id("A", archetype_name)

        node = AIArchetypeNode(
            node_id=node_id,
            node_type=NodeType.AI_ARCHETYPE,
            name=archetype_name,
            attributes=data
        )

        self._add_node(node)
        return node_id

    def _create_model_node(self, model_name: str, archetype_id: str) -> str:
        """Create a common model node and link to archetype.

        Args:
            model_name: Name of the model
            archetype_id: ID of parent archetype

        Returns:
            Node ID of created model
        """
        node_id = self._generate_node_id("M", model_name)

        # Check if model already exists
        if node_id in self._node_ids:
            # Just create edge to existing model
            self._add_edge(archetype_id, node_id, EdgeType.IMPLEMENTED_BY)
            return node_id

        node = CommonModelNode(
            node_id=node_id,
            node_type=NodeType.COMMON_MODEL,
            name=model_name,
            attributes={"model_name": model_name}
        )

        self._add_node(node)
        self._add_edge(archetype_id, node_id, EdgeType.IMPLEMENTED_BY)
        return node_id

    def _create_output_node(self, output_name: str, archetype_id: str) -> str:
        """Create an AI output node and link to archetype.

        Args:
            output_name: Name of the output
            archetype_id: ID of parent archetype

        Returns:
            Node ID of created output
        """
        node_id = self._generate_node_id("O", output_name)

        # Check if output already exists
        if node_id in self._node_ids:
            # Just create edge to existing output
            self._add_edge(archetype_id, node_id, EdgeType.PRODUCES_OUTPUT)
            return node_id

        node = AIOutputNode(
            node_id=node_id,
            node_type=NodeType.AI_OUTPUT,
            name=output_name,
            attributes={"output_name": output_name}
        )

        self._add_node(node)
        self._add_edge(archetype_id, node_id, EdgeType.PRODUCES_OUTPUT)
        return node_id

    def _load_prerequisites(self) -> None:
        """Load AI prerequisites from AI_prerequisites.json."""
        file_path = self.data_dir / "AI_prerequisites.json"
        logger.info(f"Loading prerequisites from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            prereq_data = data.get("AI_Implementation_Prerequisites", {})

            # Iterate through categories
            for category, prereqs in prereq_data.items():
                for prereq_name, prereq_info in prereqs.items():
                    self._create_prerequisite_node(
                        prereq_name,
                        category,
                        prereq_info
                    )

            logger.info(f"Loaded prerequisites from {len(prereq_data)} categories")

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise

    def _create_prerequisite_node(
        self,
        prereq_name: str,
        category: str,
        info: Dict
    ) -> str:
        """Create a prerequisite node.

        Args:
            prereq_name: Name of the prerequisite
            category: Category (Data_Quality, etc.)
            info: Additional prerequisite information

        Returns:
            Node ID of created prerequisite
        """
        node_id = self._generate_node_id("P", prereq_name)

        if node_id in self._node_ids:
            return node_id

        node = AIPrerequisiteNode(
            node_id=node_id,
            node_type=NodeType.AI_PREREQUISITE,
            name=prereq_name,
            attributes={
                "category": category,
                "description": info.get("description", ""),
                "dependent_models": info.get("dependent_models", []),
                "dependent_outputs": info.get("dependent_outputs", [])
            }
        )

        self._add_node(node)
        return node_id

    def _load_organizational_context(self) -> None:
        """Load business functions and maturity from AI_discovery.json."""
        file_path = self.data_dir / "AI_discovery.json"
        logger.info(f"Loading organizational context from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load maturity dimensions
            maturity_data = data.get("Organizational_Maturity", {})
            subdimensions = maturity_data.get("subdimensions", [])
            for subdim in subdimensions:
                self._create_maturity_node(subdim)

            # Load business functions
            function_data = data.get("Business_Function", {})
            categories = function_data.get("categories", [])
            for category in categories:
                functions = category.get("functions", [])
                for func in functions:
                    self._create_function_node(func, category.get("category", ""))

            logger.info(
                f"Loaded {len(subdimensions)} maturity dimensions and "
                f"business functions"
            )

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise

    def _create_maturity_node(self, data: Dict) -> str:
        """Create a maturity dimension node.

        Args:
            data: Maturity dimension data

        Returns:
            Node ID of created maturity dimension
        """
        name = data.get("name", "Unknown")
        node_id = self._generate_node_id("MAT", name)

        if node_id in self._node_ids:
            return node_id

        node = MaturityDimensionNode(
            node_id=node_id,
            node_type=NodeType.MATURITY_DIMENSION,
            name=name,
            attributes=data
        )

        self._add_node(node)
        return node_id

    def _create_function_node(self, data: Dict, category: str) -> str:
        """Create a business function node.

        Args:
            data: Function data
            category: Function category

        Returns:
            Node ID of created function
        """
        name = data.get("name", "Unknown")
        node_id = self._generate_node_id("F", name)

        if node_id in self._node_ids:
            return node_id

        node = BusinessFunctionNode(
            node_id=node_id,
            node_type=NodeType.BUSINESS_FUNCTION,
            name=name,
            attributes={
                "category": category,
                "tools_and_processes": data.get("tools_and_processes", [])
            }
        )

        self._add_node(node)
        return node_id

    # ========================================================================
    # Edge Creation Methods
    # ========================================================================

    def _create_archetype_edges(self) -> None:
        """Create edges from archetypes to models and outputs.

        These edges are created during node loading, so this is a placeholder
        for any additional archetype-level relationships.
        """
        # IMPLEMENTED_BY and PRODUCES_OUTPUT edges already created
        # during node creation
        pass

    def _create_prerequisite_edges(self) -> None:
        """Create REQUIRES edges from models/outputs to prerequisites."""
        logger.info("Creating prerequisite dependency edges...")

        edge_count = 0

        # Iterate through all prerequisite nodes
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]

            if node_data.get("node_type") != NodeType.AI_PREREQUISITE.value:
                continue

            attrs = node_data.get("attributes", {})
            dependent_models = attrs.get("dependent_models", [])
            dependent_outputs = attrs.get("dependent_outputs", [])

            # Create edges from models to this prerequisite
            for model_name in dependent_models:
                model_id = self._find_node_by_name(model_name, NodeType.COMMON_MODEL)
                if model_id:
                    self._add_edge(model_id, node_id, EdgeType.REQUIRES)
                    edge_count += 1

            # Create edges from outputs to this prerequisite
            for output_name in dependent_outputs:
                output_id = self._find_node_by_name(output_name, NodeType.AI_OUTPUT)
                if output_id:
                    self._add_edge(output_id, node_id, EdgeType.REQUIRES)
                    edge_count += 1

        logger.info(f"Created {edge_count} prerequisite dependency edges")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _generate_node_id(self, prefix: str, name: str) -> str:
        """Generate a unique node ID from prefix and name.

        Args:
            prefix: Node type prefix (A, M, O, P, F, MAT)
            name: Node name

        Returns:
            Unique node ID
        """
        # Sanitize name for ID
        sanitized = name.replace(" ", "_").replace("/", "_").replace("&", "and")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        return f"{prefix}_{sanitized}"

    def _add_node(self, node: GraphNode) -> None:
        """Add a node to the graph.

        Args:
            node: GraphNode instance
        """
        if node.node_id in self._node_ids:
            logger.warning(f"Node {node.node_id} already exists, skipping")
            return

        # Add to NetworkX graph
        # Handle both enum and string values for node_type
        node_type_value = node.node_type.value if hasattr(node.node_type, 'value') else node.node_type
        
        self.graph.add_node(
            node.node_id,
            node_type=node_type_value,
            name=node.name,
            attributes=node.attributes
        )

        self._node_ids.add(node.node_id)
        self.node_counter += 1

    def _add_edge(
        self,
        source: str,
        target: str,
        relationship: EdgeType,
        attributes: Optional[Dict] = None
    ) -> None:
        """Add an edge to the graph.

        Args:
            source: Source node ID
            target: Target node ID
            relationship: Edge type
            attributes: Optional edge attributes
        """
        if not self.graph.has_node(source):
            logger.warning(f"Source node {source} not found, skipping edge")
            return

        if not self.graph.has_node(target):
            logger.warning(f"Target node {target} not found, skipping edge")
            return

        # Handle both enum and string values for relationship
        relationship_value = relationship.value if hasattr(relationship, 'value') else relationship
        
        # Check if edge already exists
        if self.graph.has_edge(source, target):
            # Update relationship if different
            existing = self.graph.edges[source, target].get("relationship")
            if existing != relationship_value:
                logger.debug(
                    f"Edge {source}->{target} exists with different relationship"
                )
            return

        edge_id = f"E_{self.edge_counter}"
        self.graph.add_edge(
            source,
            target,
            edge_id=edge_id,
            relationship=relationship_value,
            attributes=attributes or {}
        )

        self.edge_counter += 1

    def _find_node_by_name(
        self,
        name: str,
        node_type: NodeType
    ) -> Optional[str]:
        """Find a node ID by name and type.

        Args:
            name: Node name to search for
            node_type: Type of node

        Returns:
            Node ID if found, None otherwise
        """
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            if (node_data.get("node_type") == node_type.value and
                node_data.get("name") == name):
                return node_id

        return None

    # ========================================================================
    # Graph Statistics
    # ========================================================================

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the constructed graph.

        Returns:
            Dictionary with node and edge counts by type
        """
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges()
        }

        # Count nodes by type
        for node_type in NodeType:
            count = sum(
                1 for _, data in self.graph.nodes(data=True)
                if data.get("node_type") == node_type.value
            )
            stats[f"nodes_{node_type.value}"] = count

        # Count edges by type
        for edge_type in EdgeType:
            count = sum(
                1 for _, _, data in self.graph.edges(data=True)
                if data.get("relationship") == edge_type.value
            )
            stats[f"edges_{edge_type.value}"] = count

        return stats
