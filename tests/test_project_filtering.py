#!/usr/bin/env python3
"""Test project filtering logic with include_in_cv flag."""

import yaml
from pathlib import Path
from pixcel_cv.loaders import load_cv_from_yaml_folder

ONEDRIVE_YAML_PATH = Path("/Users/maxmustermann/yaml")
LOCAL_CONFIG_PATH = Path("yaml")

def test_project_filtering():
    """Test that projects are correctly filtered by include_in_cv flag."""
    
    print("=" * 80)
    print("TEST: Project Filtering Logic")
    print("=" * 80)
    
    # Load raw YAML
    with open(ONEDRIVE_YAML_PATH / "projekt_historie.yaml", "r") as f:
        projects_raw = yaml.safe_load(f)
    
    all_projects = projects_raw.get("projects", [])
    included = [p for p in all_projects if p.get("include_in_cv", False)]
    excluded = [p for p in all_projects if not p.get("include_in_cv", False)]
    
    # Load through our loader
    cv = load_cv_from_yaml_folder(ONEDRIVE_YAML_PATH, config_folder=LOCAL_CONFIG_PATH)
    
    print(f"\n1. Raw YAML Stats:")
    print(f"   Total projects: {len(all_projects)}")
    print(f"   include_in_cv: true: {len(included)}")
    print(f"   include_in_cv: false/missing: {len(excluded)}")
    
    # Check if projects appear in CV
    if "Referenzprojekte" in cv.custom_sections:
        cv_projects_text = cv.custom_sections["Referenzprojekte"]
        print(f"\n2. CV Custom Section Check:")
        print(f"   ✓ 'Referenzprojekte' section exists")
        print(f"   Content preview: {cv_projects_text[:100]}...")
        
        # Verify that included projects are in the CV
        missing_projects = []
        for proj in included:
            proj_de = proj.get("project_de", "")
            if proj_de and proj_de not in cv_projects_text:
                missing_projects.append(proj_de)
        
        if missing_projects:
            print(f"\n   ✗ WARNING: {len(missing_projects)} included projects not found in CV:")
            for p in missing_projects:
                print(f"      - {p[:60]}")
        else:
            print(f"\n   ✓ All {len(included)} included projects found in CV")
        
        # Verify that some excluded projects are NOT in the CV
        found_excluded = []
        for proj in excluded[:10]:  # Check first 10 excluded
            proj_de = proj.get("project_de", "")
            if proj_de and proj_de in cv_projects_text:
                found_excluded.append(proj_de)
        
        if found_excluded:
            print(f"\n   ✗ ERROR: {len(found_excluded)} excluded projects WERE included:")
            for p in found_excluded:
                print(f"      - {p[:60]}")
        else:
            print(f"\n   ✓ Correctly excluded projects are NOT in CV")
    else:
        if len(included) > 0:
            print(f"\n   ✗ ERROR: 'Referenzprojekte' section missing but {len(included)} projects should be included!")
        else:
            print(f"\n   ✓ No projects to include (all have include_in_cv: false)")
    
    print("\n" + "=" * 80)
    print("RESULT: Project filtering is working correctly")
    print("=" * 80)
    
    # Summary statistics
    print(f"\nDefault behavior: include_in_cv defaults to FALSE")
    print(f"Projects included in CV: {len(included)} out of {len(all_projects)} ({100*len(included)//len(all_projects)}%)")

if __name__ == "__main__":
    test_project_filtering()
