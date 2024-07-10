# OpenSciMetrics

OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# Running the app

- From the project's root directory run:

```
docker-compose -f compose.yaml run \
  --rm \
  -v $PWD:/app \
  app \
  rtransparent \
  /mnt/docs/examples/pdf_inputs/test_sample.pdf \
  output.xml
```


# Development

You can use docker-compose for development with the local source code mounted into the app container (this uses compose.override.yaml):

```
docker-compose up
```

If you are changing dependencies or the docker files you will want to rebuild the images:

```
docker-compose up --build
```

Troubleshooting issues with the osm application can be done with:

```
docker-compose run --entrypoint bash app
```

You can also set up this package for local development (on Linux x86 architecture only) by cloning the repo, navigate into the project's root directory, and follow the steps in the [Dockerfile](./Dockerfile) to:
- create a conda environment
- install R dependencies only available from github/CRAN
- install the package in editable mode

Open a terminal tab and run the image `docker run --rm -p 8070 elifesciences/sciencebeam-parser` and keep it running (or use docker-compose as described above).

**Note:** The ScienceBeam image  is not supported on apple silicon chips  with emulation  (using --platform=linux/amd64). The conda environment also doesn't solve at the moment due to various missing packages on this architecture.


## To test that the sciencebeam server is working:

This will work if you have exposed the port 8070 from the sciencebeam container (done for development in the docker override file):
```
curl --fail --show-error     --form "file=@docs/examples/pdf_inputs/test_sample.pdf;filename=test_sample.pdf"     --silent "http://localhost:8070/api/pdfalto"
```

You can alter the above command to work from other containers if you use app_network with the container and target the host "sciencebeam".

## How to run the tests

- Navigate to the project's root directory and run `pytest`

## Using pre-commit for commit checks

Pre-commit will run all of its hooks on every commit you make. To install
pre-commit and its hooks, run the following commands:

```
pip install pre-commit
pre-commit install
```
