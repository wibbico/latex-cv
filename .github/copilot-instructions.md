# AI Coding Agent Instructions - Pixcel CV

## Project Overview
German LaTeX CV generator using Python, YAML, and Jinja2. Converts structured CV data (YAML) into pixel-perfect German CVs (PDF) via LaTeX templates.

**Core Architecture**: YAML Data → Pydantic Models → Jinja2 Templates → LaTeX → PDF

## Critical File Structure

```
src/pixcel_cv/
├── models.py          # Pydantic models: CurriculumVitae, ContactInfo, WorkExperience, etc.
├── loaders.py         # YAML → Pydantic conversion (MULTI-FILE YAML LOADER)
├── generator.py       # CV model → LaTeX → PDF compilation
├── templates/
│   └── german_cv.tex  # Jinja2 template with custom delimiters (<VAR>, <BLOCK>)
└── cli.py             # CLI entry point

yaml/                  # NEW STRUCTURE (migrated from OneDrive 2026-01-03)
├── cv_config.yaml     # PDF metadata, sections, professional summary
├── cv_basis.yaml      # persoenliche_daten, bildungsweg
├── berufliche_stationen.yaml  # Work experience
├── projekt_historie.yaml      # Projects with include_in_cv flag
├── skills.yaml
├── basedata.yaml
└── missionstatement.yaml
```

## YAML Loading Architecture (CRITICAL)

**Multi-file loader in `loaders.py::load_cv_from_yaml_folder(data_folder, config_folder)`**:
- Loads 7+ separate YAML files and merges into single `CurriculumVitae` model
- **Key migration (2026-01-03)**: New structure from OneDrive with German field names
- **Data files** loaded from primary folder (typically OneDrive path)
- **Config file** (cv_config.yaml) loaded from separate config folder (typically local ./yaml)
- **Projects filtering**: Only includes projects where `include_in_cv: true` (DEFAULTS TO FALSE)
- **Work experience & education**: Converted to LaTeX-formatted custom sections, NOT model lists
- **LaTeX escaping**: All user content runs through `_escape_latex()` to handle special chars

### Example YAML → Model Flow:
```python
# From OneDrive path:
# cv_basis.yaml: persoenliche_daten → ContactInfo
# berufliche_stationen.yaml → custom_sections["Beruflicher Werdegang"]
# projekt_historie.yaml (filtered) → custom_sections["Referenzprojekte"]

# From local ./yaml:
# cv_config.yaml → professional_summary and text sections
```

## Jinja2 Template Conventions

**Custom Delimiters** (avoid LaTeX conflicts):
- Variables: `<VAR>cv.contact.name</VAR>` (NOT `{{ }}`)
- Blocks: `<BLOCK>if cv.skills</BLOCK>...<BLOCK>endif</BLOCK>` (NOT `{% %}`)
- Comments: `<COMMENT>...</COMMENT>`

**Template location**: `src/pixcel_cv/templates/german_cv.tex`
**Loader**: `templates/__init__.py::load_german_cv_template()`

## Development Workflows

### Generate CV
```bash
# From OneDrive folder with local config
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --config-folder yaml \
  --pdf output/lebenslauf.pdf

# Shorthand (if cv_config.yaml is in same folder)
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --pdf output/lebenslauf.pdf

# Export LaTeX for inspection
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --config-folder yaml \
  --latex output/cv.tex --pdf output/cv.pdf

# Use XeLaTeX for better fonts
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --config-folder yaml \
  --pdf output/cv.pdf --engine xelatex
```

### Testing
```bash
uv run pytest                    # Run all tests
uv run pytest tests/test_loaders.py  # Test YAML loading
```

### Code Quality
```bash
uv run ruff check src/           # Lint
uv run ruff format src/          # Format
uv run mypy src/                 # Type check (strict mode)
```

## Project-Specific Patterns

### 1. LaTeX Special Character Escaping
**Always use `_escape_latex()` in loaders.py** when building custom sections:
```python
title_safe = _escape_latex(title)  # Handles &, %, #, _, ^, ~, {, }, \, $
```

### 2. Custom Sections Pattern
Work experience, education, and projects are stored as **LaTeX strings in `custom_sections` dict**, not as model lists:
```python
custom_sections["Beruflicher Werdegang"] = latex_formatted_work_history
custom_sections["Bildungsweg"] = latex_formatted_education
custom_sections["Referenzprojekte"] = latex_formatted_projects
```

### 3. Date Handling
German dates use MM.YYYY format as strings (e.g., "06.2017", "heute"), NOT Python date objects in work/education sections.

### 4. Project Filtering Logic
```python
# In loaders.py - projects must have include_in_cv: true (DEFAULTS TO FALSE)
filtered_projects = [p for p in projects_list if p.get("include_in_cv", False)]
```

## Key Dependencies
- **Pydantic 2.x**: Data validation (strict mode)
- **Jinja2**: Template rendering with custom delimiters
- **PyYAML**: YAML parsing
- **LaTeX distribution**: pdflatex/xelatex/lualatex must be installed on system

## Type Safety Requirements
- Python 3.12+ with strict MyPy (`disallow_untyped_defs = true`)
- All functions in `src/` must have type hints
- Use `Path` objects, not strings, for file operations

## Common Pitfalls

1. **Don't use default Jinja2 delimiters** in `.tex` files - they conflict with LaTeX
2. **Don't forget LaTeX escaping** - raw YAML strings will break LaTeX compilation
3. **YAML field names are German** in new structure: `persoenliche_daten`, `bildungsweg`, `berufliche_stationen`
4. **Work experience is NOT in `cv.work_experience`** - it's in `cv.custom_sections["Beruflicher Werdegang"]` as LaTeX
5. **PDF compilation runs twice** - required for LaTeX references to resolve properly
6. **Old YAML structure removed** - don't reference old `profile_data` patterns; fallbacks exist for compatibility

## When Modifying YAML Structure
1. Update `loaders.py::load_cv_from_yaml_folder()` to parse new fields
2. Apply `_escape_latex()` to all user-provided strings
3. Maintain backward compatibility with fallback logic
4. Update `cv_config.yaml` if adding new PDF metadata
5. Test with: `uv run python -m pixcel_cv.cli --yaml-folder yaml --pdf output/test.pdf`
