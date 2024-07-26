# OpenSciMetrics

OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# Running the app

N.B. pdf parsing does not work on Apple silicon...

- With docker-compose and python >3.11 installed, runng the following from the project's root directory:

```
pip install .
osm -f path/to/pdf-or-xml -u uuid
```

## Using pre-commit for commit checks

Pre-commit will run all of its hooks on every commit you make. To install
pre-commit and its hooks, run the following commands:

```
pip install pre-commit
pre-commit install
```
