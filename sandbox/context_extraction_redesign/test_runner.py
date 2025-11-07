"""
Test runner for context extraction validation.

Runs test cases through the extractor and compares results against expected output.
Provides detailed accuracy metrics and identifies areas for improvement.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from extractor import ContextExtractor
from test_cases import TEST_CASES
from schemas import ExtractedContext


@dataclass
class TestResult:
    """Result of a single test case."""
    test_id: int
    test_name: str
    difficulty: str
    user_message: str
    passed: bool
    accuracy_score: float  # 0.0 to 1.0
    expected: ExtractedContext
    actual: ExtractedContext
    differences: Dict[str, Any]
    notes: str


class TestRunner:
    """Run extraction tests and compute accuracy metrics."""
    
    def __init__(self, extractor: ContextExtractor):
        """
        Initialize test runner.
        
        Args:
            extractor: Configured ContextExtractor instance
        """
        self.extractor = extractor
        self.results: List[TestResult] = []
    
    def run_all_tests(self, verbose: bool = True) -> List[TestResult]:
        """
        Run all test cases.
        
        Args:
            verbose: Print progress during testing
            
        Returns:
            List of TestResult objects
        """
        self.results = []
        
        for i, test_case in enumerate(TEST_CASES, 1):
            if verbose:
                print(f"\n{'='*80}")
                print(f"Test {i}/{len(TEST_CASES)}: {test_case['name']} ({test_case['difficulty']})")
                print(f"{'='*80}")
                print(f"Message: {test_case['user_message']}")
            
            # Extract context
            try:
                actual = self.extractor.extract(test_case['user_message'])
                
                # Compare with expected
                accuracy, differences = self._compare_contexts(
                    test_case['expected'],
                    actual
                )
                
                passed = accuracy >= 0.7  # 70% threshold for passing
                
                result = TestResult(
                    test_id=test_case['id'],
                    test_name=test_case['name'],
                    difficulty=test_case['difficulty'],
                    user_message=test_case['user_message'],
                    passed=passed,
                    accuracy_score=accuracy,
                    expected=test_case['expected'],
                    actual=actual,
                    differences=differences,
                    notes=test_case['notes']
                )
                
                self.results.append(result)
                
                if verbose:
                    print(f"\n{'PASS' if passed else 'FAIL'}: {accuracy:.1%} accuracy")
                    if differences:
                        print("\nDifferences:")
                        for key, diff in differences.items():
                            print(f"  {key}: {diff}")
                
            except Exception as e:
                if verbose:
                    print(f"\nERROR: {e}")
                
                result = TestResult(
                    test_id=test_case['id'],
                    test_name=test_case['name'],
                    difficulty=test_case['difficulty'],
                    user_message=test_case['user_message'],
                    passed=False,
                    accuracy_score=0.0,
                    expected=test_case['expected'],
                    actual=None,
                    differences={"error": str(e)},
                    notes=test_case['notes']
                )
                self.results.append(result)
        
        return self.results
    
    def _compare_contexts(
        self,
        expected: ExtractedContext,
        actual: ExtractedContext
    ) -> tuple[float, Dict[str, Any]]:
        """
        Compare expected vs actual context and compute accuracy.
        
        Returns:
            (accuracy_score, differences_dict)
        """
        differences = {}
        scores = []
        
        # Compare each field
        for field in ['outputs', 'teams', 'systems', 'processes', 'assessments', 'dependencies', 'root_causes']:
            expected_items = getattr(expected, field)
            actual_items = getattr(actual, field)
            
            # Convert to comparable format
            expected_set = self._items_to_comparable(expected_items)
            actual_set = self._items_to_comparable(actual_items)
            
            # Compute precision, recall, F1
            if len(expected_set) == 0 and len(actual_set) == 0:
                score = 1.0  # Both empty = perfect match
            elif len(expected_set) == 0:
                score = 0.0  # Expected empty but got results = wrong
            else:
                matches = len(expected_set & actual_set)
                precision = matches / len(actual_set) if actual_set else 0
                recall = matches / len(expected_set) if expected_set else 0
                score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            scores.append(score)
            
            # Track differences
            if score < 1.0:
                missing = expected_set - actual_set
                extra = actual_set - expected_set
                differences[field] = {
                    "score": score,
                    "missing": list(missing) if missing else None,
                    "extra": list(extra) if extra else None
                }
        
        # Overall accuracy is average of field scores
        overall_accuracy = sum(scores) / len(scores) if scores else 0.0
        
        return overall_accuracy, differences
    
    def _items_to_comparable(self, items: List[Any]) -> set:
        """Convert list of Pydantic models to set of comparable tuples."""
        comparable = set()
        for item in items:
            # Convert to dict and then to sorted tuple of items
            item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.dict()
            # Create a hashable representation
            comparable.add(self._dict_to_tuple(item_dict))
        return comparable
    
    def _dict_to_tuple(self, d: Dict) -> tuple:
        """Convert dict to hashable tuple."""
        items = []
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                items.append((k, self._dict_to_tuple(v)))
            elif isinstance(v, list):
                items.append((k, tuple(v)))
            else:
                items.append((k, v))
        return tuple(items)
    
    def print_summary(self):
        """Print summary of test results."""
        if not self.results:
            print("No test results available.")
            return
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        avg_accuracy = sum(r.accuracy_score for r in self.results) / total
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ({passed/total:.1%})")
        print(f"Failed: {failed} ({failed/total:.1%})")
        print(f"Average Accuracy: {avg_accuracy:.1%}")
        
        # By difficulty
        print("\nBy Difficulty:")
        for difficulty in ['Simple', 'Medium', 'Complex']:
            difficulty_results = [r for r in self.results if r.difficulty == difficulty]
            if difficulty_results:
                avg = sum(r.accuracy_score for r in difficulty_results) / len(difficulty_results)
                passed_count = sum(1 for r in difficulty_results if r.passed)
                print(f"  {difficulty}: {passed_count}/{len(difficulty_results)} passed, {avg:.1%} avg accuracy")
        
        # Failed tests
        if failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - Test {r.test_id}: {r.test_name} ({r.accuracy_score:.1%})")
        
        print("\n" + "="*80)
    
    def save_results(self, filename: str = None):
        """Save detailed results to JSON file in iterations subfolder."""
        import os
        from datetime import datetime
        
        # Create iterations directory if it doesn't exist
        iterations_dir = "iterations"
        os.makedirs(iterations_dir, exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{iterations_dir}/test_results_{timestamp}.json"
        
        results_data = []
        for r in self.results:
            results_data.append({
                "test_id": r.test_id,
                "test_name": r.test_name,
                "difficulty": r.difficulty,
                "user_message": r.user_message,
                "passed": r.passed,
                "accuracy_score": r.accuracy_score,
                "differences": r.differences,
                "notes": r.notes,
                "expected": r.expected.model_dump() if r.expected else None,
                "actual": r.actual.model_dump() if r.actual else None
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nDetailed results saved to {filename}")


def main():
    """Run the test suite."""
    import sys
    
    print("Context Extraction Test Suite")
    print("="*80)
    
    # Check GCP setup
    print("\nChecking GCP configuration...")
    import sys
    import os
    project_root = os.path.join(os.path.dirname(__file__), '../..')
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    try:
        from config.settings import settings
        print(f"  ✓ GCP Project: {settings.GCP_PROJECT_ID}")
        print(f"  ✓ Location: {settings.GCP_LOCATION}")
        print(f"  ✓ Model: {settings.GEMINI_MODEL}")
        print(f"  ✓ Mock Mode: {settings.MOCK_LLM}")
    except Exception as e:
        print(f"\nERROR: Failed to load settings: {e}")
        print("Make sure you're running from the project root or have proper GCP credentials.")
        sys.exit(1)
    
    # Create extractor
    print("\nInitializing extractor...")
    from extractor import create_extractor
    extractor = create_extractor()
    
    # Run tests
    print(f"\nRunning {len(TEST_CASES)} test cases...")
    runner = TestRunner(extractor)
    runner.run_all_tests(verbose=True)
    
    # Print summary
    runner.print_summary()
    
    # Save results (will auto-generate timestamped filename in iterations/)
    runner.save_results()


if __name__ == "__main__":
    main()
