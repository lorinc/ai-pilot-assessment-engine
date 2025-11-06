"""
Tests for scope matching logic.

Tests cover:
- Exact matches
- Generic fallbacks
- No matches
- Multi-level hierarchies
- Match scoring algorithm
- Scope hierarchy generation
"""

import pytest
from src.knowledge_graph.scope_matcher import (
    ScopeMatcher,
    FactorScope,
    FactorInstance,
    create_scope,
    is_more_specific,
    get_scope_hierarchy
)


@pytest.fixture
def matcher():
    """Create a ScopeMatcher instance."""
    return ScopeMatcher()


@pytest.fixture
def sample_instances():
    """Create sample factor instances for testing."""
    return [
        # Exact: sales/salesforce_crm
        FactorInstance(
            instance_id="dq_sales_sfdc_001",
            factor_id="data_quality",
            scope=create_scope(domain="sales", system="salesforce_crm"),
            scope_label="Salesforce CRM",
            value=30,
            confidence=0.80
        ),
        # Generic: sales/all systems
        FactorInstance(
            instance_id="dq_sales_generic_001",
            factor_id="data_quality",
            scope=create_scope(domain="sales", system=None),
            scope_label="Sales Department",
            value=45,
            confidence=0.60
        ),
        # Different domain: finance/erp
        FactorInstance(
            instance_id="dq_finance_erp_001",
            factor_id="data_quality",
            scope=create_scope(domain="finance", system="erp"),
            scope_label="Finance ERP",
            value=85,
            confidence=0.90
        ),
        # Organization-wide
        FactorInstance(
            instance_id="dq_org_wide_001",
            factor_id="data_quality",
            scope=create_scope(domain=None, system=None),
            scope_label="Organization-wide",
            value=50,
            confidence=0.50
        ),
        # With team dimension
        FactorInstance(
            instance_id="dq_sales_sfdc_enterprise_001",
            factor_id="data_quality",
            scope=create_scope(domain="sales", system="salesforce_crm", team="enterprise_sales"),
            scope_label="Salesforce CRM (Enterprise Sales)",
            value=25,
            confidence=0.85
        )
    ]


class TestScopeMatchCalculation:
    """Test the scope match scoring algorithm."""
    
    def test_exact_match_all_dimensions(self, matcher):
        """Test exact match on all dimensions."""
        instance_scope = create_scope(domain="sales", system="salesforce_crm", team="enterprise_sales")
        needed_scope = create_scope(domain="sales", system="salesforce_crm", team="enterprise_sales")
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        assert score == 1.0
    
    def test_exact_match_two_dimensions(self, matcher):
        """Test exact match on domain and system, team is None."""
        instance_scope = create_scope(domain="sales", system="salesforce_crm", team=None)
        needed_scope = create_scope(domain="sales", system="salesforce_crm", team=None)
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        assert score == 1.0
    
    def test_generic_fallback_system(self, matcher):
        """Test generic fallback when instance has no system specified."""
        instance_scope = create_scope(domain="sales", system=None, team=None)
        needed_scope = create_scope(domain="sales", system="data_warehouse", team=None)
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        # domain: exact (0.33), system: generic fallback (0.20), team: don't care (0.33)
        assert score == pytest.approx(0.86, rel=0.01)
    
    def test_generic_fallback_domain(self, matcher):
        """Test generic fallback when instance has no domain specified."""
        instance_scope = create_scope(domain=None, system=None, team=None)
        needed_scope = create_scope(domain="sales", system="salesforce_crm", team=None)
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        # domain: generic fallback (0.20), system: generic fallback (0.20), team: don't care (0.33)
        assert score == pytest.approx(0.73, rel=0.01)
    
    def test_domain_mismatch(self, matcher):
        """Test that domain mismatch returns 0."""
        instance_scope = create_scope(domain="sales", system="salesforce_crm")
        needed_scope = create_scope(domain="finance", system="salesforce_crm")
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        assert score == 0.0
    
    def test_system_mismatch(self, matcher):
        """Test that system mismatch returns 0."""
        instance_scope = create_scope(domain="sales", system="salesforce_crm")
        needed_scope = create_scope(domain="sales", system="hubspot")
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        assert score == 0.0
    
    def test_dont_care_dimensions(self, matcher):
        """Test that None in needed_scope means don't care."""
        instance_scope = create_scope(domain="sales", system="salesforce_crm")
        needed_scope = create_scope(domain="sales", system=None)
        
        score = matcher.calculate_scope_match(instance_scope, needed_scope)
        # domain: exact (0.33), system: don't care (0.33), team: don't care (0.33)
        assert score == pytest.approx(0.99, rel=0.01)


class TestGetApplicableValue:
    """Test finding the most applicable instance."""
    
    def test_exact_match(self, matcher, sample_instances):
        """Test exact match returns the specific instance."""
        needed_scope = create_scope(domain="sales", system="salesforce_crm")
        
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        assert match is not None
        assert match.instance.instance_id == "dq_sales_sfdc_001"
        assert match.match_score == 1.0
        assert match.match_type == "exact"
    
    def test_generic_fallback(self, matcher, sample_instances):
        """Test fallback to generic instance when specific doesn't exist."""
        needed_scope = create_scope(domain="sales", system="data_warehouse")
        
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        assert match is not None
        assert match.instance.instance_id == "dq_sales_generic_001"
        assert match.match_score == pytest.approx(0.86, rel=0.01)
        assert match.match_type == "generic_fallback"
    
    def test_no_match(self, matcher, sample_instances):
        """Test that mismatched domain returns None."""
        needed_scope = create_scope(domain="manufacturing", system="iot_sensors")
        
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        assert match is None
    
    def test_prefers_higher_confidence_on_tie(self, matcher):
        """Test that higher confidence wins when match scores are equal."""
        instances = [
            FactorInstance(
                instance_id="dq_sales_001",
                factor_id="data_quality",
                scope=create_scope(domain="sales"),
                scope_label="Sales",
                value=40,
                confidence=0.60
            ),
            FactorInstance(
                instance_id="dq_sales_002",
                factor_id="data_quality",
                scope=create_scope(domain="sales"),
                scope_label="Sales",
                value=45,
                confidence=0.80
            )
        ]
        
        needed_scope = create_scope(domain="sales")
        match = matcher.get_applicable_value("data_quality", needed_scope, instances)
        
        assert match.instance.instance_id == "dq_sales_002"  # Higher confidence
    
    def test_prefers_more_specific_match(self, matcher, sample_instances):
        """Test that more specific match is preferred over generic."""
        # Query for sales/salesforce_crm - should get exact match, not generic sales
        needed_scope = create_scope(domain="sales", system="salesforce_crm")
        
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        assert match.instance.instance_id == "dq_sales_sfdc_001"  # Specific, not generic
        assert match.match_score == 1.0
    
    def test_team_dimension_matching(self, matcher, sample_instances):
        """Test matching with team dimension."""
        needed_scope = create_scope(domain="sales", system="salesforce_crm", team="enterprise_sales")
        
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        assert match is not None
        assert match.instance.instance_id == "dq_sales_sfdc_enterprise_001"
        assert match.match_score == 1.0


class TestFindAllMatches:
    """Test finding all matching instances."""
    
    def test_returns_all_applicable_matches(self, matcher, sample_instances):
        """Test that all applicable matches are returned."""
        needed_scope = create_scope(domain="sales", system="salesforce_crm")
        
        matches = matcher.find_all_matches("data_quality", needed_scope, sample_instances)
        
        # Should find: exact (sales/sfdc), generic (sales/all), org-wide (all/all)
        assert len(matches) >= 3
        
        # First should be exact match
        assert matches[0].instance.instance_id == "dq_sales_sfdc_001"
        assert matches[0].match_type == "exact"
    
    def test_sorted_by_match_score(self, matcher, sample_instances):
        """Test that matches are sorted by score then confidence."""
        needed_scope = create_scope(domain="sales", system="data_warehouse")
        
        matches = matcher.find_all_matches("data_quality", needed_scope, sample_instances)
        
        # Verify descending order
        for i in range(len(matches) - 1):
            assert matches[i].match_score >= matches[i + 1].match_score


class TestExplainMatch:
    """Test match explanation generation."""
    
    def test_exact_match_explanation(self, matcher, sample_instances):
        """Test explanation for exact match."""
        needed_scope = create_scope(domain="sales", system="salesforce_crm")
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        explanation = matcher.explain_match(match, needed_scope)
        
        assert "Exact match" in explanation
        assert "Salesforce CRM" in explanation
    
    def test_generic_fallback_explanation(self, matcher, sample_instances):
        """Test explanation for generic fallback."""
        needed_scope = create_scope(domain="sales", system="data_warehouse")
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        explanation = matcher.explain_match(match, needed_scope)
        
        assert "Generic fallback" in explanation or "generic" in explanation.lower()


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_create_scope(self):
        """Test scope creation helper."""
        scope = create_scope(domain="sales", system="crm")
        
        assert scope.domain == "sales"
        assert scope.system == "crm"
        assert scope.team is None
    
    def test_is_more_specific(self):
        """Test specificity comparison."""
        specific = create_scope(domain="sales", system="crm", team="enterprise")
        generic = create_scope(domain="sales", system=None, team=None)
        
        assert is_more_specific(specific, generic)
        assert not is_more_specific(generic, specific)
    
    def test_get_scope_hierarchy(self):
        """Test scope hierarchy generation."""
        scope = create_scope(domain="sales", system="crm", team="enterprise")
        hierarchy = get_scope_hierarchy(scope)
        
        # Should have 4 levels: full, no team, no system, no domain
        assert len(hierarchy) == 4
        
        # Level 1: Full scope
        assert hierarchy[0].domain == "sales"
        assert hierarchy[0].system == "crm"
        assert hierarchy[0].team == "enterprise"
        
        # Level 2: No team
        assert hierarchy[1].domain == "sales"
        assert hierarchy[1].system == "crm"
        assert hierarchy[1].team is None
        
        # Level 3: No system
        assert hierarchy[2].domain == "sales"
        assert hierarchy[2].system is None
        assert hierarchy[2].team is None
        
        # Level 4: Organization-wide
        assert hierarchy[3].domain is None
        assert hierarchy[3].system is None
        assert hierarchy[3].team is None
    
    def test_get_scope_hierarchy_partial(self):
        """Test hierarchy generation for partial scope."""
        scope = create_scope(domain="sales", system=None, team=None)
        hierarchy = get_scope_hierarchy(scope)
        
        # Should have 2 levels: domain-specific and org-wide
        assert len(hierarchy) == 2
        assert hierarchy[0].domain == "sales"
        assert hierarchy[1].domain is None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_instances_list(self, matcher):
        """Test with no instances available."""
        needed_scope = create_scope(domain="sales")
        match = matcher.get_applicable_value("data_quality", needed_scope, [])
        
        assert match is None
    
    def test_wrong_factor_id(self, matcher, sample_instances):
        """Test querying for non-existent factor."""
        needed_scope = create_scope(domain="sales")
        match = matcher.get_applicable_value("nonexistent_factor", needed_scope, sample_instances)
        
        assert match is None
    
    def test_all_none_scope(self, matcher, sample_instances):
        """Test with completely generic scope."""
        needed_scope = create_scope(domain=None, system=None, team=None)
        match = matcher.get_applicable_value("data_quality", needed_scope, sample_instances)
        
        # Should match org-wide instance
        assert match is not None
        assert match.instance.instance_id == "dq_org_wide_001"
    
    def test_multiple_exact_matches(self, matcher):
        """Test behavior with multiple exact matches (should pick higher confidence)."""
        instances = [
            FactorInstance(
                instance_id="dq_001",
                factor_id="data_quality",
                scope=create_scope(domain="sales", system="crm"),
                scope_label="CRM",
                value=30,
                confidence=0.70
            ),
            FactorInstance(
                instance_id="dq_002",
                factor_id="data_quality",
                scope=create_scope(domain="sales", system="crm"),
                scope_label="CRM",
                value=35,
                confidence=0.90
            )
        ]
        
        needed_scope = create_scope(domain="sales", system="crm")
        match = matcher.get_applicable_value("data_quality", needed_scope, instances)
        
        # Should pick the one with higher confidence
        assert match.instance.instance_id == "dq_002"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
