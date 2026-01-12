.PHONY: test lint format type-check create run run-two-column run-minimalist run-timeline run-anschreiben cv cv-portrait

# Default fallback if not set in .env
# Uses sample YAML files in yaml/examples/ as default
EXTERNAL_YAML_FOLDER ?= yaml/examples

# If a local .env exists, include it so `make` sees variables like
# EXTERNAL_YAML_FOLDER, PORTRAIT_PATH. Lines must be in `KEY=VALUE` form.
ifneq (,$(wildcard .env))
include .env
endif

export EXTERNAL_YAML_FOLDER
export PORTRAIT_PATH

test:
	uv run pytest

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

type-check:
	uv run mypy src/

cv:
	uv run python -m pixcel_cv.cli \
  --yaml-folder "$(EXTERNAL_YAML_FOLDER)" \
  --config-folder yaml \
  --pdf output/lebenslauf-timeline.pdf --engine xelatex --template timeline \
  --latex output/timeline_check2.tex

cv-portrait:
	uv run python -m pixcel_cv.cli \
  --yaml-folder "$(EXTERNAL_YAML_FOLDER)" \
  --config-folder yaml \
  --portrait "$(PORTRAIT_PATH)" \
  --pdf output/lebenslauf-with-portrait.pdf --engine xelatex \
  --latex output/cv_with_portrait.tex

anschreiben:
	uv run python -m pixcel_cv.cli $(EXTERNAL_YAML_FOLDER)/anschreiben.yaml \
  --pdf output/anschreiben.pdf \
  --latex output/anschreiben.tex \
  --engine pdflatex
