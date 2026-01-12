#!/usr/bin/env python3
"""Test OneDrive integration and project filtering logic."""

from pathlib import Path
from pixcel_cv.loaders import load_cv_from_yaml_folder

# Path to OneDrive YAML files
ONEDRIVE_YAML_PATH = Path("/Users/maxmustermann/yaml")
LOCAL_CONFIG_PATH = Path("yaml")

print("=" * 80)
print("TEST 1: Load CV with OneDrive data and local config")
print("=" * 80)

try:
    cv = load_cv_from_yaml_folder(ONEDRIVE_YAML_PATH, config_folder=LOCAL_CONFIG_PATH)
    print("✓ CV loaded successfully")
    print(f"  Name: {cv.contact.name}")
    print(f"  Email: {cv.contact.email}")
    print(f"  Phone: {cv.contact.phone}")
    print(f"  Location: {cv.contact.location}")
except Exception as e:
    print(f"✗ Error loading CV: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 2: Check custom sections (work experience, education, projects)")
print("=" * 80)

try:
    print(f"Custom sections found: {list(cv.custom_sections.keys())}")
    
    for section_name, content in cv.custom_sections.items():
        lines = content.split('\n')
        print(f"\n  {section_name}: {len(lines)} lines")
        print(f"    Preview: {lines[0][:60]}...")
except Exception as e:
    print(f"✗ Error checking sections: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 3: Verify project filtering (only include_in_cv: true projects)")
print("=" * 80)

try:
    # Load the raw projects
    import yaml
    with open(ONEDRIVE_YAML_PATH / "projekt_historie.yaml", "r") as f:
        projects_raw = yaml.safe_load(f)
    
    total_projects = len(projects_raw.get("projects", []))
    included_projects = [p for p in projects_raw.get("projects", []) if p.get("include_in_cv", False)]
    excluded_projects = [p for p in projects_raw.get("projects", []) if not p.get("include_in_cv", False)]
    
    print(f"  Total projects in YAML: {total_projects}")
    print(f"  Projects with include_in_cv: true: {len(included_projects)}")
    print(f"  Projects with include_in_cv: false/missing: {len(excluded_projects)}")
    
    if included_projects:
        print(f"\n  Included projects:")
        for p in included_projects[:5]:  # Show first 5
            print(f"    - {p.get('id')}: {p.get('project_de', 'Unknown')}")
        if len(included_projects) > 5:
            print(f"    ... and {len(included_projects) - 5} more")
    
    if excluded_projects:
        print(f"\n  Excluded projects (first 5):")
        for p in excluded_projects[:5]:
            print(f"    - {p.get('id')}: {p.get('project_de', 'Unknown')}")
        if len(excluded_projects) > 5:
            print(f"    ... and {len(excluded_projects) - 5} more")
    
    # Check if projects appear in CV custom sections
    if "Referenzprojekte" in cv.custom_sections:
        print(f"\n  ✓ Projects section found in CV")
        lines = cv.custom_sections["Referenzprojekte"].split('\n')
        print(f"    Content length: {len(lines)} lines")
    else:
        print(f"\n  ℹ No projects section (all may be filtered out)")
    
except Exception as e:
    print(f"✗ Error checking projects: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 4: Check skills and languages")
print("=" * 80)

try:
    print(f"  Skills categories: {len(cv.skills)}")
    for skill in cv.skills[:3]:  # Show first 3 categories
        print(f"    - {skill.category}: {len(skill.items)} items")
    if len(cv.skills) > 3:
        print(f"    ... and {len(cv.skills) - 3} more categories")
    
    print(f"\n  Languages: {len(cv.languages)}")
    for lang in cv.languages:
        print(f"    - {lang.name}: {lang.level}")
except Exception as e:
    print(f"✗ Error checking skills: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 5: Check professional summary")
print("=" * 80)

try:
    if cv.professional_summary:
        summary_lines = cv.professional_summary.split('\n')
        print(f"✓ Professional summary found ({len(summary_lines)} lines)")
        print(f"  Preview: {cv.professional_summary[:100]}...")
    else:
        print("ℹ No professional summary")
except Exception as e:
    print(f"✗ Error checking summary: {e}")

print("\n" + "=" * 80)
print("TEST 6: Test LaTeX generation")
print("=" * 80)

try:
    from src.pixcel_cv.generator import CVGenerator
    generator = CVGenerator(cv)
    latex = generator.to_latex()
    
    print(f"✓ LaTeX generated successfully ({len(latex)} chars)")
    
    # Check for critical content
    checks = [
        ("\\documentclass", "Document class"),
        (cv.contact.name, "Contact name"),
        ("Fachliche Zusammenfassung", "Summary section"),
        ("Beruflicher Werdegang", "Work experience section"),
    ]
    
    print("\n  LaTeX content checks:")
    for check_str, description in checks:
        if check_str in latex:
            print(f"    ✓ {description} found")
        else:
            print(f"    ✗ {description} NOT found")
    
except Exception as e:
    print(f"✗ Error generating LaTeX: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("All tests completed. Check results above for any failures.")
print("\nKey findings:")
print(f"  - OneDrive YAML path: {ONEDRIVE_YAML_PATH}")
print(f"  - Local config path: {LOCAL_CONFIG_PATH}")
print(f"  - Default include_in_cv: FALSE (only projects explicitly marked true are included)")
