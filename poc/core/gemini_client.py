"""Gemini client for LLM integration via Vertex AI."""

import os
from typing import Iterator, Optional, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from config.settings import settings
from utils.technical_logger import TechnicalLogger, LogLevel


class GeminiClient:
    """Client for interacting with Gemini via Vertex AI."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize Gemini client.
        
        Args:
            project_id: GCP project ID. Defaults to settings.GCP_PROJECT_ID
            location: GCP location. Defaults to settings.GCP_LOCATION
            model_name: Model name. Defaults to settings.GEMINI_MODEL
            logger: Technical logger instance
        """
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.location = location or settings.GCP_LOCATION
        self.model_name = model_name or settings.GEMINI_MODEL
        self.logger = logger
        
        # Initialize Vertex AI
        if not settings.MOCK_LLM:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            if self.logger:
                self.logger.info("llm_init", f"Initialized Gemini: {self.model_name}", {
                    "project": self.project_id,
                    "location": self.location,
                    "model": self.model_name
                })
        else:
            self.model = None
            if self.logger:
                self.logger.warning("llm_init", "Mock mode enabled - no real LLM calls", {
                    "mock_mode": True
                })
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generate non-streaming response.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if self.logger:
            self.logger.info("llm_call", "Generating response (non-streaming)", {
                "prompt_length": len(prompt),
                "temperature": temperature,
                "max_tokens": max_output_tokens
            })
        
        if settings.MOCK_LLM:
            response = self._mock_generate(prompt)
            if self.logger:
                self.logger.info("llm_response", "Mock response generated", {
                    "response_length": len(response)
                })
            return response
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if self.logger:
            # Note: token counts not available in response object for non-streaming
            self.logger.info("llm_response", "Response generated", {
                "response_length": len(response.text)
            })
        
        return response.text
    
    def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        **kwargs
    ) -> Iterator[str]:
        """
        Generate streaming response.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks as they're generated
        """
        if self.logger:
            self.logger.info("llm_call", "Generating response (streaming)", {
                "prompt_length": len(prompt),
                "temperature": temperature,
                "max_tokens": max_output_tokens
            })
        
        if settings.MOCK_LLM:
            response = self._mock_generate(prompt)
            if self.logger:
                self.logger.info("llm_response", "Mock response generated (streaming)", {
                    "response_length": len(response)
                })
            yield response
            return
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=True
        )
        
        total_chunks = 0
        for chunk in response:
            if chunk.text:
                total_chunks += 1
                yield chunk.text
        
        if self.logger:
            self.logger.info("llm_response", "Streaming response complete", {
                "total_chunks": total_chunks
            })
    
    def build_prompt(
        self,
        user_message: str,
        system_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Build prompt with context.
        
        Args:
            user_message: User's message
            system_context: System context (taxonomy data, etc.)
            conversation_history: Previous messages
            
        Returns:
            Formatted prompt
        """
        parts = []
        
        # Add system context if provided
        if system_context:
            parts.append("# System Context")
            for key, value in system_context.items():
                parts.append(f"\n## {key}")
                parts.append(str(value))
            parts.append("\n")
        
        # Add conversation history if provided
        if conversation_history:
            parts.append("# Conversation History")
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"\n**{role.title()}:** {content}")
            parts.append("\n")
        
        # Add current user message
        parts.append("# Current User Message")
        parts.append(user_message)
        
        return "\n".join(parts)
    
    def _mock_generate(self, prompt: str) -> str:
        """
        Mock response for testing without GCP.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        return "This is a mock response. Set MOCK_LLM=false to use real Gemini."
