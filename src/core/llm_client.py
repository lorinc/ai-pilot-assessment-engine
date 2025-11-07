"""LLM client for Gemini integration via Vertex AI."""

import os
import hashlib
from typing import Iterator, Optional, Dict, Any, List
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.language_models import TextEmbeddingModel

from config.settings import settings
from utils.logger import TechnicalLogger, LogLevel


class LLMClient:
    """Client for interacting with Gemini via Vertex AI."""
    
    # Context size limits (in characters, conservative estimate)
    MAX_PROMPT_CHARS = 30000  # ~7500 tokens (Gemini supports 1M but be conservative)
    WARN_PROMPT_CHARS = 20000  # Warning threshold
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize LLM client.
        
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
        
        # Embedding cache (in-memory)
        self.embedding_cache: Dict[str, List[float]] = {}
        
        # Initialize Vertex AI
        if not settings.MOCK_LLM:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            # Initialize embedding model (text-embedding-004 for Gemini)
            self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            if self.logger:
                self.logger.info("llm_init", f"Initialized Gemini: {self.model_name}", {
                    "project": self.project_id,
                    "location": self.location,
                    "model": self.model_name,
                    "embedding_model": "text-embedding-004"
                })
        else:
            self.model = None
            self.embedding_model = None
            if self.logger:
                self.logger.warning("llm_init", "Mock mode enabled - no real LLM calls", {
                    "mock_mode": True
                })
    
    def _validate_prompt_size(self, prompt: str, caller: str = "unknown") -> None:
        """
        Validate prompt size and raise error if too large.
        
        Args:
            prompt: The prompt to validate
            caller: Name of the calling function/module for debugging
            
        Raises:
            ValueError: If prompt exceeds MAX_PROMPT_CHARS
        """
        prompt_length = len(prompt)
        
        # Hard limit - reject
        if prompt_length > self.MAX_PROMPT_CHARS:
            error_details = {
                "caller": caller,
                "prompt_length": prompt_length,
                "max_allowed": self.MAX_PROMPT_CHARS,
                "exceeded_by": prompt_length - self.MAX_PROMPT_CHARS,
                "prompt_preview": prompt[:500] + "...",
                "prompt_end": "..." + prompt[-500:] if len(prompt) > 500 else ""
            }
            
            if self.logger:
                self.logger.error(
                    "llm_context_overflow",
                    f"🚨 CONTEXT SIZE FAILSAFE TRIGGERED by {caller}",
                    error_details
                )
            
            raise ValueError(
                f"Prompt size ({prompt_length} chars) exceeds maximum allowed ({self.MAX_PROMPT_CHARS} chars). "
                f"Caller: {caller}. Exceeded by: {prompt_length - self.MAX_PROMPT_CHARS} chars. "
                f"This is a failsafe to prevent sending unreasonably large context to the LLM. "
                f"Check logs for details."
            )
        
        # Warning threshold - log but allow
        if prompt_length > self.WARN_PROMPT_CHARS:
            if self.logger:
                self.logger.warning(
                    "llm_context_warning",
                    f"⚠️ Large context detected from {caller}",
                    {
                        "caller": caller,
                        "prompt_length": prompt_length,
                        "warn_threshold": self.WARN_PROMPT_CHARS,
                        "max_allowed": self.MAX_PROMPT_CHARS,
                        "usage_percent": round(100 * prompt_length / self.MAX_PROMPT_CHARS, 1)
                    }
                )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        caller: str = "unknown",
        **kwargs
    ) -> str:
        """
        Generate non-streaming response.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
            caller: Name of calling function/module for debugging
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
            
        Raises:
            ValueError: If prompt exceeds size limits
        """
        # FAILSAFE: Validate prompt size
        self._validate_prompt_size(prompt, caller)
        
        if self.logger:
            self.logger.info("llm_call", "Generating response (non-streaming)", {
                "caller": caller,
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
            # Calculate approximate cost
            input_tokens = len(prompt) // 4  # Rough estimate: 4 chars per token
            output_tokens = len(response.text) // 4
            input_cost = (input_tokens / 1_000_000) * 0.075  # $0.075 per 1M input tokens
            output_cost = (output_tokens / 1_000_000) * 0.30  # $0.30 per 1M output tokens
            total_cost = input_cost + output_cost
            
            self.logger.info("llm_response", "Response generated", {
                "response_length": len(response.text),
                "input_tokens_est": input_tokens,
                "output_tokens_est": output_tokens,
                "cost_usd_est": round(total_cost, 6)
            })
        
        return response.text
    
    def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        caller: str = "unknown",
        **kwargs
    ) -> Iterator[str]:
        """
        Generate streaming response.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
            caller: Name of calling function/module for debugging
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks as they're generated
            
        Raises:
            ValueError: If prompt exceeds size limits
        """
        # FAILSAFE: Validate prompt size
        self._validate_prompt_size(prompt, caller)
        
        if self.logger:
            self.logger.info("llm_call", "Generating response (streaming)", {
                "caller": caller,
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
    
    def generate_embedding(
        self,
        text: str,
        caller: str = "unknown"
    ) -> List[float]:
        """
        Generate embedding vector for text using Gemini embeddings.
        
        Args:
            text: Text to embed
            caller: Caller ID for logging
            
        Returns:
            Embedding vector (768 dimensions for text-embedding-004)
        """
        # Normalize text for caching
        normalized_text = text.strip().lower()
        
        # Check cache first
        cache_key = hashlib.md5(normalized_text.encode()).hexdigest()
        if cache_key in self.embedding_cache:
            if self.logger:
                self.logger.debug("embedding_cache_hit", f"Cache hit for text", {
                    "caller": caller,
                    "text_length": len(text),
                    "cache_key": cache_key
                })
            return self.embedding_cache[cache_key]
        
        # Handle empty text
        if not normalized_text:
            zero_vector = [0.0] * 768
            self.embedding_cache[cache_key] = zero_vector
            return zero_vector
        
        # Generate embedding
        try:
            if settings.MOCK_LLM or self.embedding_model is None:
                # Return mock embedding for testing
                import random
                random.seed(hash(normalized_text))
                embedding = [random.random() for _ in range(768)]
            else:
                # Call Gemini embedding API
                embeddings = self.embedding_model.get_embeddings([text])
                embedding = embeddings[0].values
            
            # Cache the result
            self.embedding_cache[cache_key] = embedding
            
            if self.logger:
                self.logger.info("embedding_generated", f"Generated embedding", {
                    "caller": caller,
                    "text_length": len(text),
                    "embedding_dim": len(embedding)
                })
            
            return embedding
            
        except Exception as e:
            if self.logger:
                self.logger.error("embedding_error", f"Error generating embedding: {e}", {
                    "caller": caller,
                    "text_length": len(text),
                    "error": str(e)
                })
            # Return zero vector as fallback
            zero_vector = [0.0] * 768
            self.embedding_cache[cache_key] = zero_vector
            return zero_vector
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        caller: str = "unknown"
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            caller: Caller ID for logging
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = self.generate_embedding(text, caller=caller)
            embeddings.append(embedding)
        
        return embeddings
    
    def _mock_generate(self, prompt: str) -> str:
        """
        Mock response for testing without GCP.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        return "This is a mock response. Set MOCK_LLM=false to use real Gemini."
