"""
Two-pass context extractor: Raw triplet capture → Structured refinement

Pass 1: Liberal capture of everything mentioned (simple triplets)
Pass 2: Conservative refinement into structured ExtractedContext (Python logic)
"""

import sys
import os
from typing import Optional
import re

# Add src directory to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from core.llm_client import LLMClient
from schemas import (
    ExtractedContext, Output, Team, System, Process, 
    Assessment, Dependency, RootCause, MissingInformation
)


class TwoPassExtractor:
    """Extract context using two-pass approach: raw capture → structured refinement."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the two-pass extractor.
        
        Args:
            llm_client: Existing LLMClient instance. If None, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        self.model_name = self.llm_client.model_name
        
        # Pass 1: Simple prompt for raw capture
        self.pass1_prompt = """Extract everything mentioned in this message as simple triplets.

Format: TYPE | name | properties (key:value pairs separated by commas)

Types:
- THING: Any output, deliverable, metric, or thing being discussed
- ACTOR: Any team, person, or group mentioned
- TOOL: Any system, software, or tool
- ACTIVITY: Any process, workflow, or action
- QUALITY: Any assessment, rating, or quality statement
- LINK: Any relationship or dependency (use -> for direction)
- PROBLEM: Any issue, root cause, or explanation
- UNCLEAR: Ambiguous reference needing clarification (like "it", "they", "the system")

Rules:
- Capture EVERYTHING mentioned or implied
- Use UNCLEAR for pronouns and vague references
- For LINK, use format: source -> target
- Include context clues in properties

Examples:

"CRM data quality is bad because sales team hates documentation"
→
THING | CRM data quality | related_to:CRM, domain:sales
TOOL | CRM | type:system
ACTOR | sales team | role:data_entry
ACTIVITY | documentation | owner:sales team, related_to:CRM data quality
QUALITY | bad | target:CRM data quality, keyword:bad
LINK | documentation -> CRM data quality | type:affects
PROBLEM | sales team hates documentation | affects:CRM data quality, reason:behavioral

"It's broken because they never test it properly"
→
UNCLEAR | it | context:is broken, type:thing
UNCLEAR | they | context:never test, type:actor
ACTIVITY | testing | owner:they, target:it, quality:never properly
QUALITY | broken | target:it, keyword:broken
PROBLEM | never test properly | affects:it, reason:process_issue

"Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"
→
THING | sales forecasts | domain:sales
THING | inventory planning | domain:operations
THING | inventory levels | domain:operations, symptom:overstock
QUALITY | terrible | target:sales forecasts, keyword:terrible
QUALITY | impossible | target:inventory planning, keyword:impossible
QUALITY | overstock | target:inventory levels, keyword:overstock
LINK | sales forecasts -> inventory planning | type:blocks
LINK | inventory planning -> inventory levels | type:causes_problem
PROBLEM | poor sales forecasts | affects:inventory planning, reason:dependency
PROBLEM | poor inventory planning | affects:inventory levels, reason:dependency

Message: {user_message}

Triplets:"""

    def extract(self, user_message: str) -> ExtractedContext:
        """
        Extract structured context using two-pass approach.
        
        Args:
            user_message: The user's message to analyze
            
        Returns:
            ExtractedContext object with all extracted information
        """
        # Pass 1: Get raw triplets from LLM
        raw_triplets = self._extract_raw_triplets(user_message)
        
        # Pass 2: Refine triplets into structured context (Python logic)
        context = self._refine_to_context(raw_triplets)
        
        return context
    
    def _extract_raw_triplets(self, user_message: str) -> str:
        """
        Pass 1: Extract raw triplets from user message.
        
        Args:
            user_message: The user's message
            
        Returns:
            Raw triplet string from LLM
        """
        prompt = self.pass1_prompt.format(user_message=user_message)
        
        response = self.llm_client.generate(
            prompt=prompt,
            temperature=0.1,
            max_output_tokens=2048,
            caller="two_pass_extractor_pass1"
        )
        
        return response.strip()
    
    def _refine_to_context(self, raw_triplets: str) -> ExtractedContext:
        """
        Pass 2: Refine raw triplets into structured ExtractedContext.
        
        Args:
            raw_triplets: Raw triplet string from Pass 1
            
        Returns:
            Structured ExtractedContext
        """
        # Parse triplets
        triplets = self._parse_triplets(raw_triplets)
        
        # Initialize collections
        outputs = []
        teams = []
        systems = []
        processes = []
        assessments = []
        dependencies = []
        root_causes = []
        missing_info = []
        
        # Track entity names for reference resolution
        entity_names = set()
        unclear_entities = {}  # placeholder -> context
        
        # First pass: Collect entities and track names
        for triplet in triplets:
            entity_type = triplet['type']
            name = triplet['name']
            props = triplet['properties']
            
            if entity_type == 'THING':
                output = self._create_output(name, props)
                outputs.append(output)
                entity_names.add(name)
                
            elif entity_type == 'ACTOR':
                team = self._create_team(name, props)
                teams.append(team)
                entity_names.add(name)
                
            elif entity_type == 'TOOL':
                system = self._create_system(name, props)
                systems.append(system)
                entity_names.add(name)
                
            elif entity_type == 'ACTIVITY':
                process = self._create_process(name, props)
                processes.append(process)
                entity_names.add(name)
                
            elif entity_type == 'UNCLEAR':
                # Track unclear entities for missing_information
                context = props.get('context', f"User mentioned '{name}'")
                entity_subtype = props.get('type', 'other')
                unclear_entities[name] = {
                    'context': context,
                    'type': entity_subtype
                }
        
        # Second pass: Process relationships and assessments
        for triplet in triplets:
            entity_type = triplet['type']
            name = triplet['name']
            props = triplet['properties']
            
            if entity_type == 'QUALITY':
                assessment = self._create_assessment(name, props)
                if assessment:
                    assessments.append(assessment)
                    
            elif entity_type == 'LINK':
                dependency = self._create_dependency(name, props)
                if dependency:
                    dependencies.append(dependency)
                    
            elif entity_type == 'PROBLEM':
                root_cause = self._create_root_cause(name, props)
                if root_cause:
                    root_causes.append(root_cause)
        
        # Create missing_information entries for UNCLEAR entities
        for unclear_name, info in unclear_entities.items():
            # Map 'thing' to 'output', 'actor' to 'team'
            entity_type_map = {
                'thing': 'output',
                'actor': 'team',
                'system': 'system',
                'process': 'process'
            }
            entity_type = entity_type_map.get(info['type'], 'other')
            placeholder = f"[unclear_{entity_type}]"
            question = self._generate_clarification_question(unclear_name, info)
            
            missing_info.append(MissingInformation(
                entity_type=entity_type,
                context=info['context'],
                question=question,
                placeholder_name=placeholder
            ))
            
            # Add placeholder entities
            if info['type'] == 'thing':
                outputs.append(Output(name=placeholder))
            elif info['type'] == 'actor':
                teams.append(Team(name=placeholder))
        
        return ExtractedContext(
            outputs=outputs,
            teams=teams,
            systems=systems,
            processes=processes,
            assessments=assessments,
            dependencies=dependencies,
            root_causes=root_causes,
            missing_information=missing_info
        )
    
    def _parse_triplets(self, raw_triplets: str) -> list[dict]:
        """Parse raw triplet string into structured list."""
        triplets = []
        
        for line in raw_triplets.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse: TYPE | name | properties
            parts = line.split('|')
            if len(parts) < 2:
                continue
            
            entity_type = parts[0].strip()
            name = parts[1].strip()
            properties = self._parse_properties(parts[2].strip() if len(parts) > 2 else '')
            
            triplets.append({
                'type': entity_type,
                'name': name,
                'properties': properties
            })
        
        return triplets
    
    def _parse_properties(self, prop_string: str) -> dict:
        """Parse property string into dict."""
        props = {}
        if not prop_string:
            return props
        
        # Split by comma, handle key:value pairs
        for pair in prop_string.split(','):
            pair = pair.strip()
            if ':' in pair:
                key, value = pair.split(':', 1)
                props[key.strip()] = value.strip()
        
        return props
    
    def _create_output(self, name: str, props: dict) -> Output:
        """Create Output from triplet."""
        return Output(
            name=name,
            domain=props.get('domain'),
            system=props.get('related_to') or props.get('system'),
            stakeholder=props.get('stakeholder')
        )
    
    def _create_team(self, name: str, props: dict) -> Team:
        """Create Team from triplet."""
        # Normalize role to use underscores
        role = props.get('role')
        if role:
            role = role.replace(' ', '_').replace('-', '_')
        
        return Team(name=name, role=role)
    
    def _create_system(self, name: str, props: dict) -> System:
        """Create System from triplet."""
        return System(
            name=name,
            type=props.get('type')
        )
    
    def _create_process(self, name: str, props: dict) -> Process:
        """Create Process from triplet."""
        return Process(
            name=name,
            owner=props.get('owner'),
            system=props.get('system'),
            description=props.get('description') or props.get('quality')
        )
    
    def _create_assessment(self, name: str, props: dict) -> Optional[Assessment]:
        """Create Assessment from QUALITY triplet."""
        target = props.get('target')
        keyword = props.get('keyword', name)
        
        if not target:
            return None
        
        # Map keyword to rating
        rating = self._keyword_to_rating(keyword)
        sentiment = self._rating_to_sentiment(rating)
        
        return Assessment(
            target=target,
            rating=rating,
            explicit=False,  # Triplets are always inferred
            sentiment=sentiment,
            keyword=keyword,
            symptom=props.get('symptom')
        )
    
    def _create_dependency(self, name: str, props: dict) -> Optional[Dependency]:
        """Create Dependency from LINK triplet."""
        # Parse "source -> target" format
        if '->' in name:
            parts = name.split('->')
            from_entity = parts[0].strip()
            to_entity = parts[1].strip() if len(parts) > 1 else None
        else:
            return None
        
        if not to_entity:
            return None
        
        # Map type
        dep_type = props.get('type', 'input')
        if dep_type == 'affects':
            dep_type = 'input'
        elif dep_type == 'blocks':
            dep_type = 'blocks'
        elif dep_type == 'causes_problem':
            dep_type = 'causes_problem'
        else:
            dep_type = 'input'
        
        return Dependency(
            **{
                'from': from_entity,
                'to': to_entity,
                'type': dep_type,
                'impact': props.get('impact')
            }
        )
    
    def _create_root_cause(self, name: str, props: dict) -> Optional[RootCause]:
        """Create RootCause from PROBLEM triplet."""
        output = props.get('affects')
        reason = props.get('reason', 'unknown')
        
        if not output:
            return None
        
        # Map reason to component
        component_map = {
            'dependency': 'dependency_quality',
            'behavioral': 'team_execution',
            'process_issue': 'process_maturity',
            'process': 'process_maturity',
            'system': 'system_support',
            'tool': 'system_support'
        }
        
        component = component_map.get(reason, 'team_execution')
        
        return RootCause(
            output=output,
            component=component,
            description=name,
            upstream=props.get('upstream')
        )
    
    def _keyword_to_rating(self, keyword: str) -> int:
        """Map quality keyword to 1-5 rating."""
        keyword = keyword.lower()
        
        if keyword in ['terrible', 'broken', 'impossible', 'blind']:
            return 1
        elif keyword in ['bad', 'poor', 'unreliable', 'overstock']:
            return 2
        elif keyword in ['okay', 'acceptable', 'moderate']:
            return 3
        elif keyword in ['good', 'solid']:
            return 4
        elif keyword in ['excellent', 'outstanding', 'perfect']:
            return 5
        else:
            return 2  # Default to bad if unknown
    
    def _rating_to_sentiment(self, rating: int) -> str:
        """Map rating to sentiment."""
        if rating == 1:
            return 'very_negative'
        elif rating == 2:
            return 'negative'
        elif rating == 3:
            return 'neutral'
        elif rating == 4:
            return 'positive'
        else:
            return 'very_positive'
    
    def _generate_clarification_question(self, unclear_name: str, info: dict) -> str:
        """Generate clarification question for unclear entity."""
        entity_type = info['type']
        context = info['context']
        
        if entity_type == 'thing':
            return f"What specifically is '{unclear_name}'? (e.g., a system, feature, process, or output?)"
        elif entity_type == 'actor':
            return f"Which team or group does '{unclear_name}' refer to?"
        elif entity_type == 'system':
            return f"Which system or tool is '{unclear_name}'?"
        else:
            return f"Can you clarify what '{unclear_name}' refers to?"
    
    def extract_batch(self, messages: list[str]) -> list[ExtractedContext]:
        """
        Extract context from multiple messages.
        
        Args:
            messages: List of user messages
            
        Returns:
            List of ExtractedContext objects
        """
        return [self.extract(msg) for msg in messages]


def create_extractor(llm_client: Optional[LLMClient] = None) -> TwoPassExtractor:
    """
    Factory function to create a two-pass context extractor.
    
    Args:
        llm_client: Optional existing LLMClient instance
        
    Returns:
        Configured TwoPassExtractor instance
    """
    return TwoPassExtractor(llm_client=llm_client)
