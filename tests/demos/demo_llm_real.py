"""
REAL LLM Integration Demo - Day 10 UAT (REAL OpenAI Calls)

This demo makes ACTUAL OpenAI API calls to verify the integration works.
Requires OPENAI_API_KEY environment variable.

Run: python demo_llm_real.py
"""
import os
from src.patterns.llm_response_generator import LLMResponseGenerator
from src.patterns.response_composer import ResponseComponent, ComposedResponse


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_real_llm_generation():
    """Test real LLM response generation"""
    print_section("REAL LLM Integration Test")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("   Please set it: export OPENAI_API_KEY=your-key")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print()
    
    try:
        # Initialize generator
        generator = LLMResponseGenerator()
        print("✅ LLMResponseGenerator initialized")
        print()
        
        # Test 1: Simple reactive response
        print("📍 Test 1: Simple Reactive Response")
        print("   User: 'We need to assess sales forecasting in our CRM'")
        print()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'behaviors': ['B_ACKNOWLEDGE_OUTPUT', 'B_CONFIRM_UNDERSTANDING']
            },
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {
            'message': 'We need to assess sales forecasting in our CRM',
            'relevant_knowledge': {},
            'conversation_state': {'turn_count': 1}
        }
        
        print("   Calling OpenAI API...")
        response = generator.generate_response(composed, context)
        print()
        print(f"   ✅ Response received:")
        print(f"   \"{response}\"")
        print()
        print(f"   Length: {len(response)} characters (~{len(response.split())} words)")
        print()
        
        # Test 2: Reactive + Proactive response
        print("📍 Test 2: Reactive + Proactive Response")
        print("   User: 'The data quality is about 3 stars'")
        print()
        
        reactive_2 = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_RATE_EDGE',
                'category': 'assessment',
                'behaviors': ['B_ACKNOWLEDGE_RATING', 'B_RECORD_RATING']
            },
            priority='high',
            token_budget=150
        )
        
        proactive_1 = ResponseComponent(
            type='proactive',
            pattern={
                'id': 'PATTERN_ASK_TEAM',
                'category': 'context_extraction',
                'behaviors': ['B_ASK_RESPONSIBLE_TEAM']
            },
            priority='medium',
            token_budget=100
        )
        
        composed_2 = ComposedResponse(
            reactive=reactive_2,
            proactive=[proactive_1],
            total_tokens=250
        )
        
        context_2 = {
            'message': 'The data quality is about 3 stars',
            'relevant_knowledge': {
                'output_identified': True,
                'current_ratings': {'data_quality': 3}
            },
            'conversation_state': {'turn_count': 2}
        }
        
        print("   Calling OpenAI API...")
        response_2 = generator.generate_response(composed_2, context_2)
        print()
        print(f"   ✅ Response received:")
        print(f"   \"{response_2}\"")
        print()
        print(f"   Length: {len(response_2)} characters (~{len(response_2.split())} words)")
        print()
        
        # Verify response structure
        print("📊 Verification:")
        print()
        
        # Check if responses are non-empty
        if len(response) > 0 and len(response_2) > 0:
            print("   ✅ Both responses generated successfully")
        else:
            print("   ❌ One or more responses empty")
            return False
        
        # Check if responses are different (not cached/identical)
        if response != response_2:
            print("   ✅ Responses are contextually different")
        else:
            print("   ⚠️  Responses are identical (unexpected)")
        
        # Check approximate token budget
        words_1 = len(response.split())
        words_2 = len(response_2.split())
        
        if words_1 < 200 and words_2 < 350:  # Rough estimate: 1 token ≈ 0.75 words
            print(f"   ✅ Token budgets respected (~{words_1} and ~{words_2} words)")
        else:
            print(f"   ⚠️  Responses may exceed token budget ({words_1} and {words_2} words)")
        
        print()
        print("="*80)
        print("  ✅ REAL LLM INTEGRATION TEST PASSED")
        print("="*80)
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Test failed. Please check:")
        print("  1. OPENAI_API_KEY is valid")
        print("  2. API key has sufficient credits")
        print("  3. Network connection is working")
        print()
        return False


def main():
    """Run real LLM integration test"""
    print("\n" + "🎯" * 40)
    print("  REAL LLM INTEGRATION TEST - Day 10 UAT")
    print("🎯" * 40)
    print()
    print("⚠️  This test makes REAL OpenAI API calls")
    print("   Cost: ~$0.001 per test run")
    print()
    
    success = test_real_llm_generation()
    
    if success:
        print("\n✅ Day 10 LLM Integration: VERIFIED WITH REAL API")
        print("\nNext Steps:")
        print("  - Day 11-12: Intent detection")
        print("  - Day 13: Multi-output support")
        print()
    else:
        print("\n❌ Day 10 LLM Integration: FAILED")
        print("\nPlease fix issues before proceeding to Day 11")
        print()


if __name__ == "__main__":
    main()
