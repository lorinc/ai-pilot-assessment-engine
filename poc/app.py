"""AI Pilot Assessment Engine - POC Streamlit App."""

import streamlit as st
import json
from core.session_manager import SessionManager
from core.gemini_client import GeminiClient
from core.taxonomy_loader import TaxonomyLoader
from utils.technical_logger import TechnicalLogger
from utils.log_formatter import LogFormatter
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Pilot Assessment Engine",
    page_icon="🚀",
    layout="wide"
)

# Initialize components
@st.cache_resource
def get_taxonomy_loader():
    """Get cached taxonomy loader."""
    return TaxonomyLoader()

# Initialize session manager and logger
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.technical_logger = TechnicalLogger(max_entries=20)
    session_manager = SessionManager(st.session_state)

session_manager = SessionManager(st.session_state)
logger = st.session_state.technical_logger
taxonomy = get_taxonomy_loader()

# Initialize Gemini client once and store in session state
if 'gemini_client' not in st.session_state:
    st.session_state.gemini_client = GeminiClient(logger=logger)
    logger.info("app_init", "Gemini client created and cached in session", {})

gemini = st.session_state.gemini_client

# Header
st.title("🚀 AI Pilot Assessment Engine")
st.markdown("**Proof of Concept** - Output-Centric Assessment Flow")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This POC demonstrates the core assessment flow:
    
    1. **Output Discovery** - Identify what you're creating
    2. **Context Inference** - Team, Process, System
    3. **Component Assessment** - Rate 4 components (⭐ 1-5)
    4. **MIN Calculation** - Find the bottleneck
    5. **Gap Analysis** - Compare actual vs required
    6. **Pilot Recommendation** - Get targeted suggestions
    """)
    
    st.divider()
    
    # Session info
    st.subheader("📊 Session Info")
    st.text(f"ID: {session_manager.session.session_id}")
    st.text(f"Phase: {session_manager.phase}")
    st.text(f"Messages: {len(session_manager.session.messages)}")
    
    if st.button("🔄 Start New Assessment"):
        session_manager.reset()
        st.rerun()
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    st.text(f"Model: {settings.GEMINI_MODEL}")
    st.text(f"Location: {settings.GCP_LOCATION}")
    if settings.MOCK_LLM:
        st.warning("⚠️ Mock mode enabled")

# Main layout: Fixed-height 50/50 split (chat | log)
col_chat, col_log = st.columns([1, 1])

with col_chat:
    st.subheader("💬 Chat")
    
    # Fixed-height container for chat
    chat_container = st.container(height=600)
    with chat_container:
        # Display conversation history
        for message in session_manager.get_conversation_history():
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

with col_log:
    st.subheader("🔍 Technical Log")
    
    # Fixed-height container for log
    log_container = st.container(height=600)
    
    with log_container:
        # Display log entries (last 20)
        log_entries = logger.get_entries(limit=20)
        
        if log_entries:
            # Format all entries as text
            formatted_log = LogFormatter.format_entries(log_entries)
            st.code(formatted_log, language=None)
        else:
            st.info("No log entries yet. Start chatting to see technical logs.")

# Chat input (outside columns to span full width)
if prompt := st.chat_input("Describe your challenge... (e.g., 'Our sales forecasts are always wrong')"):
    logger.info("user_input", "User message received", {"message_length": len(prompt)})
    
    # Add user message
    session_manager.add_message("user", prompt)
    
    # Generate response
    with st.spinner("Thinking..."):
        # Build context
        context = {
            "phase": session_manager.phase,
            "available_functions": [t.get("function") for t in taxonomy.load_function_templates()]
        }
        
        logger.info("context_build", "Building context for LLM", {
            "phase": session_manager.phase,
            "available_functions": context["available_functions"]
        })
        
        # Build prompt
        full_prompt = gemini.build_prompt(
            user_message=prompt,
            system_context=context,
            conversation_history=session_manager.get_conversation_history()[:-1]  # Exclude current message
        )
        
        logger.debug("prompt_built", "Prompt constructed", {
            "prompt_length": len(full_prompt),
            "prompt_preview": full_prompt
        })
        
        # Generate response
        if settings.MOCK_LLM:
            response = f"""
Thank you for sharing that challenge!

**Current Phase:** {session_manager.phase}

This is a **mock response** because MOCK_LLM is enabled in your .env file.

To use real Gemini:
1. Set `MOCK_LLM=false` in your `.env` file
2. Ensure your GCP credentials are configured
3. Restart the app

**What I would do in production:**
- Analyze your message for keywords
- Search taxonomy for matching outputs
- Suggest the most relevant output
- Ask you to confirm
- Guide you through the assessment

**Available Functions:** {', '.join(context['available_functions'][:5])}...

Try describing a specific business challenge, like:
- "Our sales forecasts are always wrong"
- "Customer support tickets take forever"
- "Financial reports are slow and error-prone"
"""
        else:
            # Use real Gemini - stream response
            response_parts = []
            
            # Create placeholder in chat container for streaming
            with col_chat:
                with chat_container:
                    with st.chat_message("assistant"):
                        response_placeholder = st.empty()
            
            for chunk in gemini.generate_stream(full_prompt):
                response_parts.append(chunk)
                response_placeholder.markdown("".join(response_parts))
            
            response = "".join(response_parts)
    
    # Add assistant message
    session_manager.add_message("assistant", response)
    logger.info("assistant_response", "Response added to conversation", {
        "response_length": len(response)
    })
    
    # Force rerun to update both chat and log displays
    st.rerun()

# Footer
st.divider()
st.caption("AI Pilot Assessment Engine POC - Built with Streamlit + Gemini")
