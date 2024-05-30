# OpenSciMetrics
OpenSciMetrics (OSM) applies NLP and LLM-based metrics and indicators related to transparency, data sharing, rigor, and open science on biomedical publications.

# How to setup and run the application
- After cloning the repo, navigate into the project's root directory by running `cd osm_cli`
- Run `python -m venv venv` to create a Virtual Environment
- Depending on your system, run the approriate command to Activate the Virtual Environment
Windows: `venv\Scripts\activate`<br>
macOS and Linux: `source venv/bin/activate`

- Next, run `pip install -r requirements.txt` to install all the dependencies.
- Finally, run `python -m osm.cli pdf-xml "path_to_file_name.pdf" file_id`

# How to run tests of the application
Run `tox`
# How to run the unit tests
- Navigate to the project's root directory and run `python -m pytest`
