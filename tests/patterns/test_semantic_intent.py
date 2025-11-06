"""
Tests for Semantic Intent Detection

Tests the OpenAI embedding-based intent detection system.
"""
import pytest
from src.patterns.semantic_intent import SemanticIntentDetector, get_detector


class TestSemanticIntentDetector:
    """Test semantic intent detection"""
    
    def test_detector_initialization(self):
        """Detector should initialize successfully"""
        detector = SemanticIntentDetector()
        assert detector is not None
        assert detector.client is not None
    
    def test_get_embedding(self):
        """Should get embedding for text"""
        detector = SemanticIntentDetector()
        
        embedding = detector.get_embedding("Data quality is 3 stars")
        
        # Should be 1536 dimensions (text-embedding-3-small)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embedding_cache(self):
        """Should cache embeddings"""
        detector = SemanticIntentDetector()
        
        text = "Test message for caching"
        
        # First call - from API
        emb1 = detector.get_embedding(text)
        
        # Second call - from cache
        emb2 = detector.get_embedding(text)
        
        # Should be identical
        assert emb1 == emb2
        
        # Should be in cache
        assert text.lower() in detector.embedding_cache
    
    def test_cosine_similarity(self):
        """Should calculate cosine similarity correctly"""
        detector = SemanticIntentDetector()
        
        # Identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = detector.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001
        
        # Orthogonal vectors
        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        similarity = detector.cosine_similarity(vec3, vec4)
        assert abs(similarity - 0.0) < 0.001
    
    def test_detect_intent_similar_messages(self):
        """Should detect similar messages"""
        detector = SemanticIntentDetector()
        
        examples = [
            "Data quality is 3 stars",
            "The team struggles with this",
            "Process is poor"
        ]
        
        # Similar message
        message = "Data quality is about 3 stars"
        matches, similarity = detector.detect_intent(message, examples, threshold=0.75)
        
        assert matches is True
        assert similarity > 0.75
    
    def test_detect_intent_dissimilar_messages(self):
        """Should not detect dissimilar messages"""
        detector = SemanticIntentDetector()
        
        examples = [
            "Data quality is 3 stars",
            "The team struggles with this",
            "Process is poor"
        ]
        
        # Dissimilar message
        message = "What's the weather like today?"
        matches, similarity = detector.detect_intent(message, examples, threshold=0.75)
        
        assert matches is False
        assert similarity < 0.75
    
    def test_detect_intent_variations(self):
        """Should handle variations of the same intent"""
        detector = SemanticIntentDetector()
        
        examples = [
            "Data quality is 3 stars",
            "I rate the data quality as 3 stars"
        ]
        
        variations = [
            "Data quality is about 3 stars",
            "Quality is 3 stars",
            "I'd rate it 3 stars",
            "The quality is around 3 stars"
        ]
        
        for variation in variations:
            matches, similarity = detector.detect_intent(variation, examples, threshold=0.70)
            assert matches is True, f"Failed to match: {variation} (similarity: {similarity})"
    
    def test_precompute_embeddings(self):
        """Should precompute embeddings"""
        detector = SemanticIntentDetector()
        
        examples = [
            "Example 1",
            "Example 2",
            "Example 3"
        ]
        
        # Precompute
        detector.precompute_embeddings(examples)
        
        # All should be in cache
        for example in examples:
            assert example.lower() in detector.embedding_cache
    
    def test_cache_stats(self):
        """Should provide cache statistics"""
        detector = SemanticIntentDetector()
        
        # Add some embeddings
        detector.get_embedding("Test 1")
        detector.get_embedding("Test 2")
        
        stats = detector.get_cache_stats()
        
        assert 'in_memory_count' in stats
        assert 'persistent_count' in stats
        assert stats['in_memory_count'] >= 2


class TestGlobalDetector:
    """Test global detector instance"""
    
    def test_get_detector_singleton(self):
        """Should return same instance"""
        detector1 = get_detector()
        detector2 = get_detector()
        
        assert detector1 is detector2


class TestRealWorldScenarios:
    """Test real-world intent detection scenarios"""
    
    def test_assessment_intent(self):
        """Should detect assessment intent"""
        detector = SemanticIntentDetector()
        
        examples = [
            "Data quality is 3 stars",
            "The team struggles with this",
            "Process is poor",
            "System support is excellent"
        ]
        
        test_messages = [
            ("Quality is about 4 stars", True),
            ("The team is weak", True),
            ("Process is mediocre", True),
            ("What's the weather?", False),
            ("I need help", False)
        ]
        
        for message, should_match in test_messages:
            matches, similarity = detector.detect_intent(message, examples, threshold=0.70)
            assert matches == should_match, f"Failed for: {message} (similarity: {similarity})"
    
    def test_confusion_intent(self):
        """Should detect confusion intent"""
        detector = SemanticIntentDetector()
        
        examples = [
            "I'm confused about this",
            "I don't understand",
            "This doesn't make sense"
        ]
        
        test_messages = [
            ("I'm confused", True),
            ("I don't get it", True),
            ("This is confusing", True),
            ("Data quality is 3 stars", False)
        ]
        
        for message, should_match in test_messages:
            matches, similarity = detector.detect_intent(message, examples, threshold=0.70)
            assert matches == should_match, f"Failed for: {message} (similarity: {similarity})"
    
    def test_threshold_sensitivity(self):
        """Should respect threshold settings"""
        detector = SemanticIntentDetector()
        
        examples = ["Data quality is 3 stars"]
        message = "Quality is approximately 3 stars"
        
        # Lower threshold - should match
        matches_low, sim_low = detector.detect_intent(message, examples, threshold=0.70)
        assert matches_low is True
        
        # Higher threshold - might not match
        matches_high, sim_high = detector.detect_intent(message, examples, threshold=0.95)
        # Similarity should be same, but matching depends on threshold
        assert sim_low == sim_high
