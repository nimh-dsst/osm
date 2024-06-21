# OpenSciMetrics
OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# How to setup and run the application
- After cloning the repo, navigate into the project's root directory by running `cd osm`
- Run `python -m venv venv` to create a Virtual Environment
- Depending on your system, run the approriate command to Activate the Virtual Environment
Windows: `venv\Scripts\activate`<br>
macOS and Linux: `source venv/bin/activate`

- Next, run `pip install -e .` to install the package with its dependencies.
- Open a terminal tab and run the image `docker run --rm -p 8082:8070 elifesciences/sciencebeam-parser` and keep it running for the rest of the testing period
- Go back to terminal(root folder)
- Finally, run `osm pdf-xml "path_to_file_name.pdf" file_id`

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
