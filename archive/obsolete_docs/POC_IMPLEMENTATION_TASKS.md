# POC Implementation Tasks

**Project:** AI Pilot Assessment Engine - Minimal POC  
**Scope:** Steps 1-8 (Output Discovery → Pilot Recommendation, No ROI)  
**Timeline:** 3 weeks  
**Tech Stack:** Python + Streamlit + Gemini (Vertex AI)

## Testing Requirements

**All code must include:**
- ✅ **Unit tests** for individual functions/methods (pytest)
- ✅ **Integration tests** for end-to-end flows
- ✅ **Test coverage** minimum 80%
- ✅ **CI/CD ready** - tests run on every deployment
- ✅ **Mock external dependencies** (Gemini API) for unit tests
- ✅ **Test fixtures** for taxonomy data

**Testing Stack:**
- `pytest>=7.4.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.11.0` - Mocking support

---

## Release 1: Core Infrastructure (Days 1-3)

### Task 1.1: Project Setup
**Estimated Time:** 2 hours

- [ ] Create project directory structure:
  ```
  poc/
  ├── app.py                    # Streamlit main app
  ├── requirements.txt          # Dependencies
  ├── .env.template             # Environment variables template
  ├── .gitignore               # Git ignore
  ├── config/
  │   └── settings.py          # Configuration
  ├── core/
  │   ├── __init__.py
  │   ├── taxonomy_loader.py   # Load JSON taxonomies
  │   ├── session_manager.py   # Streamlit session state
  │   └── gemini_client.py     # Vertex AI / Gemini integration
  ├── engines/
  │   ├── __init__.py
  │   ├── discovery.py         # Output discovery engine
  │   ├── assessment.py        # Component assessment engine
  │   └── recommender.py       # Pilot recommendation engine
  ├── models/
  │   ├── __init__.py
  │   └── data_models.py       # Pydantic models
  └── utils/
      ├── __init__.py
      └── helpers.py           # Utility functions
  ```

- [ ] Create `requirements.txt`:
  ```
  streamlit>=1.28.0
  google-cloud-aiplatform>=1.38.0
  python-dotenv>=1.0.0
  pydantic>=2.0.0
  ```

- [ ] Create `.env.template`:
  ```
  GCP_PROJECT_ID=your-project-id
  GCP_LOCATION=us-central1
  GEMINI_MODEL=gemini-1.5-pro
  ```

- [ ] Initialize git repository
- [ ] Create README.md with setup instructions

**Acceptance Criteria:**
- Project structure created
- Dependencies documented
- Git initialized

---

### Task 1.2: Taxonomy Data Loader
**Estimated Time:** 3 hours

**File:** `core/taxonomy_loader.py`

- [ ] Implement `TaxonomyLoader` class:
  ```python
  class TaxonomyLoader:
      def __init__(self, data_dir: str = "../src/data"):
          self.data_dir = Path(data_dir)
          self._cache = {}
      
      def load_function_templates(self) -> List[Dict]:
          """Load all function templates from organizational_templates/functions/"""
          pass
      
      def load_component_scales(self) -> Dict:
          """Load component_scales.json"""
          pass
      
      def load_pilot_types(self) -> Dict:
          """Load pilot_types.json"""
          pass
      
      def load_pilot_catalog(self) -> Dict:
          """Load pilot_catalog.json"""
          pass
      
      def load_inference_rules(self) -> Dict:
          """Load output_discovery.json"""
          pass
      
      def load_common_systems(self) -> Dict:
          """Load common_systems.json"""
          pass
      
      def get_output_by_id(self, output_id: str) -> Optional[Dict]:
          """Find output across all function templates"""
          pass
      
      def search_outputs(self, keywords: List[str]) -> List[Dict]:
          """Search outputs by keywords"""
          pass
  ```

- [ ] Add caching to avoid re-reading files
- [ ] Add error handling for missing files
- [ ] Write unit tests

**Acceptance Criteria:**
- Can load all taxonomy files
- Can search outputs by keywords
- Handles missing files gracefully
- Tests pass

---

### Task 1.3: Gemini Client Integration
**Estimated Time:** 4 hours

**File:** `core/gemini_client.py`

- [ ] Implement `GeminiClient` class:
  ```python
  from google.cloud import aiplatform
  from vertexai.preview.generative_models import GenerativeModel
  
  class GeminiClient:
      def __init__(self, project_id: str, location: str, model_name: str):
          aiplatform.init(project=project_id, location=location)
          self.model = GenerativeModel(model_name)
      
      def generate_stream(self, prompt: str, context: Dict = None) -> Iterator[str]:
          """Generate streaming response"""
          pass
      
      def generate(self, prompt: str, context: Dict = None) -> str:
          """Generate non-streaming response"""
          pass
      
      def build_prompt(self, user_message: str, system_context: Dict) -> str:
          """Build prompt with taxonomy context"""
          pass
  ```

- [ ] Implement streaming response handling
- [ ] Add taxonomy context injection
- [ ] Add error handling and retries
- [ ] Test with sample prompts

**Acceptance Criteria:**
- Can connect to Vertex AI
- Can stream responses
- Can inject taxonomy context
- Handles errors gracefully

---

### Task 1.4: Basic Streamlit App
**Estimated Time:** 3 hours

**File:** `app.py`

- [ ] Create basic Streamlit chat interface:
  ```python
  import streamlit as st
  from core.session_manager import SessionManager
  from core.gemini_client import GeminiClient
  
  st.set_page_config(page_title="AI Pilot Assessment", layout="wide")
  st.title("🚀 AI Pilot Assessment Engine")
  
  # Initialize session
  if 'session' not in st.session_state:
      st.session_state.session = SessionManager()
  
  # Chat interface
  for message in st.session_state.session.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])
  
  # User input
  if prompt := st.chat_input("Describe your challenge..."):
      # Add user message
      st.session_state.session.add_message("user", prompt)
      
      # Generate response (placeholder)
      with st.chat_message("assistant"):
          response = st.write_stream(generate_response(prompt))
      
      st.session_state.session.add_message("assistant", response)
  ```

- [ ] Implement `SessionManager` for state management
- [ ] Add message history display
- [ ] Add streaming response display
- [ ] Test basic chat flow

**Acceptance Criteria:**
- Chat interface works
- Messages persist in session
- Can send and receive messages
- Streaming display works

---

## Release 2: Discovery Engine (Days 4-7)

### Task 2.1: Output Matching Logic
**Estimated Time:** 6 hours

**File:** `engines/discovery.py`

- [ ] Implement `DiscoveryEngine` class:
  ```python
  class DiscoveryEngine:
      def __init__(self, taxonomy_loader: TaxonomyLoader, gemini_client: GeminiClient):
          self.taxonomy = taxonomy_loader
          self.gemini = gemini_client
      
      def identify_output(self, user_message: str, conversation_history: List) -> Dict:
          """
          Identify output from user message
          Returns: {
              'output_id': str,
              'output_name': str,
              'function': str,
              'confidence': float,
              'alternatives': List[Dict]
          }
          """
          pass
      
      def extract_keywords(self, message: str) -> List[str]:
          """Extract keywords using Gemini"""
          pass
      
      def match_inference_triggers(self, keywords: List[str]) -> List[Dict]:
          """Match keywords to inference_triggers in function templates"""
          pass
      
      def rank_outputs(self, matches: List[Dict]) -> List[Dict]:
          """Rank outputs by confidence"""
          pass
  ```

- [ ] Implement keyword extraction using Gemini
- [ ] Implement inference trigger matching
- [ ] Implement confidence scoring
- [ ] Add support for pain point matching
- [ ] Write unit tests with sample inputs

**Acceptance Criteria:**
- Can identify outputs from user descriptions
- Returns confidence scores
- Handles ambiguous cases (multiple matches)
- Tests pass with various inputs

---

### Task 2.2: Context Inference
**Estimated Time:** 4 hours

**File:** `engines/discovery.py` (extend)

- [ ] Implement context inference:
  ```python
  def infer_creation_context(self, output_data: Dict) -> Dict:
      """
      Load typical_creation_context from output
      Returns: {
          'team': str,
          'process': str,
          'step': str,
          'system': str,
          'confidence': float
      }
      """
      pass
  
  def validate_context(self, context: Dict, user_message: str) -> Dict:
      """
      Ask user to confirm or correct context
      Uses Gemini to generate validation prompt
      """
      pass
  ```

- [ ] Load typical_creation_context from matched output
- [ ] Generate validation prompt using Gemini
- [ ] Handle user corrections
- [ ] Update confidence based on validation

**Acceptance Criteria:**
- Can load context from output definition
- Generates natural validation prompts
- Handles user corrections
- Updates confidence appropriately

---

### Task 2.3: Discovery Conversation Flow
**Estimated Time:** 6 hours

**File:** `app.py` (extend)

- [ ] Implement discovery conversation flow:
  ```python
  def handle_discovery_phase(user_message: str, session: SessionManager):
      """
      Steps 1-3: Output Discovery & Context Inference
      """
      # Step 1: Identify output
      discovery_result = discovery_engine.identify_output(
          user_message, 
          session.conversation_history
      )
      
      if discovery_result['confidence'] > 0.7:
          # High confidence - suggest output
          response = format_output_suggestion(discovery_result)
      else:
          # Low confidence - ask clarifying question
          response = generate_clarifying_question(discovery_result)
      
      # Step 2-3: Context inference (if output confirmed)
      if session.output_confirmed:
          context = discovery_engine.infer_creation_context(session.output)
          response = format_context_validation(context)
      
      return response
  ```

- [ ] Implement state machine for discovery flow
- [ ] Add clarifying questions for ambiguous cases
- [ ] Add context validation prompts
- [ ] Handle user corrections
- [ ] Test with multiple scenarios

**Acceptance Criteria:**
- Can complete discovery flow (Steps 1-3)
- Handles high/low confidence cases
- Asks clarifying questions when needed
- Validates context with user
- State transitions work correctly

---

## Phase 3: Assessment Engine (Days 8-12)

### Task 3.1: Component Assessment Logic
**Estimated Time:** 8 hours

**File:** `engines/assessment.py`

- [ ] Implement `AssessmentEngine` class:
  ```python
  class AssessmentEngine:
      def __init__(self, taxonomy_loader: TaxonomyLoader, gemini_client: GeminiClient):
          self.taxonomy = taxonomy_loader
          self.gemini = gemini_client
          self.component_scales = taxonomy_loader.load_component_scales()
      
      def assess_component(self, component_name: str, user_description: str) -> Dict:
          """
          Infer component rating from user description
          Returns: {
              'component': str,
              'rating': int (1-5),
              'description': str,
              'confidence': float,
              'indicators_matched': List[str]
          }
          """
          pass
      
      def generate_assessment_prompt(self, component_name: str) -> str:
          """Generate prompt to ask about component"""
          pass
      
      def infer_rating_from_description(self, component_name: str, description: str) -> int:
          """Use Gemini + component_scales.json to infer rating"""
          pass
      
      def validate_rating(self, component: str, rating: int, description: str) -> str:
          """Generate validation prompt"""
          pass
      
      def calculate_actual_quality(self, components: Dict[str, int]) -> Dict:
          """
          Calculate MIN of 4 components
          Returns: {
              'actual_quality': int,
              'bottleneck': List[str],
              'calculation': str
          }
          """
          return {
              'actual_quality': min(components.values()),
              'bottleneck': [k for k, v in components.items() if v == min(components.values())],
              'calculation': f"MIN({', '.join(map(str, components.values()))}) = {min(components.values())}"
          }
  ```

- [ ] Load component scales from taxonomy
- [ ] Implement rating inference using Gemini
- [ ] Implement MIN calculation (rule-based)
- [ ] Add validation prompts
- [ ] Write unit tests

**Acceptance Criteria:**
- Can assess all 4 components
- Infers ratings from descriptions
- Correctly calculates MIN
- Identifies bottlenecks
- Tests pass

---

### Task 3.2: Assessment Conversation Flow
**Estimated Time:** 6 hours

**File:** `app.py` (extend)

- [ ] Implement assessment conversation flow:
  ```python
  def handle_assessment_phase(session: SessionManager):
      """
      Steps 4-5: Component Assessment & MIN Calculation
      """
      components_to_assess = [
          'team_execution',
          'system_capabilities',
          'process_maturity',
          'dependency_quality'
      ]
      
      # Assess each component
      for component in components_to_assess:
          if component not in session.components:
              # Ask about component
              prompt = assessment_engine.generate_assessment_prompt(component)
              return prompt
      
      # All components assessed - calculate MIN
      if len(session.components) == 4:
          result = assessment_engine.calculate_actual_quality(session.components)
          session.actual_quality = result['actual_quality']
          session.bottleneck = result['bottleneck']
          return format_min_calculation(result)
  ```

- [ ] Implement sequential component assessment
- [ ] Add conversational prompts for each component
- [ ] Add rating validation
- [ ] Display MIN calculation
- [ ] Test with various inputs

**Acceptance Criteria:**
- Can assess all 4 components sequentially
- Infers ratings from user descriptions
- Validates ratings with user
- Calculates and displays MIN
- Shows bottleneck clearly

---

### Task 3.3: Gap Analysis
**Estimated Time:** 4 hours

**File:** `engines/assessment.py` (extend)

- [ ] Implement gap analysis:
  ```python
  def collect_required_quality(self, actual_quality: int) -> str:
      """Generate prompt to collect required quality"""
      return f"""
      Current quality: {'⭐' * actual_quality}
      
      What quality level do you need?
      (Rate from ⭐ to ⭐⭐⭐⭐⭐)
      """
  
  def analyze_gap(self, actual: int, required: int, components: Dict) -> Dict:
      """
      Analyze gap between actual and required
      Returns: {
          'gap': int,
          'bottleneck': List[str],
          'improvement_needed': int
      }
      """
      return {
          'gap': required - actual,
          'bottleneck': [k for k, v in components.items() if v == actual],
          'improvement_needed': required - actual
      }
  ```

- [ ] Implement required quality collection
- [ ] Implement gap calculation
- [ ] Format gap analysis display
- [ ] Test with various scenarios

**Acceptance Criteria:**
- Can collect required quality from user
- Calculates gap correctly
- Identifies bottleneck components
- Displays gap analysis clearly

---

## Phase 4: Recommendation Engine (Days 13-16)

### Task 4.1: Pilot Selection Logic
**Estimated Time:** 6 hours

**File:** `engines/recommender.py`

- [ ] Implement `RecommenderEngine` class:
  ```python
  class RecommenderEngine:
      def __init__(self, taxonomy_loader: TaxonomyLoader, gemini_client: GeminiClient):
          self.taxonomy = taxonomy_loader
          self.gemini = gemini_client
          self.pilot_types = taxonomy_loader.load_pilot_types()
          self.pilot_catalog = taxonomy_loader.load_pilot_catalog()
      
      def recommend_pilots(self, bottleneck: List[str], gap: int, output_context: Dict) -> List[Dict]:
          """
          Recommend pilots based on bottleneck
          Returns: List of 2-3 pilot recommendations
          """
          pass
      
      def select_pilot_types(self, bottleneck_component: str) -> List[Dict]:
          """Map bottleneck to pilot types"""
          component_mapping = {
              'team_execution': 'team_execution',
              'system_capabilities': 'system_capabilities',
              'process_maturity': 'process_maturity'
          }
          category = component_mapping.get(bottleneck_component)
          return self.pilot_types['pilot_categories'][category]['pilot_types']
      
      def find_pilot_examples(self, output_name: str, bottleneck: str) -> List[Dict]:
          """Find specific examples from pilot_catalog"""
          pass
      
      def format_recommendation(self, pilot: Dict, gap: int) -> str:
          """Format pilot recommendation for display"""
          pass
  ```

- [ ] Implement bottleneck → pilot category mapping
- [ ] Load relevant pilot types
- [ ] Find specific examples from catalog
- [ ] Rank pilots by relevance
- [ ] Write unit tests

**Acceptance Criteria:**
- Maps bottlenecks to pilot categories correctly
- Loads relevant pilot types
- Finds specific examples
- Returns 2-3 recommendations
- Tests pass

---

### Task 4.2: Recommendation Formatting
**Estimated Time:** 4 hours

**File:** `engines/recommender.py` (extend)

- [ ] Implement recommendation formatting:
  ```python
  def format_recommendations(self, pilots: List[Dict], gap: int, actual: int, required: int) -> str:
      """
      Format recommendations for display
      """
      output = f"""
      ## 🎯 Pilot Recommendations
      
      **Current Quality:** {'⭐' * actual}
      **Target Quality:** {'⭐' * required}
      **Gap:** {gap} stars
      
      Based on your bottleneck, here are {len(pilots)} pilot options:
      
      """
      
      for i, pilot in enumerate(pilots, 1):
          output += f"""
          ### Option {i}: {pilot['name']}
          
          **What it does:** {pilot['description']}
          
          **Expected Impact:** {'⭐' * actual} → {'⭐' * required}
          
          **Timeline:** {pilot['timeline']}
          
          **Cost:** {pilot['cost']}
          
          **Prerequisites:**
          {format_prerequisites(pilot['prerequisites'])}
          
          ---
          """
      
      return output
  ```

- [ ] Format recommendations with star ratings
- [ ] Include all pilot details
- [ ] Make it easy to compare options
- [ ] Test with various scenarios

**Acceptance Criteria:**
- Recommendations are clearly formatted
- All details included (impact, timeline, cost, prerequisites)
- Easy to compare options
- Displays correctly in Streamlit

---

### Task 4.3: End-to-End Flow Integration
**Estimated Time:** 6 hours

**File:** `app.py` (complete integration)

- [ ] Integrate all phases into complete flow:
  ```python
  def main():
      st.title("🚀 AI Pilot Assessment Engine")
      
      # Initialize session
      if 'phase' not in st.session_state:
          st.session_state.phase = 'discovery'
          st.session_state.session = SessionManager()
      
      # Display chat history
      for message in st.session_state.session.messages:
          with st.chat_message(message["role"]):
              st.markdown(message["content"])
      
      # User input
      if prompt := st.chat_input("Describe your challenge..."):
          # Add user message
          st.session_state.session.add_message("user", prompt)
          
          # Route to appropriate phase
          if st.session_state.phase == 'discovery':
              response = handle_discovery_phase(prompt, st.session_state.session)
          elif st.session_state.phase == 'assessment':
              response = handle_assessment_phase(st.session_state.session)
          elif st.session_state.phase == 'gap_analysis':
              response = handle_gap_analysis(st.session_state.session)
          elif st.session_state.phase == 'recommendation':
              response = handle_recommendation(st.session_state.session)
          
          # Display response
          with st.chat_message("assistant"):
              st.markdown(response)
          
          st.session_state.session.add_message("assistant", response)
  ```

- [ ] Implement phase transitions
- [ ] Add state management
- [ ] Add progress indicator
- [ ] Handle edge cases
- [ ] Test complete flow

**Acceptance Criteria:**
- Complete flow works (Steps 1-8)
- Phase transitions are smooth
- State is maintained correctly
- User can complete full assessment
- Edge cases handled

---

## Phase 5: Polish & Testing (Days 17-21)

### Task 5.1: Error Handling & Edge Cases
**Estimated Time:** 4 hours

- [ ] Add error handling:
  - Gemini API failures
  - Missing taxonomy files
  - Invalid user inputs
  - Session timeout
  - Network errors

- [ ] Handle edge cases:
  - Multiple bottlenecks (tied MIN)
  - Zero dependencies
  - Unknown systems
  - Ambiguous output identification
  - User corrections mid-flow

- [ ] Add graceful degradation
- [ ] Add retry logic
- [ ] Test error scenarios

**Acceptance Criteria:**
- All errors handled gracefully
- User-friendly error messages
- System recovers from failures
- Edge cases work correctly

---

### Task 5.2: UI/UX Improvements
**Estimated Time:** 4 hours

- [ ] Add visual improvements:
  - Star rating display (⭐⭐⭐)
  - Progress indicator
  - Component summary cards
  - Recommendation comparison table
  - Export button (save assessment)

- [ ] Add helpful features:
  - "Start over" button
  - "Go back" to previous step
  - Example prompts
  - Help text / tooltips

- [ ] Improve conversation flow:
  - Better prompts
  - Clearer validation questions
  - More natural language

**Acceptance Criteria:**
- UI is clean and intuitive
- Visual elements work correctly
- Helpful features implemented
- Conversation feels natural

---

### Task 5.3: Demo Scenarios & Documentation
**Estimated Time:** 6 hours

- [ ] Create demo scenarios:
  1. **Sales Forecast** (happy path)
     - User: "Our sales forecasts are always wrong"
     - Expected: Identify output, assess components, recommend AI Copilot
  
  2. **Customer Support Tickets**
     - User: "Support tickets take forever to resolve"
     - Expected: Identify output, find process bottleneck, recommend automation
  
  3. **Finance Reports**
     - User: "Financial reports are slow and error-prone"
     - Expected: Identify output, find multiple bottlenecks, recommend options

- [ ] Write documentation:
  - README.md with setup instructions
  - User guide
  - Demo script
  - Architecture overview
  - Known limitations

- [ ] Create demo video/screenshots

**Acceptance Criteria:**
- 3 demo scenarios work end-to-end
- Documentation is complete
- Demo materials ready
- Can present to stakeholders

---

### Task 5.4: Testing & Bug Fixes
**Estimated Time:** 6 hours

- [ ] Write integration tests:
  - Full flow tests for each demo scenario
  - Phase transition tests
  - State management tests

- [ ] Manual testing:
  - Test all conversation paths
  - Test error cases
  - Test edge cases
  - Test on different browsers

- [ ] Fix bugs found during testing
- [ ] Performance optimization
- [ ] Code cleanup

**Acceptance Criteria:**
- All tests pass
- No critical bugs
- Performance is acceptable
- Code is clean

---

## Deployment (Optional - Day 21)

### Task 6.1: Cloud Run Deployment
**Estimated Time:** 4 hours

- [ ] Create Dockerfile:
  ```dockerfile
  FROM python:3.10-slim
  
  WORKDIR /app
  
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  
  COPY . .
  
  EXPOSE 8080
  
  CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
  ```

- [ ] Create `.gcloudignore`
- [ ] Deploy to Cloud Run:
  ```bash
  gcloud run deploy ai-pilot-assessment \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
  ```

- [ ] Test deployed app
- [ ] Document deployment process

**Acceptance Criteria:**
- App deployed to Cloud Run
- Accessible via public URL
- Works correctly in production
- Deployment documented

---

## Summary

### Total Estimated Time: ~100 hours (3 weeks)

**Phase Breakdown:**
- Release 1: Core Infrastructure (12 hours / 1.5 days)
- Release 2: Discovery Engine (16 hours / 2 days)
- Phase 3: Assessment Engine (18 hours / 2.5 days)
- Phase 4: Recommendation Engine (16 hours / 2 days)
- Phase 5: Polish & Testing (20 hours / 2.5 days)
- Deployment: (4 hours / 0.5 days)

**Key Milestones:**
- Day 3: Basic infrastructure working
- Day 7: Output discovery working
- Day 12: Component assessment working
- Day 16: Recommendations working
- Day 21: POC complete and demo-ready

**Success Criteria:**
- ✅ Can complete full assessment flow (Steps 1-8)
- ✅ Works with 2-3 function templates
- ✅ Gemini integration working
- ✅ Streamlit UI functional
- ✅ 3 demo scenarios working
- ✅ Documentation complete
