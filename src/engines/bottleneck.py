"""Bottleneck identification and gap analysis engine."""

from typing import Optional, Dict, Any, List, Tuple

from core.graph_manager import GraphManager
from utils.logger import TechnicalLogger


class BottleneckEngine:
    """
    Identifies bottlenecks and analyzes gaps between current and required quality.
    
    Process:
    1. Calculate output quality using MIN of incoming edges
    2. Identify bottleneck edges (those with MIN score)
    3. Calculate gap between current and required quality
    4. Categorize root causes by edge type
    5. Generate improvement recommendations
    """
    
    # Root cause categories map to AI solution types
    ROOT_CAUSE_MAPPING = {
        "dependency_quality": {
            "category": "Dependency Issue",
            "solution_type": "Data Quality/Pipeline AI Pilots",
            "description": "Upstream inputs or dependencies are inadequate"
        },
        "team_execution": {
            "category": "Execution Issue",
            "solution_type": "Augmentation/Automation AI Pilots",
            "description": "Team lacks capability or capacity to execute"
        },
        "process_maturity": {
            "category": "Process Issue",
            "solution_type": "Process Intelligence AI Pilots",
            "description": "Process is immature or inefficient"
        },
        "system_capabilities": {
            "category": "System Issue",
            "solution_type": "Intelligent Features AI Pilots",
            "description": "Systems/tools lack necessary capabilities"
        }
    }
    
    def __init__(
        self,
        graph_manager: GraphManager,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize bottleneck engine.
        
        Args:
            graph_manager: Graph manager for accessing assessment data
            logger: Technical logger instance
        """
        self.graph = graph_manager
        self.logger = logger
    
    def analyze_output(self, output_id: str, required_quality: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze output quality and identify bottlenecks.
        
        Args:
            output_id: Output node ID
            required_quality: Required quality level (1-5), None if not specified
            
        Returns:
            Analysis dict with current quality, bottlenecks, gaps, recommendations
        """
        if self.logger:
            self.logger.info("bottleneck_analyze", f"Analyzing output: {output_id}", {
                "output_id": output_id,
                "required_quality": required_quality
            })
        
        # Calculate current quality (MIN of incoming edges)
        current_quality = self.graph.calculate_output_quality(output_id)
        
        if current_quality is None:
            return {
                "output_id": output_id,
                "status": "not_assessed",
                "message": "No edges assessed yet"
            }
        
        # Identify bottlenecks
        bottlenecks = self.graph.identify_bottlenecks(output_id)
        
        # Calculate gap if required quality specified
        gap = None
        gap_stars = None
        if required_quality is not None:
            gap = required_quality - current_quality
            gap_stars = int(round(gap))
        
        # Categorize bottlenecks by root cause
        root_causes = self._categorize_root_causes(bottlenecks)
        
        # Get all edges for context
        all_edges = self.graph.get_incoming_edges(output_id)
        
        analysis = {
            "output_id": output_id,
            "status": "analyzed",
            "current_quality": current_quality,
            "current_quality_display": self._score_to_stars(current_quality),
            "required_quality": required_quality,
            "required_quality_display": self._score_to_stars(required_quality) if required_quality else None,
            "gap": gap,
            "gap_stars": gap_stars,
            "bottleneck_count": len(bottlenecks),
            "bottlenecks": self._format_bottlenecks(bottlenecks),
            "root_causes": root_causes,
            "all_edges": self._format_edges(all_edges),
            "edge_count": len(all_edges)
        }
        
        if self.logger:
            self.logger.info("bottleneck_complete", "Analysis complete", {
                "output_id": output_id,
                "current_quality": round(current_quality, 2),
                "bottleneck_count": len(bottlenecks),
                "gap": round(gap, 2) if gap else None
            })
        
        return analysis
    
    def _categorize_root_causes(self, bottlenecks: List[Tuple[str, str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Categorize bottlenecks by root cause type."""
        root_causes = []
        
        for source_id, target_id, edge_data in bottlenecks:
            edge_type = edge_data.get("edge_type", "unknown")
            mapping = self.ROOT_CAUSE_MAPPING.get(edge_type, {
                "category": "Unknown",
                "solution_type": "General Improvement",
                "description": "Unknown root cause"
            })
            
            # Get source node details
            source_node = self.graph.get_node(source_id)
            source_name = source_node.get("name", source_id) if source_node else source_id
            
            root_causes.append({
                "edge_type": edge_type,
                "source_id": source_id,
                "source_name": source_name,
                "score": edge_data.get("current_score"),
                "confidence": edge_data.get("current_confidence"),
                "category": mapping["category"],
                "solution_type": mapping["solution_type"],
                "description": mapping["description"]
            })
        
        return root_causes
    
    def _format_bottlenecks(self, bottlenecks: List[Tuple[str, str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Format bottlenecks for display."""
        formatted = []
        
        for source_id, target_id, edge_data in bottlenecks:
            source_node = self.graph.get_node(source_id)
            source_name = source_node.get("name", source_id) if source_node else source_id
            
            formatted.append({
                "source_id": source_id,
                "source_name": source_name,
                "edge_type": edge_data.get("edge_type"),
                "score": edge_data.get("current_score"),
                "score_display": self._score_to_stars(edge_data.get("current_score")),
                "confidence": edge_data.get("current_confidence"),
                "evidence_count": len(edge_data.get("evidence", []))
            })
        
        return formatted
    
    def _format_edges(self, edges: List[Tuple[str, str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Format all edges for display."""
        formatted = []
        
        for source_id, target_id, edge_data in edges:
            source_node = self.graph.get_node(source_id)
            source_name = source_node.get("name", source_id) if source_node else source_id
            
            score = edge_data.get("current_score")
            formatted.append({
                "source_id": source_id,
                "source_name": source_name,
                "edge_type": edge_data.get("edge_type"),
                "score": score,
                "score_display": self._score_to_stars(score),
                "confidence": edge_data.get("current_confidence"),
                "is_bottleneck": False  # Will be marked by caller if needed
            })
        
        return formatted
    
    def _score_to_stars(self, score: Optional[float]) -> str:
        """Convert numeric score to star display."""
        if score is None:
            return "Not assessed"
        
        # Round to nearest 0.5
        rounded = round(score * 2) / 2
        full_stars = int(rounded)
        half_star = (rounded - full_stars) >= 0.5
        
        stars = "⭐" * full_stars
        if half_star:
            stars += "½"
        
        return f"{stars} ({score:.1f})"
    
    def get_improvement_priority(self, output_id: str) -> List[Dict[str, Any]]:
        """
        Get prioritized list of improvement opportunities.
        
        Args:
            output_id: Output node ID
            
        Returns:
            List of improvement opportunities sorted by priority
        """
        analysis = self.analyze_output(output_id)
        
        if analysis.get("status") != "analyzed":
            return []
        
        bottlenecks = analysis.get("bottlenecks", [])
        
        # Sort by score (lowest first) and confidence (highest first)
        prioritized = sorted(
            bottlenecks,
            key=lambda x: (x.get("score", 5), -x.get("confidence", 0))
        )
        
        return prioritized
    
    def compare_outputs(self, output_ids: List[str]) -> Dict[str, Any]:
        """
        Compare quality across multiple outputs.
        
        Args:
            output_ids: List of output IDs to compare
            
        Returns:
            Comparison summary
        """
        comparisons = []
        
        for output_id in output_ids:
            quality = self.graph.calculate_output_quality(output_id)
            bottlenecks = self.graph.identify_bottlenecks(output_id)
            
            output_node = self.graph.get_node(output_id)
            output_name = output_node.get("name", output_id) if output_node else output_id
            
            comparisons.append({
                "output_id": output_id,
                "output_name": output_name,
                "quality": quality,
                "quality_display": self._score_to_stars(quality),
                "bottleneck_count": len(bottlenecks)
            })
        
        # Sort by quality (lowest first)
        comparisons.sort(key=lambda x: x.get("quality", 0) if x.get("quality") is not None else 0)
        
        return {
            "output_count": len(comparisons),
            "outputs": comparisons,
            "lowest_quality": comparisons[0] if comparisons else None,
            "highest_quality": comparisons[-1] if comparisons else None
        }
    
    def get_gap_summary(self, output_id: str, required_quality: float) -> Dict[str, Any]:
        """
        Get detailed gap summary.
        
        Args:
            output_id: Output node ID
            required_quality: Required quality level
            
        Returns:
            Gap summary with improvement needs
        """
        analysis = self.analyze_output(output_id, required_quality)
        
        if analysis.get("status") != "analyzed":
            return {"status": "not_assessed"}
        
        gap = analysis.get("gap", 0)
        gap_stars = analysis.get("gap_stars", 0)
        
        # Categorize gap severity
        if gap <= 0:
            severity = "none"
            message = "Output meets or exceeds required quality"
        elif gap <= 1:
            severity = "minor"
            message = "Small improvement needed (1 star gap)"
        elif gap <= 2:
            severity = "moderate"
            message = "Moderate improvement needed (2 star gap)"
        elif gap <= 3:
            severity = "significant"
            message = "Significant improvement needed (3 star gap)"
        else:
            severity = "critical"
            message = "Critical improvement needed (4+ star gap)"
        
        return {
            "output_id": output_id,
            "current_quality": analysis["current_quality"],
            "required_quality": required_quality,
            "gap": gap,
            "gap_stars": gap_stars,
            "severity": severity,
            "message": message,
            "bottlenecks": analysis["bottlenecks"],
            "root_causes": analysis["root_causes"]
        }
    
    def get_solution_recommendations(self, output_id: str) -> List[Dict[str, Any]]:
        """
        Get AI solution recommendations based on bottlenecks.
        
        Args:
            output_id: Output node ID
            
        Returns:
            List of solution recommendations
        """
        analysis = self.analyze_output(output_id)
        
        if analysis.get("status") != "analyzed":
            return []
        
        root_causes = analysis.get("root_causes", [])
        
        # Group by solution type
        solution_types = {}
        for cause in root_causes:
            solution_type = cause["solution_type"]
            if solution_type not in solution_types:
                solution_types[solution_type] = {
                    "solution_type": solution_type,
                    "root_causes": [],
                    "priority": "high" if cause["score"] < 2 else "medium" if cause["score"] < 3 else "low"
                }
            solution_types[solution_type]["root_causes"].append(cause)
        
        recommendations = list(solution_types.values())
        
        # Sort by priority and number of root causes
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 3), -len(x["root_causes"]))
        )
        
        return recommendations
