# Gemini on Streamlit Boilerplate

A production-ready boilerplate for building conversational AI applications using Google Gemini and Streamlit, with modular context loading and function calling capabilities.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Setup Instructions](#setup-instructions)
- [Implementation Guide](#implementation-guide)
- [Context Loading System](#context-loading-system)
- [Function Calling](#function-calling)
- [Best Practices](#best-practices)

---

## Overview

This boilerplate provides a complete foundation for building Streamlit applications powered by Google Gemini with:

- **Modular LLM client architecture** with abstract base classes
- **Context loading system** for dynamic system instructions
- **Function calling support** for tool use
- **Session state management** for persistent conversations
- **Clean separation of concerns** between UI, business logic, and LLM interaction

---

## Project Structure

```
your-project/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── static/                     # Static assets (images, icons)
│   └── logo.png
├── src/
│   ├── __init__.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract LLM client interface
│   │   ├── gemini.py          # Gemini client implementation
│   │   ├── context_loader.py # Context loading utilities
│   │   └── functions.py       # Function call schemas
│   └── data/
│       ├── __init__.py
│       └── handlers.py        # Data persistence handlers
└── context/
    └── system_context.md      # System instructions for LLM
```

---

## Core Components

### 1. Configuration (`config.py`)

```python
"""Configuration management for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-flash-latest")

# Application Settings
APP_TITLE = "Your App Name"
APP_ICON = "🤖"
```

### 2. LLM Base Classes (`src/llm/base.py`)

```python
"""Abstract base class for LLM clients."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """A message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str


class FunctionCall(BaseModel):
    """A function call proposed by the LLM."""
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    """Response from the LLM."""
    content: Optional[str] = None
    function_calls: List[FunctionCall] = []
    finish_reason: str = "stop"


class LLMClient(ABC):
    """Abstract LLM client interface."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[LLMMessage],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a chat request to the LLM."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used."""
        pass
```

### 3. Gemini Client (`src/llm/gemini.py`)

```python
"""Gemini LLM client implementation."""
import json
from typing import List, Dict, Any, Optional

import google.generativeai as genai

from .base import LLMClient, LLMMessage, LLMResponse, FunctionCall


class GeminiClient(LLMClient):
    """Google Gemini LLM client."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest", system_instruction: str = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key
            model_name: Model to use (default: gemini-flash-latest)
            system_instruction: Optional system instruction for the model
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction
        )
    
    def chat(
        self,
        messages: List[LLMMessage],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a chat request to Gemini."""
        # Convert messages to Gemini format
        gemini_messages = self._convert_messages(messages)
        
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=temperature,
        )
        
        # Add function declarations if provided
        tools = None
        if functions:
            tools = [genai.protos.Tool(function_declarations=self._convert_functions(functions))]
        
        try:
            # Start chat
            chat = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Send message
            response = chat.send_message(
                gemini_messages[-1]["parts"][0] if gemini_messages else "",
                generation_config=generation_config,
                tools=tools,
            )
            
            # Parse response
            return self._parse_response(response)
            
        except Exception as e:
            # Return error as content
            return LLMResponse(
                content=f"Error calling Gemini API: {str(e)}",
                finish_reason="error"
            )
    
    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model_name
    
    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert LLMMessage format to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            # Skip system messages (handled via system_instruction)
            if msg.role == "system":
                continue
            
            role = "user" if msg.role == "user" else "model"
            gemini_messages.append({
                "role": role,
                "parts": [msg.content]
            })
        
        return gemini_messages
    
    def _convert_functions(self, functions: List[Dict[str, Any]]) -> List[Any]:
        """Convert function definitions to Gemini format."""
        function_declarations = []
        
        for func in functions:
            declaration = genai.protos.FunctionDeclaration(
                name=func["name"],
                description=func.get("description", ""),
                parameters=self._convert_schema(func.get("parameters", {}))
            )
            function_declarations.append(declaration)
        
        return function_declarations
    
    def _convert_schema(self, schema: Dict[str, Any]) -> Any:
        """Recursively convert JSON schema to Gemini Schema format."""
        schema_type = self._get_gemini_type(schema.get("type", "string"))
        
        schema_args = {
            "type": schema_type,
            "description": schema.get("description", "")
        }
        
        # Handle object properties
        if schema.get("properties"):
            schema_args["properties"] = {
                k: self._convert_schema(v)
                for k, v in schema["properties"].items()
            }
        
        # Handle array items
        if schema.get("items"):
            schema_args["items"] = self._convert_schema(schema["items"])
        
        # Handle required fields
        if schema.get("required"):
            schema_args["required"] = schema["required"]
        
        return genai.protos.Schema(**schema_args)
    
    def _get_gemini_type(self, json_type: str) -> Any:
        """Convert JSON schema type to Gemini type."""
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_mapping.get(json_type, genai.protos.Type.STRING)
    
    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse Gemini response to LLMResponse format."""
        content = None
        function_calls = []
        
        # Extract function calls first
        for part in response.parts:
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call
                function_calls.append(FunctionCall(
                    name=fc.name,
                    arguments=dict(fc.args)
                ))
        
        # Extract text content (only if no function calls)
        if not function_calls:
            try:
                if response.text:
                    content = response.text
            except ValueError:
                # response.text raises ValueError when there's a function call
                pass
        
        return LLMResponse(
            content=content,
            function_calls=function_calls,
            finish_reason="stop"
        )
```

---

## Context Loading System

### Context Loader (`src/llm/context_loader.py`)

```python
"""Context loader for LLM session initialization."""

from pathlib import Path
from typing import List, Dict


def load_system_context() -> str:
    """
    Load the system context from modular files.
    
    Reads all .md files from context/ directory in alphabetical order
    and concatenates them into a single context string.
    """
    context_dir = Path(__file__).parent.parent.parent / "context"
    
    # Get all .md files, sorted alphabetically
    context_files = sorted([
        f for f in context_dir.glob("*.md") 
        if f.name != "README.md"
    ])
    
    # Read and concatenate all files
    context_parts = []
    for file_path in context_files:
        content = file_path.read_text()
        context_parts.append(content)
    
    # Join with double newline separator
    return "\n\n".join(context_parts)


def build_dynamic_context(base_context: str, **kwargs) -> str:
    """
    Build dynamic context by combining base context with runtime data.
    
    Args:
        base_context: Base system context
        **kwargs: Additional context data to inject
    
    Returns:
        Complete context string
    """
    context_parts = [base_context]
    
    # Add any dynamic context sections
    if kwargs:
        context_parts.append("---")
        context_parts.append("**Current Session Context:**")
        for key, value in kwargs.items():
            context_parts.append(f"- {key}: {value}")
    
    return "\n\n".join(context_parts)
```

### System Context File (`context/system_context.md`)

```markdown
# System Instructions

You are a helpful AI assistant built with Google Gemini and Streamlit.

## Your Capabilities

- Engage in natural conversation
- Use available functions to perform actions
- Provide clear and concise responses

## Guidelines

- Be helpful and informative
- Use functions when appropriate to accomplish tasks
- Ask for clarification when needed
```

---

## Function Calling

### Function Definitions (`src/llm/functions.py`)

```python
"""LLM function call schemas."""

# Example function definitions
EXAMPLE_FUNCTIONS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "save_note",
        "description": "Save a note to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the note"
                }
            },
            "required": ["title", "content"]
        }
    }
]

# All available functions
ALL_FUNCTIONS = EXAMPLE_FUNCTIONS
```

### Function Execution

```python
def execute_function_call(function_name: str, arguments: dict) -> dict:
    """Execute a function call and return the result."""
    try:
        if function_name == "get_weather":
            # Implement weather fetching logic
            location = arguments.get("location")
            unit = arguments.get("unit", "celsius")
            return {
                "success": True,
                "result": f"Weather in {location}: 22°{unit[0].upper()}, Sunny"
            }
        
        elif function_name == "save_note":
            # Implement note saving logic
            title = arguments.get("title")
            content = arguments.get("content")
            # Save to database...
            return {
                "success": True,
                "result": f"Note '{title}' saved successfully"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Main Application (`app.py`)

```python
"""Main Streamlit application."""

import streamlit as st
from pathlib import Path

import config
from src.llm import GeminiClient
from src.llm.base import LLMMessage
from src.llm.context_loader import load_system_context, build_dynamic_context
from src.llm.functions import ALL_FUNCTIONS


# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "system_context" not in st.session_state:
        base_context = load_system_context()
        st.session_state.system_context = build_dynamic_context(
            base_context,
            user_id="demo_user",
            session_start=str(Path.cwd())
        )
    
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = GeminiClient(
            api_key=config.GOOGLE_API_KEY,
            model_name=config.DEFAULT_MODEL,
            system_instruction=st.session_state.system_context
        )


def render_sidebar():
    """Render sidebar with configuration."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.text(f"Model: {st.session_state.llm_client.get_model_name()}")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_chat():
    """Render chat interface."""
    st.title(config.APP_TITLE)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show function calls if present
            if "function_calls" in message and message["function_calls"]:
                for fc in message["function_calls"]:
                    with st.expander(f"🔧 Function: {fc['name']}"):
                        st.json(fc["arguments"])
    
    # Chat input
    prompt = st.chat_input("What would you like to know?")
    
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get LLM response
        with st.spinner("Thinking..."):
            messages = [
                LLMMessage(role=msg["role"], content=msg["content"])
                for msg in st.session_state.messages
            ]
            
            response = st.session_state.llm_client.chat(
                messages=messages,
                functions=ALL_FUNCTIONS,
                temperature=0.7
            )
            
            # Handle function calls
            if response.function_calls:
                # Add assistant message with function calls
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content or "I'll execute these functions:",
                    "function_calls": [
                        {"name": fc.name, "arguments": fc.arguments}
                        for fc in response.function_calls
                    ]
                })
                
                # Execute function calls
                function_results = []
                for fc in response.function_calls:
                    result = execute_function_call(fc.name, fc.arguments)
                    function_results.append(str(result))
                
                # Add function results as assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "\n\n".join(function_results)
                })
            
            else:
                # No function calls, just add response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content
                })
        
        st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
```

---

## Setup Instructions

### 1. Install Dependencies

Create `requirements.txt`:

```txt
streamlit>=1.28.0
google-generativeai>=0.3.0
pydantic>=2.5.0
python-dotenv>=1.0.0
```

Install:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
DEFAULT_MODEL=gemini-flash-latest
```

### 3. Create Directory Structure

```bash
mkdir -p src/llm src/data context static
touch src/__init__.py src/llm/__init__.py src/data/__init__.py
```

### 4. Run Application

```bash
streamlit run app.py
```

---

## Best Practices

### 1. **Modular Context Management**

- Store system instructions in separate markdown files
- Use `context_loader.py` to dynamically load and combine contexts
- Keep context files organized by topic (e.g., `01_role.md`, `02_capabilities.md`)

### 2. **Error Handling**

- Always wrap LLM calls in try-except blocks
- Return user-friendly error messages
- Log errors for debugging

### 3. **Session State**

- Initialize all session state variables in one place
- Use descriptive names for session state keys
- Clear session state appropriately on resets

### 4. **Function Calling**

- Define clear, descriptive function schemas
- Validate function arguments before execution
- Return structured results from function executions

### 5. **Performance**

- Cache system context loading with `@st.cache_data`
- Limit conversation history length for long sessions
- Use appropriate temperature settings (0.7 for creative, 0.2 for factual)

### 6. **Security**

- Never commit `.env` files to version control
- Validate and sanitize all user inputs
- Use environment variables for all sensitive data

---

## Extending the Boilerplate

### Adding New Functions

1. Define function schema in `src/llm/functions.py`
2. Implement function logic in your business layer
3. Add execution handler in `execute_function_call()`
4. Update `ALL_FUNCTIONS` list

### Adding Multiple Context Files

```python
# context/01_role.md
# context/02_capabilities.md
# context/03_guidelines.md
```

The context loader will automatically combine them in alphabetical order.

### Customizing UI

- Modify `st.set_page_config()` for branding
- Add custom CSS with `st.markdown()` and `unsafe_allow_html=True`
- Create custom components with `st.columns()` and `st.container()`

---

## Common Patterns

### Pattern 1: Stateful Conversations

```python
# Store conversation context in session state
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {}

# Update context during conversation
st.session_state.conversation_context["last_topic"] = "weather"
```

### Pattern 2: Multi-Step Workflows

```python
# Track workflow state
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = 1

# Progress through steps
if st.session_state.workflow_step == 1:
    # Step 1 logic
    pass
elif st.session_state.workflow_step == 2:
    # Step 2 logic
    pass
```

### Pattern 3: Dynamic Function Loading

```python
def get_available_functions(user_role: str) -> List[Dict]:
    """Return functions based on user role."""
    if user_role == "admin":
        return ADMIN_FUNCTIONS + USER_FUNCTIONS
    return USER_FUNCTIONS
```

---

## Troubleshooting

### Issue: "API key not found"

**Solution:** Ensure `.env` file exists and contains `GOOGLE_API_KEY`

### Issue: "Function calls not working"

**Solution:** Verify function schema matches Gemini's expected format (use `genai.protos.Schema`)

### Issue: "Context too long"

**Solution:** Reduce context size or implement context summarization

### Issue: "Session state not persisting"

**Solution:** Check that session state initialization happens before any UI rendering

---

## Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## License

This boilerplate is provided as-is for educational and development purposes.

---

**Happy Building! 🚀**
