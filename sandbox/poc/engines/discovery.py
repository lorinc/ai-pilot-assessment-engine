"""Discovery engine for identifying outputs from user descriptions."""

import re
from typing import Dict, List, Optional, Tuple
from core.taxonomy_loader import TaxonomyLoader
from core.gemini_client import GeminiClient
from models.data_models import Output, CreationContext
from utils.technical_logger import TechnicalLogger


class DiscoveryEngine:
    """
    Identifies organizational outputs from user descriptions.
    
    Uses keyword extraction, taxonomy search, and confidence scoring
    to match user problems to specific outputs in the taxonomy.
    """
    
    def __init__(
        self,
        taxonomy_loader: TaxonomyLoader,
        gemini_client: Optional[GeminiClient] = None,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize discovery engine.
        
        Args:
            taxonomy_loader: Taxonomy data loader
            gemini_client: Optional Gemini client for advanced keyword extraction
            logger: Optional technical logger
        """
        self.taxonomy = taxonomy_loader
        self.gemini = gemini_client
        self.logger = logger
    
    def extract_keywords(self, user_message: str) -> List[str]:
        """
        Extract keywords from user message.
        
        Uses simple heuristics: lowercase, split on whitespace/punctuation,
        filter common words, extract meaningful terms.
        
        Args:
            user_message: User's description of their problem
            
        Returns:
            List of extracted keywords
        """
        # Common stop words to filter out
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'we', 'our', 'have', 'this', 'they',
            'can', 'cant', 'cannot', 'could', 'should', 'would', 'my', 'me',
            'i', 'you', 'your', 'us', 'them', 'their', 'been', 'being', 'do',
            'does', 'did', 'doing', 'but', 'if', 'or', 'because', 'when',
            'where', 'why', 'how', 'all', 'each', 'more', 'most', 'other',
            'some', 'such', 'than', 'too', 'very', 'just', 'so', 'get', 'got'
        }
        
        # Lowercase and extract words
        text = user_message.lower()
        
        # Split on whitespace and punctuation, keep words with 3+ chars
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter stop words and deduplicate
        keywords = list(set(w for w in words if w not in stop_words))
        
        if self.logger:
            self.logger.debug("keyword_extraction", f"Extracted {len(keywords)} keywords", {
                "keywords": keywords[:10],  # First 10 for logging
                "total_count": len(keywords)
            })
        
        return keywords
    
    def match_outputs(self, keywords: List[str]) -> List[Dict]:
        """
        Match keywords to outputs in taxonomy.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matches with scores, sorted by relevance
        """
        matches = self.taxonomy.search_outputs(keywords)
        
        if self.logger:
            self.logger.info("taxonomy_search", f"Found {len(matches)} matches", {
                "query": ", ".join(keywords[:5]),
                "result_count": len(matches)
            })
        
        return matches
    
    def calculate_confidence(
        self,
        match_score: int,
        user_message: str,
        output: Dict
    ) -> float:
        """
        Calculate confidence score for a match.
        
        Confidence is based on:
        - Match score from taxonomy search (0-100 points)
        - Pain point overlap (bonus points)
        - Message length and specificity (normalization)
        
        Args:
            match_score: Raw score from taxonomy search
            user_message: Original user message
            output: Matched output dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from match score (normalize to 0-1)
        # Typical match scores range from 5-50, excellent matches 50+
        base_confidence = min(match_score / 50.0, 1.0)
        
        # Bonus for pain point mentions
        pain_points = output.get("common_pain_points", [])
        message_lower = user_message.lower()
        pain_point_matches = sum(
            1 for pp in pain_points
            if any(word in message_lower for word in pp.lower().split()[:3])
        )
        
        if pain_points:
            pain_point_bonus = min(pain_point_matches / len(pain_points), 0.2)
        else:
            pain_point_bonus = 0.0
        
        # Penalty for very short messages (less specific)
        if len(user_message.split()) < 5:
            length_penalty = 0.1
        else:
            length_penalty = 0.0
        
        # Calculate final confidence
        confidence = base_confidence + pain_point_bonus - length_penalty
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        
        return confidence
    
    def identify_output(
        self,
        user_message: str,
        min_confidence: float = 0.5
    ) -> Tuple[Optional[Output], float, List[Dict]]:
        """
        Identify output from user message.
        
        Args:
            user_message: User's description of their problem
            min_confidence: Minimum confidence threshold (default 0.5)
            
        Returns:
            Tuple of (best_match_output, confidence, all_matches)
            Returns (None, 0.0, matches) if no match meets threshold
        """
        # Extract keywords
        keywords = self.extract_keywords(user_message)
        
        if not keywords:
            if self.logger:
                self.logger.warning("no_keywords", "No keywords extracted from message", {
                    "message_length": len(user_message)
                })
            return None, 0.0, []
        
        # Search taxonomy
        matches = self.match_outputs(keywords)
        
        if not matches:
            if self.logger:
                self.logger.info("no_matches", "No outputs matched keywords", {
                    "keywords": keywords[:5]
                })
            return None, 0.0, []
        
        # Calculate confidence for each match
        scored_matches = []
        for match in matches:
            output_dict = match["output"]
            score = match["score"]
            confidence = self.calculate_confidence(score, user_message, output_dict)
            
            scored_matches.append({
                "output": output_dict,
                "score": score,
                "confidence": confidence
            })
        
        # Sort by confidence
        scored_matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Get best match
        best_match = scored_matches[0]
        best_confidence = best_match["confidence"]
        
        if best_confidence >= min_confidence:
            # Convert to Output model
            output_dict = best_match["output"]
            output = Output(
                id=output_dict["id"],
                name=output_dict["name"],
                function=output_dict["function"],
                description=output_dict.get("description")
            )
            
            if self.logger:
                self.logger.info("output_identified", f"Identified: {output.name}", {
                    "output_name": output.name,
                    "confidence": f"{best_confidence:.2f}",
                    "function": output.function
                })
            
            return output, best_confidence, scored_matches
        else:
            if self.logger:
                self.logger.warning("low_confidence", f"Best match below threshold", {
                    "best_confidence": f"{best_confidence:.2f}",
                    "threshold": min_confidence,
                    "best_match": best_match["output"]["name"]
                })
            
            return None, best_confidence, scored_matches
    
    def infer_context(self, output: Output) -> Optional[CreationContext]:
        """
        Infer creation context from output's typical context.
        
        Args:
            output: Identified output
            
        Returns:
            CreationContext with inferred values, or None if not available
        """
        # Get output details from taxonomy
        output_dict = self.taxonomy.get_output_by_id(output.id)
        
        if not output_dict:
            if self.logger:
                self.logger.warning("context_inference_failed", "Output not found in taxonomy", {
                    "output_id": output.id
                })
            return None
        
        # Extract typical creation context
        typical_context = output_dict.get("typical_creation_context", {})
        
        if not typical_context:
            if self.logger:
                self.logger.warning("no_typical_context", "No typical context defined", {
                    "output_id": output.id
                })
            return None
        
        # Create context with medium confidence (needs user validation)
        context = CreationContext(
            team=typical_context.get("team", "Unknown Team"),
            process=typical_context.get("process", "Unknown Process"),
            step=typical_context.get("step"),
            system=typical_context.get("system", "Unknown System"),
            confidence=0.6  # Medium confidence, needs validation
        )
        
        if self.logger:
            self.logger.info("context_inferred", "Context inferred from taxonomy", {
                "team": context.team,
                "system": context.system,
                "process": context.process
            })
        
        return context
    
    def generate_clarifying_question(
        self,
        matches: List[Dict],
        user_message: str
    ) -> str:
        """
        Generate clarifying question when confidence is low.
        
        Args:
            matches: List of potential matches
            user_message: Original user message
            
        Returns:
            Clarifying question string
        """
        if not matches:
            return (
                "I couldn't identify a specific output from your description. "
                "Could you be more specific about what you're trying to create or improve? "
                "For example: 'sales forecast', 'customer support tickets', 'financial reports', etc."
            )
        
        # Show top 3 matches
        top_matches = matches[:3]
        options = []
        for i, match in enumerate(top_matches, 1):
            output = match["output"]
            options.append(f"{i}. **{output['name']}** ({output['function']})")
        
        question = (
            "I found a few possible matches. Which one best describes what you're working on?\n\n"
            + "\n".join(options) +
            "\n\nOr describe it differently if none of these match."
        )
        
        return question
