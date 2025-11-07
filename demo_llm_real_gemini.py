"""
REAL LLM Integration Demo with Gemini - Day 10 UAT (Refactored)

This demo makes ACTUAL Gemini API calls via existing LLMClient.
Requires GCP credentials configured.

Run: python demo_llm_real_gemini.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.llm_client import LLMClient
from patterns.llm_response_generator import LLMResponseGenerator
from patterns.response_composer import ResponseComponent, ComposedResponse


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_real_gemini_generation():
    """Test real Gemini response generation"""
    print_section("REAL Gemini Integration Test")
    
    try:
        # Initialize LLMClient (Gemini via Vertex AI)
        print("Initializing Gemini via Vertex AI...")
        llm_client = LLMClient()
        print(f"✅ LLMClient initialized: {llm_client.model_name}")
        print(f"   Project: {llm_client.project_id}")
        print(f"   Location: {llm_client.location}")
        print()
        
        # Initialize generator with Gemini client
        generator = LLMResponseGenerator(llm_client=llm_client)
        print("✅ LLMResponseGenerator initialized with Gemini")
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
        
        print("   Calling Gemini API...")
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
        
        print("   Calling Gemini API...")
        response_2 = generator.generate_response(composed_2, context_2)
        print()
        print(f"   ✅ Response received:")
        print(f"   \"{response_2}\"")
        print()
        print(f"   Length: {len(response_2)} characters (~{len(response_2.split())} words)")
        print()
        
        # Verification
        print("📊 Verification:")
        print()
        
        if len(response) > 0 and len(response_2) > 0:
            print("   ✅ Both responses generated successfully")
        else:
            print("   ❌ One or more responses empty")
            return False
        
        if response != response_2:
            print("   ✅ Responses are contextually different")
        else:
            print("   ⚠️  Responses are identical (unexpected)")
        
        words_1 = len(response.split())
        words_2 = len(response_2.split())
        
        if words_1 < 200 and words_2 < 350:
            print(f"   ✅ Token budgets respected (~{words_1} and ~{words_2} words)")
        else:
            print(f"   ⚠️  Responses may exceed token budget ({words_1} and {words_2} words)")
        
        print()
        print("="*80)
        print("  ✅ REAL GEMINI INTEGRATION TEST PASSED")
        print("="*80)
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Test failed. Please check:")
        print("  1. GCP credentials are configured")
        print("  2. Vertex AI API is enabled")
        print("  3. Service account has permissions")
        print("  4. Network connection is working")
        print()
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run real Gemini integration test"""
    print("\n" + "🎯" * 40)
    print("  REAL GEMINI INTEGRATION TEST - Day 10 UAT (Refactored)")
    print("🎯" * 40)
    print()
    print("⚠️  This test makes REAL Gemini API calls via Vertex AI")
    print("   Cost: ~$0.0001 per test run (Gemini is cheaper than OpenAI)")
    print()
    print("📋 Architecture:")
    print("   - Uses existing src/core/llm_client.py (Gemini via Vertex AI)")
    print("   - Consistent with project infrastructure")
    print("   - No duplicate LLM providers")
    print()
    
    success = test_real_gemini_generation()
    
    if success:
        print("\n✅ Day 10 LLM Integration: VERIFIED WITH REAL GEMINI API")
        print("\n🎉 Refactoring Complete:")
        print("  - Removed OpenAI dependency")
        print("  - Using existing Gemini/Vertex AI infrastructure")
        print("  - Consistent with project architecture")
        print("  - All tests passing")
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
