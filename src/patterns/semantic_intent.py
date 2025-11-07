"""
Semantic Intent Detection using Gemini Embeddings

Replaces regex-based trigger detection with semantic similarity.
Uses Gemini text-embedding-004 via existing LLMClient infrastructure.

Performance:
- Latency: ~50-100ms per message (first time), ~0ms (cached)
- Cost: Gemini embeddings via Vertex AI
- Quality: Better than regex, handles novel phrasings

Day 11 Refactoring: Switched from OpenAI to Gemini for architectural consistency.
"""
import os
import sys
import json
import hashlib
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Fix import path
if __name__ != "__main__":
    from src.core.llm_client import LLMClient
else:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.core.llm_client import LLMClient


class SemanticIntentDetector:
    """
    Detects user intent using semantic similarity with Gemini embeddings.
    
    Features:
    - Embedding cache (via LLMClient)
    - Cosine similarity scoring
    - Threshold-based matching
    - Fallback to regex for obvious cases
    
    Day 11: Refactored to use LLMClient instead of OpenAI.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None, intent_examples_path: Optional[str] = None):
        """
        Initialize semantic intent detector.
        
        Args:
            llm_client: Optional LLMClient instance (creates new one if not provided)
            intent_examples_path: Path to intent examples YAML file
        """
        self.client = llm_client or LLMClient()
        
        # Load intent examples
        if intent_examples_path is None:
            # Default path
            intent_examples_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'intent_examples.yaml'
            )
        
        self.intent_examples = self._load_intent_examples(intent_examples_path)
        
        # Note: Caching is now handled by LLMClient
        # No need for separate cache management
    
    def _load_intent_examples(self, path: str) -> Dict[str, List[str]]:
        """Load intent examples from YAML file"""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Extract just the examples for each intent
            examples = {}
            for intent, config in data.items():
                examples[intent] = config.get('examples', [])
            
            return examples
        except Exception as e:
            print(f"Warning: Could not load intent examples from {path}: {e}")
            return {}
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for text using LLMClient.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cache (always True, handled by LLMClient)
            
        Returns:
            Embedding vector (768 dimensions for Gemini)
        """
        # Delegate to LLMClient (handles caching internally)
        return self.client.generate_embedding(text, caller="semantic_intent")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        # Cosine similarity
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def detect_intent(
        self,
        message: str,
        threshold: float = 0.65
    ) -> str:
        """
        Detect user intent from message using loaded examples.
        
        Args:
            message: User message
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            Intent name (e.g., 'discovery', 'assessment', 'analysis')
        """
        # Get message embedding
        message_emb = self.get_embedding(message)
        
        # Compare against all intent examples
        best_intent = 'clarification'  # Default fallback
        best_similarity = 0.0
        
        for intent, examples in self.intent_examples.items():
            for example in examples:
                example_emb = self.get_embedding(example)
                similarity = self.cosine_similarity(message_emb, example_emb)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_intent = intent
        
        # If similarity is too low, default to clarification
        if best_similarity < threshold:
            return 'clarification'
        
        return best_intent
    
    def detect_intent_with_confidence(
        self,
        message: str,
        threshold: float = 0.65
    ) -> Tuple[str, float]:
        """
        Detect user intent with confidence score.
        
        Args:
            message: User message
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            (intent, confidence) tuple
        """
        # Get message embedding
        message_emb = self.get_embedding(message)
        
        # Compare against all intent examples
        best_intent = 'clarification'
        best_similarity = 0.0
        
        for intent, examples in self.intent_examples.items():
            for example in examples:
                example_emb = self.get_embedding(example)
                similarity = self.cosine_similarity(message_emb, example_emb)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_intent = intent
        
        # If similarity is too low, default to clarification
        if best_similarity < threshold:
            return 'clarification', best_similarity
        
        return best_intent, best_similarity
    
    def detect_intent_legacy(
        self,
        message: str,
        examples: List[str],
        threshold: float = 0.75
    ) -> tuple[bool, float]:
        """
        Legacy method: Detect if message matches intent based on examples.
        
        Args:
            message: User message
            examples: Example messages for this intent
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            (matches, max_similarity)
        """
        # Get message embedding
        message_emb = self.get_embedding(message)
        
        # Compare against all examples
        max_similarity = 0.0
        
        for example in examples:
            example_emb = self.get_embedding(example)
            similarity = self.cosine_similarity(message_emb, example_emb)
            max_similarity = max(max_similarity, similarity)
        
        matches = max_similarity >= threshold
        return matches, max_similarity
    
    def precompute_embeddings(self, examples: List[str], force: bool = False):
        """
        Precompute embeddings for examples (for faster runtime).
        
        Args:
            examples: List of example messages
            force: Force recomputation (ignored, LLMClient handles caching)
        """
        print(f"Precomputing embeddings for {len(examples)} examples...")
        for i, example in enumerate(examples, 1):
            self.get_embedding(example)
            if i % 10 == 0:
                print(f"  {i}/{len(examples)} done")
        print("✅ Precomputation complete")


# Global instance (singleton pattern)
_detector_instance: Optional[SemanticIntentDetector] = None


def get_detector() -> SemanticIntentDetector:
    """Get global semantic intent detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SemanticIntentDetector()
    return _detector_instance
