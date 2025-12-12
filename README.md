# OpenSciMetrics

OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

## Dashboard

The Open Science Metrics Dashboard visualizes data sharing and code sharing trends across biomedical research funders and journals, based on analysis of PubMed Central publications.

**Live Dashboard:** [https://www.opensciencemetrics.org](https://www.opensciencemetrics.org)

### Features

- **Splitting Variables:** View trends by Journal or Funder
- **Presets:** Quick selection of top journals/funders by data sharing count or percent
- **Aggregation Metrics:** Data Sharing %, Code Sharing %, article counts
- **Interactive Charts:** Toggle individual lines, hover for details
- **Year Range Filter:** Focus on specific time periods (default: 2010-2024)

## CLI Tool (Legacy)

The repository also contains a command line tool for processing individual PDFs and XMLs. Note: This tool is not currently being actively maintained.

With docker-compose and python >=3.11 installed:

```bash
pip install .
osm -f path/to/pdf-or-xml -u uuid
```

For processing many files, start docker-compose dependencies separately:

```bash
docker compose up  # In one terminal
osm -f path/to/pdf-or-xml -u uuid --user-managed-compose  # In another terminal
```

## Contributing

To set up a development environment:

```bash
pip install -e .
docker compose -f compose.yaml -f compose.development.override.yaml up --build
```

In another terminal:

```bash
export OSM_API="http://localhost:80"
osm -f path/to/pdf-or-xml -u uuid --user-managed-compose
```

### Pre-commit Hooks

Pre-commit runs checks on every commit. To install:

```bash
pip install pre-commit
pre-commit install
```

### Apple Silicon Notes

On Apple silicon, you must use emulation:

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
docker pull mongo:4.4.6
```

Note: PDF parsing does not work on Apple silicon.
