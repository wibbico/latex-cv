# Pixcel CV - German Pixel-Perfect LaTeX CV Generator

Generate professional, pixel-perfect CVs in German using Python and LaTeX. Control every aspect of your CV layout with clean, maintainable data structures.

## Features

- **Pure Python + YAML**: Define your CV in clean YAML, generate perfect LaTeX
- **German Layout Standards**: DIN A4 optimized with modern moderncv styling
- **Type-Safe**: Full Pydantic validation and MyPy type checking
- **Professional**: Direct PDF export with configurable LaTeX engines
- **Maintainable**: Separation of data (YAML) and presentation (LaTeX templates)
- **Extensible**: Custom sections and template overrides supported

## Project Structure

```
latex-cv/
├── src/pixcel_cv/
│   ├── __init__.py                 # Package entry point
│   ├── models.py                   # Pydantic CV data models
│   ├── loaders.py                  # YAML multi-file loader
│   ├── generator.py                # CV to LaTeX/PDF compiler
│   ├── cli.py                      # Command-line interface
│   └── templates/
│       ├── __init__.py             # Template loader
│       └── german_cv.tex           # Jinja2 LaTeX template
├── yaml/
│   ├── cv_config.yaml              # PDF metadata, professional summary
│   ├── cv_basis.yaml               # Personal data (persoenliche_daten)
│   ├── berufliche_stationen.yaml   # Work experience
│   ├── projekt_historie.yaml       # Projects (with include_in_cv filter)
│   ├── skills.yaml                 # Technical skills
│   └── missionstatement.yaml       # Mission statement
├── tests/
│   ├── test_models.py
│   ├── test_generator.py
│   ├── test_cli.py
│   └── show_behavior_change.py     # Demo script
├── output/                          # Generated PDFs/LaTeX
├── pyproject.toml                   # Dependencies and config
├── README.md
└── IMPLEMENTATION_SUMMARY.md
```

## Architecture & Design Decision

### Data vs. Layout Separation

**Recommendation: YAML for Data + Jinja2 for Templates (chosen approach)**

| Aspect | YAML Data | Markdown | Pure Code |
|--------|-----------|----------|-----------|
| **Data Structure** | ✅ Clean, hierarchical | ❌ Awkward metadata | ❌ Verbose |
| **Layout Control** | ✅ Full Jinja2 flexibility | ⚠️ Limited CSS/styling | ✅ Ultimate control |
| **German Standards** | ✅ Easy to implement | ⚠️ Requires custom CSS | ✅ Can be perfect |
| **Maintainability** | ✅ Easy to update | ✅ Readable | ⚠️ Code sprawl |
| **Type Safety** | ✅ Pydantic validation | ❌ None | ✅ Native |
| **Collaboration** | ✅ Non-tech friendly | ✅ Very friendly | ❌ Dev-only |

**Why YAML + Jinja2?**
1. Clean separation between content and presentation
2. YAML is easily editable by non-developers
3. Jinja2 provides full LaTeX control without compromise
4. Pydantic ensures data integrity
5. Easy to create variants (different languages/styles) without code duplication

## Installation

```bash
# Clone or navigate to project directory
cd latex-cv

# Install dependencies (with uv)
uv sync

# Or install in editable mode
pip install -e .
```

## Quick Start

### 1. Generate CV from Separate YAML Folders

The system loads data from one folder and config from another (recommended for keeping data in sync). **Note: `xelatex` is the recommended engine for modern fonts.**

```bash
# Load data from OneDrive, config from local ./yaml
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --config-folder yaml \
  --pdf output/lebenslauf.pdf --engine xelatex

# Export LaTeX for inspection
uv run python -m pixcel_cv.cli \
  --yaml-folder "/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml" \
  --config-folder yaml \
  --latex output/lebenslauf.tex --pdf output/lebenslauf.pdf --engine xelatex
```

### 2. Or generate from single folder (backward compatible)

```bash
# All YAML files in one folder
uv run python -m pixcel_cv.cli --yaml-folder yaml --pdf output/lebenslauf.pdf
```

### YAML Folder Structure (Multi-File Loader)

The `yaml/` folder uses a **multi-file structure** where:
- **Data files** are loaded from a primary folder (typically OneDrive path with actual CV data)
- **Config file** (`cv_config.yaml`) is loaded from a separate folder (typically local `./yaml`)

Files in `yaml/` folder:

- **cv_config.yaml** - PDF metadata, sections list, professional summary
- **cv_basis.yaml** - Personal data (persoenliche_daten → ContactInfo)
- **berufliche_stationen.yaml** - Work experience (formatted as LaTeX in custom_sections)
- **projekt_historie.yaml** - Project history (only includes projects with `include_in_cv: true`)
- **skills.yaml** - Technical skills with categories
- **missionstatement.yaml** - Professional summary/mission statement

Example:

## Data Models

### CV Structure (Pydantic)

The system converts YAML data into Pydantic models for type-safe validation:

```python
CurriculumVitae
├── contact: ContactInfo (from cv_basis.yaml persoenliche_daten)
│   ├── name: str
│   ├── email: str
│   ├── phone: str (optional)
│   ├── location: str (optional)
├── professional_summary: str (from cv_config.yaml)
├── custom_sections: dict[str, str]  (LaTeX-formatted sections)
│   ├── "Beruflicher Werdegang" (from berufliche_stationen.yaml)
│   ├── "Bildungsweg" (education)
│   ├── "Referenzprojekte" (from projekt_historie.yaml, filtered by include_in_cv)
│   └── Other custom sections
└── skills: list[Skill] (from skills.yaml)
```

### Key Features of Data Models

- **German field names**: `persoenliche_daten`, `berufliche_stationen`, `bildungsweg`
- **LaTeX escaping**: All user-provided text is automatically escaped for LaTeX special characters
- **Project filtering**: Projects only included if `include_in_cv: true` (defaults to false)
- **Custom sections**: Work experience, education, projects stored as formatted LaTeX strings

## Development

### Code Quality

```bash
# Format code
uv run ruff format src/

# Check types
uv run mypy src/

# Lint
uv run ruff check src/ --fix

# Run tests
uv run pytest
```

### Requirements

- **Python**: 3.12+
- **LaTeX**: TeX Live, MiKTeX, or MacTeX
  - Must include `moderncv` package
  - Recommended: `xelatex` for better font support

### Package Dependencies

- `pydantic>=2.0` - Data validation
- `jinja2>=3.0` - Template rendering
- `pyyaml>=6.0` - YAML parsing
- `ruff>=0.3.0` - Formatter & linter
- `mypy>=1.0` - Type checker

## LaTeX Setup

### macOS

```bash
brew install mactex
# or
brew install mactex-no-gui  # smaller download
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install texlive-full
```

### Windows

- Download [MiKTeX](https://miktex.org/) or [TeX Live for Windows](https://tug.org/texlive/windows.html)

## Advanced Usage

### Custom LaTeX Template

Edit `src/pixcel_cv/templates.py` to modify the German template or create variations for different styles.

Template variables available:
- `contact` - ContactInfo object
- `professional_summary` - String
- `work_experience` - List of WorkExperience
- `education` - List of Education
- `skills` - List of Skill
- `languages` - List of Language
- `certifications` - List of Certification
- `custom_sections` - Dict of custom sections

### Programmatic Usage

```python
from pixcel_cv.loaders import load_cv_from_yaml_folder
from pixcel_cv.generator import CVGenerator
from pathlib import Path

# Load CV from separate folders (data + config)
cv = load_cv_from_yaml_folder(
    data_folder=Path("/Users/thomas/Library/CloudStorage/OneDrive-WIBBICOGmbH/#PROFIL/yaml"),
    config_folder=Path("yaml")
)

# Or load from single folder
cv = load_cv_from_yaml_folder(Path("yaml"))

# Generate
generator = CVGenerator(cv)

# Export to LaTeX
latex_source = generator.to_latex()

# Export to PDF
generator.to_pdf(Path("output/cv.pdf"), engine="xelatex")
```

## Examples

See test files in `tests/` for complete examples:
- `test_models.py` - Data model usage
- `test_generator.py` - PDF generation
- `test_cli.py` - CLI examples
- `show_behavior_change.py` - Demo of project filtering behavior

## License

MIT
