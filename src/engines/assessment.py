"""Assessment engine - conversational rating inference and evidence tracking."""

import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from core.llm_client import LLMClient
from core.graph_manager import GraphManager
from utils.logger import TechnicalLogger


class AssessmentEngine:
    """
    Assesses edge quality through conversational inference.
    
    Process:
    1. User describes situation ("The team is junior, no one to learn from")
    2. LLM infers rating (⭐⭐) and evidence tier (3 - direct statement)
    3. System validates with user
    4. Evidence stored with edge
    5. Bayesian aggregation calculates final score
    """
    
    # Evidence tier weights (3^(tier-1))
    TIER_WEIGHTS = {
        1: 1,    # AI inferred from indirect data
        2: 3,    # User mentioned indirectly
        3: 9,    # User stated directly
        4: 27,   # User provided example
        5: 81    # User provided quantified example
    }
    
    # Prior parameters for Bayesian aggregation
    PRIOR_MEAN = 2.5  # μ (middle of 1-5 scale)
    PRIOR_CONFIDENCE = 10  # C (equivalent to 10 weight units)
    
    def __init__(
        self,
        llm_client: LLMClient,
        graph_manager: GraphManager,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize assessment engine.
        
        Args:
            llm_client: LLM client for inference
            graph_manager: Graph manager for storing assessments
            logger: Technical logger instance
        """
        self.llm = llm_client
        self.graph = graph_manager
        self.logger = logger
    
    def infer_rating(
        self,
        user_statement: str,
        edge_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Infer rating from user statement.
        
        Args:
            user_statement: User's description of the situation
            edge_type: Edge type being assessed (team_execution, system_capabilities, etc.)
            context: Additional context (output name, team name, etc.)
            
        Returns:
            Dict with inferred_score, evidence_tier, reasoning, confidence
        """
        if self.logger:
            self.logger.info("assessment_infer", "Starting rating inference", {
                "edge_type": edge_type,
                "statement_length": len(user_statement)
            })
        
        # Build prompt for rating inference
        prompt = self._build_inference_prompt(user_statement, edge_type, context)
        
        # Get LLM response (non-streaming)
        response = self.llm.generate(prompt, caller=f"AssessmentEngine.infer_rating[{edge_type}]")
        
        # Parse response
        inference = self._parse_inference_response(response)
        
        if self.logger:
            self.logger.info("assessment_infer", "Rating inference complete", {
                "edge_type": edge_type,
                "inferred_score": inference.get("inferred_score"),
                "evidence_tier": inference.get("evidence_tier")
            })
        
        return inference
    
    def _build_inference_prompt(
        self,
        user_statement: str,
        edge_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for rating inference."""
        
        context = context or {}
        output_name = context.get("output_name", "the output")
        
        # Edge type descriptions
        edge_descriptions = {
            "team_execution": {
                "name": "Team Execution Capability",
                "description": "How well the team can execute to create this output",
                "factors": "skills, experience, capacity, motivation, collaboration"
            },
            "system_capabilities": {
                "name": "System/Tool Capabilities",
                "description": "How well the systems/tools support creating this output",
                "factors": "features, reliability, integration, usability, performance"
            },
            "process_maturity": {
                "name": "Process Maturity",
                "description": "How mature and effective the process is for creating this output",
                "factors": "standardization, documentation, automation, quality controls, efficiency"
            },
            "dependency_quality": {
                "name": "Dependency Quality",
                "description": "How good the upstream inputs/dependencies are",
                "factors": "accuracy, completeness, timeliness, consistency, reliability"
            }
        }
        
        edge_info = edge_descriptions.get(edge_type, {
            "name": "Factor",
            "description": "Quality of this factor",
            "factors": "various aspects"
        })
        
        prompt = f"""You are an expert at assessing organizational capabilities from user descriptions.

User's Statement:
"{user_statement}"

Context:
- Output being assessed: {output_name}
- Factor being assessed: {edge_info['name']}
- Factor description: {edge_info['description']}
- Key aspects: {edge_info['factors']}

Rating Scale (1-5 stars):
⭐ (1 star) - Critical issues, major blockers, completely inadequate
⭐⭐ (2 stars) - Significant problems, frequent issues, below acceptable
⭐⭐⭐ (3 stars) - Functional but with issues, acceptable baseline
⭐⭐⭐⭐ (4 stars) - Good quality, minor issues only, above average
⭐⭐⭐⭐⭐ (5 stars) - Excellent, best-in-class, no significant issues

Evidence Tiers:
1. AI inferred from indirect data (lowest confidence)
2. User mentioned indirectly (moderate confidence)
3. User stated directly (high confidence)
4. User provided specific example (very high confidence)
5. User provided quantified example (highest confidence)

Tasks:
1. Infer the rating (1-5) based on the user's statement
2. Classify the evidence tier (1-5) based on how explicitly the user stated it
3. Provide reasoning for both

Return your response in this JSON format:
{{
  "inferred_score": 2,
  "evidence_tier": 3,
  "reasoning": "User directly stated 'the team is junior' which indicates limited experience and capability. This is a direct statement (tier 3) suggesting significant skill gaps (2 stars).",
  "confidence": 0.8
}}

Only return valid JSON, no additional text."""
        
        return prompt
    
    def _parse_inference_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM inference response."""
        try:
            data = json.loads(response)
            
            # Validate and constrain values
            inferred_score = max(1, min(5, data.get("inferred_score", 3)))
            evidence_tier = max(1, min(5, data.get("evidence_tier", 2)))
            
            return {
                "inferred_score": inferred_score,
                "evidence_tier": evidence_tier,
                "reasoning": data.get("reasoning", ""),
                "confidence": max(0.0, min(1.0, data.get("confidence", 0.5)))
            }
        
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error("assessment_parse", f"Failed to parse inference: {str(e)}", {
                    "response": response[:200]
                })
            
            # Return default inference
            return {
                "inferred_score": 3,
                "evidence_tier": 2,
                "reasoning": "Could not parse LLM response",
                "confidence": 0.3
            }
    
    def calculate_bayesian_score(self, evidence_list: List[Dict[str, Any]]) -> Tuple[float, float]:
        """
        Calculate Bayesian weighted score from evidence.
        
        Formula:
        WAR = sum(score_i * weight_i) / sum(weight_i)
        Confidence = sum(weight_i) / (sum(weight_i) + C)
        Final_Score = (Confidence * WAR) + ((1 - Confidence) * μ)
        
        Args:
            evidence_list: List of evidence dicts with 'score' and 'tier'
            
        Returns:
            Tuple of (final_score, confidence)
        """
        if not evidence_list:
            return self.PRIOR_MEAN, 0.0
        
        # Calculate weighted average rating (WAR)
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for evidence in evidence_list:
            score = evidence.get("score", 3)
            tier = evidence.get("tier", 1)
            weight = self.TIER_WEIGHTS.get(tier, 1)
            
            total_weighted_score += score * weight
            total_weight += weight
        
        war = total_weighted_score / total_weight if total_weight > 0 else self.PRIOR_MEAN
        
        # Calculate confidence
        confidence = total_weight / (total_weight + self.PRIOR_CONFIDENCE)
        
        # Calculate final score (blend WAR with prior)
        final_score = (confidence * war) + ((1 - confidence) * self.PRIOR_MEAN)
        
        if self.logger:
            self.logger.info("assessment_bayesian", "Bayesian score calculated", {
                "evidence_count": len(evidence_list),
                "total_weight": total_weight,
                "war": round(war, 2),
                "confidence": round(confidence, 2),
                "final_score": round(final_score, 2)
            })
        
        return final_score, confidence
    
    def assess_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        user_statement: str,
        conversation_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess an edge from user statement.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Edge type
            user_statement: User's statement about this factor
            conversation_id: Current conversation ID
            context: Additional context
            
        Returns:
            Assessment result with score, confidence, evidence
        """
        # Infer rating from statement
        inference = self.infer_rating(user_statement, edge_type, context)
        
        # Get existing edge or create new one
        edge_data = self.graph.get_edge(source_id, target_id)
        
        if edge_data is None:
            # Create new edge
            self.graph.add_edge(
                source_id,
                target_id,
                edge_type,
                score=None,  # Will be calculated from evidence
                confidence=0.0
            )
            evidence_list = []
        else:
            # Get existing evidence
            evidence_list = edge_data.get("evidence", [])
        
        # Add new evidence
        new_evidence = {
            "statement": user_statement,
            "score": inference["inferred_score"],
            "tier": inference["evidence_tier"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_id": conversation_id,
            "reasoning": inference["reasoning"]
        }
        
        evidence_list.append(new_evidence)
        
        # Calculate Bayesian score
        final_score, confidence = self.calculate_bayesian_score(evidence_list)
        
        # Update edge with new score and evidence
        self.graph.update_edge_rating(source_id, target_id, final_score, confidence)
        self.graph.add_evidence(
            source_id,
            target_id,
            user_statement,
            inference["evidence_tier"],
            conversation_id
        )
        
        if self.logger:
            self.logger.info("assessment_complete", "Edge assessment complete", {
                "edge_type": edge_type,
                "final_score": round(final_score, 2),
                "confidence": round(confidence, 2),
                "evidence_count": len(evidence_list)
            })
        
        return {
            "source_id": source_id,
            "target_id": target_id,
            "edge_type": edge_type,
            "inferred_score": inference["inferred_score"],
            "evidence_tier": inference["evidence_tier"],
            "final_score": final_score,
            "confidence": confidence,
            "evidence_count": len(evidence_list),
            "reasoning": inference["reasoning"]
        }
    
    def get_edge_assessment_summary(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of edge assessment.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Summary dict or None
        """
        edge_data = self.graph.get_edge(source_id, target_id)
        if not edge_data:
            return None
        
        evidence_list = edge_data.get("evidence", [])
        
        return {
            "edge_type": edge_data.get("edge_type"),
            "current_score": edge_data.get("current_score"),
            "current_confidence": edge_data.get("current_confidence"),
            "evidence_count": len(evidence_list),
            "evidence": evidence_list,
            "score_display": self._score_to_stars(edge_data.get("current_score", 0))
        }
    
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
    
    def get_assessment_progress(self, output_id: str) -> Dict[str, Any]:
        """
        Get assessment progress for an output.
        
        Args:
            output_id: Output node ID
            
        Returns:
            Progress summary
        """
        incoming_edges = self.graph.get_incoming_edges(output_id)
        
        assessed = 0
        total = len(incoming_edges)
        
        edge_summaries = []
        for source_id, target_id, edge_data in incoming_edges:
            score = edge_data.get("current_score")
            if score is not None:
                assessed += 1
            
            edge_summaries.append({
                "source_id": source_id,
                "edge_type": edge_data.get("edge_type"),
                "assessed": score is not None,
                "score": score,
                "confidence": edge_data.get("current_confidence", 0.0)
            })
        
        return {
            "output_id": output_id,
            "total_edges": total,
            "assessed_edges": assessed,
            "completion_percentage": (assessed / total * 100) if total > 0 else 0,
            "edges": edge_summaries
        }
    
    def validate_rating(self, score: float) -> bool:
        """Validate that a rating is in valid range."""
        return 1 <= score <= 5
    
    def get_tier_weight(self, tier: int) -> int:
        """Get weight for evidence tier."""
        return self.TIER_WEIGHTS.get(tier, 1)
