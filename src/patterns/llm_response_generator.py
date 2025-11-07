"""
LLM Response Generator - Day 10 (Release 2.2)

Generates actual responses from composed components (reactive + proactive).

Architecture:
1. Build prompt from ComposedResponse + context
2. Call Gemini API (via existing LLMClient) with appropriate parameters
3. Return generated response

Token Optimization:
- Uses selective context (from PatternEngine)
- Respects token budgets per component
- Generates concise, focused responses

Note: Uses existing src/core/llm_client.py (Gemini via Vertex AI)
"""
from typing import Dict, Any, Optional
from src.core.llm_client import LLMClient
from src.patterns.response_composer import ComposedResponse, ResponseComponent


class LLMResponseGenerator:
    """
    Generates LLM responses from composed components.
    
    Features:
    - Prompt building for reactive + proactive composition
    - Sequential composition (reactive first, then proactive)
    - Token budget enforcement
    - Error handling
    
    Uses existing LLMClient (Gemini via Vertex AI) for consistency.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize LLM response generator.
        
        Args:
            llm_client: Optional LLMClient instance. If not provided, creates new one.
        """
        self.client = llm_client or LLMClient()
        self.caller_id = "pattern_response_generator"
    
    def generate_response(
        self,
        composed: ComposedResponse,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate LLM response from composed components.
        
        Args:
            composed: ComposedResponse with reactive + proactive components
            context: Context dict with message, knowledge, state
            
        Returns:
            Generated response string
        """
        try:
            # Build prompt (includes system instructions)
            prompt = self.build_prompt(composed, context)
            
            # Calculate max OUTPUT tokens
            # Note: total_tokens is the budget for the RESPONSE, not including prompt
            # Add generous buffer to allow natural completion (not cut off mid-sentence)
            # Gemini sometimes cuts off early, so we use 2x the budget
            max_tokens = int(composed.total_tokens * 2)
            
            # Call Gemini via existing LLMClient
            response = self.client.generate(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=max_tokens,
                caller=self.caller_id
            )
            
            return response
            
        except Exception as e:
            # Fallback on error
            return self._generate_fallback_response(e)
    
    def build_prompt(
        self,
        composed: ComposedResponse,
        context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for LLM from composed components and context.
        
        Includes system instructions at the top (Gemini doesn't have separate system role).
        
        Args:
            composed: ComposedResponse with reactive + proactive components
            context: Context dict with message, knowledge, state
            
        Returns:
            Prompt string
        """
        parts = []
        
        # System instructions (at top for Gemini)
        parts.append("# System Role")
        parts.append(self._get_system_prompt())
        parts.append("")
        parts.append("---")
        parts.append("")
        
        # User message
        message = context.get('message', '')
        parts.append(f"# User Message")
        parts.append(f"\"{message}\"")
        parts.append("")
        
        # Conversation state (minimal)
        conv_state = context.get('conversation_state', {})
        turn_count = conv_state.get('turn_count', 0)
        if turn_count > 0:
            parts.append(f"# Conversation Context")
            parts.append(f"Turn: {turn_count}")
            parts.append("")
        
        # Relevant knowledge (if any)
        knowledge = context.get('relevant_knowledge', {})
        if knowledge:
            parts.append("# Relevant Context:")
            for key, value in knowledge.items():
                parts.append(f"  - {key}: {value}")
            parts.append("")
        
        # Response structure
        parts.append("# Your Response Should:")
        parts.append(f"")
        parts.append(f"## 1. REACTIVE (answer user directly):")
        parts.append(f"   - Pattern: {composed.reactive.pattern.get('id', 'N/A')}")
        parts.append(f"   - Category: {composed.reactive.pattern.get('category', 'N/A')}")
        
        behaviors = composed.reactive.pattern.get('behaviors', [])
        if behaviors:
            parts.append(f"   - Behaviors: {', '.join(behaviors)}")
        
        parts.append(f"   - Budget: ~{composed.reactive.token_budget} tokens")
        parts.append("")
        
        # Proactive components (if any)
        if composed.proactive:
            for i, proactive in enumerate(composed.proactive, start=2):
                parts.append(f"## {i}. PROACTIVE (advance conversation):")
                parts.append(f"   - Pattern: {proactive.pattern.get('id', 'N/A')}")
                parts.append(f"   - Category: {proactive.pattern.get('category', 'N/A')}")
                
                behaviors = proactive.pattern.get('behaviors', [])
                if behaviors:
                    parts.append(f"   - Behaviors: {', '.join(behaviors)}")
                
                parts.append(f"   - Budget: ~{proactive.token_budget} tokens")
                parts.append("")
        
        # Instructions
        parts.append("# Instructions:")
        parts.append("- Respond naturally and conversationally")
        parts.append("- Address the reactive part first (answer user)")
        if composed.proactive:
            parts.append("- Then add proactive parts (advance conversation)")
            parts.append("- Keep each part concise and focused")
        parts.append("- Provide a complete, helpful response")
        # Note: Token budget is enforced via max_output_tokens parameter, not in prompt
        
        return "\n".join(parts)
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for LLM.
        
        Returns:
            System prompt string
        """
        return (
            "You are an AI assistant helping users assess their organization's "
            "readiness for AI pilot projects. You guide them through identifying "
            "outputs, rating capabilities, and recommending AI solutions.\n\n"
            "Your responses should be:\n"
            "- Professional but conversational\n"
            "- Concise and focused\n"
            "- Structured (reactive first, then proactive)\n"
            "- Helpful and actionable\n\n"
            "Follow the pattern behaviors specified in each request."
        )
    
    def _generate_fallback_response(self, error: Exception) -> str:
        """
        Generate fallback response on error.
        
        Args:
            error: Exception that occurred
            
        Returns:
            Fallback response string
        """
        return (
            "I encountered an error generating a response. "
            "Let me try to help you anyway - could you rephrase your question?"
        )


def format_response_with_structure(
    reactive_text: str,
    proactive_texts: list[str]
) -> str:
    """
    Format response with clear reactive → proactive structure.
    
    Args:
        reactive_text: Reactive response text
        proactive_texts: List of proactive response texts
        
    Returns:
        Formatted response string
    """
    parts = [reactive_text]
    
    if proactive_texts:
        parts.extend(proactive_texts)
    
    return " ".join(parts)
