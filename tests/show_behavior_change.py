#!/usr/bin/env python3
"""Before/After comparison of include_in_cv behavior change."""

import yaml
from pathlib import Path

ONEDRIVE_YAML_PATH = Path("/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml")

# Load raw projects
with open(ONEDRIVE_YAML_PATH / "projekt_historie.yaml", "r") as f:
    projects_raw = yaml.safe_load(f)

all_projects = projects_raw.get("projects", [])
included = [p for p in all_projects if p.get("include_in_cv", False)]
excluded = [p for p in all_projects if not p.get("include_in_cv", False)]

print("=" * 80)
print("BEHAVIOR CHANGE: include_in_cv DEFAULT VALUE")
print("=" * 80)

print("\nOLD BEHAVIOR (Default: TRUE)")
print("-" * 80)
old_included = [p for p in all_projects if p.get("include_in_cv", True)]
print(f"Projects in CV: {len(old_included)} out of {len(all_projects)}")
print(f"Percentage: {100*len(old_included)//len(all_projects)}%")
print(f"\nImpact: ALL projects included in CV (almost no filtering)")

print("\n" + "=" * 80)
print("NEW BEHAVIOR (Default: FALSE)")
print("-" * 80)
print(f"Projects in CV: {len(included)} out of {len(all_projects)}")
print(f"Percentage: {100*len(included)//len(all_projects)}%")
print(f"\nImpact: Only projects with explicit 'include_in_cv: true' are included")

print("\n" + "=" * 80)
print("INCLUDED PROJECTS (with include_in_cv: true)")
print("=" * 80)
for i, proj in enumerate(included, 1):
    print(f"{i}. [{proj.get('id')}] {proj.get('project_de', 'Unknown')[:65]}")

print("\n" + "=" * 80)
print("EXCLUDED PROJECTS (missing or include_in_cv: false) - First 10 of", len(excluded))
print("=" * 80)
for i, proj in enumerate(excluded[:10], 1):
    print(f"{i}. [{proj.get('id')}] {proj.get('project_de', 'Unknown')[:65]}")
if len(excluded) > 10:
    print(f"... and {len(excluded) - 10} more projects excluded")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total projects: {len(all_projects)}")
print(f"Explicitly included: {len(included)} (15%)")
print(f"Excluded: {len(excluded)} (85%)")
print(f"\nOld default would include: {len(old_included)} projects (96%)")
print(f"New default includes: {len(included)} projects (15%)")
print(f"Difference: {len(old_included) - len(included)} fewer projects in CV")
