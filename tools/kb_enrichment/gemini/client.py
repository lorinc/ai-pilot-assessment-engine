"""Gemini API client using Vertex AI."""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.language_models import TextEmbeddingModel

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Vertex AI Gemini API."""
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        project_id: Optional[str] = None,
        location: str = "us-central1"
    ):
        """Initialize Gemini client.
        
        Args:
            model_name: Gemini model name
            temperature: Sampling temperature (0-1)
            max_output_tokens: Maximum tokens in response
            project_id: GCP project ID (defaults to env or gcloud config)
            location: GCP region
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        
        # Initialize Vertex AI
        project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        
        try:
            vertexai.init(project=project_id, location=location)
            logger.info(f"Initialized Vertex AI: project={project_id}, location={location}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise
        
        # Initialize model
        self.model = GenerativeModel(model_name)
        logger.info(f"Loaded model: {model_name}")
        
        # Initialize embedding model
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        logger.info("Loaded embedding model: text-embedding-004")
        
        # Track API usage
        self.total_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        retry_count: int = 3
    ) -> str:
        """Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: If True, request JSON output
            retry_count: Number of retries on failure
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails after retries
        """
        config = GenerationConfig(
            temperature=temperature or self.temperature,
            max_output_tokens=max_tokens or self.max_output_tokens,
        )
        
        # Add JSON instruction if needed
        if json_mode:
            prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        
        for attempt in range(retry_count):
            try:
                logger.debug(f"Generating (attempt {attempt + 1}/{retry_count})...")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=config
                )
                
                # Extract text
                text = response.text
                
                # Track usage
                self.total_calls += 1
                # Note: Token counting would require additional API calls
                # For now, we estimate based on text length
                self.total_input_tokens += len(prompt) // 4
                self.total_output_tokens += len(text) // 4
                
                logger.debug(f"Generated {len(text)} characters")
                
                return text
                
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < retry_count - 1:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Generation failed after {retry_count} attempts")
                    raise
    
    def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """Generate and parse JSON response.
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            retry_count: Number of retries on failure
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        text = self.generate(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
            retry_count=retry_count
        )
        
        # Try to extract JSON from markdown code blocks
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {text[:500]}...")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.get_embeddings(texts)
            return [emb.values for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def estimate_cost(self) -> Dict[str, Any]:
        """Estimate API usage cost.
        
        Returns:
            Cost estimation dictionary
        """
        # Rough pricing (as of 2024, subject to change)
        # Gemini 1.5 Pro: ~$0.00125/1K input tokens, ~$0.005/1K output tokens
        # Embeddings: ~$0.00001/1K tokens
        
        input_cost = (self.total_input_tokens / 1000) * 0.00125
        output_cost = (self.total_output_tokens / 1000) * 0.005
        total_cost = input_cost + output_cost
        
        return {
            "total_calls": self.total_calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "breakdown": {
                "input_cost": round(input_cost, 4),
                "output_cost": round(output_cost, 4)
            }
        }
    
    def get_usage_summary(self) -> str:
        """Get human-readable usage summary.
        
        Returns:
            Summary string
        """
        cost = self.estimate_cost()
        
        return (
            f"API Usage Summary:\n"
            f"  Total Calls: {cost['total_calls']}\n"
            f"  Input Tokens: {cost['input_tokens']:,}\n"
            f"  Output Tokens: {cost['output_tokens']:,}\n"
            f"  Estimated Cost: ${cost['estimated_cost_usd']:.4f}"
        )
