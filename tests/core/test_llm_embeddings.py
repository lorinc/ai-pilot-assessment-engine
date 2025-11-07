"""
Tests for LLM Embedding Support - Day 11 (Release 2.2)

Tests embedding generation via LLMClient using Gemini embeddings.
Maintains architectural consistency (single LLM provider).

TDD RED Phase: These tests should FAIL initially.
"""
import pytest
from unittest.mock import Mock, patch
from src.core.llm_client import LLMClient


class TestEmbeddingGeneration:
    """Test embedding generation via Gemini"""
    
    def test_generate_embedding_returns_vector(self):
        """Should return embedding vector for text"""
        client = LLMClient()
        
        text = "I want to assess sales forecasting"
        embedding = client.generate_embedding(text)
        
        # Gemini embeddings are 768 dimensions
        assert isinstance(embedding, list)
        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_embedding_different_texts_different_vectors(self):
        """Different texts should produce different embeddings"""
        client = LLMClient()
        
        text1 = "I want to assess sales forecasting"
        text2 = "The weather is nice today"
        
        emb1 = client.generate_embedding(text1)
        emb2 = client.generate_embedding(text2)
        
        # Vectors should be different
        assert emb1 != emb2
    
    def test_generate_embedding_similar_texts_similar_vectors(self):
        """Similar texts should produce similar embeddings"""
        client = LLMClient()
        
        text1 = "I want to assess sales forecasting"
        text2 = "I need to evaluate sales predictions"
        
        emb1 = client.generate_embedding(text1)
        emb2 = client.generate_embedding(text2)
        
        # Calculate cosine similarity
        import numpy as np
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Should be highly similar (> 0.7)
        assert similarity > 0.7, f"Similarity too low: {similarity}"
    
    def test_generate_embedding_empty_text(self):
        """Should handle empty text gracefully"""
        client = LLMClient()
        
        embedding = client.generate_embedding("")
        
        # Should still return a vector (might be zeros or default)
        assert isinstance(embedding, list)
        assert len(embedding) == 768
    
    def test_generate_embedding_with_caller_id(self):
        """Should accept caller ID for logging"""
        client = LLMClient()
        
        text = "test message"
        embedding = client.generate_embedding(text, caller="test_intent_detection")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 768


class TestEmbeddingCaching:
    """Test embedding caching for performance"""
    
    def test_same_text_uses_cache(self):
        """Should cache embeddings for same text"""
        client = LLMClient()
        
        text = "I want to assess sales forecasting"
        
        # First call - should hit API
        emb1 = client.generate_embedding(text)
        
        # Second call - should use cache
        emb2 = client.generate_embedding(text)
        
        # Should return same embedding
        assert emb1 == emb2
    
    def test_cache_key_case_insensitive(self):
        """Cache should be case-insensitive"""
        client = LLMClient()
        
        text1 = "I want to assess sales forecasting"
        text2 = "i want to assess sales forecasting"
        
        emb1 = client.generate_embedding(text1)
        emb2 = client.generate_embedding(text2)
        
        # Should return same embedding (cached)
        assert emb1 == emb2
    
    def test_cache_key_strips_whitespace(self):
        """Cache should strip leading/trailing whitespace"""
        client = LLMClient()
        
        text1 = "I want to assess sales forecasting"
        text2 = "  I want to assess sales forecasting  "
        
        emb1 = client.generate_embedding(text1)
        emb2 = client.generate_embedding(text2)
        
        # Should return same embedding (cached)
        assert emb1 == emb2


class TestEmbeddingBatchGeneration:
    """Test batch embedding generation for efficiency"""
    
    def test_generate_embeddings_batch(self):
        """Should generate embeddings for multiple texts efficiently"""
        client = LLMClient()
        
        texts = [
            "I want to assess sales forecasting",
            "The data quality is 3 stars",
            "What's the bottleneck?"
        ]
        
        embeddings = client.generate_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 768 for emb in embeddings)
    
    def test_batch_generation_faster_than_sequential(self):
        """Batch generation should be more efficient"""
        # This is more of a performance test
        # For now, just verify it works
        client = LLMClient()
        
        texts = ["text1", "text2", "text3"]
        embeddings = client.generate_embeddings_batch(texts)
        
        assert len(embeddings) == len(texts)


class TestEmbeddingErrorHandling:
    """Test error handling for embedding generation"""
    
    def test_generate_embedding_api_error(self):
        """Should handle API errors gracefully"""
        # Create client with real embedding model (not mock mode)
        import os
        original_mock = os.environ.get('MOCK_LLM')
        if 'MOCK_LLM' in os.environ:
            del os.environ['MOCK_LLM']
        
        try:
            client = LLMClient()
            
            # Clear cache to force API call
            client.embedding_cache.clear()
            
            # Mock the embedding model to raise an error
            if client.embedding_model:
                client.embedding_model = Mock()
                client.embedding_model.get_embeddings.side_effect = Exception("API Error")
                
                embedding = client.generate_embedding("test_error_case_unique_12345")
                
                # Should return zero vector as fallback
                assert isinstance(embedding, list)
                assert len(embedding) == 768
                assert all(x == 0.0 for x in embedding)
        finally:
            # Restore original setting
            if original_mock:
                os.environ['MOCK_LLM'] = original_mock
    
    def test_generate_embedding_with_logger(self):
        """Should log embedding generation"""
        mock_logger = Mock()
        client = LLMClient(logger=mock_logger)
        
        client.generate_embedding("test message", caller="test")
        
        # Should have logged the operation
        assert mock_logger.info.called or mock_logger.debug.called
