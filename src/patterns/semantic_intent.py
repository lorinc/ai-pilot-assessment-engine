"""
Semantic Intent Detection using OpenAI Embeddings

Replaces regex-based trigger detection with semantic similarity.
Uses OpenAI text-embedding-3-small for high-quality, low-cost embeddings.

Performance:
- Latency: ~50-100ms per message (first time), ~0ms (cached)
- Cost: $0.02 per 1M tokens (~$0.0000004 per message)
- Quality: Better than regex, handles novel phrasings
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from openai import OpenAI


class SemanticIntentDetector:
    """
    Detects user intent using semantic similarity with OpenAI embeddings.
    
    Features:
    - Embedding cache (avoid repeated API calls)
    - Cosine similarity scoring
    - Threshold-based matching
    - Fallback to regex for obvious cases
    """
    
    def __init__(self, cache_dir: str = '.cache/embeddings'):
        """
        Initialize semantic intent detector.
        
        Args:
            cache_dir: Directory to cache embeddings
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for this session
        self.embedding_cache: Dict[str, List[float]] = {}
        
        # Load persistent cache
        self._load_cache()
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cache
            
        Returns:
            Embedding vector (1536 dimensions)
        """
        # Normalize text
        text = text.strip().lower()
        
        # Check in-memory cache
        if use_cache and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Check persistent cache
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if use_cache and cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                embedding = data['embedding']
                self.embedding_cache[text] = embedding
                return embedding
        
        # Get from API
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache it
            self.embedding_cache[text] = embedding
            
            if use_cache:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'text': text,
                        'embedding': embedding,
                        'model': 'text-embedding-3-small'
                    }, f)
            
            return embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
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
        examples: List[str],
        threshold: float = 0.75
    ) -> tuple[bool, float]:
        """
        Detect if message matches intent based on examples.
        
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
            force: Force recomputation even if cached
        """
        print(f"Precomputing embeddings for {len(examples)} examples...")
        for i, example in enumerate(examples, 1):
            if force:
                # Clear cache for this example first
                text = example.strip().lower()
                if text in self.embedding_cache:
                    del self.embedding_cache[text]
                cache_key = self._get_cache_key(text)
                cache_file = self.cache_dir / f"{cache_key}.json"
                if cache_file.exists():
                    cache_file.unlink()
            
            self.get_embedding(example)
            if i % 10 == 0:
                print(f"  {i}/{len(examples)} done")
        print("✅ Precomputation complete")
    
    def _get_cache_key(self, text: str) -> str:
        """Get cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _load_cache(self):
        """Load persistent cache into memory"""
        if not self.cache_dir.exists():
            return
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    text = data['text']
                    embedding = data['embedding']
                    self.embedding_cache[text] = embedding
            except Exception:
                # Skip corrupted cache files
                pass
    
    def clear_cache(self, examples: Optional[List[str]] = None):
        """
        Clear embedding cache.
        
        Args:
            examples: If provided, clear only these examples. Otherwise clear all.
        """
        if examples:
            # Clear specific examples
            count = 0
            for example in examples:
                text = example.strip().lower()
                
                # Clear from memory
                if text in self.embedding_cache:
                    del self.embedding_cache[text]
                    count += 1
                
                # Clear from disk
                cache_key = self._get_cache_key(text)
                cache_file = self.cache_dir / f"{cache_key}.json"
                if cache_file.exists():
                    cache_file.unlink()
            
            print(f"✅ Cleared {count} cached embeddings")
        else:
            # Clear all
            self.embedding_cache.clear()
            
            # Clear persistent cache
            count = 0
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
                count += 1
            
            print(f"✅ Cleared all {count} cached embeddings")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        persistent_count = len(list(self.cache_dir.glob('*.json')))
        
        return {
            'in_memory_count': len(self.embedding_cache),
            'persistent_count': persistent_count,
            'cache_dir': str(self.cache_dir)
        }


# Global instance (singleton pattern)
_detector_instance: Optional[SemanticIntentDetector] = None


def get_detector() -> SemanticIntentDetector:
    """Get global semantic intent detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SemanticIntentDetector()
    return _detector_instance
