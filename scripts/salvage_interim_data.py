#!/usr/bin/env python3
"""
Salvage Operation Scripts
==========================

Scripts used to extract and repurpose content from interim_data_files/
into the new output-centric taxonomy structure.

Author: AI Pilot Assessment Engine Team
Date: 2025-11-02
"""

import json
import os
from pathlib import Path


def extract_pain_point_mapping():
    """
    Extract pain point mapping from problem_taxonomy.json
    Creates: inference_rules/pain_point_mapping.json
    """
    print("Extracting pain point mapping...")
    
    # Read problem taxonomy
    with open('src/data/interim_data_files/problem_taxonomy.json', 'r') as f:
        problems = json.load(f)
    
    # Create pain point mapping
    pain_point_mapping = {
        "description": "Mapping from problem taxonomy to output pain points for better inference",
        "version": "1.0",
        "source": "problem_taxonomy.json",
        "categories": []
    }
    
    for category_name, subcategories in problems.items():
        category = {
            "category": category_name,
            "subcategories": []
        }
        
        for subcategory_name, pain_points in subcategories.items():
            subcategory = {
                "subcategory": subcategory_name,
                "pain_points": pain_points,
                "maps_to_outputs": [],  # To be filled in by function templates
                "inference_keywords": []  # To be extracted from pain points
            }
            category["subcategories"].append(subcategory)
        
        pain_point_mapping["categories"].append(category)
    
    # Save
    output_path = 'src/data/inference_rules/pain_point_mapping.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(pain_point_mapping, f, indent=2)
    
    total_categories = len(pain_point_mapping['categories'])
    total_subcategories = sum(len(cat['subcategories']) for cat in pain_point_mapping['categories'])
    total_pain_points = sum(
        len(subcat['pain_points']) 
        for cat in pain_point_mapping['categories'] 
        for subcat in cat['subcategories']
    )
    
    print(f"✓ Created pain_point_mapping.json")
    print(f"  - {total_categories} categories")
    print(f"  - {total_subcategories} subcategories")
    print(f"  - {total_pain_points} pain points")
    
    return pain_point_mapping


def extract_ai_archetypes():
    """
    Extract AI archetypes from AI_use_case_taxonomy.json
    Creates: inference_rules/ai_archetypes.json
    """
    print("\nExtracting AI archetypes...")
    
    # Read AI use case taxonomy
    with open('src/data/interim_data_files/AI_use_case_taxonomy.json', 'r') as f:
        ai_taxonomy = json.load(f)
    
    # Extract archetypes
    archetypes = {
        "description": "AI/ML use case archetypes with technical details for pilot recommendations",
        "version": "1.0",
        "source": "AI_use_case_taxonomy.json",
        "archetypes": ai_taxonomy["AI_Use_Case_Archetypes"]
    }
    
    # Save
    output_path = 'src/data/inference_rules/ai_archetypes.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(archetypes, f, indent=2)
    
    print(f"✓ Created ai_archetypes.json")
    print(f"  - {len(archetypes['archetypes'])} archetypes")
    
    # Print first few
    print("  Examples:")
    for i, arch in enumerate(archetypes['archetypes'][:5], 1):
        print(f"    {i}. {arch['archetype']}")
    
    return archetypes


def extract_pilot_catalog():
    """
    Extract pilot catalog from automation_opportunity_taxonomy.json
    Creates: pilot_catalog.json
    """
    print("\nExtracting pilot catalog...")
    
    # Read automation opportunity taxonomy
    with open('src/data/interim_data_files/automation_opportunity_taxonomy.json', 'r') as f:
        automation = json.load(f)
    
    # Extract all use cases
    pilot_catalog = {
        "description": "Catalog of specific pilot projects extracted from automation opportunities",
        "version": "1.0",
        "source": "automation_opportunity_taxonomy.json",
        "total_pilots": 0,
        "categories": []
    }
    
    for category_data in automation["AutomationOpportunities"]:
        category = {
            "category": category_data["category"],
            "pilot_count": category_data["records_count"],
            "pilots": []
        }
        
        for record in category_data["records"]:
            pilot = {
                "use_case": record["use_case"],
                "pain_points": record["consolidated_pain_points"],
                "ai_archetypes": record["key_archetypes"],
                "applicable_functions": [],  # To be mapped
                "applicable_outputs": []     # To be mapped
            }
            category["pilots"].append(pilot)
        
        pilot_catalog["categories"].append(category)
        pilot_catalog["total_pilots"] += category_data["records_count"]
    
    # Save
    output_path = 'src/data/pilot_catalog.json'
    
    with open(output_path, 'w') as f:
        json.dump(pilot_catalog, f, indent=2)
    
    print(f"✓ Created pilot_catalog.json")
    print(f"  - {pilot_catalog['total_pilots']} pilots across {len(pilot_catalog['categories'])} categories")
    
    # Print summary
    for cat in pilot_catalog['categories']:
        print(f"    - {cat['category']}: {cat['pilot_count']} pilots")
    
    return pilot_catalog


def extract_capability_framework():
    """
    Extract capability framework from business_capability_taxonomy.json
    Creates: capability_framework.json
    """
    print("\nExtracting capability framework...")
    
    # Read business capability taxonomy
    with open('src/data/interim_data_files/business_capability_taxonomy.json', 'r') as f:
        capabilities = json.load(f)
    
    # Restructure for component assessment
    capability_framework = {
        "description": "Organizational capabilities mapped to component assessment",
        "version": "1.0",
        "source": "business_capability_taxonomy.json",
        "usage": "Use these capabilities as detailed indicators for component scales",
        "pillars": []
    }
    
    for pillar_data in capabilities["T1_Organizational_Capabilities"]:
        pillar = {
            "pillar": pillar_data["T1_Pillar"],
            "maps_to_component": "",  # To be filled based on pillar type
            "categories": []
        }
        
        for category_data in pillar_data["T2_Categories"]:
            category = {
                "category": category_data["T2_Category"],
                "capabilities": category_data["T3_Capabilities"]
            }
            pillar["categories"].append(category)
        
        capability_framework["pillars"].append(pillar)
    
    # Save
    output_path = 'src/data/capability_framework.json'
    
    with open(output_path, 'w') as f:
        json.dump(capability_framework, f, indent=2)
    
    # Count total capabilities
    total_caps = sum(
        len(cat['capabilities']) 
        for pillar in capability_framework['pillars'] 
        for cat in pillar['categories']
    )
    
    print(f"✓ Created capability_framework.json")
    print(f"  - {len(capability_framework['pillars'])} pillars")
    print(f"  - {total_caps} total capabilities")
    
    return capability_framework


def list_available_functions():
    """
    List all functions available in business_core_function_taxonomy.json
    for creating function templates
    """
    print("\nListing available functions...")
    
    # Read the business_core_function_taxonomy
    with open('src/data/interim_data_files/business_core_function_taxonomy.json', 'r') as f:
        taxonomy = json.load(f)
    
    # Extract all functions
    functions_to_create = []
    for category in taxonomy['Business_Function']['categories']:
        for func in category['functions']:
            functions_to_create.append({
                'name': func['name'],
                'category': category['category'],
                'processes': func['tools_and_processes'],
                'process_count': len(func['tools_and_processes'])
            })
    
    # Print summary
    print(f"\n✓ Found {len(functions_to_create)} functions to create templates for:")
    print("\nBy Category:")
    
    current_category = None
    for i, func in enumerate(functions_to_create, 1):
        if func['category'] != current_category:
            current_category = func['category']
            print(f"\n  {current_category}:")
        
        print(f"    {i}. {func['name']} ({func['process_count']} processes)")
    
    return functions_to_create


def generate_salvage_report():
    """
    Generate a comprehensive report of the salvage operation
    """
    print("\n" + "="*70)
    print("SALVAGE OPERATION REPORT")
    print("="*70)
    
    # Check what files exist
    data_dir = Path('src/data')
    
    files_created = {
        'pain_point_mapping': data_dir / 'inference_rules/pain_point_mapping.json',
        'ai_archetypes': data_dir / 'inference_rules/ai_archetypes.json',
        'pilot_catalog': data_dir / 'pilot_catalog.json',
        'capability_framework': data_dir / 'capability_framework.json'
    }
    
    print("\nFiles Created:")
    for name, path in files_created.items():
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {path.relative_to('src/data')} ({size:,} bytes)")
        else:
            print(f"  ✗ {path.relative_to('src/data')} (not found)")
    
    # Count function templates
    functions_dir = data_dir / 'organizational_templates/functions'
    if functions_dir.exists():
        function_files = list(functions_dir.glob('*.json'))
        print(f"\nFunction Templates: {len(function_files)}")
        for f in sorted(function_files):
            print(f"  ✓ {f.stem}")
    
    print("\n" + "="*70)


def main():
    """
    Run all salvage operations
    """
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║              SALVAGE OPERATION - INTERIM DATA FILES              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Extract all content
        extract_pain_point_mapping()
        extract_ai_archetypes()
        extract_pilot_catalog()
        extract_capability_framework()
        list_available_functions()
        
        # Generate report
        generate_salvage_report()
        
        print("\n✓ Salvage operation complete!")
        print("\nNext steps:")
        print("  1. Create remaining function templates (14 more)")
        print("  2. Map pain points to outputs in function templates")
        print("  3. Link AI archetypes to pilot types")
        print("  4. Map pilot catalog to applicable outputs")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Make sure you're running this from the project root directory")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
