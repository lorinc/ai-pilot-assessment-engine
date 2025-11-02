"""Log formatter for user-friendly display."""

from typing import Dict, Any


class LogFormatter:
    """Formats technical log entries for user-friendly display."""
    
    # Map log types to user-friendly templates
    # For types that need detailed data display, template returns None to use custom formatting
    TEMPLATES = {
        "app_init": "Gemini client created and cached in session",
        "llm_init": "Initialized LLM: {model}",
        "llm_call": "Sending prompt to LLM ({prompt_length} chars, temp={temperature})",
        "llm_response": "Received LLM response ({response_length} chars, {total_chunks} chunks)",
        "user_input": "User message received ({message_length} chars)",
        "context_build": None,  # Custom formatting with details
        "prompt_built": None,  # Custom formatting with details
        "assistant_response": "Response added to conversation ({response_length} chars)",
        "decision": "Decision: {decision}",
        "tool_call": "Tool call: {tool} - {description}",
        "taxonomy_search": "Searching taxonomy: {query} → {result_count} results",
        "output_identified": "Output identified: {output_name} (confidence: {confidence})",
        "context_inferred": "Context inferred: team={team}, system={system}",
        "phase_transition": "Phase transition: {from_phase} → {to_phase}",
        "error": "Error: {error_message}",
        "warning": "Warning: {warning_message}",
    }
    
    @staticmethod
    def format_entry(entry: Dict[str, Any]) -> str:
        """
        Format a log entry into a user-friendly message (possibly multi-line).
        
        Args:
            entry: Log entry dict with timestamp, level, type, message, metadata
            
        Returns:
            Formatted string (may contain newlines for detailed logs)
        """
        timestamp = entry["timestamp"][:19].replace("T", " ")
        level = entry["level"]
        log_type = entry["type"]
        metadata = entry.get("metadata", {})
        
        # Level icon
        level_icons = {
            "DEBUG": "🔵",
            "INFO": "🟢",
            "WARNING": "🟡",
            "ERROR": "🔴"
        }
        icon = level_icons.get(level, "⚪")
        
        # Get template for this log type
        template = LogFormatter.TEMPLATES.get(log_type)
        
        # Custom formatting for detailed logs
        if template is None:
            if log_type == "context_build":
                message = LogFormatter._format_context_build(metadata)
            elif log_type == "prompt_built":
                message = LogFormatter._format_prompt_built(metadata)
            else:
                message = entry["message"]
        elif template:
            # Try to format with metadata
            try:
                message = template.format(**metadata)
            except (KeyError, ValueError):
                # Fallback to original message if formatting fails
                message = entry["message"]
        else:
            # No template, use original message
            message = entry["message"]
        
        # Format: [timestamp] LEVEL: message
        return f"{icon} [{timestamp}] {level}: {message}"
    
    @staticmethod
    def _format_context_build(metadata: Dict[str, Any]) -> str:
        """Format context_build with details."""
        phase = metadata.get("phase", "unknown")
        functions = metadata.get("available_functions", [])
        function_count = len(functions)
        
        lines = [
            f"Building context for LLM:",
            f"  Phase: {phase}",
            f"  Available functions ({function_count}): {', '.join(functions[:5])}{'...' if function_count > 5 else ''}"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_prompt_built(metadata: Dict[str, Any]) -> str:
        """Format prompt_built with actual prompt content."""
        prompt_length = metadata.get("prompt_length", 0)
        prompt_preview = metadata.get("prompt_preview", "")
        
        lines = [
            f"Prompt constructed ({prompt_length} chars):",
            f"  Preview: {prompt_preview[:200]}{'...' if len(prompt_preview) > 200 else ''}"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_entries(entries: list) -> str:
        """
        Format multiple log entries into a multi-line string.
        
        Args:
            entries: List of log entry dicts
            
        Returns:
            Multi-line formatted string
        """
        return "\n".join(LogFormatter.format_entry(entry) for entry in entries)
