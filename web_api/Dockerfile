FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /app

COPY ./web_api/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/app/requirements.txt

# Consider installing from pypi
RUN mkdir -p /opt/osm
COPY pyproject.toml /opt/osm
COPY osm /opt/osm/osm
ARG PSEUDO_VERSION=0.0.1 # strongly recommended to update based on git describe
RUN SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=${PSEUDO_VERSION} pip install -e /opt/osm
RUN --mount=source=.git,target=/opt/osm/.git,type=bind pip install -e /opt/osm
COPY ./web_api/main.py /app/app/main.py

# relies on the fact that the uvicorn-gunicorn image has a default CMD
