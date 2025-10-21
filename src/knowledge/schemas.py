"""Pydantic schemas for knowledge graph nodes and edges.

This module defines the data models for the knowledge graph structure,
providing validation and type safety for nodes and edges.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enums for Type Safety
# ============================================================================

class NodeType(str, Enum):
    """Valid node types in the knowledge graph."""
    AI_ARCHETYPE = "AI_ARCHETYPE"
    COMMON_MODEL = "COMMON_MODEL"
    AI_OUTPUT = "AI_OUTPUT"
    AI_PREREQUISITE = "AI_PREREQUISITE"
    BUSINESS_FUNCTION = "BUSINESS_FUNCTION"
    MATURITY_DIMENSION = "MATURITY_DIMENSION"


class EdgeType(str, Enum):
    """Valid edge types (relationships) in the knowledge graph."""
    IMPLEMENTED_BY = "IMPLEMENTED_BY"  # Archetype -> Model
    PRODUCES_OUTPUT = "PRODUCES_OUTPUT"  # Archetype -> Output
    REQUIRES = "REQUIRES"  # Model/Output -> Prerequisite
    APPLIES_TO_FUNCTION = "APPLIES_TO_FUNCTION"  # Archetype -> Function
    OPERATES_IN = "OPERATES_IN"  # Function -> Tool/Process
    GOVERNS_READINESS_FOR = "GOVERNS_READINESS_FOR"  # Maturity -> Prerequisite


class PrerequisiteCategory(str, Enum):
    """Categories of AI prerequisites."""
    DATA_QUALITY = "Data_Quality"
    DATA_QUANTITY = "Data_Quantity"
    DATA_FORMAT_AND_STRUCTURE = "Data_Format_and_Structure"
    TECHNICAL_EXPERTISE = "Technical_Expertise"
    DOMAIN_KNOWLEDGE = "Domain_Knowledge"
    INFRASTRUCTURE = "Infrastructure"
    MLOPS_CAPABILITIES = "MLOps_Capabilities"
    EXTERNAL_RESOURCES = "External_Resources"
    ORGANIZATIONAL_READINESS = "Organizational_Readiness"
    SPECIALIZED_REQUIREMENTS = "Specialized_Requirements"


class AnalyticalPurpose(str, Enum):
    """Analytical purposes of AI archetypes."""
    DESCRIPTIVE = "Descriptive"
    DIAGNOSTIC = "Diagnostic"
    PREDICTIVE = "Predictive"
    PRESCRIPTIVE = "Prescriptive"
    GENERATIVE = "Generative"
    RETRIEVAL = "Retrieval"
    REASONING = "Reasoning"
    GOVERNANCE = "Governance"


class ComplexityLevel(str, Enum):
    """Implementation complexity levels."""
    BASIC = "Basic"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


# ============================================================================
# Node Schemas
# ============================================================================

class GraphNode(BaseModel):
    """Base model for all knowledge graph nodes."""
    node_id: str = Field(..., description="Unique identifier for the node")
    node_type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Human-readable name")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional attributes specific to node type"
    )

    class Config:
        use_enum_values = True

    @field_validator('node_id')
    @classmethod
    def validate_node_id(cls, v: str) -> str:
        """Ensure node_id is not empty."""
        if not v or not v.strip():
            raise ValueError("node_id cannot be empty")
        return v.strip()


class AIArchetypeNode(GraphNode):
    """Node representing an AI use-case archetype."""
    node_type: Literal[NodeType.AI_ARCHETYPE] = NodeType.AI_ARCHETYPE
    core_task: Optional[str] = None
    analytical_purpose: List[AnalyticalPurpose] = Field(default_factory=list)
    technical_family: Optional[str] = None
    agnostic_scope: Optional[str] = None

    def __init__(self, **data):
        # Extract specific fields from attributes if present
        if 'attributes' in data:
            attrs = data['attributes']
            data['core_task'] = attrs.get('core_task')
            data['analytical_purpose'] = attrs.get('analytical_purpose', [])
            data['technical_family'] = attrs.get('technical_family')
            data['agnostic_scope'] = attrs.get('agnostic_scope')
        super().__init__(**data)


class CommonModelNode(GraphNode):
    """Node representing a specific ML model or algorithm."""
    node_type: Literal[NodeType.COMMON_MODEL] = NodeType.COMMON_MODEL


class AIOutputNode(GraphNode):
    """Node representing an AI system output or artifact."""
    node_type: Literal[NodeType.AI_OUTPUT] = NodeType.AI_OUTPUT


class AIPrerequisiteNode(GraphNode):
    """Node representing an implementation prerequisite."""
    node_type: Literal[NodeType.AI_PREREQUISITE] = NodeType.AI_PREREQUISITE
    category: Optional[PrerequisiteCategory] = None
    description: Optional[str] = None

    def __init__(self, **data):
        if 'attributes' in data:
            attrs = data['attributes']
            data['category'] = attrs.get('category')
            data['description'] = attrs.get('description')
        super().__init__(**data)


class BusinessFunctionNode(GraphNode):
    """Node representing a business function or department."""
    node_type: Literal[NodeType.BUSINESS_FUNCTION] = NodeType.BUSINESS_FUNCTION
    category: Optional[str] = None
    tools_and_processes: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        if 'attributes' in data:
            attrs = data['attributes']
            data['category'] = attrs.get('category')
            data['tools_and_processes'] = attrs.get('tools_and_processes', [])
        super().__init__(**data)


class MaturityDimensionNode(GraphNode):
    """Node representing an organizational maturity dimension."""
    node_type: Literal[NodeType.MATURITY_DIMENSION] = NodeType.MATURITY_DIMENSION
    description: Optional[str] = None
    levels: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        if 'attributes' in data:
            attrs = data['attributes']
            data['description'] = attrs.get('description')
            data['levels'] = attrs.get('levels', [])
            data['metrics'] = attrs.get('metrics', [])
        super().__init__(**data)


# ============================================================================
# Edge Schemas
# ============================================================================

class GraphEdge(BaseModel):
    """Model for knowledge graph edges (relationships)."""
    edge_id: str = Field(..., description="Unique identifier for the edge")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: EdgeType = Field(..., description="Type of relationship")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge attributes"
    )

    class Config:
        use_enum_values = True

    @field_validator('edge_id')
    @classmethod
    def validate_edge_id(cls, v: str) -> str:
        """Ensure edge_id is not empty."""
        if not v or not v.strip():
            raise ValueError("edge_id cannot be empty")
        return v.strip()


# ============================================================================
# Maturity Mapping Schemas
# ============================================================================

class ArchetypeMaturityRequirement(BaseModel):
    """Mapping of archetype to minimum maturity requirements."""
    archetype_id: str = Field(..., description="ID of the AI archetype")
    min_ai_maturity: str = Field(..., description="Minimum AI maturity stage")
    min_data_maturity: str = Field(..., description="Minimum data maturity level")
    min_technical_stack: str = Field(..., description="Minimum technical stack sophistication")
    complexity_level: ComplexityLevel = Field(..., description="Implementation complexity")

    class Config:
        use_enum_values = True


class MaturityPrerequisiteConstraint(BaseModel):
    """Mapping of maturity level to prerequisite satisfaction."""
    maturity_dimension: str = Field(..., description="Name of maturity dimension")
    level: str = Field(..., description="Specific maturity level")
    satisfied_prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisites that can be satisfied at this level"
    )
    unsatisfied_prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisites that cannot be satisfied at this level"
    )


# ============================================================================
# Graph Schema Container
# ============================================================================

class KnowledgeGraphSchema(BaseModel):
    """Complete knowledge graph structure."""
    version: str = Field(default="1.0", description="Schema version")
    description: str = Field(
        default="Knowledge graph for AI solution discovery",
        description="Graph description"
    )
    nodes: List[GraphNode] = Field(default_factory=list, description="All graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="All graph edges")

    def get_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Retrieve a node by its ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_edges_by_source(self, source_id: str) -> List[GraphEdge]:
        """Get all edges originating from a source node."""
        return [edge for edge in self.edges if edge.source == source_id]

    def get_edges_by_target(self, target_id: str) -> List[GraphEdge]:
        """Get all edges pointing to a target node."""
        return [edge for edge in self.edges if edge.target == target_id]

    def get_edges_by_type(self, relationship: EdgeType) -> List[GraphEdge]:
        """Get all edges of a specific relationship type."""
        return [edge for edge in self.edges if edge.relationship == relationship]
