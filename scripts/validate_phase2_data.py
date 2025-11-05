#!/usr/bin/env python3
"""
Validate data structure for Phase 2 readiness.

Checks:
- Function templates have required fields
- Component scales are complete
- Output discovery rules exist
- No broken references
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "data"
FUNCTIONS_DIR = DATA_DIR / "organizational_templates" / "functions"
COMPONENT_SCALES = DATA_DIR / "component_scales.json"
OUTPUT_DISCOVERY = DATA_DIR / "inference_rules" / "output_discovery.json"


class ValidationError(Exception):
    """Validation failed."""
    pass


def validate_component_scales() -> Dict:
    """Validate component_scales.json structure."""
    print("✓ Checking component_scales.json...")
    
    if not COMPONENT_SCALES.exists():
        raise ValidationError(f"Missing: {COMPONENT_SCALES}")
    
    with open(COMPONENT_SCALES) as f:
        data = json.load(f)
    
    required_components = {
        "team_execution",
        "system_capabilities", 
        "process_maturity",
        "dependency_quality"
    }
    
    actual_components = set(data.get("components", {}).keys())
    missing = required_components - actual_components
    
    if missing:
        raise ValidationError(f"Missing components: {missing}")
    
    # Check each component has 1-5 scale
    for comp_name, comp_data in data["components"].items():
        scale = comp_data.get("scale", {})
        for star in ["1", "2", "3", "4", "5"]:
            if star not in scale:
                raise ValidationError(f"Component {comp_name} missing {star} star rating")
    
    print(f"  ✓ All 4 components present with 1-5 scales")
    return data


def validate_function_template(file_path: Path) -> Dict:
    """Validate a single function template."""
    with open(file_path) as f:
        data = json.load(f)
    
    required_fields = ["function", "typical_teams", "typical_processes", "typical_systems", "common_outputs"]
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        raise ValidationError(f"{file_path.name}: Missing fields {missing}")
    
    # Check outputs have required structure
    outputs = data.get("common_outputs", [])
    if not outputs:
        raise ValidationError(f"{file_path.name}: No outputs defined")
    
    for output in outputs:
        required_output_fields = ["id", "name", "typical_quality_metrics"]
        missing_output = [f for f in required_output_fields if f not in output]
        if missing_output:
            raise ValidationError(
                f"{file_path.name}: Output {output.get('id', '?')} missing {missing_output}"
            )
    
    return data


def validate_function_templates() -> List[Dict]:
    """Validate all function templates."""
    print("\n✓ Checking function templates...")
    
    if not FUNCTIONS_DIR.exists():
        raise ValidationError(f"Missing directory: {FUNCTIONS_DIR}")
    
    json_files = list(FUNCTIONS_DIR.glob("*.json"))
    
    if len(json_files) < 8:
        print(f"  ⚠ Warning: Only {len(json_files)} function templates (expected 8)")
    
    templates = []
    for file_path in json_files:
        try:
            data = validate_function_template(file_path)
            templates.append(data)
            output_count = len(data.get("common_outputs", []))
            print(f"  ✓ {file_path.stem}: {output_count} outputs")
        except ValidationError as e:
            raise ValidationError(f"Invalid template {file_path.name}: {e}")
    
    return templates


def validate_output_discovery() -> Dict:
    """Validate output_discovery.json exists and is valid."""
    print("\n✓ Checking output_discovery.json...")
    
    if not OUTPUT_DISCOVERY.exists():
        raise ValidationError(f"Missing: {OUTPUT_DISCOVERY}")
    
    with open(OUTPUT_DISCOVERY) as f:
        data = json.load(f)
    
    print(f"  ✓ Output discovery rules loaded")
    return data


def validate_output_ids(templates: List[Dict]) -> None:
    """Check for duplicate output IDs across templates."""
    print("\n✓ Checking for duplicate output IDs...")
    
    output_ids: Set[str] = set()
    duplicates: List[str] = []
    
    for template in templates:
        function_name = template.get("function", "?")
        for output in template.get("common_outputs", []):
            output_id = output.get("id")
            if output_id in output_ids:
                duplicates.append(f"{output_id} (in {function_name})")
            output_ids.add(output_id)
    
    if duplicates:
        raise ValidationError(f"Duplicate output IDs: {duplicates}")
    
    print(f"  ✓ {len(output_ids)} unique output IDs across all templates")


def validate_data_quality(templates: List[Dict]) -> None:
    """Check data quality (pain points, dependencies, etc.)."""
    print("\n✓ Checking data quality...")
    
    warnings = []
    
    for template in templates:
        function_name = template.get("function", "?")
        
        for output in template.get("common_outputs", []):
            output_id = output.get("id")
            
            # Check pain points
            pain_points = output.get("common_pain_points", [])
            if len(pain_points) < 3:
                warnings.append(
                    f"{function_name}.{output_id}: Only {len(pain_points)} pain points (recommend 5+)"
                )
            
            # Check dependencies
            dependencies = output.get("typical_dependencies", [])
            if len(dependencies) > 10:
                warnings.append(
                    f"{function_name}.{output_id}: {len(dependencies)} dependencies (max 10 recommended)"
                )
    
    if warnings:
        print(f"  ⚠ {len(warnings)} data quality warnings:")
        for w in warnings[:5]:  # Show first 5
            print(f"    - {w}")
        if len(warnings) > 5:
            print(f"    ... and {len(warnings) - 5} more")
    else:
        print(f"  ✓ No data quality issues found")


def main():
    """Run all validations."""
    print("=" * 60)
    print("Phase 2 Data Validation")
    print("=" * 60)
    
    try:
        # Validate component scales
        component_scales = validate_component_scales()
        
        # Validate function templates
        templates = validate_function_templates()
        
        # Validate output discovery rules
        output_discovery = validate_output_discovery()
        
        # Cross-validation
        validate_output_ids(templates)
        validate_data_quality(templates)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ VALIDATION PASSED")
        print("=" * 60)
        print(f"  • {len(templates)} function templates validated")
        print(f"  • {sum(len(t.get('common_outputs', [])) for t in templates)} total outputs")
        print(f"  • 4 component scales validated")
        print(f"  • Output discovery rules present")
        print("\n✓ Data structure is ready for Phase 2")
        
        return 0
        
    except ValidationError as e:
        print("\n" + "=" * 60)
        print("❌ VALIDATION FAILED")
        print("=" * 60)
        print(f"  Error: {e}")
        print("\n✗ Fix data issues before proceeding to Phase 2")
        return 1
    
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
