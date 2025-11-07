"""
Pydantic schemas for structured context extraction.

These schemas define the structure of information we want to extract
from user messages about business outputs, teams, systems, and processes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Output(BaseModel):
    """A business output (deliverable, artifact, or capability) mentioned or implied in the message."""
    name: str = Field(
        description="EXACT name from user's message (e.g., 'sales forecasts' not 'forecast'). Use '[unclear_output]' for ambiguous references like 'it' or 'that thing'."
    )
    domain: Optional[str] = Field(
        None, 
        description="Business domain using underscores: sales, operations, customer_support, data, project_management. Leave None if unclear."
    )
    system: Optional[str] = Field(None, description="Primary system producing this output, if mentioned")
    stakeholder: Optional[str] = Field(None, description="Who consumes/uses this output, if mentioned")


class Team(BaseModel):
    """A team or group of people mentioned or implied (including pronouns like 'they')."""
    name: str = Field(
        description="EXACT team name from message (e.g., 'sales team'). Use '[team_they_refer_to]' for unclear pronouns like 'they' or 'the team'."
    )
    role: Optional[str] = Field(
        None, 
        description="Role using underscores: data_entry, development, support, stakeholder, data_quality, data_engineer. Leave None if unclear."
    )


class System(BaseModel):
    """A software system or tool mentioned or implied."""
    name: str = Field(
        description="EXACT system name from message (e.g., 'CRM', 'JIRA'). Use '[system_mentioned]' for vague references like 'the system' or 'the tool'."
    )
    type: Optional[str] = Field(
        None, 
        description="System type: software_system, database, crm, project_management_system, data_pipeline, observability. Leave None if unclear."
    )


class Process(BaseModel):
    """A business process or workflow described or implied."""
    name: str = Field(
        description="Concise process name (e.g., 'sales documentation', 'ticket updates'). Infer from context if not explicitly named."
    )
    owner: Optional[str] = Field(None, description="Team or role that owns this process, if mentioned or inferable")
    system: Optional[str] = Field(None, description="System where process happens, if mentioned")
    description: Optional[str] = Field(None, description="Brief description of what the process does, if mentioned")


class Assessment(BaseModel):
    """An assessment or rating of something. Create ONE assessment per distinct target."""
    target: str = Field(
        description="What is being assessed - use EXACT name from outputs/systems/processes. For cascading problems, create separate assessments for each thing evaluated."
    )
    rating: int = Field(
        description="Quality rating 1-5 stars. Keywords: 1='terrible/broken/impossible', 2='bad/poor/unreliable', 3='okay/acceptable', 4='good/solid', 5='excellent/outstanding'", 
        ge=1, le=5
    )
    explicit: bool = Field(description="True if user gave explicit star rating (e.g., '3 stars'), False if inferred from keywords")
    sentiment: Literal["very_negative", "negative", "neutral", "positive", "very_positive"] = Field(
        description="Sentiment: very_negative for 1 star, negative for 2, neutral for 3, positive for 4, very_positive for 5"
    )
    keyword: Optional[str] = Field(None, description="The keyword that indicated quality (e.g., 'bad', 'excellent', 'terrible')")
    symptom: Optional[str] = Field(None, description="Symptom or impact mentioned (e.g., 'constantly firefighting', 'overstock')")


class Dependency(BaseModel):
    """A dependency relationship between two things. For cascading chains ('X causes Y causes Z'), create multiple: X→Y and Y→Z."""
    from_entity: str = Field(
        alias="from", 
        description="Source entity name - EXACT match to an output/system/process name already extracted"
    )
    to_entity: str = Field(
        alias="to", 
        description="Target entity name - EXACT match to an output/system/process name already extracted"
    )
    type: Literal["input", "blocks", "causes_problem"] = Field(
        description="Type: 'input' (feeds into), 'blocks' (prevents), 'causes_problem' (creates issue)"
    )
    impact: Optional[str] = Field(None, description="Optional description of how the dependency affects the target")


class RootCause(BaseModel):
    """Root cause analysis explaining WHY something is bad/broken."""
    output: str = Field(
        description="Which output has the problem - EXACT match to an output name already extracted"
    )
    component: Literal["dependency_quality", "team_execution", "process_maturity", "system_support"] = Field(
        description="Root cause type: dependency_quality (poor upstream input), team_execution (team capacity/skills/motivation), process_maturity (inadequate process), system_support (inadequate tools)"
    )
    description: str = Field(description="Brief explanation of the root cause")
    upstream: Optional[str] = Field(
        None, 
        description="If component is dependency_quality, name the upstream dependency causing the problem"
    )
    sentiment: Optional[Literal["negative", "neutral", "positive"]] = Field(None, description="Sentiment about the cause")


class MissingInformation(BaseModel):
    """Information that is implied but unclear - needs user clarification. Add entry whenever you use a placeholder name like '[unclear_output]'."""
    entity_type: Literal["output", "team", "system", "process", "other"] = Field(
        description="Type of entity that needs clarification"
    )
    context: str = Field(description="What we know about this entity from the message context")
    question: str = Field(
        description="Specific, conversational question to ask user (e.g., 'What specifically is broken?' or 'Which team are you referring to?')"
    )
    placeholder_name: str = Field(
        description="The placeholder name you used in extraction (e.g., '[unclear_output]', '[team_they_refer_to]', '[system_mentioned]')"
    )


class ExtractedContext(BaseModel):
    """Complete extracted context from a user message."""
    outputs: List[Output] = Field(default_factory=list, description="Business outputs mentioned")
    teams: List[Team] = Field(default_factory=list, description="Teams mentioned")
    systems: List[System] = Field(default_factory=list, description="Systems mentioned")
    processes: List[Process] = Field(default_factory=list, description="Processes mentioned")
    assessments: List[Assessment] = Field(default_factory=list, description="Quality assessments")
    dependencies: List[Dependency] = Field(default_factory=list, description="Dependency relationships")
    root_causes: List[RootCause] = Field(default_factory=list, description="Root cause analysis")
    missing_information: List[MissingInformation] = Field(
        default_factory=list, 
        description="Information that is implied but unclear - needs user clarification"
    )

    class Config:
        populate_by_name = True  # Allow both 'from' and 'from_entity'
