# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenSciMetrics (OSM) applies NLP and LLM-based metrics to analyze transparency, data sharing, rigor, and open science indicators in biomedical publications. The project processes PDFs and XML files from sources like PubMed Central.

## Development Commands

```bash
# Install for development
pip install -e .

# Install with optional dependencies
pip install -e ".[dev]"      # Development tools (pytest, ruff, tox)
pip install -e ".[server]"   # FastAPI server
pip install -e ".[llm]"      # LLM extraction tools
pip install -e ".[plot]"     # Visualization (streamlit, plotly, panel)

# Run tests
pytest tests/
tox                          # Run full test suite with tox

# Run a single test
pytest tests/test_schema_helpers.py -v
pytest tests/test_schema_helpers.py::test_function_name -v

# Linting and formatting (via pre-commit)
pip install pre-commit
pre-commit install
pre-commit run --all-files   # Run all hooks manually

# Run the CLI
osm -f path/to/pdf-or-xml -u uuid

# Development with docker-compose
docker compose -f compose.yaml -f compose.development.override.yaml up --build
# In another terminal:
export OSM_API="http://localhost:80"
osm -f path/to/pdf-or-xml -u uuid --user-managed-compose
```

## Architecture

### Core Pipeline (`osm/pipeline/`)

The processing pipeline follows a modular design with three component types:

1. **Parsers** (`parsers.py`) - Convert input documents to XML
   - `ScienceBeamParser`: Converts PDFs to TEI XML via elifesciences/sciencebeam-parser
   - `PMCParser`/`NoopParser`: Pass-through for XML files from PubMed Central

2. **Extractors** (`extractors.py`) - Extract metrics from XML
   - `RTransparentExtractor`: Calls rtransparent R service on port 8071

3. **Savers** (`savers.py`) - Persist results
   - `FileSaver`: Writes files to disk
   - `JSONSaver`: Writes JSON metrics
   - `OSMSaver`: Uploads to OSM API/MongoDB

The `Pipeline` class (`core.py`) orchestrates these: parsers → extractors → savers.

### Schemas (`osm/schemas/`)

Pydantic/Odmantic models for MongoDB persistence:
- `Invocation`: Main document model containing metrics, components, work reference
- `RtransparentMetrics`: ~190 boolean/string fields for transparency indicators (COI, funding, registration, open data/code)
- `Work`: Publication identifiers (pmid, doi, openalex_id)
- `Component`: Tracks parser/extractor versions

### External Components (`external_components/`)

- `rtransparent/`: R service exposing rtransparent package via HTTP (port 8071)
- `llm_extraction/`: LLM-based extraction tools

### Web Components (`web/`)

- `api/`: FastAPI backend (port 80) - receives processed metrics
- `dashboard/`: Streamlit dashboard (port 8501) - visualizes metrics data
- `deploy/terraform/`: OpenTofu IaC for AWS deployment

## Docker Services

Production compose (`compose.yaml`):
- `sciencebeam`: PDF parser on port 8070
- `rtransparent`: R metrics extraction on port 8071

Development compose adds (`compose.development.override.yaml`):
- `db`: MongoDB on port 27017
- `dashboard`: Streamlit on port 8501
- `web_api`: FastAPI on port 80

## Code Conventions

- Prefer `httpx` over `requests` for HTTP requests
- Use type hints everywhere possible
- Pre-commit hooks enforce: ruff (lint/format), isort, trailing whitespace, OpenTofu validation

## Infrastructure Deployment

Uses OpenTofu (>=1.8.0) for AWS infrastructure. See `web/deploy/terraform/README.md` for:
- State resource bootstrap (one-time manual step)
- Shared/staging/production deployments
- Required GitHub secrets (AWS credentials, SSH keys, MongoDB URI)

CI/CD workflows in `.github/workflows/`:
- `tests.yml`: Run pytest
- `lint.yml`: Run linting
- `build-docker.yml`: Build Docker images
- `deploy-docker.yml`: Deploy to staging/production
- `deploy-opentofu.yml`: Infrastructure deployment

## Key Data Flow

1. User provides PDF/XML + unique ID via CLI
2. PDF → ScienceBeam → TEI XML (skipped for PMC XML)
3. XML → RTransparent → 190+ transparency metrics
4. Results → local JSON + OSM API (MongoDB)
5. Dashboard queries MongoDB for visualization
