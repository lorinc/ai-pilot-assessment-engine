"""
Test cases for context extraction validation.

Each test case contains:
- user_message: What the user says
- expected: Expected ExtractedContext structure
- difficulty: Simple, Medium, or Complex
- notes: Special considerations
"""

from schemas import (
    ExtractedContext, Output, Team, System, Process,
    Assessment, Dependency, RootCause
)


TEST_CASES = [
    {
        "id": 1,
        "name": "Simple Assessment",
        "difficulty": "Simple",
        "user_message": "The data quality is 3 stars.",
        "expected": ExtractedContext(
            outputs=[],
            teams=[],
            systems=[],
            processes=[],
            assessments=[
                Assessment(
                    target="data quality",
                    rating=3,
                    explicit=True,
                    sentiment="neutral"
                )
            ],
            dependencies=[],
            root_causes=[]
        ),
        "notes": "Clear, explicit rating. No other context."
    },
    
    {
        "id": 2,
        "name": "The Sentence That Broke Us",
        "difficulty": "Complex",
        "user_message": "I think data quality in our CRM is bad because the sales team hates to document their work.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="CRM data quality", domain="sales", system="CRM")
            ],
            teams=[
                Team(name="sales team", role="data_entry")
            ],
            systems=[
                System(name="CRM", type="software_system")
            ],
            processes=[
                Process(
                    name="sales documentation",
                    owner="sales team",
                    description="document their work"
                )
            ],
            assessments=[
                Assessment(
                    target="CRM data quality",
                    rating=2,
                    explicit=False,
                    sentiment="negative",
                    keyword="bad"
                )
            ],
            dependencies=[
                Dependency(**{"from": "sales documentation", "to": "CRM data quality", "type": "input"})
            ],
            root_causes=[
                RootCause(
                    output="CRM data quality",
                    component="team_execution",
                    description="sales team hates to document",
                    sentiment="negative"
                )
            ]
        ),
        "notes": "Multi-entity, implicit rating, causal chain, sentiment analysis."
    },
    
    {
        "id": 3,
        "name": "Multi-Output Dependency Chain",
        "difficulty": "Complex",
        "user_message": "Our sales forecasts are terrible, which makes inventory planning impossible, so we always overstock.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="sales forecasts", domain="sales"),
                Output(name="inventory planning", domain="operations"),
                Output(name="inventory levels", domain="operations")
            ],
            teams=[],
            systems=[],
            processes=[],
            assessments=[
                Assessment(
                    target="sales forecasts",
                    rating=1,
                    explicit=False,
                    sentiment="very_negative",
                    keyword="terrible"
                ),
                Assessment(
                    target="inventory planning",
                    rating=1,
                    explicit=False,
                    sentiment="very_negative",
                    keyword="impossible"
                ),
                Assessment(
                    target="inventory levels",
                    rating=2,
                    explicit=False,
                    sentiment="negative",
                    keyword="overstock"
                )
            ],
            dependencies=[
                Dependency(**{"from": "sales forecasts", "to": "inventory planning", "type": "input", "impact": "blocks"}),
                Dependency(**{"from": "inventory planning", "to": "inventory levels", "type": "input", "impact": "causes_problem"})
            ],
            root_causes=[
                RootCause(
                    output="inventory planning",
                    component="dependency_quality",
                    description="poor sales forecasts",
                    upstream="sales forecasts"
                ),
                RootCause(
                    output="inventory levels",
                    component="dependency_quality",
                    description="poor inventory planning",
                    upstream="inventory planning"
                )
            ]
        ),
        "notes": "Cascading dependencies, multiple outputs, implicit ratings, causal chain."
    },
    
    {
        "id": 4,
        "name": "Team + Process + System",
        "difficulty": "Complex",
        "user_message": "The engineering team uses JIRA but they don't update tickets, so project managers have no visibility.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="project visibility", domain="project_management", stakeholder="project managers")
            ],
            teams=[
                Team(name="engineering team", role="development"),
                Team(name="project managers", role="stakeholder")
            ],
            systems=[
                System(name="JIRA", type="project_management_system")
            ],
            processes=[
                Process(name="ticket updates", owner="engineering team", system="JIRA")
            ],
            assessments=[
                Assessment(
                    target="project visibility",
                    rating=1,
                    explicit=False,
                    sentiment="negative",
                    keyword="no visibility"
                )
            ],
            dependencies=[
                Dependency(**{"from": "ticket updates", "to": "project visibility", "type": "input"})
            ],
            root_causes=[
                RootCause(
                    output="project visibility",
                    component="process_maturity",
                    description="engineering team doesn't update tickets"
                )
            ]
        ),
        "notes": "Multiple teams, process issue, system mentioned but not root cause."
    },
    
    {
        "id": 5,
        "name": "Implicit Assessment with Symptom",
        "difficulty": "Complex",
        "user_message": "We're constantly firefighting because our monitoring is blind to production issues.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="production monitoring", domain="operations")
            ],
            teams=[],
            systems=[
                System(name="monitoring system", type="observability")
            ],
            processes=[],
            assessments=[
                Assessment(
                    target="production monitoring",
                    rating=1,
                    explicit=False,
                    sentiment="very_negative",
                    keyword="blind",
                    symptom="constantly firefighting"
                )
            ],
            dependencies=[],
            root_causes=[
                RootCause(
                    output="production monitoring",
                    component="system_support",
                    description="monitoring system is blind to production issues"
                )
            ]
        ),
        "notes": "Implicit rating, symptom mentioned, system inadequacy."
    },
    
    {
        "id": 6,
        "name": "Positive Assessment",
        "difficulty": "Medium",
        "user_message": "Our customer support team is excellent at resolving tickets quickly.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="ticket resolution", domain="customer_support")
            ],
            teams=[
                Team(name="customer support team", role="support")
            ],
            systems=[],
            processes=[
                Process(name="ticket resolution", owner="customer support team", description="resolving tickets quickly")
            ],
            assessments=[
                Assessment(
                    target="ticket resolution",
                    rating=5,
                    explicit=False,
                    sentiment="very_positive",
                    keyword="excellent"
                )
            ],
            dependencies=[],
            root_causes=[]
        ),
        "notes": "Positive assessment, team execution strength."
    },
    
    {
        "id": 7,
        "name": "Ambiguous Reference",
        "difficulty": "Complex",
        "user_message": "It's broken because they never test it properly.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="[unclear_output]")
            ],
            teams=[
                Team(name="[team_they_refer_to]")
            ],
            systems=[],
            processes=[
                Process(name="testing", owner="[team_they_refer_to]", description="never test it properly")
            ],
            assessments=[
                Assessment(
                    target="[unclear_output]",
                    rating=1,
                    explicit=False,
                    sentiment="very_negative",
                    keyword="broken"
                )
            ],
            dependencies=[],
            root_causes=[
                RootCause(
                    output="[unclear_output]",
                    component="process_maturity",
                    description="never test it properly"
                )
            ]
        ),
        "notes": "Ambiguous pronouns - should extract with placeholders and ask for clarification."
    },
    
    {
        "id": 8,
        "name": "Multiple Systems",
        "difficulty": "Complex",
        "user_message": "Data flows from Salesforce to our data warehouse, but the ETL pipeline is unreliable.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="data warehouse data quality", domain="data")
            ],
            teams=[],
            systems=[
                System(name="Salesforce", type="crm"),
                System(name="data warehouse", type="database"),
                System(name="ETL pipeline", type="data_pipeline")
            ],
            processes=[
                Process(name="data flow", description="flows from Salesforce to data warehouse")
            ],
            assessments=[
                Assessment(
                    target="ETL pipeline",
                    rating=2,
                    explicit=False,
                    sentiment="negative",
                    keyword="unreliable"
                )
            ],
            dependencies=[
                Dependency(**{"from": "Salesforce", "to": "data warehouse", "type": "input"})
            ],
            root_causes=[
                RootCause(
                    output="data warehouse data quality",
                    component="system_support",
                    description="ETL pipeline is unreliable"
                )
            ]
        ),
        "notes": "Multiple systems, data flow, system reliability issue."
    },
    
    {
        "id": 9,
        "name": "Partial Information",
        "difficulty": "Simple",
        "user_message": "I want to work on sales forecasting.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="sales forecasting", domain="sales")
            ],
            teams=[],
            systems=[],
            processes=[],
            assessments=[],
            dependencies=[],
            root_causes=[]
        ),
        "notes": "User intent to focus on output, no assessment or problem."
    },
    
    {
        "id": 10,
        "name": "Comparative Assessment",
        "difficulty": "Complex",
        "user_message": "Our data quality used to be 4 stars, but now it's down to 2 because we lost our data engineer.",
        "expected": ExtractedContext(
            outputs=[
                Output(name="data quality")
            ],
            teams=[
                Team(name="data engineering", role="data_quality")
            ],
            systems=[],
            processes=[],
            assessments=[
                Assessment(
                    target="data quality",
                    rating=2,
                    explicit=True,
                    sentiment="negative"
                )
            ],
            dependencies=[],
            root_causes=[
                RootCause(
                    output="data quality",
                    component="team_execution",
                    description="lost our data engineer"
                )
            ]
        ),
        "notes": "Temporal comparison, explicit current rating, team capacity issue."
    }
]
