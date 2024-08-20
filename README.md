# OpenSciMetrics

OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# Running the app

N.B. pdf parsing does not work on Apple silicon...

- With docker-compose and python >=3.11 installed, run the following from the project's root directory:

```
pip install .
osm -f path/to/pdf-or-xml -u uuid
```

If you have many files to upload you may with to start up the docker-compose  dependencies in a separate terminal window:

```
docker compose up # docker-compose on some systems
```

And then tell the osm tool that this has been handled:

```
osm -f path/to/pdf-or-xml -u uuid --user-managed-compose
osm -f path/to/pdf-or-xml2 -u uuid2 --user-managed-compose
```

# Contributing

If you wish to contribute to this project you can set up a development environment with the following:

```
pip install -e .
docker compose -f compose.yaml -f compose.development.override.yaml up --build
```
And in another terminal:

```
export OSM_API="http://localhost:80"
osm -f path/to/pdf-or-xml -u uuid --user-managed-compose
```


## Using pre-commit for commit checks

Pre-commit will run all of its hooks on every commit you make. To install
pre-commit and its hooks, run the following commands:

```
pip install pre-commit
pre-commit install
```
