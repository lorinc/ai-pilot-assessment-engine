"""AI Pilot Assessment Engine - Main Streamlit Application."""

import streamlit as st
from datetime import datetime

from core.llm_client import LLMClient
from core.firebase_client import FirebaseClient
from core.session_manager import SessionManager
from utils.logger import TechnicalLogger
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Pilot Assessment Engine",
    page_icon="🚀",
    layout="wide"
)

# Initialize components (cached)
@st.cache_resource
def get_firebase_client():
    """Get cached Firebase client."""
    logger = TechnicalLogger(max_entries=50)
    return FirebaseClient(logger=logger), logger

# Initialize Firebase and logger
firebase_client, tech_logger = get_firebase_client()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.tech_logger = tech_logger

# Initialize session manager
session_manager = SessionManager(
    st.session_state,
    firebase_client=firebase_client,
    logger=tech_logger
)

# Initialize LLM client (cached per session)
if 'llm_client' not in st.session_state:
    st.session_state.llm_client = LLMClient(logger=tech_logger)
    tech_logger.info("app_init", "LLM client initialized", {})

llm_client = st.session_state.llm_client

# ============================================================================
# AUTHENTICATION
# ============================================================================

def render_auth_ui():
    """Render authentication UI."""
    st.title("🚀 AI Pilot Assessment Engine")
    st.markdown("### Welcome!")
    st.markdown("Please sign in to continue.")
    
    # Mock authentication for development
    if settings.MOCK_FIREBASE:
        st.info("🔧 **Development Mode**: Mock authentication enabled")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Sign In (Mock)", type="primary", use_container_width=True):
                session_manager.user_id = "mock_user_123"
                session_manager.create_conversation()
                tech_logger.info("auth", "Mock user signed in", {"user_id": "mock_user_123"})
                st.rerun()
    else:
        # Real Firebase authentication
        st.markdown("#### Sign In Options")
        
        tab1, tab2 = st.tabs(["🔐 Anonymous Access", "📧 Email Sign-In"])
        
        with tab1:
            st.markdown("""
            **Quick Start (No Account Required)**
            
            Sign in anonymously to try the assessment engine. Your session will be temporary.
            """)
            
            if st.button("Continue as Guest", type="primary", use_container_width=True):
                # Generate anonymous user ID
                import uuid
                anon_user_id = f"anon_{uuid.uuid4().hex[:12]}"
                session_manager.user_id = anon_user_id
                session_manager.create_conversation()
                tech_logger.info("auth", "Anonymous user signed in", {"user_id": anon_user_id})
                st.rerun()
        
        with tab2:
            st.markdown("""
            **Sign In with Email**
            
            For persistent sessions and saved assessments.
            """)
            
            with st.form("email_signin"):
                email = st.text_input("Email", placeholder="your.email@company.com")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)
                with col2:
                    create = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if email and password:
                        # For now, accept any email/password combination
                        # In production, this would verify against Firebase Auth
                        user_id = email.split('@')[0].replace('.', '_')
                        session_manager.user_id = f"user_{user_id}"
                        session_manager.create_conversation()
                        tech_logger.info("auth", "User signed in", {"email": email})
                        st.success(f"✅ Signed in as {email}")
                        st.rerun()
                    else:
                        st.error("Please enter both email and password")
                
                if create:
                    if email and password:
                        user_id = email.split('@')[0].replace('.', '_')
                        session_manager.user_id = f"user_{user_id}"
                        session_manager.create_conversation()
                        tech_logger.info("auth", "New user account created", {"email": email})
                        st.success(f"✅ Account created! Signed in as {email}")
                        st.rerun()
                    else:
                        st.error("Please enter both email and password")
            
            st.markdown("---")
            st.caption("💡 **Note**: Email authentication is simplified for UAT. Production will use Firebase Auth with proper security.")

# Check authentication
if not session_manager.user_id:
    render_auth_ui()
    st.stop()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚀 AI Pilot Assessment Engine")
with col2:
    # Display user info
    user_display = session_manager.user_id
    if user_display.startswith("anon_"):
        st.markdown("👤 **Guest User**")
    elif user_display.startswith("user_"):
        st.markdown(f"👤 **{user_display.replace('user_', '')}**")
    else:
        st.markdown(f"👤 **{user_display}**")

st.markdown(f"**Session ID:** `{session_manager.session_id}` | **Phase:** {session_manager.phase.title()}")

# Sidebar
with st.sidebar:
    st.header("👤 User Info")
    
    # User details
    if session_manager.user_id.startswith("anon_"):
        st.info("🔓 **Anonymous Session**\n\nYour conversation is temporary and will not be saved.")
    elif session_manager.user_id.startswith("user_"):
        email = session_manager.user_id.replace('user_', '').replace('_', '.') + "@company.com"
        st.success(f"✅ **Signed In**\n\n{email}")
    else:
        st.info(f"🔧 **Development Mode**\n\n{session_manager.user_id}")
    
    # Session controls
    st.divider()
    st.subheader("⚙️ Session Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New\nAssessment", use_container_width=True):
            session_manager.reset()
            tech_logger.info("session", "New assessment started", {})
            st.rerun()
    
    with col2:
        if st.button("🚪 Sign\nOut", use_container_width=True, type="secondary"):
            tech_logger.info("auth", "User signed out", {"user_id": session_manager.user_id})
            # Clear user ID to trigger auth screen
            session_manager.user_id = None
            st.session_state.clear()
            st.rerun()
    
    # About section
    st.divider()
    st.subheader("ℹ️ About")
    st.markdown("""
    This system helps identify AI opportunities through conversational assessment.
    
    **Features:**
    - 🎯 Output-centric factor assessment
    - 🔍 Bottleneck identification
    - 💡 AI pilot recommendations
    - 📊 Feasibility analysis
    """)
    
    # Technical log viewer
    st.divider()
    st.subheader("📋 Technical Log")
    
    with st.expander("View Logs", expanded=False):
        log_entries = tech_logger.get_entries(limit=20)
        if log_entries:
            for entry in reversed(log_entries):
                level_emoji = {
                    "DEBUG": "🔍",
                    "INFO": "ℹ️",
                    "WARNING": "⚠️",
                    "ERROR": "❌"
                }.get(entry["level"], "📝")
                
                st.text(f"{level_emoji} [{entry['type']}] {entry['message']}")
                if entry.get("metadata"):
                    st.json(entry["metadata"])
        else:
            st.text("No log entries yet")

# ============================================================================
# CHAT INTERFACE
# ============================================================================

# Display chat messages
st.subheader("💬 Conversation")

for message in session_manager.messages:
    role = message.get("role", "user")
    content = message.get("content", "")
    
    with st.chat_message(role):
        st.markdown(content)

# Chat input
if prompt := st.chat_input("Describe your problem or ask a question..."):
    # Add user message
    session_manager.add_message("user", prompt, persist=True)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Build prompt with conversation history
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session_manager.messages[:-1]  # Exclude current message
        ]
        
        full_prompt = llm_client.build_prompt(
            user_message=prompt,
            conversation_history=conversation_history if conversation_history else None
        )
        
        # Stream response
        try:
            for chunk in llm_client.generate_stream(full_prompt):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Save assistant response
            session_manager.add_message("assistant", full_response, persist=True)
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            message_placeholder.error(error_msg)
            tech_logger.error("llm_error", error_msg, {"error": str(e)})

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption(f"Phase 1: Core Infrastructure | Session: {session_manager.session_id}")
