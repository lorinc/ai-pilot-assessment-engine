"""
Quick validation script to check testbed setup.

Validates:
- All imports work
- Schemas are valid
- Test cases load correctly
- Extractor can be instantiated (if API key present)
"""

import sys


def validate_imports():
    """Check that all required modules can be imported."""
    print("Validating imports...")
    
    import sys
    import os
    project_root = os.path.join(os.path.dirname(__file__), '../..')
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    try:
        import pydantic
        print("  ✓ pydantic")
    except ImportError:
        print("  ✗ pydantic - check project venv")
        return False
    
    try:
        from core.llm_client import LLMClient
        print("  ✓ LLMClient (project)")
    except ImportError as e:
        print(f"  ✗ LLMClient - {e}")
        return False
    
    try:
        import vertexai
        print("  ✓ vertexai")
    except ImportError:
        print("  ✗ vertexai - check project venv")
        return False
    
    return True


def validate_schemas():
    """Check that schemas are valid."""
    print("\nValidating schemas...")
    try:
        from schemas import (
            ExtractedContext, Output, Team, System, Process,
            Assessment, Dependency, RootCause
        )
        
        # Try creating a simple instance
        context = ExtractedContext(
            outputs=[Output(name="test output")],
            assessments=[Assessment(target="test", rating=3, explicit=True, sentiment="neutral")]
        )
        
        print("  ✓ All schemas valid")
        print(f"  ✓ Created test ExtractedContext: {len(context.outputs)} outputs")
        return True
    except Exception as e:
        print(f"  ✗ Schema validation failed: {e}")
        return False


def validate_test_cases():
    """Check that test cases load correctly."""
    print("\nValidating test cases...")
    try:
        from test_cases import TEST_CASES
        
        print(f"  ✓ Loaded {len(TEST_CASES)} test cases")
        
        # Check structure
        for i, tc in enumerate(TEST_CASES, 1):
            required_keys = ['id', 'name', 'difficulty', 'user_message', 'expected', 'notes']
            missing = [k for k in required_keys if k not in tc]
            if missing:
                print(f"  ✗ Test case {i} missing keys: {missing}")
                return False
        
        print("  ✓ All test cases have required fields")
        
        # Count by difficulty
        difficulties = {}
        for tc in TEST_CASES:
            diff = tc['difficulty']
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        print(f"  ✓ Breakdown: {difficulties}")
        
        return True
    except Exception as e:
        print(f"  ✗ Test case validation failed: {e}")
        return False


def validate_extractor():
    """Check that extractor can be created."""
    print("\nValidating extractor...")
    
    try:
        from extractor import create_extractor
        extractor = create_extractor()
        print("  ✓ Extractor created successfully")
        print(f"  ✓ Using model: {extractor.model_name}")
        return True
    except Exception as e:
        print(f"  ✗ Extractor creation failed: {e}")
        print("    Make sure GCP credentials are configured")
        return False


def main():
    """Run all validations."""
    print("="*80)
    print("TESTBED VALIDATION")
    print("="*80)
    
    results = []
    
    results.append(("Imports", validate_imports()))
    results.append(("Schemas", validate_schemas()))
    results.append(("Test Cases", validate_test_cases()))
    results.append(("Extractor", validate_extractor()))
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✓ All validations passed! Ready to run tests.")
        print("\nNext step: python test_runner.py")
    else:
        print("\n✗ Some validations failed. Fix issues above before running tests.")
        sys.exit(1)


if __name__ == "__main__":
    main()
