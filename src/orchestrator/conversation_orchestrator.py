"""Conversation orchestrator - manages the full assessment flow."""

from typing import Optional, Dict, Any, List
from enum import Enum

from core.llm_client import LLMClient
from core.firebase_client import FirebaseClient
from core.graph_manager import GraphManager
from core.session_manager import SessionManager
from engines.discovery import OutputDiscoveryEngine
from engines.assessment import AssessmentEngine
from engines.bottleneck import BottleneckEngine
from utils.logger import TechnicalLogger


class AssessmentPhase(Enum):
    """Assessment conversation phases."""
    DISCOVERY = "discovery"
    ASSESSMENT = "assessment"
    ANALYSIS = "analysis"
    RECOMMENDATIONS = "recommendations"
    COMPLETE = "complete"


class ConversationOrchestrator:
    """
    Orchestrates the full assessment conversation flow.
    
    Flow:
    1. Discovery: Identify output from user description
    2. Assessment: Assess all 4 edge types (Team, Tool, Process, Dependencies)
    3. Analysis: Calculate quality, identify bottlenecks, analyze gaps
    4. Recommendations: Generate AI pilot recommendations
    5. Complete: Present final report
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        firebase_client: FirebaseClient,
        session_manager: SessionManager,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize conversation orchestrator.
        
        Args:
            llm_client: LLM client for inference
            firebase_client: Firebase client for persistence
            session_manager: Session manager for state
            logger: Technical logger instance
        """
        self.llm = llm_client
        self.firebase = firebase_client
        self.session = session_manager
        self.logger = logger
        
        # Initialize engines
        self.graph = GraphManager(
            firebase_client=firebase_client,
            user_id=session_manager.user_id,
            logger=logger
        )
        
        self.discovery = OutputDiscoveryEngine(
            llm_client=llm_client,
            logger=logger
        )
        
        self.assessment = AssessmentEngine(
            llm_client=llm_client,
            graph_manager=self.graph,
            logger=logger
        )
        
        self.bottleneck = BottleneckEngine(
            graph_manager=self.graph,
            logger=logger
        )
        
        # State
        self.current_phase = AssessmentPhase.DISCOVERY
        self.current_output_id = None
        self.current_output_name = None
        self.required_quality = None
        self.edges_to_assess = []
        self.current_edge_index = 0
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message and return response.
        
        Args:
            user_message: User's message
            
        Returns:
            Response dict with message, phase, data
        """
        if self.logger:
            self.logger.info("orchestrator_process", f"Processing message in phase: {self.current_phase.value}", {
                "phase": self.current_phase.value,
                "message_length": len(user_message)
            })
        
        # Route to appropriate handler based on phase
        if self.current_phase == AssessmentPhase.DISCOVERY:
            return self._handle_discovery(user_message)
        elif self.current_phase == AssessmentPhase.ASSESSMENT:
            return self._handle_assessment(user_message)
        elif self.current_phase == AssessmentPhase.ANALYSIS:
            return self._handle_analysis(user_message)
        elif self.current_phase == AssessmentPhase.RECOMMENDATIONS:
            return self._handle_recommendations(user_message)
        else:
            return {
                "message": "Assessment complete. Type 'restart' to begin a new assessment.",
                "phase": self.current_phase.value,
                "data": {}
            }
    
    def _handle_discovery(self, user_message: str) -> Dict[str, Any]:
        """Handle discovery phase."""
        # Discover outputs from user description
        candidates = self.discovery.discover_output(
            user_message,
            self.session.get_conversation_history()
        )
        
        if not candidates:
            return {
                "message": "I couldn't identify a specific output from your description. Could you provide more details about what you're trying to improve?",
                "phase": self.current_phase.value,
                "data": {"candidates": []}
            }
        
        # Take top candidate
        top_candidate = candidates[0]
        self.current_output_id = top_candidate["id"]
        self.current_output_name = top_candidate["name"]
        
        # Infer creation context
        context = self.discovery.infer_creation_context(self.current_output_id)
        
        # Create graph and nodes
        graph_id = self.graph.create_graph(self.current_output_id, self.current_output_name)
        
        # Create output node
        self.graph.add_node(
            self.current_output_id,
            "output",
            name=self.current_output_name,
            description=top_candidate.get("description", "")
        )
        
        # Create context nodes
        team_id = f"team_{self.current_output_id}"
        tool_id = f"tool_{self.current_output_id}"
        process_id = f"process_{self.current_output_id}"
        
        self.graph.add_node(
            team_id,
            "people",
            name=context["team"]["name"],
            archetype=context["team"]["archetype"]
        )
        
        self.graph.add_node(
            tool_id,
            "tool",
            name=context["system"]["name"],
            category=context["system"]["category"]
        )
        
        self.graph.add_node(
            process_id,
            "process",
            name=context["process"]["name"],
            step=context["process"]["step"]
        )
        
        # Prepare edges to assess
        self.edges_to_assess = [
            {"source_id": team_id, "target_id": self.current_output_id, "edge_type": "team_execution", "name": "Team Capability"},
            {"source_id": tool_id, "target_id": self.current_output_id, "edge_type": "system_capabilities", "name": "System/Tool Quality"},
            {"source_id": process_id, "target_id": self.current_output_id, "edge_type": "process_maturity", "name": "Process Maturity"}
        ]
        self.current_edge_index = 0
        
        # Move to assessment phase
        self.current_phase = AssessmentPhase.ASSESSMENT
        self.session.phase = self.current_phase.value
        
        return {
            "message": f"Great! I identified **{self.current_output_name}**.\n\nLet's assess the factors affecting its quality. I'll ask about:\n1. Team capability\n2. System/tool quality\n3. Process maturity\n\nLet's start with the **team**. How would you describe the team's capability to create high-quality {self.current_output_name}?",
            "phase": self.current_phase.value,
            "data": {
                "output_id": self.current_output_id,
                "output_name": self.current_output_name,
                "context": context,
                "graph_id": graph_id,
                "confidence": top_candidate.get("confidence", 0.0)
            }
        }
    
    def _handle_assessment(self, user_message: str) -> Dict[str, Any]:
        """Handle assessment phase."""
        if self.current_edge_index >= len(self.edges_to_assess):
            # All edges assessed, move to analysis
            self.current_phase = AssessmentPhase.ANALYSIS
            self.session.phase = self.current_phase.value
            
            return {
                "message": f"Thank you! I've assessed all the key factors.\n\nNow, what quality level do you **need** for {self.current_output_name}? (1-5 stars, where ⭐=critical issues, ⭐⭐⭐=functional, ⭐⭐⭐⭐⭐=excellent)",
                "phase": self.current_phase.value,
                "data": {
                    "assessment_complete": True
                }
            }
        
        # Assess current edge
        edge = self.edges_to_assess[self.current_edge_index]
        
        result = self.assessment.assess_edge(
            edge["source_id"],
            edge["target_id"],
            edge["edge_type"],
            user_message,
            self.session.conversation_id,
            {"output_name": self.current_output_name}
        )
        
        # Move to next edge
        self.current_edge_index += 1
        
        if self.current_edge_index < len(self.edges_to_assess):
            # Ask about next edge
            next_edge = self.edges_to_assess[self.current_edge_index]
            
            return {
                "message": f"I'm hearing that's about **{result['score_display']}**.\n\nNext, let's talk about the **{next_edge['name'].lower()}**. How would you describe it?",
                "phase": self.current_phase.value,
                "data": {
                    "edge_assessed": edge["edge_type"],
                    "inferred_score": result["inferred_score"],
                    "final_score": result["final_score"],
                    "confidence": result["confidence"],
                    "progress": f"{self.current_edge_index}/{len(self.edges_to_assess)}"
                }
            }
        else:
            # All edges assessed
            self.current_phase = AssessmentPhase.ANALYSIS
            self.session.phase = self.current_phase.value
            
            return {
                "message": f"Got it, that's about **{result['score_display']}**.\n\nNow, what quality level do you **need** for {self.current_output_name}? (1-5 stars)",
                "phase": self.current_phase.value,
                "data": {
                    "edge_assessed": edge["edge_type"],
                    "inferred_score": result["inferred_score"],
                    "final_score": result["final_score"],
                    "assessment_complete": True
                }
            }
    
    def _handle_analysis(self, user_message: str) -> Dict[str, Any]:
        """Handle analysis phase."""
        # Parse required quality from user message
        try:
            # Look for numbers 1-5 in message
            import re
            numbers = re.findall(r'\b[1-5]\b', user_message)
            if numbers:
                self.required_quality = float(numbers[0])
            else:
                # Default to 4 if not specified
                self.required_quality = 4.0
        except:
            self.required_quality = 4.0
        
        # Analyze output
        analysis = self.bottleneck.analyze_output(self.current_output_id, self.required_quality)
        
        if analysis.get("status") != "analyzed":
            return {
                "message": "I couldn't complete the analysis. Please try again.",
                "phase": self.current_phase.value,
                "data": {}
            }
        
        # Get gap summary
        gap_summary = self.bottleneck.get_gap_summary(self.current_output_id, self.required_quality)
        
        # Format bottleneck message
        bottlenecks = analysis["bottlenecks"]
        if bottlenecks:
            bottleneck_text = "\n".join([
                f"- **{b['source_name']}**: {b['score_display']}"
                for b in bottlenecks
            ])
        else:
            bottleneck_text = "No single bottleneck - all factors are equally limiting"
        
        # Move to recommendations
        self.current_phase = AssessmentPhase.RECOMMENDATIONS
        self.session.phase = self.current_phase.value
        
        message = f"""**Analysis Complete!**

**Current Quality:** {analysis['current_quality_display']}
**Required Quality:** {analysis['required_quality_display']}
**Gap:** {gap_summary['gap_stars']} stars ({gap_summary['severity']})

**Bottleneck(s):**
{bottleneck_text}

{gap_summary['message']}

Would you like to see AI pilot recommendations to address these bottlenecks?"""
        
        return {
            "message": message,
            "phase": self.current_phase.value,
            "data": {
                "analysis": analysis,
                "gap_summary": gap_summary
            }
        }
    
    def _handle_recommendations(self, user_message: str) -> Dict[str, Any]:
        """Handle recommendations phase."""
        # Get solution recommendations
        recommendations = self.bottleneck.get_solution_recommendations(self.current_output_id)
        
        if not recommendations:
            return {
                "message": "No specific recommendations available at this time.",
                "phase": self.current_phase.value,
                "data": {}
            }
        
        # Format recommendations
        rec_text = []
        for i, rec in enumerate(recommendations[:3], 1):  # Top 3
            root_causes = rec["root_causes"]
            causes_text = ", ".join([rc["source_name"] for rc in root_causes])
            
            rec_text.append(
                f"**{i}. {rec['solution_type']}** (Priority: {rec['priority']})\n"
                f"   Addresses: {causes_text}"
            )
        
        message = f"""**Recommended AI Pilot Types:**

{chr(10).join(rec_text)}

These recommendations are based on your bottleneck analysis. Each pilot type targets specific root causes identified in your assessment.

**Next Steps:**
- Review detailed pilot options in Phase 4 (Recommendation Engine)
- Assess feasibility and prerequisites
- Generate comprehensive report

Type 'restart' to assess another output, or 'report' to generate a full assessment report."""
        
        # Move to complete
        self.current_phase = AssessmentPhase.COMPLETE
        self.session.phase = self.current_phase.value
        
        return {
            "message": message,
            "phase": self.current_phase.value,
            "data": {
                "recommendations": recommendations
            }
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress summary."""
        return {
            "phase": self.current_phase.value,
            "output_id": self.current_output_id,
            "output_name": self.current_output_name,
            "assessment_progress": f"{self.current_edge_index}/{len(self.edges_to_assess)}" if self.edges_to_assess else "0/0",
            "graph_summary": self.graph.get_graph_summary() if self.graph.graph_id else None
        }
    
    def reset(self):
        """Reset orchestrator for new assessment."""
        self.current_phase = AssessmentPhase.DISCOVERY
        self.current_output_id = None
        self.current_output_name = None
        self.required_quality = None
        self.edges_to_assess = []
        self.current_edge_index = 0
        
        # Reset graph
        self.graph = GraphManager(
            firebase_client=self.firebase,
            user_id=self.session.user_id,
            logger=self.logger
        )
        
        # Reset session
        self.session.reset()
        
        if self.logger:
            self.logger.info("orchestrator_reset", "Orchestrator reset for new assessment")
