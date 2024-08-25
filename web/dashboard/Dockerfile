FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /app


# Create the environment
RUN pip install holoviews panel pymongo odmantic pandas pyarrow pydantic[email]

RUN mkdir -p /opt/data
ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
COPY ./tempdata/matches.parquet /opt/data/matches.parquet

RUN mkdir -p /opt/osm
COPY pyproject.toml /opt/osm
COPY osm /opt/osm/osm
ARG PSEUDO_VERSION=0.0.1 # strongly recommended to update based on git describe
RUN SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=${PSEUDO_VERSION} pip install -e /opt/osm
RUN --mount=source=.git,target=/opt/osm/.git,type=bind pip install -e /opt/osm

# # Copy the project files and install the package
COPY web/dashboard/ /app
CMD ["python", "app.py"]
