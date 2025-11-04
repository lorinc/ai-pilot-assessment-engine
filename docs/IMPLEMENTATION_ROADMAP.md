# Implementation Roadmap - Testable Increments

**Version:** 1.0  
**Date:** 2025-11-04  
**Purpose:** Define testable implementation increments with clear success criteria

**Source:** `output_centric_factor_model_exploration.md` Increments 1-3

---

## Overview

The implementation follows 3 testable increments, each building on the previous:

1. **Increment 1:** Single Output Assessment (3-5 days)
2. **Increment 2:** Output Dependencies (4-6 days)
3. **Increment 3:** Root Cause Decomposition (5-7 days)

**Total Estimated Time:** 12-18 days

---

## Increment 1: Single Output-Centric Factor Assessment

**Goal:** User can assess capability to deliver ONE specific output in conversation

**Duration:** 3-5 days

### What Gets Built

#### 1.1 Data Model Updates
**Files:** `models/data_models.py`

**Changes:**
- ✅ Keep `Output` model (already exists)
- ✅ Keep `CreationContext` model (already exists)
- ❌ Remove `ComponentAssessment` (replace with simpler structure)
- ❌ Remove `QualityAssessment` (not needed in output-centric model)
- ❌ Remove `PilotRecommendation` (will rebuild later)
- ✅ Add `OutputFactor` model:

```python
class ComponentRating(BaseModel):
    """Rating for a single component (1-5 stars)."""
    rating: int = Field(..., ge=1, le=5)
    description: str = Field(..., description="User's description")
    confidence: float = Field(0.8, ge=0.0, le=1.0)

class OutputFactor(BaseModel):
    """Output-centric factor assessment."""
    output: Output
    context: CreationContext
    
    # 4 components (1-5 stars each)
    dependency_quality: ComponentRating
    team_execution: ComponentRating
    process_maturity: ComponentRating
    system_support: ComponentRating
    
    # Calculated fields
    factor_value: int = Field(..., ge=1, le=5, description="MIN of components")
    bottlenecks: List[str] = Field(..., description="Components at MIN value")
    
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def calculate_factor(self) -> int:
        """Calculate factor as MIN of all components."""
        return min(
            self.dependency_quality.rating,
            self.team_execution.rating,
            self.process_maturity.rating,
            self.system_support.rating
        )
    
    def identify_bottlenecks(self) -> List[str]:
        """Identify components at MIN value."""
        min_val = self.factor_value
        bottlenecks = []
        if self.dependency_quality.rating == min_val:
            bottlenecks.append("dependency_quality")
        if self.team_execution.rating == min_val:
            bottlenecks.append("team_execution")
        if self.process_maturity.rating == min_val:
            bottlenecks.append("process_maturity")
        if self.system_support.rating == min_val:
            bottlenecks.append("system_support")
        return bottlenecks
```

#### 1.2 Session Manager Updates
**Files:** `core/session_manager.py`

**Changes:**
- ❌ Remove `phase` tracking (no more phases)
- ❌ Remove `current_component` tracking
- ✅ Add `current_factor: Optional[OutputFactor]` to session
- ✅ Simplify to track: output, context, factor, messages

```python
class SessionManager:
    """Manages assessment session state."""
    
    def __init__(self, state):
        self.state = state
        
        # Initialize session
        if 'session' not in self.state or self.state.session is None:
            self.state.session = AssessmentSession(
                session_id=f"sess_{uuid.uuid4().hex[:8]}",
                created_at=datetime.utcnow().isoformat() + "Z"
            )
    
    @property
    def output(self) -> Optional[Output]:
        """Get current output."""
        return self.state.session.output
    
    @output.setter
    def output(self, value: Output):
        """Set current output."""
        self.state.session.output = value
    
    @property
    def context(self) -> Optional[CreationContext]:
        """Get current context."""
        return self.state.session.context
    
    @context.setter
    def context(self, value: CreationContext):
        """Set current context."""
        self.state.session.context = value
    
    @property
    def factor(self) -> Optional[OutputFactor]:
        """Get current factor assessment."""
        return getattr(self.state.session, 'factor', None)
    
    @factor.setter
    def factor(self, value: OutputFactor):
        """Set current factor assessment."""
        self.state.session.factor = value
```

#### 1.3 Conversation Flow
**Files:** `app.py`

**Changes:**
- ✅ Use DiscoveryEngine for output identification (already built)
- ✅ Add 4-component question flow
- ✅ Calculate MIN() and identify bottlenecks
- ✅ Display results

**Conversation Flow:**
```python
# 1. Output identification (existing DiscoveryEngine)
if not session_manager.output:
    output, confidence, matches = discovery_engine.identify_output(user_message)
    if output:
        session_manager.output = output
        context = discovery_engine.infer_context(output)
        session_manager.context = context
        # Ask for component ratings
        st.write("Let's assess the capability to deliver {output.name}...")

# 2. Component questions (new)
if session_manager.output and not session_manager.factor:
    # Show 4 questions with star rating inputs
    dep_rating = st.slider("1. Dependency Quality (1-5 stars)", 1, 5, 3)
    team_rating = st.slider("2. Team Execution (1-5 stars)", 1, 5, 3)
    proc_rating = st.slider("3. Process Maturity (1-5 stars)", 1, 5, 3)
    sys_rating = st.slider("4. System Support (1-5 stars)", 1, 5, 3)
    
    if st.button("Calculate Factor"):
        factor = OutputFactor(
            output=session_manager.output,
            context=session_manager.context,
            dependency_quality=ComponentRating(rating=dep_rating, description="..."),
            team_execution=ComponentRating(rating=team_rating, description="..."),
            process_maturity=ComponentRating(rating=proc_rating, description="..."),
            system_support=ComponentRating(rating=sys_rating, description="...")
        )
        factor.factor_value = factor.calculate_factor()
        factor.bottlenecks = factor.identify_bottlenecks()
        session_manager.factor = factor

# 3. Display results (new)
if session_manager.factor:
    st.write(f"Factor Value: {'⭐' * session_manager.factor.factor_value}")
    st.write(f"Bottlenecks: {', '.join(session_manager.factor.bottlenecks)}")
```

### Test Scenario

**User Input:**
```
"Our sales team struggles to produce accurate forecasts in the CRM system"
```

**System Actions:**
1. DiscoveryEngine extracts: Output="Sales Forecast", Team="Sales Team", System="CRM"
2. Creates Output entity (if not exists)
3. Infers context from taxonomy
4. Asks 4 component questions:
   - Q1: "How would you rate the quality of data you receive from upstream sources? (1-5 stars)"
   - User: "3 stars - customer data is okay but not great"
   - Q2: "How would you rate your team's skills and resources? (1-5 stars)"
   - User: "3 stars - decent but we lack ML expertise"
   - Q3: "How mature is your forecasting process? (1-5 stars)"
   - User: "2 stars - very ad-hoc, no standard process"
   - Q4: "How well does your CRM system support forecasting? (1-5 stars)"
   - User: "2 stars - no built-in forecasting tools"
5. Calculates: `factor_value = MIN(3, 3, 2, 2) = 2 stars`
6. Identifies bottlenecks: `["process_maturity", "system_support"]`
7. Stores OutputFactor in session

**Verification:**
```python
# Check session state
assert session_manager.output.id == "sales_forecast"
assert session_manager.output.name == "Sales Forecast"
assert session_manager.context.team == "Sales Operations"
assert session_manager.context.system == "Salesforce CRM"

# Check factor
assert session_manager.factor.factor_value == 2
assert "process_maturity" in session_manager.factor.bottlenecks
assert "system_support" in session_manager.factor.bottlenecks

# Check component ratings
assert session_manager.factor.dependency_quality.rating == 3
assert session_manager.factor.team_execution.rating == 3
assert session_manager.factor.process_maturity.rating == 2
assert session_manager.factor.system_support.rating == 2
```

### Success Criteria

- ✅ User can describe an output problem in natural language
- ✅ System extracts Output + Team + Process + System
- ✅ System asks 4 component questions (1-5 stars each)
- ✅ System calculates factor as MIN(components)
- ✅ System identifies bottleneck(s) (components at MIN value)
- ✅ Session stores output-centric factor with context
- ✅ End-to-end conversation → storage → retrieval works

### Files Modified

- `models/data_models.py` - Add OutputFactor, ComponentRating
- `core/session_manager.py` - Remove phases, add factor tracking
- `app.py` - Add 4-component question flow, MIN() calculation
- `tests/unit/test_data_models.py` - Add OutputFactor tests
- `tests/unit/test_session_manager.py` - Update for new structure

---

## Increment 2: Output Dependency Chain (2 Outputs)

**Goal:** User can identify that Output A depends on Output B, system traces quality impact

**Duration:** 4-6 days

### What Gets Built

#### 2.1 Data Model Updates
**Files:** `models/data_models.py`

**Add:**
```python
class OutputDependency(BaseModel):
    """Dependency between two outputs."""
    source_output_id: str = Field(..., description="Output being depended on")
    target_output_id: str = Field(..., description="Output that depends on source")
    strength: int = Field(..., ge=1, le=5, description="How critical (1-5 stars)")
    description: Optional[str] = None
```

#### 2.2 Session Manager Updates
**Files:** `core/session_manager.py`

**Add:**
```python
@property
def dependencies(self) -> List[OutputDependency]:
    """Get output dependencies."""
    return getattr(self.state.session, 'dependencies', [])

def add_dependency(self, dependency: OutputDependency):
    """Add output dependency."""
    if not hasattr(self.state.session, 'dependencies'):
        self.state.session.dependencies = []
    self.state.session.dependencies.append(dependency)
```

#### 2.3 Dependency Detection
**Files:** `engines/discovery.py` (extend)

**Add:**
```python
def detect_dependencies(self, user_message: str, current_output: Output) -> List[Dict]:
    """
    Detect mentions of upstream outputs in user message.
    
    Args:
        user_message: User's description
        current_output: Current output being assessed
        
    Returns:
        List of potential dependencies
    """
    # Extract keywords
    keywords = self.extract_keywords(user_message)
    
    # Search for other outputs
    matches = self.taxonomy.search_outputs(keywords)
    
    # Filter out current output
    dependencies = [
        match for match in matches 
        if match["output"]["id"] != current_output.id
    ]
    
    return dependencies
```

#### 2.4 Conversation Flow
**Files:** `app.py`

**Add dependency detection:**
```python
# After component questions, ask about dependencies
if session_manager.factor and not session_manager.dependencies:
    st.write("Does {output.name} depend on any upstream outputs?")
    
    # Detect potential dependencies from conversation
    if "depends on" in user_message or "relies on" in user_message:
        potential_deps = discovery_engine.detect_dependencies(
            user_message, 
            session_manager.output
        )
        
        if potential_deps:
            st.write("I detected these potential dependencies:")
            for i, dep in enumerate(potential_deps[:3], 1):
                st.write(f"{i}. {dep['output']['name']}")
            
            selected = st.selectbox("Select dependency", ...)
            strength = st.slider("How critical is this dependency? (1-5 stars)", 1, 5, 3)
            
            if st.button("Add Dependency"):
                dependency = OutputDependency(
                    source_output_id=selected["output"]["id"],
                    target_output_id=session_manager.output.id,
                    strength=strength
                )
                session_manager.add_dependency(dependency)
```

### Test Scenario

**Setup:**
- Output A = "Sales Forecast" (factor_value=2)
- Output B = "Clean Customer Data" (factor_value=3)

**User Input:**
```
"Sales forecasts depend heavily on clean customer data from the data engineering team"
```

**System Actions:**
1. Detects mention of "clean customer data"
2. Searches taxonomy, finds Output B
3. Asks: "How critical is clean customer data for sales forecasts? (1-5 stars)"
4. User: "5 stars - absolutely critical"
5. Creates OutputDependency: source=B, target=A, strength=5
6. Stores dependency

**System Response:**
```
"I see. Your Sales Forecast quality (⭐⭐) is limited by Clean Customer Data quality (⭐⭐⭐). 
Since this dependency is critical (⭐⭐⭐⭐⭐), improving customer data quality could significantly 
improve forecast quality."
```

**Verification:**
```python
# Check dependency
deps = session_manager.dependencies
assert len(deps) == 1
assert deps[0].source_output_id == "clean_customer_data"
assert deps[0].target_output_id == "sales_forecast"
assert deps[0].strength == 5

# Check impact analysis
# If Clean Customer Data improves from ⭐⭐⭐ to ⭐⭐⭐⭐⭐,
# and it's a critical dependency (⭐⭐⭐⭐⭐),
# then Dependency Quality component could improve from ⭐⭐⭐ to ⭐⭐⭐⭐
```

### Success Criteria

- ✅ User can declare dependency between 2 outputs
- ✅ System stores dependency with strength (1-5 stars)
- ✅ System identifies upstream quality bottlenecks
- ✅ System explains impact of upstream improvements
- ✅ Conversation explains bottleneck to user

### Files Modified

- `models/data_models.py` - Add OutputDependency
- `core/session_manager.py` - Add dependency tracking
- `engines/discovery.py` - Add dependency detection
- `app.py` - Add dependency conversation flow
- `tests/unit/test_discovery.py` - Add dependency detection tests

---

## Increment 3: Root Cause Decomposition (4 Sub-Factors)

**Goal:** System asks diagnostic questions to identify if problem is Dependency/Execution/Process/System

**Duration:** 5-7 days

### What Gets Built

#### 3.1 Root Cause Mapping
**Files:** `engines/recommendation.py` (new)

**Create:**
```python
class RecommendationEngine:
    """Generates AI pilot recommendations based on bottlenecks."""
    
    COMPONENT_TO_ROOT_CAUSE = {
        "dependency_quality": "Dependency Issue",
        "team_execution": "Execution Issue",
        "process_maturity": "Process Issue",
        "system_support": "System Issue"
    }
    
    ROOT_CAUSE_TO_AI_CATEGORY = {
        "Dependency Issue": "Data Quality/Pipeline AI Pilots",
        "Execution Issue": "Augmentation/Automation AI Pilots",
        "Process Issue": "Process Intelligence AI Pilots",
        "System Issue": "Intelligent Features AI Pilots"
    }
    
    def __init__(self, taxonomy_loader: TaxonomyLoader, logger: Optional[TechnicalLogger] = None):
        self.taxonomy = taxonomy_loader
        self.logger = logger
    
    def identify_root_causes(self, bottlenecks: List[str]) -> List[str]:
        """Map bottlenecks to root cause types."""
        return [
            self.COMPONENT_TO_ROOT_CAUSE[bottleneck]
            for bottleneck in bottlenecks
        ]
    
    def map_to_ai_categories(self, root_causes: List[str]) -> List[str]:
        """Map root causes to AI solution categories."""
        return [
            self.ROOT_CAUSE_TO_AI_CATEGORY[root_cause]
            for root_cause in root_causes
        ]
    
    def recommend_pilots(
        self, 
        output: Output, 
        factor: OutputFactor
    ) -> List[Dict]:
        """
        Recommend AI pilots based on bottlenecks.
        
        Args:
            output: Output being assessed
            factor: Factor assessment with bottlenecks
            
        Returns:
            List of pilot recommendations
        """
        # Identify root causes
        root_causes = self.identify_root_causes(factor.bottlenecks)
        
        # Map to AI categories
        ai_categories = self.map_to_ai_categories(root_causes)
        
        # Search pilot catalog
        pilots = []
        for category in ai_categories:
            matching_pilots = self.taxonomy.load_pilot_catalog()
            # Filter by category and output function
            filtered = [
                p for p in matching_pilots
                if p.get("category") == category
                and output.function in p.get("applicable_functions", [])
            ]
            pilots.extend(filtered)
        
        # Prioritize by impact
        sorted_pilots = self._prioritize_pilots(pilots, factor)
        
        return sorted_pilots
    
    def _prioritize_pilots(self, pilots: List[Dict], factor: OutputFactor) -> List[Dict]:
        """Prioritize pilots by expected impact."""
        # Priority: System > Process > Team > Dependency
        priority_order = {
            "system_support": 1,
            "process_maturity": 2,
            "team_execution": 3,
            "dependency_quality": 4
        }
        
        for pilot in pilots:
            # Determine which component this pilot improves
            component = pilot.get("improves_component")
            pilot["priority"] = priority_order.get(component, 5)
        
        return sorted(pilots, key=lambda p: p["priority"])
```

#### 3.2 Conversation Flow
**Files:** `app.py`

**Add recommendation display:**
```python
# After factor calculation, show recommendations
if session_manager.factor:
    st.write(f"Factor Value: {'⭐' * session_manager.factor.factor_value}")
    st.write(f"Bottlenecks: {', '.join(session_manager.factor.bottlenecks)}")
    
    # Generate recommendations
    recommendation_engine = RecommendationEngine(taxonomy)
    pilots = recommendation_engine.recommend_pilots(
        session_manager.output,
        session_manager.factor
    )
    
    st.write("### Recommended AI Pilots")
    for i, pilot in enumerate(pilots[:3], 1):
        st.write(f"**{i}. {pilot['name']}**")
        st.write(f"- Category: {pilot['category']}")
        st.write(f"- Addresses: {pilot['improves_component']}")
        st.write(f"- Expected Impact: {pilot['expected_impact']}")
        st.write(f"- Timeline: {pilot['timeline']}")
        st.write(f"- Cost: {pilot['cost_range']}")
```

### Test Scenario

**Setup:**
- Output = "Sales Forecast"
- Factor = 2 stars
- Bottlenecks = ["process_maturity", "system_support"]

**System Actions:**
1. Identifies root causes: ["Process Issue", "System Issue"]
2. Maps to AI categories: ["Process Intelligence", "Intelligent Features"]
3. Searches pilot catalog for matching pilots
4. Prioritizes by impact (System > Process)
5. Presents top 3 recommendations

**System Response:**
```
"Root cause analysis complete.

Factor value: ⭐⭐ (2 stars)

Your bottlenecks are (weakest links):
1. Process Maturity (⭐⭐) - No standardized forecasting process
2. System Support (⭐⭐) - CRM lacks forecasting tools

### Recommended AI Pilots

**1. Add ML-powered forecasting module to CRM**
- Category: Intelligent Features (addresses System Support bottleneck)
- Expected Impact: System Support ⭐⭐ → ⭐⭐⭐⭐ (+2 stars)
- Overall Factor: ⭐⭐ → ⭐⭐⭐ (+1 star, limited by Process)
- Timeline: 8-12 weeks
- Cost: €20k-€40k
- Prerequisites: Team willing to adopt new tool, Data access available

**2. Process mining for forecasting workflow**
- Category: Process Intelligence (addresses Process Maturity bottleneck)
- Expected Impact: Process Maturity ⭐⭐ → ⭐⭐⭐ (+1 star)
- Overall Factor: ⭐⭐ → ⭐⭐ (no change, still limited by System)
- Timeline: 6-8 weeks
- Cost: €15k-€25k

**Suggested Approach:**
Focus on Recommendation 1 first (System Support). This would have immediate impact 
and enable process improvements. Once System is at ⭐⭐⭐⭐, improving Process to ⭐⭐⭐ 
would lift overall factor to ⭐⭐⭐."
```

**Verification:**
```python
# Check recommendations
pilots = recommendation_engine.recommend_pilots(
    session_manager.output,
    session_manager.factor
)

assert len(pilots) >= 2
assert pilots[0]["category"] == "Intelligent Features"
assert pilots[0]["improves_component"] == "system_support"
assert pilots[1]["category"] == "Process Intelligence"
assert pilots[1]["improves_component"] == "process_maturity"

# Check prioritization (System before Process)
assert pilots[0]["priority"] < pilots[1]["priority"]
```

### Success Criteria

- ✅ System asks 4 diagnostic questions in conversation
- ✅ Each component stored separately (1-5 star scale)
- ✅ Factor value calculated as MIN(components)
- ✅ System identifies bottleneck(s) (lowest component(s))
- ✅ System maps bottlenecks to root cause types
- ✅ System recommends AI pilots based on root causes
- ✅ User receives actionable recommendation focused on weakest link

### Files Modified

- `engines/recommendation.py` - New file for recommendation logic
- `app.py` - Add recommendation display
- `tests/unit/test_recommendation.py` - New test file

---

## Testing Strategy

### Unit Tests

**Per Increment:**
- Increment 1: 30-40 tests (data models, session manager, app logic)
- Increment 2: 15-20 tests (dependency detection, impact analysis)
- Increment 3: 20-25 tests (recommendation engine, prioritization)

**Total:** ~65-85 new tests

### Integration Tests

**End-to-End Scenarios:**
1. Complete assessment flow (user input → recommendation)
2. Multi-output dependency chain
3. Edge cases (no matches, contradictions, etc.)

### Manual Testing

**User Acceptance:**
- Test conversation flow with real user descriptions
- Verify recommendations make sense
- Check UX compliance with TBD constraints (#11, #12, #13, #14)

---

## Deployment Strategy

### Increment 1
- Deploy to dev environment
- Test with synthetic data
- Verify MIN() calculation correctness

### Increment 2
- Deploy to dev environment
- Test dependency detection accuracy
- Verify impact analysis logic

### Increment 3
- Deploy to staging environment
- Test with pilot catalog data
- User acceptance testing
- Production deployment

---

## Rollback Plan

Each increment is independently deployable. If issues arise:

1. **Increment 3 fails:** Rollback to Increment 2 (dependency tracking still works)
2. **Increment 2 fails:** Rollback to Increment 1 (single output assessment still works)
3. **Increment 1 fails:** Rollback to current POC (DiscoveryEngine only)

---

## Success Metrics

### Technical Metrics
- ✅ All tests passing (target: 95%+ coverage)
- ✅ No regressions in existing functionality
- ✅ Performance: Assessment completes in <5 minutes

### User Metrics
- ✅ Output identified in ≤3 user turns
- ✅ Component questions answered in single response
- ✅ Recommendations align with bottlenecks (validated by user)

### Business Metrics
- ✅ Recommendations are actionable (user can act on them)
- ✅ Recommendations are specific (not generic advice)
- ✅ Recommendations are prioritized (clear next steps)

---

## References

- **Concept:** `docs/CONCEPT.md`
- **Decision Flow:** `docs/DECISION_FLOW.md`
- **Source Design:** `docs/2_technical_spec/output_centric_factor_model_exploration.md`
- **UX Constraints:** `docs/1_functional_spec/TBD.md`
