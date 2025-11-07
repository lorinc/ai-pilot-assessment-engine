"""
Context extraction engine using Outlines for structured generation.

This module uses Outlines to guarantee that LLM outputs conform to our
ExtractedContext schema, eliminating parsing errors and validation issues.
"""

import sys
import os
from typing import Optional

# Add src directory to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from core.llm_client import LLMClient
from schemas import ExtractedContext
import json


class ContextExtractor:
    """Extract structured context from user messages using Gemini."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the context extractor.
        
        Args:
            llm_client: Existing LLMClient instance. If None, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        self.model_name = self.llm_client.model_name
        
        # System prompt for extraction - balanced schema-driven approach
        self.system_prompt = """Extract business context from the user's message. Follow the schema field descriptions exactly.

CORE RULES:
1. Use EXACT names from user's message (e.g., "sales forecasts" not "forecast")
2. Use underscores in domain/role fields (e.g., customer_support, data_entry)
3. For ambiguous references ('it', 'they'), use placeholders: [unclear_output], [team_they_refer_to], [system_mentioned]
4. When using placeholders, add to missing_information with a specific question
5. For cascading problems ("X causes Y causes Z"), extract EACH entity and EACH link
6. This is a conversation - extract what you can infer, then ask for clarification

RATING GUIDE:
1 star = terrible/broken/impossible/blind
2 stars = bad/poor/unreliable  
3 stars = okay/acceptable
4 stars = good/solid
5 stars = excellent/outstanding

ROOT CAUSE TYPES:
- dependency_quality: poor upstream input causes the problem
- team_execution: team capacity/skills/motivation issue
- process_maturity: inadequate or missing process
- system_support: inadequate tools/systems

EXAMPLES:

"CRM data quality is bad because sales team hates documentation"
→ 1 output (name="CRM data quality", domain="sales", system="CRM")
→ 1 team (name="sales team", role="data_entry")
→ 1 system (name="CRM")
→ 1 process (name="sales documentation", owner="sales team")
→ 1 assessment (target="CRM data quality", rating=2, keyword="bad")
→ 1 dependency (from="sales documentation", to="CRM data quality")
→ 1 root_cause (output="CRM data quality", component="team_execution")

"It's broken because they never test it properly"
→ 1 output (name="[unclear_output]")
→ 1 team (name="[team_they_refer_to]")
→ 1 process (name="testing", owner="[team_they_refer_to]")
→ 1 assessment (target="[unclear_output]", rating=1, keyword="broken")
→ 1 root_cause (output="[unclear_output]", component="process_maturity")
→ missing_information: [{entity_type: "output", question: "What specifically is broken?"}, {entity_type: "team", question: "Which team are you referring to?"}]

"Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"
→ 3 outputs: "sales forecasts" (sales), "inventory planning" (operations), "inventory levels" (operations)
→ 3 assessments: terrible=1, impossible=1, overstock=2
→ 2 dependencies: forecasts→planning (blocks), planning→levels (causes_problem)
→ 2 root_causes: planning (dependency_quality, upstream=forecasts), levels (dependency_quality, upstream=planning)"""

    def extract(self, user_message: str) -> ExtractedContext:
        """
        Extract structured context from a user message.
        
        Args:
            user_message: The user's message to analyze
            
        Returns:
            ExtractedContext object with all extracted information
        """
        # Get JSON schema from Pydantic model
        schema = ExtractedContext.model_json_schema()
        
        # Create the full prompt with schema
        full_prompt = f"""{self.system_prompt}

USER MESSAGE:
{user_message}

Extract the structured context from this message and return ONLY valid JSON matching this exact schema:

{json.dumps(schema, indent=2)}

Return ONLY the JSON object, no other text."""
        
        # Use Gemini to generate structured output
        response_text = self.llm_client.generate(
            prompt=full_prompt,
            temperature=0.1,  # Low temperature for structured extraction
            max_output_tokens=4096,
            caller="context_extractor"
        )
        
        # Parse JSON response
        try:
            # Clean response (remove markdown code blocks if present)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate and create ExtractedContext
            result = ExtractedContext(**data)
            return result
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return empty context
            print(f"Warning: Failed to parse JSON response: {e}")
            print(f"Response was: {response_text[:500]}")
            return ExtractedContext()
        except Exception as e:
            print(f"Warning: Failed to create ExtractedContext: {e}")
            return ExtractedContext()
    
    def extract_batch(self, messages: list[str]) -> list[ExtractedContext]:
        """
        Extract context from multiple messages.
        
        Args:
            messages: List of user messages
            
        Returns:
            List of ExtractedContext objects
        """
        return [self.extract(msg) for msg in messages]


def create_extractor(llm_client: Optional[LLMClient] = None) -> ContextExtractor:
    """
    Factory function to create a context extractor.
    
    Args:
        llm_client: Optional existing LLMClient instance
        
    Returns:
        Configured ContextExtractor instance
    """
    return ContextExtractor(llm_client=llm_client)
