"""
Scope matching logic for finding the most applicable factor instance.

This module implements the scope matching algorithm that determines which
factor instance best matches a needed scope, with support for exact matches,
generic fallbacks, and hierarchical scope matching.
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class FactorScope:
    """Scope dimensions for a factor instance."""
    domain: Optional[str] = None
    system: Optional[str] = None
    team: Optional[str] = None


@dataclass
class FactorInstance:
    """Scoped factor instance."""
    instance_id: str
    factor_id: str
    scope: FactorScope
    scope_label: str
    value: int
    confidence: float


@dataclass
class ScopeMatch:
    """Result of scope matching."""
    instance: FactorInstance
    match_score: float  # 0.0 to 1.0
    match_type: str  # "exact" | "generic_fallback" | "partial"


class ScopeMatcher:
    """
    Matches factor instances to needed scopes using intelligent fallback logic.
    
    The matcher finds the most specific applicable instance for a given scope,
    falling back to more generic instances when exact matches don't exist.
    """
    
    def calculate_scope_match(
        self,
        instance_scope: FactorScope,
        needed_scope: FactorScope
    ) -> float:
        """
        Calculate how well an instance scope matches a needed scope.
        
        Args:
            instance_scope: The scope of the factor instance
            needed_scope: The scope being queried for
            
        Returns:
            Match score from 0.0 (no match) to 1.0 (exact match)
            
        Algorithm:
            - Each dimension (domain, system, team) contributes 0.33 to the score
            - Exact match on dimension: +0.33
            - Generic instance (None) matching specific need: +0.20
            - Don't care (needed is None): +0.33
            - Mismatch: return 0.0 (instance doesn't apply)
        """
        score = 0.0
        dimensions = ["domain", "system", "team"]
        
        for dim in dimensions:
            instance_val = getattr(instance_scope, dim)
            needed_val = getattr(needed_scope, dim)
            
            if needed_val is None:
                # Don't care about this dimension - full credit
                score += 0.33
            elif instance_val == needed_val:
                # Exact match - full credit
                score += 0.33
            elif instance_val is None and needed_val is not None:
                # Instance is more generic - partial credit
                # This allows fallback to generic instances
                score += 0.20
            else:
                # Mismatch - instance doesn't apply
                return 0.0
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_applicable_value(
        self,
        factor_id: str,
        needed_scope: FactorScope,
        instances: List[FactorInstance]
    ) -> Optional[ScopeMatch]:
        """
        Find the most applicable factor instance for a given scope.
        
        Args:
            factor_id: The factor to query
            needed_scope: The scope needed
            instances: List of available factor instances
            
        Returns:
            ScopeMatch with best matching instance, or None if no match
            
        Selection Logic:
            1. Calculate match score for each instance
            2. Filter out non-matching instances (score = 0)
            3. Sort by match score (descending), then confidence (descending)
            4. Return the best match
        """
        # Filter instances for this factor
        factor_instances = [i for i in instances if i.factor_id == factor_id]
        
        if not factor_instances:
            return None
        
        # Calculate match scores
        candidates: List[Tuple[FactorInstance, float]] = []
        for instance in factor_instances:
            match_score = self.calculate_scope_match(instance.scope, needed_scope)
            if match_score > 0:
                candidates.append((instance, match_score))
        
        if not candidates:
            return None
        
        # Sort by match score (descending), then confidence (descending)
        candidates.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
        
        # Get best match
        best_instance, best_score = candidates[0]
        
        # Determine match type
        if best_score == 1.0:
            match_type = "exact"
        elif best_score >= 0.6:
            match_type = "generic_fallback"
        else:
            match_type = "partial"
        
        return ScopeMatch(
            instance=best_instance,
            match_score=best_score,
            match_type=match_type
        )
    
    def find_all_matches(
        self,
        factor_id: str,
        needed_scope: FactorScope,
        instances: List[FactorInstance]
    ) -> List[ScopeMatch]:
        """
        Find all matching instances, sorted by match quality.
        
        Useful for showing users alternative assessments or understanding
        the full scope hierarchy.
        
        Args:
            factor_id: The factor to query
            needed_scope: The scope needed
            instances: List of available factor instances
            
        Returns:
            List of ScopeMatch objects, sorted by match score and confidence
        """
        # Filter instances for this factor
        factor_instances = [i for i in instances if i.factor_id == factor_id]
        
        if not factor_instances:
            return []
        
        # Calculate match scores
        matches: List[ScopeMatch] = []
        for instance in factor_instances:
            match_score = self.calculate_scope_match(instance.scope, needed_scope)
            if match_score > 0:
                # Determine match type
                if match_score == 1.0:
                    match_type = "exact"
                elif match_score >= 0.6:
                    match_type = "generic_fallback"
                else:
                    match_type = "partial"
                
                matches.append(ScopeMatch(
                    instance=instance,
                    match_score=match_score,
                    match_type=match_type
                ))
        
        # Sort by match score (descending), then confidence (descending)
        matches.sort(key=lambda x: (x.match_score, x.instance.confidence), reverse=True)
        
        return matches
    
    def explain_match(
        self,
        match: ScopeMatch,
        needed_scope: FactorScope
    ) -> str:
        """
        Generate human-readable explanation of why this instance matches.
        
        Args:
            match: The scope match to explain
            needed_scope: The scope that was queried
            
        Returns:
            Human-readable explanation string
        """
        instance_scope = match.instance.scope
        
        if match.match_type == "exact":
            return f"Exact match for {match.instance.scope_label}"
        
        # Explain the fallback
        explanations = []
        
        # Check each dimension
        if needed_scope.domain and instance_scope.domain == needed_scope.domain:
            explanations.append(f"domain matches ({needed_scope.domain})")
        elif needed_scope.domain and instance_scope.domain is None:
            explanations.append(f"generic across all domains")
        
        if needed_scope.system and instance_scope.system == needed_scope.system:
            explanations.append(f"system matches ({needed_scope.system})")
        elif needed_scope.system and instance_scope.system is None:
            explanations.append(f"generic across all systems")
        
        if needed_scope.team and instance_scope.team == needed_scope.team:
            explanations.append(f"team matches ({needed_scope.team})")
        elif needed_scope.team and instance_scope.team is None:
            explanations.append(f"generic across all teams")
        
        if explanations:
            return f"Generic fallback: {', '.join(explanations)}"
        else:
            return "Partial match"


def create_scope(
    domain: Optional[str] = None,
    system: Optional[str] = None,
    team: Optional[str] = None
) -> FactorScope:
    """
    Convenience function to create a FactorScope.
    
    Args:
        domain: Domain name or None for generic
        system: System name or None for generic
        team: Team name or None for generic
        
    Returns:
        FactorScope instance
    """
    return FactorScope(domain=domain, system=system, team=team)


def is_more_specific(scope1: FactorScope, scope2: FactorScope) -> bool:
    """
    Check if scope1 is more specific than scope2.
    
    A scope is more specific if it has more non-None dimensions.
    
    Args:
        scope1: First scope to compare
        scope2: Second scope to compare
        
    Returns:
        True if scope1 is more specific than scope2
    """
    def count_specific_dimensions(scope: FactorScope) -> int:
        count = 0
        if scope.domain is not None:
            count += 1
        if scope.system is not None:
            count += 1
        if scope.team is not None:
            count += 1
        return count
    
    return count_specific_dimensions(scope1) > count_specific_dimensions(scope2)


def get_scope_hierarchy(scope: FactorScope) -> List[FactorScope]:
    """
    Generate the scope hierarchy from most specific to most generic.
    
    For example, {domain: "sales", system: "crm", team: "enterprise"} generates:
    1. {domain: "sales", system: "crm", team: "enterprise"}
    2. {domain: "sales", system: "crm", team: None}
    3. {domain: "sales", system: None, team: None}
    4. {domain: None, system: None, team: None}
    
    Args:
        scope: The scope to generate hierarchy for
        
    Returns:
        List of scopes from most specific to most generic
    """
    hierarchy = []
    
    # Start with the original scope
    current = FactorScope(
        domain=scope.domain,
        system=scope.system,
        team=scope.team
    )
    hierarchy.append(current)
    
    # Remove team if present
    if current.team is not None:
        current = FactorScope(
            domain=current.domain,
            system=current.system,
            team=None
        )
        hierarchy.append(current)
    
    # Remove system if present
    if current.system is not None:
        current = FactorScope(
            domain=current.domain,
            system=None,
            team=None
        )
        hierarchy.append(current)
    
    # Remove domain if present
    if current.domain is not None:
        current = FactorScope(
            domain=None,
            system=None,
            team=None
        )
        hierarchy.append(current)
    
    return hierarchy
