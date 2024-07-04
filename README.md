# OpenSciMetrics

OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# How to setup and run the application

- After cloning the repo, navigate into the project's root directory by running `cd osm`
- Run `python -m venv venv` to create a Virtual Environment
- Depending on your system, run the approriate command to Activate the Virtual Environment
  Windows: `venv\Scripts\activate`<br>
  macOS and Linux: `source venv/bin/activate`
- Ensure that R is installed on your system. You can download and install it from CRAN.
- Run the following `Rscript install_packages.R` to install the necessary R packages
- Next, run `pip install -e .` to install the package with its dependencies.
- Open a terminal tab and run the image `docker run --rm -p 8070:8070 elifesciences/sciencebeam-parser` and keep it running

**Note:** The ScienceBeam image is not supported by all apple silicon chips. You may need to consider using an alternative systems.

- Finally, run `osm pdf-xml-json "path_to_file_name.pdf" output_file_path`

# How to run tests of the application

Run `tox`

# How to run the unit tests

- Navigate to the project's root directory and run `pytest`

# Using pre-commit for commit checks

Pre-commit will run all of its hooks on every commit you make. To install
pre-commit and its hooks, run the following commands:

```
pip install pre-commit
pre-commit install
```

# How to build the Docker image and run the Docker container

- Navigate to the project's root directory and run `docker-compose up --build`
- When the image is built and the containers are running, open another terminal and start osm container in interactive mode using the command `docker-compose run osm bash`
- You can do file conversions in the container using this command `osm pdf-xml-json "path_to_file_name.pdf" output_file_path`
